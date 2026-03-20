# Metabase MCP Plus

[![PyPI version](https://badge.fury.io/py/metabase-mcp-plus.svg)](https://badge.fury.io/py/metabase-mcp-plus)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/schachan/metabase-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/schachan/metabase-mcp/actions/workflows/ci.yml)

An enhanced **Model Context Protocol (MCP) server** for **Metabase**, enabling AI assistants like **Claude**, **Cursor**, and other MCP clients to query databases, execute SQL, manage dashboards, cards, and collections — all through natural language.

## Quick Start

### Using uvx (No Installation Required)

```bash
uvx metabase-mcp-plus
```

### Using pip

```bash
pip install metabase-mcp-plus
metabase-mcp-plus
```

### From Source

```bash
git clone https://github.com/schachan/metabase-mcp.git
cd metabase-mcp
uv sync
uv run python server.py
```

## Configuration

Set environment variables directly or create a `.env` file:

```bash
cp .env.example .env
```

### API Key Authentication (Recommended)

```env
METABASE_URL=https://your-metabase-instance.com
METABASE_API_KEY=your-api-key-here
```

### Email/Password Authentication

```env
METABASE_URL=https://your-metabase-instance.com
METABASE_USER_EMAIL=your-email@example.com
METABASE_PASSWORD=your-password
```

### Optional: Custom Host/Port (SSE/HTTP transports)

```env
HOST=localhost  # Default: 0.0.0.0
PORT=9000       # Default: 8000
```

## Available Tools (22)

### Database Operations (6 tools)

| Tool | Description |
|------|-------------|
| `list_databases` | List all configured databases |
| `get_database` | Get details of a specific database |
| `list_tables` | Get all tables in a database with metadata |
| `get_table_fields` | Retrieve field/column information for a table |
| `list_database_schemas` | List all schemas in a database |
| `get_schema_tables` | Get tables within a specific schema |

### Query Operations (1 tool)

| Tool | Description |
|------|-------------|
| `execute_query` | Execute native SQL queries with parameter support |

### Card / Question Management (6 tools)

| Tool | Description |
|------|-------------|
| `list_cards` | List all saved questions/cards |
| `get_card` | Get details of a specific card |
| `execute_card` | Run a saved question and return results |
| `create_card` | Create a new question with a SQL query |
| `update_card` | Update an existing card's name, query, or collection |
| `archive_card` | Archive a card |

### Dashboard Management (5 tools)

| Tool | Description |
|------|-------------|
| `list_dashboards` | List all dashboards |
| `get_dashboard` | Get full dashboard details including cards |
| `create_dashboard` | Create a new dashboard |
| `update_dashboard` | Update a dashboard's name, description, or cards |
| `delete_dashboard` | Delete a dashboard |

### Collection Management (3 tools)

| Tool | Description |
|------|-------------|
| `list_collections` | Browse all collections |
| `get_collection_items` | List items within a collection |
| `create_collection` | Create a new collection |

### Search (1 tool)

| Tool | Description |
|------|-------------|
| `search` | Search across cards, dashboards, collections, and tables |

## Transport Methods

```bash
metabase-mcp-plus                # STDIO (default, for IDE integration)
metabase-mcp-plus --sse          # Server-Sent Events
metabase-mcp-plus --http         # Streamable HTTP
```

Or from source:

```bash
uv run python server.py          # STDIO
uv run python server.py --sse    # SSE
uv run python server.py --http   # HTTP
```

## IDE Integration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "metabase": {
            "command": "uvx",
            "args": ["metabase-mcp-plus"],
            "env": {
                "METABASE_URL": "https://your-metabase-instance.com",
                "METABASE_API_KEY": "your-api-key-here"
            }
        }
    }
}
```

### Cursor

Add to your MCP settings (`.cursor/mcp.json`):

```json
{
    "mcpServers": {
        "metabase": {
            "command": "uvx",
            "args": ["metabase-mcp-plus"],
            "env": {
                "METABASE_URL": "https://your-metabase-instance.com",
                "METABASE_API_KEY": "your-api-key-here"
            }
        }
    }
}
```

## Project Structure

```
metabase-mcp/
├── server.py              # Entry point — CLI arg parsing and transport selection
├── app.py                 # FastMCP app setup, env loading, client instantiation
├── client.py              # MetabaseClient with auth, retry, and error handling
├── tools/
│   ├── __init__.py        # Registers all tool modules
│   ├── databases.py       # Database, table, schema, and field tools
│   ├── queries.py         # SQL query execution
│   ├── cards.py           # Card CRUD and execution
│   ├── dashboards.py      # Dashboard CRUD
│   ├── collections.py     # Collection browsing and creation
│   └── search.py          # Cross-entity search
├── tests/                 # Comprehensive test suite (95% coverage)
├── .github/workflows/
│   ├── ci.yml             # Lint + test on push/PR
│   └── publish.yml        # Release → PyPI + attach assets
├── RELEASING.md           # How to cut a release (trusted publisher setup)
└── pyproject.toml
```

## Development

```bash
# Install with dev dependencies
uv sync --group dev

# Run linting and formatting
uv run ruff check .
uv run ruff format .

# Run tests with coverage
uv run pytest tests/ --cov=. --cov=tools --cov-report=term-missing -v
```

## Architecture Highlights

- **Modular tools** — each domain (databases, cards, dashboards, etc.) is a separate module
- **Automatic auth retry** — expired session tokens are refreshed transparently on 401
- **Custom exceptions** — `MetabaseAPIError` and `MetabaseAuthError` for typed error handling
- **Error handler decorator** — `@tool_error_handler` eliminates boilerplate try/except across all 22 tools
- **Middleware stack** — built-in error handling and logging middleware via FastMCP

## Releases & PyPI

Publishing to [PyPI](https://pypi.org/project/metabase-mcp-plus/) is automated when you **publish a GitHub Release** (workflow [`.github/workflows/publish.yml`](.github/workflows/publish.yml)): lint → test → build → attach wheels to the release → upload to PyPI (trusted publisher / OIDC).

See **[RELEASING.md](RELEASING.md)** for one-time PyPI + GitHub environment setup and the exact tag/version rules (`v1.2.3` must match `version = "1.2.3"` in `pyproject.toml`).

## License

MIT License — see [LICENSE](LICENSE) for details.

## Resources

- [Metabase API Documentation](https://www.metabase.com/docs/latest/api-documentation)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)
