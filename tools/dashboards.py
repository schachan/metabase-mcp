"""Dashboard management tools for Metabase."""

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

from app import mcp, metabase_client
from client import tool_error_handler


@mcp.tool
@tool_error_handler
async def list_dashboards(ctx: Context) -> list[dict[str, Any]]:
    """
    List all dashboards in Metabase.

    Returns:
        A list of dashboard metadata dictionaries.
    """
    await ctx.info("Fetching list of dashboards")
    result = await metabase_client.request("GET", "/dashboard")
    dashboard_count = len(result) if isinstance(result, list) else 0
    await ctx.info(f"Successfully retrieved {dashboard_count} dashboards")
    return result


@mcp.tool
@tool_error_handler
async def get_dashboard(dashboard_id: int, ctx: Context) -> dict[str, Any]:
    """
    Get detailed information about a specific dashboard.

    Args:
        dashboard_id: The ID of the dashboard.

    Returns:
        Dictionary with full dashboard metadata including cards, parameters, and layout.
    """
    await ctx.info(f"Fetching details for dashboard {dashboard_id}")
    result = await metabase_client.request("GET", f"/dashboard/{dashboard_id}")
    await ctx.info(f"Successfully retrieved dashboard '{result.get('name', 'unknown')}'")
    return result


@mcp.tool
@tool_error_handler
async def create_dashboard(
    name: str,
    ctx: Context,
    description: str | None = None,
    collection_id: int | None = None,
    parameters: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Create a new dashboard in Metabase.

    Args:
        name: Name of the dashboard.
        description: Optional description.
        collection_id: Optional collection to place the dashboard in.
        parameters: Optional dashboard filter parameters.

    Returns:
        The created dashboard object.
    """
    await ctx.info(f"Creating new dashboard '{name}'")

    payload: dict[str, Any] = {"name": name}

    if description:
        payload["description"] = description
    if collection_id is not None:
        payload["collection_id"] = collection_id
        await ctx.debug(f"Dashboard will be placed in collection {collection_id}")
    if parameters:
        payload["parameters"] = parameters

    result = await metabase_client.request("POST", "/dashboard", json=payload)
    await ctx.info(f"Successfully created dashboard with ID {result.get('id')}")

    return result


@mcp.tool
@tool_error_handler
async def update_dashboard(
    dashboard_id: int,
    ctx: Context,
    name: str | None = None,
    description: str | None = None,
    collection_id: int | None = None,
    parameters: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Update an existing dashboard in Metabase.

    Args:
        dashboard_id: The ID of the dashboard to update.
        name: New name for the dashboard.
        description: New description.
        collection_id: Move dashboard to this collection.
        parameters: New dashboard filter parameters.

    Returns:
        The updated dashboard object.
    """
    await ctx.info(f"Updating dashboard {dashboard_id}")

    payload: dict[str, Any] = {}
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if collection_id is not None:
        payload["collection_id"] = collection_id
    if parameters is not None:
        payload["parameters"] = parameters

    if not payload:
        raise ToolError("No update fields provided")

    result = await metabase_client.request("PUT", f"/dashboard/{dashboard_id}", json=payload)
    await ctx.info(f"Successfully updated dashboard {dashboard_id}")

    return result


@mcp.tool
@tool_error_handler
async def delete_dashboard(dashboard_id: int, ctx: Context) -> dict[str, Any]:
    """
    Delete a dashboard from Metabase.

    Args:
        dashboard_id: The ID of the dashboard to delete.

    Returns:
        Confirmation of the deletion.
    """
    await ctx.info(f"Deleting dashboard {dashboard_id}")
    result = await metabase_client.request("DELETE", f"/dashboard/{dashboard_id}")
    await ctx.info(f"Successfully deleted dashboard {dashboard_id}")
    return result
