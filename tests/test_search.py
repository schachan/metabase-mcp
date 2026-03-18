"""Tests for search tools."""

import pytest
from fastmcp.exceptions import ToolError

from tools.search import search


@pytest.mark.asyncio
async def test_search(mock_ctx, mock_request):
    mock_request.return_value = {
        "data": [
            {"id": 1, "name": "Revenue Report", "model": "card"},
            {"id": 2, "name": "Revenue Dashboard", "model": "dashboard"},
        ]
    }
    result = await search.fn("revenue", mock_ctx)
    assert len(result["data"]) == 2
    call_kwargs = mock_request.call_args
    assert call_kwargs[1]["params"]["q"] == "revenue"


@pytest.mark.asyncio
async def test_search_with_model_filter(mock_ctx, mock_request):
    mock_request.return_value = {
        "data": [{"id": 1, "name": "Revenue Report", "model": "card"}]
    }
    await search.fn("revenue", mock_ctx, models=["card"])
    call_kwargs = mock_request.call_args
    assert call_kwargs[1]["params"]["models"] == ["card"]


@pytest.mark.asyncio
async def test_search_empty_results(mock_ctx, mock_request):
    mock_request.return_value = {"data": []}
    result = await search.fn("nonexistent", mock_ctx)
    assert result["data"] == []


@pytest.mark.asyncio
async def test_search_api_error(mock_ctx, mock_request):
    mock_request.side_effect = Exception("Server error")
    with pytest.raises(ToolError, match="Error in search"):
        await search.fn("test", mock_ctx)
