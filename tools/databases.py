"""Database exploration tools for Metabase."""

from typing import Any

from fastmcp import Context

from app import mcp, metabase_client
from client import tool_error_handler


@mcp.tool
@tool_error_handler
async def list_databases(ctx: Context) -> dict[str, Any]:
    """
    List all databases configured in Metabase.

    Returns:
        A dictionary containing all available databases with their metadata.
    """
    await ctx.info("Fetching list of databases from Metabase")
    result = await metabase_client.request("GET", "/database")
    await ctx.info(f"Successfully retrieved {len(result.get('data', []))} databases")
    return result


@mcp.tool
@tool_error_handler
async def list_tables(database_id: int, ctx: Context) -> str:
    """
    List all tables in a specific database.

    Args:
        database_id: The ID of the database to query.

    Returns:
        Formatted markdown table showing table details.
    """
    await ctx.info(f"Fetching tables for database {database_id}")
    result = await metabase_client.request("GET", f"/database/{database_id}/metadata")

    tables = result.get("tables", [])
    await ctx.debug(f"Found {len(tables)} tables in database {database_id}")

    formatted_tables = [
        {
            "table_id": table.get("id"),
            "display_name": table.get("display_name"),
            "description": table.get("description") or "No description",
            "entity_type": table.get("entity_type"),
        }
        for table in tables
    ]

    formatted_tables.sort(key=lambda x: x.get("display_name", ""))

    lines = [
        f"# Tables in Database {database_id}",
        "",
        f"**Total Tables:** {len(formatted_tables)}",
        "",
    ]

    if not formatted_tables:
        await ctx.warning(f"No tables found in database {database_id}")
        lines.append("*No tables found in this database.*")
        return "\n".join(lines) + "\n"

    lines.append("| Table ID | Display Name | Description | Entity Type |")
    lines.append("|----------|--------------|-------------|--------------|")

    for table in formatted_tables:
        table_id = table.get("table_id", "N/A")
        display_name = str(table.get("display_name", "N/A")).replace("|", "\\|")
        description = str(table.get("description", "No description")).replace("|", "\\|")
        entity_type = table.get("entity_type", "N/A")
        lines.append(f"| {table_id} | {display_name} | {description} | {entity_type} |")

    await ctx.info(f"Successfully formatted {len(formatted_tables)} tables")
    return "\n".join(lines) + "\n"


@mcp.tool
@tool_error_handler
async def get_table_fields(table_id: int, ctx: Context, limit: int = 20) -> dict[str, Any]:
    """
    Get all fields/columns in a specific table.

    Args:
        table_id: The ID of the table.
        limit: Maximum number of fields to return (default: 20).

    Returns:
        Dictionary with field metadata, truncated if necessary.
    """
    await ctx.info(f"Fetching fields for table {table_id}")
    result = await metabase_client.request("GET", f"/table/{table_id}/query_metadata")

    if limit > 0 and "fields" in result and len(result["fields"]) > limit:
        total_fields = len(result["fields"])
        result["fields"] = result["fields"][:limit]
        result["_truncated"] = True
        result["_total_fields"] = total_fields
        result["_limit_applied"] = limit
        await ctx.info(f"Truncated {total_fields} fields to {limit} fields")
    else:
        await ctx.info(f"Retrieved {len(result.get('fields', []))} fields")

    return result


@mcp.tool
@tool_error_handler
async def get_database(database_id: int, ctx: Context) -> dict[str, Any]:
    """
    Get detailed information about a specific database.

    Args:
        database_id: The ID of the database.

    Returns:
        Dictionary with full database metadata including engine, features, and settings.
    """
    await ctx.info(f"Fetching details for database {database_id}")
    result = await metabase_client.request("GET", f"/database/{database_id}")
    await ctx.info(f"Successfully retrieved database '{result.get('name', 'unknown')}'")
    return result


@mcp.tool
@tool_error_handler
async def list_database_schemas(database_id: int, ctx: Context) -> list[str]:
    """
    List all schemas in a specific database.

    Args:
        database_id: The ID of the database.

    Returns:
        A list of schema names available in the database.
    """
    await ctx.info(f"Fetching schemas for database {database_id}")
    result = await metabase_client.request("GET", f"/database/{database_id}/schemas")
    await ctx.info(f"Found {len(result)} schemas in database {database_id}")
    return result


@mcp.tool
@tool_error_handler
async def get_schema_tables(
    database_id: int, schema_name: str, ctx: Context
) -> list[dict[str, Any]]:
    """
    List all tables within a specific schema of a database.

    Args:
        database_id: The ID of the database.
        schema_name: The name of the schema.

    Returns:
        A list of table metadata dictionaries for the given schema.
    """
    await ctx.info(f"Fetching tables for schema '{schema_name}' in database {database_id}")
    result = await metabase_client.request("GET", f"/database/{database_id}/schema/{schema_name}")
    table_count = len(result) if isinstance(result, list) else 0
    await ctx.info(f"Found {table_count} tables in schema '{schema_name}'")
    return result
