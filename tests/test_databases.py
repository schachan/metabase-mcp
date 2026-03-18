"""Tests for database tools."""

import pytest
from fastmcp.exceptions import ToolError

from tools.databases import (
    get_database,
    get_schema_tables,
    get_table_fields,
    list_database_schemas,
    list_databases,
    list_tables,
)


@pytest.mark.asyncio
async def test_list_databases(mock_ctx, mock_request):
    mock_request.return_value = {"data": [{"id": 1, "name": "TestDB"}]}
    result = await list_databases.fn(mock_ctx)
    assert result == {"data": [{"id": 1, "name": "TestDB"}]}
    mock_request.assert_called_once_with("GET", "/database")


@pytest.mark.asyncio
async def test_list_tables_returns_markdown(mock_ctx, mock_request):
    mock_request.return_value = {
        "tables": [
            {
                "id": 1,
                "display_name": "Users",
                "description": "User table",
                "entity_type": "entity/GenericTable",
            },
            {
                "id": 2,
                "display_name": "Orders",
                "description": None,
                "entity_type": "entity/GenericTable",
            },
        ]
    }
    result = await list_tables.fn(1, mock_ctx)
    assert "# Tables in Database 1" in result
    assert "**Total Tables:** 2" in result
    assert "Users" in result
    assert "Orders" in result
    assert "No description" in result


@pytest.mark.asyncio
async def test_list_tables_empty_database(mock_ctx, mock_request):
    mock_request.return_value = {"tables": []}
    result = await list_tables.fn(99, mock_ctx)
    assert "No tables found" in result


@pytest.mark.asyncio
async def test_get_table_fields_with_limit(mock_ctx, mock_request):
    fields = [{"name": f"field_{i}"} for i in range(30)]
    mock_request.return_value = {"fields": fields}
    result = await get_table_fields.fn(1, mock_ctx, limit=10)
    assert len(result["fields"]) == 10
    assert result["_truncated"] is True
    assert result["_total_fields"] == 30


@pytest.mark.asyncio
async def test_get_table_fields_no_truncation(mock_ctx, mock_request):
    fields = [{"name": f"field_{i}"} for i in range(5)]
    mock_request.return_value = {"fields": fields}
    result = await get_table_fields.fn(1, mock_ctx, limit=20)
    assert len(result["fields"]) == 5
    assert "_truncated" not in result


@pytest.mark.asyncio
async def test_get_database(mock_ctx, mock_request):
    mock_request.return_value = {"id": 1, "name": "TestDB", "engine": "postgres"}
    result = await get_database.fn(1, mock_ctx)
    assert result["name"] == "TestDB"
    mock_request.assert_called_once_with("GET", "/database/1")


@pytest.mark.asyncio
async def test_list_database_schemas(mock_ctx, mock_request):
    mock_request.return_value = ["public", "analytics", "staging"]
    result = await list_database_schemas.fn(1, mock_ctx)
    assert result == ["public", "analytics", "staging"]
    mock_request.assert_called_once_with("GET", "/database/1/schemas")


@pytest.mark.asyncio
async def test_get_schema_tables(mock_ctx, mock_request):
    mock_request.return_value = [
        {"id": 1, "name": "users", "schema": "public"},
        {"id": 2, "name": "orders", "schema": "public"},
    ]
    result = await get_schema_tables.fn(1, "public", mock_ctx)
    assert len(result) == 2
    mock_request.assert_called_once_with("GET", "/database/1/schema/public")


@pytest.mark.asyncio
async def test_database_tool_error(mock_ctx, mock_request):
    mock_request.side_effect = Exception("Connection refused")
    with pytest.raises(ToolError, match="Error in list_databases"):
        await list_databases.fn(mock_ctx)
