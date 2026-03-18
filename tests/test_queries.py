"""Tests for query tools."""

import pytest
from fastmcp.exceptions import ToolError

from tools.queries import execute_query


@pytest.mark.asyncio
async def test_execute_query(mock_ctx, mock_request):
    mock_request.return_value = {"data": {"rows": [["Alice", 30], ["Bob", 25]]}}
    result = await execute_query.fn(1, "SELECT name, age FROM users", mock_ctx)
    assert len(result["data"]["rows"]) == 2
    mock_request.assert_called_once()
    call_args = mock_request.call_args
    assert call_args[0] == ("POST", "/dataset")


@pytest.mark.asyncio
async def test_execute_query_with_parameters(mock_ctx, mock_request):
    mock_request.return_value = {"data": {"rows": [["Alice", 30]]}}
    params = [
        {
            "type": "category",
            "target": ["variable", ["template-tag", "name"]],
            "value": "Alice",
        }
    ]
    await execute_query.fn(
        1,
        "SELECT * FROM users WHERE name = {{name}}",
        mock_ctx,
        native_parameters=params,
    )
    call_kwargs = mock_request.call_args
    payload = call_kwargs[1]["json"]
    assert payload["native"]["parameters"] == params


@pytest.mark.asyncio
async def test_execute_query_api_error(mock_ctx, mock_request):
    mock_request.side_effect = Exception("Connection refused")
    with pytest.raises(ToolError, match="Error in execute_query"):
        await execute_query.fn(1, "SELECT 1", mock_ctx)
