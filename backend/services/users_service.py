import uuid
from typing import List, Dict, Any
from datetime import datetime

from fastapi import HTTPException, status

from schemas.user import UserCreate, UserUpdate, UserPublic, User, CurrentUser
from utils.security import hash_password, verify_password, create_access_token

from backend.repositories.users_repo import UserRepository, user_repository
from backend.schemas.review import ReviewOut
from backend.services.review_service import ReviewService
from backend.services.penalties_service import PenaltiesService
from backend.services.flags_service import FlagsService
<<<<<<< HEAD

=======
from datetime import datetime, timezone
>>>>>>> main

class UserService:
    """
    Coordinate user lifecycle operations, including auth, profile updates,
    reviews, penalties, and moderation flags.
    """

    def __init__(
        self,
        user_repo: UserRepository = user_repository,
        review_service: ReviewService | None = None,
        penalty_service: PenaltiesService | None = None,
        flags_service: FlagsService | None = None,
    ) -> None:
        """
        Initialize the user service with its backing repository and related services.
        """
        self.user_repo = user_repo
        self.review_service = review_service or ReviewService()
        self.penalty_service = penalty_service or PenaltiesService()
        self.flags_service = flags_service or FlagsService()

    def list_users(self) -> List[UserPublic]:
        """
        Return all users as public-safe representations.
        """
        return [UserPublic(**it) for it in (self.user_repo.load_users() or [])]

    def save_user(self, payload: CurrentUser) -> None:
        """
        Persist changes to a current user payload (e.g., updated token_version) back to storage.
        """
        users = self.user_repo.load_users() or []

        target_username = payload.username.strip().lower()
        updated = False

        for user in users:
            if user.username.strip().lower() == target_username:
                user.token_version = payload.token_version
                updated = True
                break

        if not updated:
            raise ValueError(f"User {payload.username} not found")

        self.user_repo.save_users(users)

    # ---------------------------------
    #   REGISTRATION/LOGIN
    # ---------------------------------
    def register(self, payload: UserCreate) -> Dict[str, Any]:
        """
        Register a new user, enforcing unique username and email, and issue an access token.
        """
        users = self.user_repo.load_users() or []
        new_id = str(uuid.uuid4())

        if any(it.get("id") == new_id for it in users):
            raise HTTPException(status_code=409, detail="ID collision; retry.")

        if any(it.get("username").lower() == payload.username.strip().lower() for it in users):
            raise HTTPException(status_code=409, detail="Username taken.")

        if any(it.get("email").lower() == payload.email.strip().lower() for it in users):
            raise HTTPException(status_code=409, detail="Email in use.")

        is_first_user = len(users) == 0
        role = "admin" if is_first_user else "user"

        new_user = User(
            id=new_id,
            username=payload.username.strip(),
            email=payload.email.strip(),
            password_hash=hash_password(payload.password),
            role=role,
            penalties=[],
            reviews=[],
            watchlist=[],
            token_version=0,
<<<<<<< HEAD
            registered_at=datetime.utcnow(),
=======
            registered_at=datetime.now(timezone.utc)
>>>>>>> main
        ).model_dump()

        users.append(new_user)
        self.user_repo.save_users(users)

        token = create_access_token(new_user["id"], new_user["role"], new_user["token_version"])
        return {"token": token, "user": UserPublic(**new_user)}

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user by username and password, returning a new access token on success.
        """
        try:
            user = self._internal_get_user(username)
        except HTTPException:
            # Normalize to a generic auth error to avoid leaking existence of accounts
            raise HTTPException(status_code=401, detail="Username or password incorrect")

        if not verify_password(password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Username or password incorrect")

        token = create_access_token(
            sub=user["id"],
            role=user["role"],
            token_version=user["token_version"],
        )

        return {"token": token, "user": UserPublic(**user)}

    # ---------------------------------
    #   GET USER
    # ---------------------------------
    def get_user_by_id(self, user_id: str) -> UserPublic:
        """
        Retrieve a single user as public data by their unique id.
        """
        users = self.user_repo.load_users() or []
        for it in users:
            if it.get("id") == user_id:
                return UserPublic(**it)
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

    def get_user_by_username(self, username: str) -> UserPublic:
        """
        Retrieve a single user as public data by their username.
        """
        users = self.user_repo.load_users() or []
        for it in users:
            if it.get("username").lower() == username.lower():
                return UserPublic(**it)
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")

    # Returns *internal* user dict (with email, hash, penalties, etc.)
    def _internal_get_user(self, username: str) -> dict:
        """
        Return the full internal user record (including sensitive fields) by username.
        """
        users = self.user_repo.load_users() or []
        for it in users:
            if it.get("username").lower() == username.lower():
                return it
        raise HTTPException(status_code=404, detail="User not found")

    # ---------------------------------
    #   USER UPDATE/DELETE
    # ---------------------------------
    def update_user(self, user_id: str, payload: UserUpdate) -> UserPublic:
        """
        Apply partial updates to a user profile, respecting uniqueness and password hashing rules.
        """
        users = self.user_repo.load_users() or []

        for idx, it in enumerate(users):
            if it["id"] == user_id:
                stored = User(**it)
                update_data = payload.model_dump(exclude_unset=True)

                # Unique username validation
                if "username" in update_data:
                    update_data["username"] = update_data["username"].strip()
                    if any(
                        u["username"].lower() == update_data["username"].lower()
                        and u["id"] != user_id
                        for u in users
                    ):
                        raise HTTPException(status_code=409, detail="Username taken.")

                # Unique email validation
                if "email" in update_data:
                    update_data["email"] = update_data["email"].strip()
                    if any(
                        u["email"].lower() == update_data["email"].lower()
                        and u["id"] != user_id
                        for u in users
                    ):
                        raise HTTPException(status_code=409, detail="Email in use.")

                # Secure password handling
                if "password" in update_data:
                    update_data["password_hash"] = hash_password(
                        update_data.pop("password")
                    )

                updated = stored.model_copy(update=update_data)
                users[idx] = updated.model_dump()
                self.user_repo.save_users(users)
                return UserPublic(**updated.model_dump())

        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

    def delete_user(self, user_id: str) -> None:
        """
        Permanently remove a user record by id.
        """
        users = self.user_repo.load_users() or []
        new_users = [it for it in users if it.get("id") != user_id]
        if len(new_users) == len(users):
            raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
        self.user_repo.save_users(new_users)

    # ---------------------------------
    #   SEARCH USERS
    # ---------------------------------
    def search_users(self, username: str = "") -> list[dict]:
        """
        Perform a case-insensitive partial username search and return public user dicts.
        """
        users = self.user_repo.load_users() or []
        username = (username or "").strip().lower()

        matches: list[dict] = []
        for u in users:
            u_name = str(u.get("username", "")).lower()
            if not username or username in u_name:
                matches.append(UserPublic(**u).model_dump())
        return matches

    def search_users_admin(
        self,
        username: str = "",
        email: str = "",
        role: str = "",
    ) -> list[dict]:
        """
        Perform case-insensitive partial matches on username, email, and role for admin usage.
        """
        users = self.user_repo.load_users() or []

        username = (username or "").strip().lower()
        email = (email or "").strip().lower()
        role = (role or "").strip().lower()

        matches: list[dict] = []
        for u in users:
            u_name = str(u.get("username", "")).lower()
            u_email = str(u.get("email", "")).lower()
            u_role = str(u.get("role", "")).lower()

            if (
                (not username or username in u_name)
                and (not email or email in u_email)
                and (not role or role in u_role)
            ):
                matches.append(u)

        return matches

    # ---------------------------------
    #   PROMOTE USER
    # ---------------------------------
    def promote_user(self, user_id: str) -> dict:
        """
        Promote a user to the admin role, handling persistence and basic error cases.
        """
        try:
            users = self.user_repo.load_users() or []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load users: {e}")

        for u in users:
            if u["id"] == user_id:
                if u.get("role") == "admin":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User already an admin",
                    )
                u["role"] = "admin"
                try:
                    self.user_repo.save_users(users)
                except Exception as e:
                    raise HTTPException(
                        status_code=500, detail=f"Failed to save users: {e}"
                    )
                return u

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found",
        )

    # ---------------------------------
    #   REVIEW MANAGEMENT
    # ---------------------------------
    def get_user_reviews(self, user_id: str) -> list[ReviewOut]:
        """
        Return all reviews authored by a specific user.
        """
        reviews, _ = self.review_service.get_reviews_by_user_id(user_id)
        return reviews

    def remove_review_from_user(self, user_id: str, movie_id: str) -> None:
        """
        Delegate deletion of a user's review for a given movie to the review service.
        """
        return self.review_service.delete_user_review(user_id, movie_id)

    def sync_user_reviews(self, user_id: str) -> None:
        """
        Refresh the reviews snapshot stored on a user record from the review service.
        """
        reviews, _ = self.review_service.get_reviews_by_user_id(user_id)
        users = self.user_repo.load_users() or []

        for u in users:
            if u["id"] == user_id:
                u["reviews"] = [r.model_dump() for r in reviews]
                break

        self.user_repo.save_users(users)

    # ---------------------------------
    #   PENALTY MANAGEMENT
    # ---------------------------------
    def add_penalty_to_user(
        self,
        user_id: str,
        reason: str,
        admin_id: str,
        flag_id: str | None = None,
    ):
        """
        Create a penalty entry for a user and attach it to their stored record.
        """
        new_penalty = self.penalty_service.add_penalty(
            user_id=user_id,
            reason=reason,
            issued_by=admin_id,
            source_flag_id=flag_id,
        )

        users = self.user_repo.load_users() or []
        for u in users:
            if u["id"] == user_id:
                if "penalties" not in u:
                    u["penalties"] = []
                u["penalties"].append(new_penalty)
                break

        self.user_repo.save_users(users)
        return new_penalty

    def get_user_penalties(self, user_id: str) -> list[dict]:
        """
        Return all penalties associated with a given user.
        """
        return self.penalty_service.get_for_user(user_id)

    def deactivate_penalty(self, penalty_id: int, admin_id: str) -> dict | None:
        """
        Deactivate a penalty and propagate the updated penalty to any user records that reference it.
        """
        updated_penalty = self.penalty_service.deactivate_penalty(
            penalty_id, admin_id
        )

        if not updated_penalty:
            return None

        users = self.user_repo.load_users() or []
        for u in users:
            if "penalties" in u:
                for p in u["penalties"]:


                    if p["penalty_id"] == penalty_id:
                        p.update(updated_penalty)

        self.user_repo.save_users(users)
        return updated_penalty

    # ---------------------------------
    #   FLAG MANAGEMENT
    # ---------------------------------
    def get_user_flags(self, user_id: str):
        """
        Retrieve all moderation flags that target a specific user.
        """
        all_flags = self.flags_service.get_all_flags()
        return [f for f in all_flags if f["flagged_user_id"] == user_id]

    def change_flag_status(self, flag_id: int, new_status: str):
        """
        Update the status of a flag and return the updated record, or None if not found.
        """
        updated_flag = self.flags_service.update_flag_status(flag_id, new_status)
        if not updated_flag:
            return None
        return updated_flag


# Shared Service Instance
user_service = UserService()
