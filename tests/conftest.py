"""Shared test fixtures for Metabase MCP server tests."""

import os

os.environ.setdefault("METABASE_URL", "http://localhost:3000")
os.environ.setdefault("METABASE_API_KEY", "test-api-key-for-testing")

from unittest.mock import AsyncMock

import pytest

from app import metabase_client


@pytest.fixture
def mock_ctx():
    """Mock FastMCP Context with async logging methods."""
    ctx = AsyncMock()
    ctx.info = AsyncMock()
    ctx.debug = AsyncMock()
    ctx.warning = AsyncMock()
    ctx.error = AsyncMock()
    return ctx


@pytest.fixture
def mock_request(monkeypatch):
    """Patch metabase_client.request to return controlled responses."""
    mock = AsyncMock()
    monkeypatch.setattr(metabase_client, "request", mock)
    return mock
