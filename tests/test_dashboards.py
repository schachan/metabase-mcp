"""Tests for dashboard tools."""

import pytest
from fastmcp.exceptions import ToolError

from tools.dashboards import (
    create_dashboard,
    delete_dashboard,
    get_dashboard,
    list_dashboards,
    update_dashboard,
)


@pytest.mark.asyncio
async def test_list_dashboards(mock_ctx, mock_request):
    mock_request.return_value = [
        {"id": 1, "name": "Dashboard 1"},
        {"id": 2, "name": "Dashboard 2"},
    ]
    result = await list_dashboards.fn(mock_ctx)
    assert len(result) == 2
    mock_request.assert_called_once_with("GET", "/dashboard")


@pytest.mark.asyncio
async def test_get_dashboard(mock_ctx, mock_request):
    mock_request.return_value = {
        "id": 1,
        "name": "Sales Dashboard",
        "dashcards": [{"id": 10, "card_id": 5}],
    }
    result = await get_dashboard.fn(1, mock_ctx)
    assert result["name"] == "Sales Dashboard"
    assert len(result["dashcards"]) == 1
    mock_request.assert_called_once_with("GET", "/dashboard/1")


@pytest.mark.asyncio
async def test_create_dashboard(mock_ctx, mock_request):
    mock_request.return_value = {"id": 20, "name": "New Dashboard"}
    result = await create_dashboard.fn("New Dashboard", mock_ctx)
    assert result["id"] == 20
    call_kwargs = mock_request.call_args
    assert call_kwargs[1]["json"]["name"] == "New Dashboard"


@pytest.mark.asyncio
async def test_create_dashboard_with_collection(mock_ctx, mock_request):
    mock_request.return_value = {"id": 21, "name": "Team Dashboard", "collection_id": 5}
    await create_dashboard.fn(
        "Team Dashboard",
        mock_ctx,
        description="Team metrics",
        collection_id=5,
    )
    call_kwargs = mock_request.call_args
    payload = call_kwargs[1]["json"]
    assert payload["description"] == "Team metrics"
    assert payload["collection_id"] == 5


@pytest.mark.asyncio
async def test_update_dashboard(mock_ctx, mock_request):
    mock_request.return_value = {"id": 1, "name": "Renamed Dashboard"}
    result = await update_dashboard.fn(1, mock_ctx, name="Renamed Dashboard")
    assert result["name"] == "Renamed Dashboard"
    call_kwargs = mock_request.call_args
    assert call_kwargs[0] == ("PUT", "/dashboard/1")


@pytest.mark.asyncio
async def test_update_dashboard_no_fields_raises(mock_ctx, mock_request):
    with pytest.raises(ToolError, match="No update fields provided"):
        await update_dashboard.fn(1, mock_ctx)


@pytest.mark.asyncio
async def test_delete_dashboard(mock_ctx, mock_request):
    mock_request.return_value = {}
    await delete_dashboard.fn(1, mock_ctx)
    mock_request.assert_called_once_with("DELETE", "/dashboard/1")


@pytest.mark.asyncio
async def test_dashboard_api_error(mock_ctx, mock_request):
    mock_request.side_effect = Exception("Server error")
    with pytest.raises(ToolError, match="Error in list_dashboards"):
        await list_dashboards.fn(mock_ctx)
