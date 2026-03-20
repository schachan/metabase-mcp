"""Metabase MCP application setup - shared FastMCP instance and client."""

import inspect
import logging
import os

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware

from client import MetabaseClient

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

METABASE_URL = os.getenv("METABASE_URL")
METABASE_USER_EMAIL = os.getenv("METABASE_USER_EMAIL")
METABASE_PASSWORD = os.getenv("METABASE_PASSWORD")
METABASE_API_KEY = os.getenv("METABASE_API_KEY")

if not METABASE_URL or (
    not METABASE_API_KEY and (not METABASE_USER_EMAIL or not METABASE_PASSWORD)
):
    raise ValueError(
        "METABASE_URL is required, and either METABASE_API_KEY or both "
        "METABASE_USER_EMAIL and METABASE_PASSWORD must be provided"
    )

# FastMCP v3+ uses a single on_duplicate=; v2 / early v3 use per-component kwargs.
_fastmcp_params = inspect.signature(FastMCP.__init__).parameters
if "on_duplicate" in _fastmcp_params:
    mcp = FastMCP(
        name="metabase-mcp",
        on_duplicate="error",
    )
elif "on_duplicate_tools" in _fastmcp_params:
    mcp = FastMCP(
        name="metabase-mcp",
        on_duplicate_tools="error",
        on_duplicate_resources="warn",
        on_duplicate_prompts="warn",
    )
else:
    mcp = FastMCP(name="metabase-mcp")

mcp.add_middleware(ErrorHandlingMiddleware())
mcp.add_middleware(LoggingMiddleware())

metabase_client = MetabaseClient(
    base_url=METABASE_URL,
    api_key=METABASE_API_KEY,
    user_email=METABASE_USER_EMAIL,
    password=METABASE_PASSWORD,
)
