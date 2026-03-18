"""Tool registration - importing modules registers tools via @mcp.tool decorators."""

from tools import cards, collections, dashboards, databases, queries, search

__all__ = ["cards", "collections", "dashboards", "databases", "queries", "search"]
