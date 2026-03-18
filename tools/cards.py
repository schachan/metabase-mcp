"""Card/question management tools for Metabase."""

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

from app import mcp, metabase_client
from client import tool_error_handler


@mcp.tool
@tool_error_handler
async def list_cards(ctx: Context) -> dict[str, Any]:
    """
    List all saved questions/cards in Metabase.

    Returns:
        Dictionary containing all cards with their metadata.
    """
    await ctx.info("Fetching list of saved cards/questions")
    result = await metabase_client.request("GET", "/card")
    card_count = len(result) if isinstance(result, list) else len(result.get("data", []))
    await ctx.info(f"Successfully retrieved {card_count} cards")
    return result


@mcp.tool
@tool_error_handler
async def get_card(card_id: int, ctx: Context) -> dict[str, Any]:
    """
    Get detailed information about a specific card/question.

    Args:
        card_id: The ID of the card to retrieve.

    Returns:
        Dictionary with full card metadata including query, visualization settings,
        and collection info.
    """
    await ctx.info(f"Fetching details for card {card_id}")
    result = await metabase_client.request("GET", f"/card/{card_id}")
    await ctx.info(f"Successfully retrieved card '{result.get('name', 'unknown')}'")
    return result


@mcp.tool
@tool_error_handler
async def execute_card(
    card_id: int,
    ctx: Context,
    parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Execute a saved Metabase question/card and retrieve results.

    Args:
        card_id: The ID of the card to execute.
        parameters: Optional parameters for the card execution.

    Returns:
        Card execution results.
    """
    await ctx.info(f"Executing card {card_id}")
    payload: dict[str, Any] = {}
    if parameters:
        payload["parameters"] = parameters
        await ctx.debug(f"Card parameters: {parameters}")

    result = await metabase_client.request("POST", f"/card/{card_id}/query", json=payload)

    row_count = len(result.get("data", {}).get("rows", []))
    await ctx.info(f"Card {card_id} executed successfully, returned {row_count} rows")

    return result


@mcp.tool
@tool_error_handler
async def create_card(
    name: str,
    database_id: int,
    query: str,
    ctx: Context,
    description: str | None = None,
    collection_id: int | None = None,
    visualization_settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create a new question/card in Metabase.

    Args:
        name: Name of the card.
        database_id: ID of the database to query.
        query: SQL query for the card.
        description: Optional description.
        collection_id: Optional collection to place the card in.
        visualization_settings: Optional visualization configuration.

    Returns:
        The created card object.
    """
    await ctx.info(f"Creating new card '{name}' in database {database_id}")

    payload: dict[str, Any] = {
        "name": name,
        "database_id": database_id,
        "dataset_query": {
            "database": database_id,
            "type": "native",
            "native": {"query": query},
        },
        "display": "table",
        "visualization_settings": visualization_settings or {},
    }

    if description:
        payload["description"] = description
    if collection_id is not None:
        payload["collection_id"] = collection_id
        await ctx.debug(f"Card will be placed in collection {collection_id}")

    result = await metabase_client.request("POST", "/card", json=payload)
    await ctx.info(f"Successfully created card with ID {result.get('id')}")

    return result


@mcp.tool
@tool_error_handler
async def update_card(
    card_id: int,
    ctx: Context,
    name: str | None = None,
    description: str | None = None,
    query: str | None = None,
    database_id: int | None = None,
    collection_id: int | None = None,
    visualization_settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Update an existing card/question in Metabase.

    Args:
        card_id: The ID of the card to update.
        name: New name for the card.
        description: New description.
        query: New SQL query (requires database_id).
        database_id: Database ID for the query.
        collection_id: Move card to this collection.
        visualization_settings: New visualization configuration.

    Returns:
        The updated card object.
    """
    await ctx.info(f"Updating card {card_id}")

    payload: dict[str, Any] = {}
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if collection_id is not None:
        payload["collection_id"] = collection_id
    if visualization_settings is not None:
        payload["visualization_settings"] = visualization_settings
    if query is not None and database_id is not None:
        payload["dataset_query"] = {
            "database": database_id,
            "type": "native",
            "native": {"query": query},
        }

    if not payload:
        raise ToolError("No update fields provided")

    result = await metabase_client.request("PUT", f"/card/{card_id}", json=payload)
    await ctx.info(f"Successfully updated card {card_id}")

    return result


@mcp.tool
@tool_error_handler
async def archive_card(card_id: int, ctx: Context) -> dict[str, Any]:
    """
    Archive a card/question in Metabase (soft delete).

    This sets the card's archived status to true, which hides it from normal views
    but preserves the data. Safer than permanent deletion.

    Args:
        card_id: The ID of the card to archive.

    Returns:
        The updated card object with archived status.
    """
    await ctx.info(f"Archiving card {card_id}")
    result = await metabase_client.request("PUT", f"/card/{card_id}", json={"archived": True})
    await ctx.info(f"Successfully archived card {card_id}")
    return result
