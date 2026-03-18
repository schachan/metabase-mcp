"""Tests for collection tools."""

import pytest
from fastmcp.exceptions import ToolError

from tools.collections import create_collection, get_collection_items, list_collections


@pytest.mark.asyncio
async def test_list_collections(mock_ctx, mock_request):
    mock_request.return_value = [{"id": 1, "name": "Root"}, {"id": 2, "name": "Analytics"}]
    result = await list_collections.fn(mock_ctx)
    assert len(result) == 2
    mock_request.assert_called_once_with("GET", "/collection")


@pytest.mark.asyncio
async def test_create_collection(mock_ctx, mock_request):
    mock_request.return_value = {"id": 10, "name": "New Collection"}
    result = await create_collection.fn("New Collection", mock_ctx)
    assert result["id"] == 10
    call_kwargs = mock_request.call_args
    assert call_kwargs[1]["json"]["name"] == "New Collection"


@pytest.mark.asyncio
async def test_create_collection_with_optional_fields(mock_ctx, mock_request):
    mock_request.return_value = {"id": 11, "name": "Sub Collection"}
    await create_collection.fn(
        "Sub Collection",
        mock_ctx,
        description="A sub collection",
        color="#FF0000",
        parent_id=1,
    )
    call_kwargs = mock_request.call_args
    payload = call_kwargs[1]["json"]
    assert payload["description"] == "A sub collection"
    assert payload["color"] == "#FF0000"
    assert payload["parent_id"] == 1


@pytest.mark.asyncio
async def test_get_collection_items(mock_ctx, mock_request):
    mock_request.return_value = {
        "data": [
            {"id": 1, "model": "card", "name": "Question 1"},
            {"id": 2, "model": "dashboard", "name": "Dashboard 1"},
        ]
    }
    result = await get_collection_items.fn(1, mock_ctx)
    assert len(result["data"]) == 2
    mock_request.assert_called_once_with("GET", "/collection/1/items", params={})


@pytest.mark.asyncio
async def test_get_collection_items_with_model_filter(mock_ctx, mock_request):
    mock_request.return_value = {
        "data": [{"id": 1, "model": "card", "name": "Question 1"}]
    }
    await get_collection_items.fn(1, mock_ctx, models=["card"])
    call_kwargs = mock_request.call_args
    assert call_kwargs[1]["params"]["models"] == ["card"]


@pytest.mark.asyncio
async def test_collection_api_error(mock_ctx, mock_request):
    mock_request.side_effect = Exception("Server error")
    with pytest.raises(ToolError, match="Error in list_collections"):
        await list_collections.fn(mock_ctx)
