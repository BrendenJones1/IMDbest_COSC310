from fastapi import APIRouter, Depends, HTTPException, Query
from backend.utils.security import decode_access_token, require_admin
from backend.services.users_service import user_service

router = APIRouter(prefix="/admin", tags=["admin"])

# -------------------------------
# LIST USERS
# -------------------------------
@router.get("/users")
def list_all_users(current_user: dict = Depends(decode_access_token)):
    require_admin(current_user)
    return user_service.list_users()


# -------------------------------
# DELETE A USER 
# -------------------------------
@router.delete("/users/{user_id}")
def delete_user(user_id: str, current_user: dict = Depends(decode_access_token)):
    require_admin(current_user)
    return user_service.delete_user(user_id)


# -------------------------------
# PROMOTE USER TO ADMIN 
# -------------------------------
@router.post("/users/{user_id}/promote")
def promote_user(user_id: str, current_user: dict = Depends(decode_access_token)):
    require_admin(current_user)
    try:
        updated_user = user_service.promote_user(user_id)
        return {"message": f"User {user_id} promoted to admin.", "user": updated_user}
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# -------------------------------
# GET A USER'S REVIEWS
# -------------------------------
@router.get("/users/{user_id}/reviews")
def get_user_reviews(user_id: str, current_user: dict = Depends(decode_access_token)):
    require_admin(current_user)
    return user_service.get_user_reviews(user_id)

# -------------------------------
# DELETE A USER'S REVIEW
# -------------------------------
@router.delete("/users/{user_id}/reviews/delete")
def delete_user_review(user_id: str, movie_id: str, current_user: dict = Depends(decode_access_token)):
    require_admin(current_user)
    return user_service.remove_review_from_user(user_id, movie_id)

# -------------------------------
# SEARCH USERS
# -------------------------------
@router.get("/users/search")
def search_users(
        username: str | None = Query(None),
        email: str | None = Query(None),
        role: str | None = Query(None),
        current_user: dict = Depends(decode_access_token)
        ):
    require_admin(current_user)
    return user_service.search_users_admin(username=username, email=email, role=role)
    

from backend.services.flags_service import FlagsService
flags_service = FlagsService()

# -------------------------------
# GET ALL FLAGS
# -------------------------------
@router.get("/flags")
def get_all_flags(current_user: dict = Depends(decode_access_token)):
    require_admin(current_user)
    return flags_service.get_all_flags()


# -------------------------------
# GET ALL PENALTIES FOR A USER
# -------------------------------
@router.get("/users/{user_id}/penalties")
def admin_get_penalties(user_id: str, current_user=Depends(decode_access_token)):
    require_admin(current_user)
    return user_service.get_user_penalties(user_id)


# -------------------------------
# ISSUE A PENALTY TO A USER
# -------------------------------
@router.post("/users/{user_id}/penalties")
def admin_add_penalty(
    user_id: str,
    reason: str,
    flag_id: str | None = None,
    current_user=Depends(decode_access_token)
):
    require_admin(current_user)
    admin_id = current_user["sub"]  # the issuing admin

    new_penalty = user_service.add_penalty_to_user(
        user_id=user_id,
        reason=reason,
        admin_id=admin_id,
        flag_id=flag_id
    )
    return new_penalty


# -------------------------------
# DEACTIVATE A PENALTY
# -------------------------------
@router.put("/penalties/{penalty_id}/deactivate")
def admin_deactivate_penalty(
    penalty_id: int,
    current_user=Depends(decode_access_token)
):
    require_admin(current_user)
    admin_id = current_user["sub"]

    result = user_service.deactivate_penalty(penalty_id, admin_id)
    if not result:
        raise HTTPException(status_code=404, detail="Penalty not found or already inactive")

    return result

# -------------------------------
# GET FLAGS
# -------------------------------
@router.get("/flags")
def get_all_flags(current_user: dict = Depends(decode_access_token)):
    require_admin(current_user)
    return user_service.flags_service.get_all_flags()

# -------------------------------
# GET FLAGS BY PENDING
# -------------------------------
@router.get("/flags/pending")
def get_pending_flags(current_user: dict = Depends(decode_access_token)):
    require_admin(current_user)
    return user_service.flags_service.get_pending_flags()

# -------------------------------
# CHANGE A FLAG STATUS
# -------------------------------
@router.put("/flags/{flag_id}/status")
def update_flag_status(
    flag_id: int,
    new_status: str,
    current_user: dict = Depends(decode_access_token),
):
    require_admin(current_user)

    if new_status not in {"approved", "rejected", "pending"}:
        return {"error": "invalid status"}

    updated = user_service.change_flag_status(flag_id, new_status)
    if not updated:
        return {"error": "flag not found"}

    return updated
