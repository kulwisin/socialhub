from __future__ import annotations

from app.core.auth import create_access_token, hash_password, verify_password
from app.core.exceptions import ConflictError, ValidationError
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import UserResponse


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        log_repo: ActivityLogRepository,
    ) -> None:
        self._users = user_repo
        self._logs = log_repo

    async def register(
        self,
        email: str,
        password: str,
        name: str | None = None,
    ) -> TokenResponse:
        """Create a new user account and return a JWT."""
        existing = await self._users.get_by_email(email)
        if existing is not None:
            raise ConflictError(f"An account with email '{email}' already exists.")

        user = await self._users.create(
            {
                "email": email,
                "password_hash": hash_password(password),
                "name": name,
                "is_active": True,
            }
        )
        await self._logs.log(
            event_type="user.registered",
            resource_type="user",
            resource_id=user.id,
            description=f"New user registered: {email}",
            metadata={"email": email},
        )

        token = create_access_token(str(user.id), user.email)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    async def login(self, email: str, password: str) -> TokenResponse:
        """Verify credentials and return a JWT."""
        user = await self._users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise ValidationError("Invalid email or password.")
        if not user.is_active:
            raise ValidationError("User account is disabled.")

        await self._logs.log(
            event_type="user.login",
            resource_type="user",
            resource_id=user.id,
            description=f"User logged in: {email}",
            metadata={"email": email},
        )

        token = create_access_token(str(user.id), user.email)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )
