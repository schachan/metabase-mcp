"""Tests for MetabaseClient optimizations."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from client import (
    MetabaseAPIError,
    MetabaseAuthError,
    MetabaseClient,
    _safe_json,
    tool_error_handler,
)
from fastmcp.exceptions import ToolError


class TestSafeJson:
    def test_valid_json(self):
        resp = MagicMock()
        resp.content = b'{"error": "not found"}'
        resp.json.return_value = {"error": "not found"}
        assert _safe_json(resp) == {"error": "not found"}

    def test_empty_content(self):
        resp = MagicMock()
        resp.content = b""
        assert _safe_json(resp) is None

    def test_invalid_json(self):
        resp = MagicMock()
        resp.content = b"<html>502 Bad Gateway</html>"
        resp.json.side_effect = ValueError("Not JSON")
        assert _safe_json(resp) is None


class TestMetabaseClientInit:
    def test_api_key_auth(self):
        client = MetabaseClient(base_url="http://mb:3000", api_key="key123")
        assert client.auth_method.value == "api_key"
        assert client.base_url == "http://mb:3000"

    def test_session_auth(self):
        client = MetabaseClient(
            base_url="http://mb:3000/",
            user_email="user@test.com",
            password="pass",
        )
        assert client.auth_method.value == "session"
        assert client.base_url == "http://mb:3000"

    @pytest.mark.asyncio
    async def test_context_manager(self):
        async with MetabaseClient(base_url="http://mb:3000", api_key="k") as client:
            assert client.base_url == "http://mb:3000"


class TestMetabaseClientRetry:
    @pytest.mark.asyncio
    async def test_retries_on_401_for_session_auth(self):
        client = MetabaseClient(
            base_url="http://mb:3000",
            user_email="u@t.com",
            password="p",
        )
        client.session_token = "expired-token"

        first_response = MagicMock()
        first_response.status_code = 401
        first_response.is_success = False
        first_response.content = b""
        first_response.text = "Unauthorized"

        second_response = MagicMock()
        second_response.status_code = 200
        second_response.is_success = True
        second_response.content = b'{"ok": true}'
        second_response.json.return_value = {"ok": True}

        session_response = MagicMock()
        session_response.status_code = 200
        session_response.json.return_value = {"id": "new-token"}

        call_count = 0

        async def mock_request(method, url, headers, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return first_response
            return second_response

        async def mock_post(url, json):
            return session_response

        client.client.request = mock_request
        client.client.post = mock_post

        result = await client.request("GET", "/database")
        assert result == {"ok": True}
        assert client.session_token == "new-token"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_no_retry_for_api_key_auth(self):
        client = MetabaseClient(base_url="http://mb:3000", api_key="key123")

        fail_response = MagicMock()
        fail_response.status_code = 401
        fail_response.is_success = False
        fail_response.content = b'{"message": "Invalid key"}'
        fail_response.json.return_value = {"message": "Invalid key"}

        async def mock_request(method, url, headers, **kwargs):
            return fail_response

        client.client.request = mock_request

        with pytest.raises(MetabaseAuthError) as exc_info:
            await client.request("GET", "/database")
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_raises_api_error_on_500(self):
        client = MetabaseClient(base_url="http://mb:3000", api_key="key123")

        error_response = MagicMock()
        error_response.status_code = 500
        error_response.is_success = False
        error_response.content = b'{"message": "Internal error"}'
        error_response.json.return_value = {"message": "Internal error"}

        async def mock_request(method, url, headers, **kwargs):
            return error_response

        client.client.request = mock_request

        with pytest.raises(MetabaseAPIError) as exc_info:
            await client.request("GET", "/database")
        assert exc_info.value.status_code == 500
        assert not isinstance(exc_info.value, MetabaseAuthError)


class TestToolErrorHandler:
    @pytest.mark.asyncio
    async def test_wraps_exception_as_tool_error(self):
        ctx = AsyncMock()

        @tool_error_handler
        async def failing_tool(ctx):
            raise ValueError("something broke")

        with pytest.raises(ToolError, match="Error in failing_tool"):
            await failing_tool(ctx)
        ctx.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_passes_through_tool_error(self):
        ctx = AsyncMock()

        @tool_error_handler
        async def tool_with_validation(ctx):
            raise ToolError("No update fields provided")

        with pytest.raises(ToolError, match="No update fields provided"):
            await tool_with_validation(ctx)

    @pytest.mark.asyncio
    async def test_returns_result_on_success(self):
        ctx = AsyncMock()

        @tool_error_handler
        async def good_tool(ctx):
            return {"result": "ok"}

        result = await good_tool(ctx)
        assert result == {"result": "ok"}
