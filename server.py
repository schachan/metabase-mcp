#!/usr/bin/env python3
"""
Metabase FastMCP Server

A FastMCP server that provides tools to interact with Metabase databases,
execute queries, manage cards, dashboards, and work with collections.
"""

import logging
import os
import sys

import tools  # noqa: F401 — registers all tool handlers
from app import mcp

logger = logging.getLogger(__name__)


def main() -> None:
    """
    Main entry point for the Metabase MCP server.

    Supports multiple transport methods:
    - STDIO (default): For IDE integration
    - SSE: Server-Sent Events for web apps
    - HTTP: Standard HTTP for API access
    """
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    transport = "stdio"
    if "--sse" in sys.argv:
        transport = "sse"
    elif "--http" in sys.argv:
        transport = "streamable-http"
    elif "--stdio" in sys.argv:
        transport = "stdio"

    logger.info(f"Starting Metabase MCP server with {transport} transport")

    try:
        if transport in ["sse", "streamable-http"]:
            logger.info(f"Server will be available at http://{host}:{port}")
            mcp.run(transport=transport, host=host, port=port)
        else:
            mcp.run(transport=transport)

    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
