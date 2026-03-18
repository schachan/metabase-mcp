"""Metabase HTTP client for API operations."""

import functools
import logging
from enum import Enum
from typing import Any

import httpx
from fastmcp.exceptions import ToolError

logger = logging.getLogger(__name__)


class AuthMethod(Enum):
    SESSION = "session"
    API_KEY = "api_key"


class MetabaseAPIError(Exception):
    """Raised when the Metabase API returns a non-success response."""

    def __init__(self, status_code: int, message: str, detail: Any = None):
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class MetabaseAuthError(MetabaseAPIError):
    """Raised on authentication/authorization failures (401/403)."""


class MetabaseClient:
    """HTTP client for Metabase API operations."""

    _MAX_AUTH_RETRIES = 1

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        user_email: str | None = None,
        password: str | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.session_token: str | None = None
        self.api_key = api_key
        self.user_email = user_email
        self.password = password
        self.auth_method = AuthMethod.API_KEY if api_key else AuthMethod.SESSION
        self.client = httpx.AsyncClient(timeout=30.0)

        logger.info("Using %s authentication method", self.auth_method.value)

    async def __aenter__(self) -> "MetabaseClient":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    async def _get_headers(self) -> dict[str, str]:
        """Get appropriate authentication headers."""
        headers = {"Content-Type": "application/json"}

        if self.auth_method == AuthMethod.API_KEY and self.api_key:
            headers["X-API-KEY"] = self.api_key
        elif self.auth_method == AuthMethod.SESSION:
            if not self.session_token:
                await self._get_session_token()
            if self.session_token:
                headers["X-Metabase-Session"] = self.session_token

        return headers

    async def _get_session_token(self) -> str:
        """Get Metabase session token for email/password authentication."""
        if self.auth_method == AuthMethod.API_KEY and self.api_key:
            return self.api_key

        if not self.user_email or not self.password:
            raise MetabaseAuthError(
                status_code=401,
                message="Email and password required for session authentication",
            )

        login_data = {"username": self.user_email, "password": self.password}
        response = await self.client.post(f"{self.base_url}/api/session", json=login_data)

        if response.status_code != 200:
            detail = _safe_json(response)
            raise MetabaseAuthError(
                status_code=response.status_code,
                message=f"Authentication failed: {response.status_code}",
                detail=detail,
            )

        session_data = response.json()
        token = session_data.get("id")
        if not token:
            raise MetabaseAuthError(
                status_code=response.status_code,
                message="Session response missing 'id' field",
                detail=session_data,
            )

        self.session_token = token
        logger.info("Successfully obtained session token")
        return self.session_token

    async def request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Make authenticated request to Metabase API with automatic 401 retry."""
        url = f"{self.base_url}/api{path}"

        for attempt in range(1 + self._MAX_AUTH_RETRIES):
            headers = await self._get_headers()
            logger.debug("Making %s request to %s", method, path)

            response = await self.client.request(method=method, url=url, headers=headers, **kwargs)

            if response.status_code == 401 and attempt < self._MAX_AUTH_RETRIES:
                if self.auth_method == AuthMethod.SESSION:
                    logger.info("Session expired, refreshing token and retrying")
                    self.session_token = None
                    continue
                break

            if not response.is_success:
                detail = _safe_json(response)
                if response.status_code in (401, 403):
                    raise MetabaseAuthError(
                        status_code=response.status_code,
                        message=f"API request to {path} failed with status {response.status_code}",
                        detail=detail,
                    )
                raise MetabaseAPIError(
                    status_code=response.status_code,
                    message=f"API request to {path} failed with status {response.status_code}",
                    detail=detail,
                )

            logger.debug("Successful response from %s", path)
            if not response.content:
                return {}
            return response.json()

        detail = _safe_json(response)
        raise MetabaseAuthError(
            status_code=response.status_code,
            message=f"API request to {path} failed after auth retry",
            detail=detail,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()


def _safe_json(response: httpx.Response) -> Any:
    """Extract JSON from a response, returning None on parse failure."""
    if not response.content:
        return None
    try:
        return response.json()
    except Exception:
        return None


def tool_error_handler(func):  # type: ignore[no-untyped-def]
    """Decorator that wraps tool functions with consistent error logging and ToolError raising."""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        ctx = kwargs.get("ctx")
        if ctx is None:
            for arg in args:
                if hasattr(arg, "error") and hasattr(arg, "info"):
                    ctx = arg
                    break

        try:
            return await func(*args, **kwargs)
        except ToolError:
            raise
        except Exception as e:
            error_msg = f"Error in {func.__name__}: {e}"
            if ctx:
                await ctx.error(error_msg)
            raise ToolError(error_msg) from e

    return wrapper
