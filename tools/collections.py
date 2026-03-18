"""Collection management tools for Metabase."""

from typing import Any

from fastmcp import Context

from app import mcp, metabase_client
from client import tool_error_handler


@mcp.tool
@tool_error_handler
async def list_collections(ctx: Context) -> dict[str, Any]:
    """
    List all collections in Metabase.

    Returns:
        Dictionary containing all collections with their metadata.
    """
    await ctx.info("Fetching list of collections")
    result = await metabase_client.request("GET", "/collection")
    collection_count = len(result) if isinstance(result, list) else len(result.get("data", []))
    await ctx.info(f"Successfully retrieved {collection_count} collections")
    return result


@mcp.tool
@tool_error_handler
async def get_collection_items(
    collection_id: int,
    ctx: Context,
    models: list[str] | None = None,
) -> dict[str, Any]:
    """
    List items inside a specific collection.

    Args:
        collection_id: The ID of the collection to browse.
        models: Optional filter for item types (e.g., ["card", "dashboard", "collection"]).

    Returns:
        Dictionary containing the items in the collection.
    """
    await ctx.info(f"Fetching items for collection {collection_id}")
    params: dict[str, Any] = {}
    if models:
        params["models"] = models
        await ctx.debug(f"Filtering by models: {models}")

    result = await metabase_client.request(
        "GET", f"/collection/{collection_id}/items", params=params
    )
    item_count = len(result.get("data", [])) if isinstance(result, dict) else len(result)
    await ctx.info(f"Found {item_count} items in collection {collection_id}")
    return result


@mcp.tool
@tool_error_handler
async def create_collection(
    name: str,
    ctx: Context,
    description: str | None = None,
    color: str | None = None,
    parent_id: int | None = None,
) -> dict[str, Any]:
    """
    Create a new collection in Metabase.

    Args:
        name: Name of the collection.
        description: Optional description.
        color: Optional color for the collection.
        parent_id: Optional parent collection ID.

    Returns:
        The created collection object.
    """
    await ctx.info(f"Creating new collection '{name}'")

    payload: dict[str, Any] = {"name": name}

    if description:
        payload["description"] = description
    if color:
        payload["color"] = color
        await ctx.debug(f"Collection color: {color}")
    if parent_id is not None:
        payload["parent_id"] = parent_id
        await ctx.debug(f"Collection parent ID: {parent_id}")

    result = await metabase_client.request("POST", "/collection", json=payload)
    await ctx.info(f"Successfully created collection with ID {result.get('id')}")

    return result
