"""Query execution tools for Metabase."""

from typing import Any

from fastmcp import Context

from app import mcp, metabase_client
from client import tool_error_handler


@mcp.tool
@tool_error_handler
async def execute_query(
    database_id: int,
    query: str,
    ctx: Context,
    native_parameters: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Execute a native SQL query against a Metabase database.

    Args:
        database_id: The ID of the database to query.
        query: The SQL query to execute.
        native_parameters: Optional parameters for the query.

    Returns:
        Query execution results.
    """
    await ctx.info(f"Executing query on database {database_id}")
    await ctx.debug(f"Query: {query[:100]}...")

    payload: dict[str, Any] = {
        "database": database_id,
        "type": "native",
        "native": {"query": query},
    }

    if native_parameters:
        payload["native"]["parameters"] = native_parameters
        await ctx.debug(f"Query parameters: {len(native_parameters)} parameters provided")

    result = await metabase_client.request("POST", "/dataset", json=payload)

    row_count = len(result.get("data", {}).get("rows", []))
    await ctx.info(f"Query executed successfully, returned {row_count} rows")

    return result
