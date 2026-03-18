"""Search tools for Metabase."""

from typing import Any

from fastmcp import Context

from app import mcp, metabase_client
from client import tool_error_handler


@mcp.tool
@tool_error_handler
async def search(
    query: str,
    ctx: Context,
    models: list[str] | None = None,
) -> dict[str, Any]:
    """
    Search across Metabase entities by keyword.

    Searches cards (questions), dashboards, collections, and tables for matching results.

    Args:
        query: The search keyword or phrase.
        models: Optional filter for entity types
                (e.g., ["card", "dashboard", "collection", "table"]).

    Returns:
        Dictionary containing search results with matched entities.
    """
    await ctx.info(f"Searching Metabase for '{query}'")

    params: dict[str, Any] = {"q": query}
    if models:
        params["models"] = models
        await ctx.debug(f"Filtering search by models: {models}")

    result = await metabase_client.request("GET", "/search", params=params)
    result_count = len(result.get("data", [])) if isinstance(result, dict) else len(result)
    await ctx.info(f"Search returned {result_count} results")

    return result
