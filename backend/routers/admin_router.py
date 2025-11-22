from fastapi import APIRouter, Depends, HTTPException, Query
from backend.utils.security import decode_access_token, require_admin
from backend.services.users_service import user_service
from backend.services.flags_service import FlagsService

router = APIRouter(prefix="/admin", tags=["admin"])
flags_service = FlagsService()

flags_service = FlagsService()


@router.get("/users")
def list_all_users(current_user: dict = Depends(decode_access_token)):
    """
    Return a list of all users for administrative review and management.
    """
    require_admin(current_user)
    return user_service.list_users()


@router.delete("/users/{user_id}")
def delete_user(user_id: str, current_user: dict = Depends(decode_access_token)):
    """
    Permanently delete a user account identified by user_id.
    """
    require_admin(current_user)
    return user_service.delete_user(user_id)


@router.post("/users/{user_id}/promote")
def promote_user(user_id: str, current_user: dict = Depends(decode_access_token)):
    """
    Elevate a user to admin role and return the updated user record.
    """
    require_admin(current_user)
    try:
        updated_user = user_service.promote_user(user_id)
        return {"message": f"User {user_id} promoted to admin.", "user": updated_user}
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/users/{user_id}/reviews")
def get_user_reviews(user_id: str, current_user: dict = Depends(decode_access_token)):
    """
    Retrieve all reviews authored by a specific user.
    """
    require_admin(current_user)
    return user_service.get_user_reviews(user_id)


@router.delete("/users/{user_id}/reviews/delete")
def delete_user_review(
    user_id: str,
    movie_id: str,
    current_user: dict = Depends(decode_access_token),
):
    """
    Remove a specific review by a user for the given movie.
    """
    require_admin(current_user)
    return user_service.remove_review_from_user(user_id, movie_id)


@router.get("/users/search")
def search_users(
    username: str | None = Query(None),
    email: str | None = Query(None),
    role: str | None = Query(None),
    current_user: dict = Depends(decode_access_token),
):
    """
    Search users by optional username, email, and role filters for admin use.
    """
    require_admin(current_user)
    return user_service.search_users_admin(username=username, email=email, role=role)


@router.get("/flags")
def get_all_flags(current_user: dict = Depends(decode_access_token)):
    """
    Retrieve all content flags for administrative review.
    """
    require_admin(current_user)
    return flags_service.get_all_flags()


@router.get("/users/{user_id}/penalties")
def admin_get_penalties(user_id: str, current_user=Depends(decode_access_token)):
    """
    Retrieve all penalties associated with a specific user.
    """
    require_admin(current_user)
    return user_service.get_user_penalties(user_id)


@router.post("/users/{user_id}/penalties")
def admin_add_penalty(
    user_id: str,
    reason: str,
    flag_id: str | None = None,
    current_user=Depends(decode_access_token),
):
    """
    Issue a new penalty to a user, optionally linking it to a flag.
    """
    require_admin(current_user)
    admin_id = current_user["sub"]  # id of the admin issuing this penalty

    new_penalty = user_service.add_penalty_to_user(
        user_id=user_id,
        reason=reason,
        admin_id=admin_id,
        flag_id=flag_id,
    )
    return new_penalty


@router.put("/penalties/{penalty_id}/deactivate")
def admin_deactivate_penalty(
    penalty_id: int,
    current_user=Depends(decode_access_token),
):
    """
    Deactivate an existing penalty so it no longer counts against the user.
    """
    require_admin(current_user)
    admin_id = current_user["sub"]

    result = user_service.deactivate_penalty(penalty_id, admin_id)
    if not result:
        raise HTTPException(status_code=404, detail="Penalty not found or already inactive")

    return result

@router.get("/flags")
def get_all_flags(current_user: dict = Depends(decode_access_token)):
    """
    Retrieve all flags using the flags service attached to the user service.
    """
    require_admin(current_user)
    return user_service.flags_service.get_all_flags()


@router.get("/flags/pending")
def get_pending_flags(current_user: dict = Depends(decode_access_token)):
    """
    Retrieve only flags that are still in a pending review state.
    """
    require_admin(current_user)
    return user_service.flags_service.get_pending_flags()


@router.put("/flags/{flag_id}/status")
def update_flag_status(
    flag_id: int,
    new_status: str,
    current_user: dict = Depends(decode_access_token),
):
    """
    Update the status of a flag (approved, rejected, or pending) and return the result.
    """
    require_admin(current_user)

    if new_status not in {"approved", "rejected", "pending"}:
        raise HTTPException(status_code=400, detail="invalid status")

    updated = user_service.change_flag_status(flag_id, new_status)
    if not updated:
        raise HTTPException(status_code=404, detail="flag not found")

    return updated
