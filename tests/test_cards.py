"""Tests for card/question tools."""

import pytest
from fastmcp.exceptions import ToolError

from tools.cards import (
    archive_card,
    create_card,
    execute_card,
    get_card,
    list_cards,
    update_card,
)


@pytest.mark.asyncio
async def test_list_cards(mock_ctx, mock_request):
    mock_request.return_value = [{"id": 1, "name": "Card 1"}, {"id": 2, "name": "Card 2"}]
    result = await list_cards.fn(mock_ctx)
    assert len(result) == 2
    mock_request.assert_called_once_with("GET", "/card")


@pytest.mark.asyncio
async def test_get_card(mock_ctx, mock_request):
    mock_request.return_value = {"id": 5, "name": "Revenue Report", "display": "bar"}
    result = await get_card.fn(5, mock_ctx)
    assert result["name"] == "Revenue Report"
    mock_request.assert_called_once_with("GET", "/card/5")


@pytest.mark.asyncio
async def test_execute_card(mock_ctx, mock_request):
    mock_request.return_value = {"data": {"rows": [[100], [200]]}}
    result = await execute_card.fn(1, mock_ctx)
    assert len(result["data"]["rows"]) == 2


@pytest.mark.asyncio
async def test_execute_card_with_parameters(mock_ctx, mock_request):
    mock_request.return_value = {"data": {"rows": [[100]]}}
    params = {"category": "Gadget"}
    await execute_card.fn(1, mock_ctx, parameters=params)
    call_kwargs = mock_request.call_args
    assert call_kwargs[1]["json"]["parameters"] == params


@pytest.mark.asyncio
async def test_create_card(mock_ctx, mock_request):
    mock_request.return_value = {"id": 10, "name": "New Card"}
    result = await create_card.fn("New Card", 1, "SELECT 1", mock_ctx)
    assert result["id"] == 10
    call_kwargs = mock_request.call_args
    payload = call_kwargs[1]["json"]
    assert payload["name"] == "New Card"
    assert payload["dataset_query"]["native"]["query"] == "SELECT 1"


@pytest.mark.asyncio
async def test_create_card_with_optional_fields(mock_ctx, mock_request):
    mock_request.return_value = {"id": 11, "name": "Card In Collection"}
    await create_card.fn(
        "Card In Collection",
        1,
        "SELECT 1",
        mock_ctx,
        description="A test card",
        collection_id=5,
        visualization_settings={"table.pivot_column": "QUANTITY"},
    )
    call_kwargs = mock_request.call_args
    payload = call_kwargs[1]["json"]
    assert payload["description"] == "A test card"
    assert payload["collection_id"] == 5
    assert payload["visualization_settings"]["table.pivot_column"] == "QUANTITY"


@pytest.mark.asyncio
async def test_update_card(mock_ctx, mock_request):
    mock_request.return_value = {"id": 5, "name": "Updated Name"}
    result = await update_card.fn(5, mock_ctx, name="Updated Name")
    assert result["name"] == "Updated Name"
    call_kwargs = mock_request.call_args
    assert call_kwargs[0] == ("PUT", "/card/5")
    assert call_kwargs[1]["json"]["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_update_card_no_fields_raises(mock_ctx, mock_request):
    with pytest.raises(ToolError, match="No update fields provided"):
        await update_card.fn(5, mock_ctx)


@pytest.mark.asyncio
async def test_archive_card(mock_ctx, mock_request):
    mock_request.return_value = {"id": 5, "archived": True}
    result = await archive_card.fn(5, mock_ctx)
    assert result["archived"] is True
    call_kwargs = mock_request.call_args
    assert call_kwargs[1]["json"]["archived"] is True


@pytest.mark.asyncio
async def test_card_api_error(mock_ctx, mock_request):
    mock_request.side_effect = Exception("Not found")
    with pytest.raises(ToolError, match="Error in get_card"):
        await get_card.fn(999, mock_ctx)
