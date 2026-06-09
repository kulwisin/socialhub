from __future__ import annotations

import uuid

from app.core.crypto import encrypt
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.social_account_repository import SocialAccountRepository
from app.schemas.social_account import SocialAccountCreate, SocialAccountResponse

_VALID_PLATFORMS = {"instagram", "youtube", "tiktok", "x", "threads", "snapchat"}


class SocialAccountService:
    def __init__(
        self,
        account_repo: SocialAccountRepository,
        log_repo: ActivityLogRepository,
    ) -> None:
        self._accounts = account_repo
        self._logs = log_repo

    async def list_accounts(self, user_id: uuid.UUID) -> list[SocialAccountResponse]:
        """Return all social accounts belonging to a user."""
        accounts = await self._accounts.list_by_user(user_id)
        return [SocialAccountResponse.model_validate(a) for a in accounts]

    async def add_account(
        self,
        user_id: uuid.UUID,
        data: SocialAccountCreate,
    ) -> SocialAccountResponse:
        """Connect a new social account for the user. Encrypts tokens before storage."""
        if data.platform not in _VALID_PLATFORMS:
            raise ValidationError(
                f"Unknown platform '{data.platform}'. "
                f"Valid options: {sorted(_VALID_PLATFORMS)}"
            )

        existing = await self._accounts.get_by_platform_user(
            user_id, data.platform, data.platform_user_id
        )
        if existing is not None:
            raise ConflictError(
                f"Account '{data.username}' on {data.platform} is already connected."
            )

        row = await self._accounts.create(
            {
                "user_id": user_id,
                "platform": data.platform,
                "platform_user_id": data.platform_user_id,
                "username": data.username,
                "display_name": data.display_name,
                "profile_image_url": data.profile_image_url,
                "access_token_enc": encrypt(data.access_token),
                "refresh_token_enc": encrypt(data.refresh_token) if data.refresh_token else None,
                "token_expires_at": data.token_expires_at,
                "facebook_page_id": data.facebook_page_id,
                "instagram_business_id": data.instagram_business_id,
                "is_active": True,
            }
        )
        await self._logs.log(
            event_type="account.connected",
            resource_type="social_account",
            resource_id=row.id,
            description=f"Connected {data.platform} account @{data.username}",
            metadata={"platform": data.platform, "username": data.username},
        )
        return SocialAccountResponse.model_validate(row)

    async def remove_account(self, user_id: uuid.UUID, account_id: uuid.UUID) -> None:
        """Delete a social account, verifying it belongs to the user first."""
        account = await self._accounts.get(account_id)
        if account is None or account.user_id != user_id:
            raise NotFoundError(f"Social account {account_id} not found.")

        await self._logs.log(
            event_type="account.disconnected",
            resource_type="social_account",
            resource_id=account_id,
            description=f"Disconnected {account.platform} account @{account.username}",
            metadata={"platform": account.platform, "username": account.username},
        )
        await self._accounts.delete(account_id)

    async def toggle_active(
        self,
        user_id: uuid.UUID,
        account_id: uuid.UUID,
        is_active: bool,
    ) -> SocialAccountResponse:
        """Enable or disable a social account."""
        account = await self._accounts.get(account_id)
        if account is None or account.user_id != user_id:
            raise NotFoundError(f"Social account {account_id} not found.")

        updated = await self._accounts.update(account_id, {"is_active": is_active})
        if updated is None:
            raise NotFoundError(f"Social account {account_id} not found.")

        state = "enabled" if is_active else "disabled"
        await self._logs.log(
            event_type=f"account.{state}",
            resource_type="social_account",
            resource_id=account_id,
            description=f"Account @{account.username} on {account.platform} {state}",
            metadata={"platform": account.platform, "is_active": is_active},
        )
        return SocialAccountResponse.model_validate(updated)
