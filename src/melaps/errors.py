"""SDK error types — one class per API failure mode."""


class MelapsError(Exception):
    """Base SDK error."""


class AuthenticationError(MelapsError):
    """Invalid or expired API key (HTTP 401)."""


class ValidationError(MelapsError):
    """The request was rejected (HTTP 400/422)."""


class NotFoundError(MelapsError):
    """The resource does not exist (HTTP 404)."""


class RateLimitError(MelapsError):
    """Rate limited (HTTP 429). ``retry_after`` is in seconds."""

    def __init__(self, message="rate limit exceeded", retry_after=60):
        super().__init__(message)
        self.retry_after = retry_after
