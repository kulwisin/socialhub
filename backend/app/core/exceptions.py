"""Domain exceptions — raised by services, mapped to HTTP by middleware."""
from __future__ import annotations


class SocialHubError(Exception):
    """Base exception for all application errors."""


class NotFoundError(SocialHubError):
    """Resource does not exist."""


class ValidationError(SocialHubError):
    """Input failed domain validation."""


class ConflictError(SocialHubError):
    """Operation conflicts with existing state."""


class PlatformAuthError(SocialHubError):
    """OAuth or token error from a social platform."""


class PlatformPublishError(SocialHubError):
    """Platform rejected a publish request."""


class MediaProcessingError(SocialHubError):
    """File upload or processing failed."""
