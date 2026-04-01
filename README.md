# Rust Documentation MCP Server

An MCP (Model Context Protocol) server that serves locally downloaded Rust documentation to Claude, enabling you to access Rust library documentation even behind corporate firewalls or without internet access.

## Overview

This project allows you to:

- **Access Rust documentation offline**: Download Rust crate documentation once and use it multiple times
- **Overcome network restrictions**: Works perfectly when Claude cannot access the internet
- **Search and browse crates**: Query documentation for any Rust library (Polars, Serde, Tokio, etc.)
- **Integrate with Claude**: Works seamlessly with Claude via the MCP protocol

## Requirements

- Python 3.10 or higher
- Poetry (for dependency management)
- Locally downloaded Rust documentation (you'll generate this)

## Installation

### 1. Clone and Setup

```bash
cd ~/repos/rust_doc_mcp
poetry install
```

This creates a virtual environment and installs all dependencies.

### 2. Download Rust Documentation

Before using the server, you need to generate/download documentation for the crates you want to access.

#### Option A: Using Cargo (Recommended for development)

```bash
# For a specific crate like Polars
cargo doc --package polars --no-deps
# Documentation will be in target/doc/polars/

# Or use a Rust project that depends on the crate
cd ~/your-rust-project
cargo doc --package polars --no-deps
```

#### Option B: Download from docs.rs (for published crates)

You can manually download HTML documentation if you have access to it, or use tools like `wget` or `curl`:

```bash
# Example: Download Polars docs if you have internet access
wget -r -np -nd -A '*.html,*.css,*.js,*.wasm' https://docs.rs/polars/ -P ~/rust_docs/polars
```

### 3. Configure the Server

Create the configuration file at `~/.config/rust-doc-mcp/config.json`:

```json
{
  "crates": {
    "polars": {
      "name": "polars",
      "path": "/path/to/polars/documentation",
      "description": "Polars - Fast DataFrame library"
    },
    "serde": {
      "name": "serde",
      "path": "/path/to/serde/documentation",
      "description": "Serialization framework"
    }
  }
}
```

**Key points:**
- `path`: Must be the root directory of the HTML documentation (the one containing `index.html`)
- Use absolute paths or `~` for home directory
- Add as many crates as you need

#### Finding Your Documentation Path

If you generated docs with `cargo doc`, the path is typically:
```
target/doc/{crate_name}/
```

Example:
```bash
# After running 'cargo doc --package polars'
# The path would be something like:
/home/username/my-rust-project/target/doc/polars/
```

### 4. Configure Claude

Add the MCP server to your Claude configuration. The configuration file location depends on your setup:

#### For Claude Desktop App

Edit `~/.claude/claude.json` (create it if it doesn't exist):

```json
{
  "mcpServers": {
    "rust-doc": {
      "command": "poetry",
      "args": ["run", "rust-doc-mcp"],
      "cwd": "/path/to/rust_doc_mcp"
    }
  }
}
```

Or if you prefer to use the installed script:

```json
{
  "mcpServers": {
    "rust-doc": {
      "command": "/path/to/venv/bin/rust-doc-mcp"
    }
  }
}
```

#### For Claude Web/Code Editor

Configure through the settings interface to point to your MCP server.

## Usage

Once configured, you can ask Claude questions about your Rust documentation:

### Available Tools

The server exposes these tools to Claude:

#### `search_rust_docs`
Search for documentation within a crate.

```
Query: "search_rust_docs" with crate="polars" and query="DataFrame"
Response: Returns matching documentation pages with previews
```

#### `get_rust_doc`
Retrieve the full HTML documentation for a specific item.

```
Query: "get_rust_doc" with crate="polars" and path="polars/struct.DataFrame.html"
Response: Returns the complete HTML documentation
```

#### `list_rust_crates`
List all configured crates and their status.

```
Query: "list_rust_crates"
Response: Shows all available crates
```

#### `list_crate_docs`
List all documentation files in a specific crate.

```
Query: "list_crate_docs" with crate="polars"
Response: Shows all indexed documentation pages
```

### Example Conversations

**Example 1: Search for DataFrame documentation**
```
You: "Search the Polars documentation for information about DataFrames"
Claude: [Uses search_rust_docs to find relevant pages]
```

**Example 2: Get specific API documentation**
```
You: "Show me the Polars DataFrame struct documentation"
Claude: [Uses get_rust_doc to retrieve the full page]
```

## Troubleshooting

### "Crate not found" Error

**Problem**: Claude says a crate isn't found.

**Solution**:
1. Check your config file: `cat ~/.config/rust-doc-mcp/config.json`
2. Verify the path exists: `ls /path/to/documentation/index.html`
3. Ensure the path points to the documentation root (contains `index.html`)
4. Restart Claude/the MCP server

### No Search Results

**Problem**: Searches return no results even though documentation exists.

**Solution**:
1. Verify the documentation was generated properly (check for `index.html`)
2. The indexer looks for `.html` files recursively
3. Check that the documentation path is correct in the config
4. Some minimal documentation might not index well

### "Index appears empty"

**Problem**: The crate is loaded but `list_crate_docs` shows nothing.

**Solution**:
1. The documentation might not have been fully generated
2. Regenerate: `cargo doc --package {crate} --no-deps --all-features`
3. Check that the directory actually contains `.html` files
4. You may need to re-index by restarting the server

## Advanced Configuration

### Multiple Crates

Add as many crates as needed to your config:

```json
{
  "crates": {
    "polars": {
      "name": "polars",
      "path": "~/rust_docs/polars",
      "description": "Fast DataFrame library"
    },
    "serde": {
      "name": "serde",
      "path": "~/rust_docs/serde",
      "description": "Serialization framework"
    },
    "tokio": {
      "name": "tokio",
      "path": "~/rust_docs/tokio",
      "description": "Async runtime"
    }
  }
}
```

### Generating Comprehensive Documentation

For the most complete documentation, generate with all features:

```bash
cargo doc --package {crate} --no-deps --all-features --document-private-items
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Quality

```bash
# Format code
poetry run black rust_doc_mcp/

# Lint
poetry run ruff check rust_doc_mcp/

# Type checking
poetry run mypy rust_doc_mcp/
```

### Project Structure

```
rust_doc_mcp/
├── __init__.py          # Package initialization
├── config.py            # Configuration management
├── indexer.py           # Documentation indexing and search
└── server.py            # MCP server implementation

pyproject.toml           # Poetry configuration
README.md               # This file
```

## How It Works

1. **Configuration**: You specify which Rust crate documentation to serve and where it's located
2. **Indexing**: When the server starts, it indexes all HTML files in the documentation directories
3. **Searching**: Claude can search indexed documentation by keywords
4. **Retrieval**: Claude can request the full HTML content of specific pages
5. **Serving**: The MCP server returns documentation through the MCP protocol to Claude

## Limitations

- Documentation must be downloaded/generated manually (no automatic downloads)
- Search is basic keyword-based (no full-text search features)
- Very large documentation sets might take time to index on first run
- HTML rendering in Claude may have limitations

## Contributing

Contributions are welcome! Areas for improvement:

- Better search algorithms
- Caching for faster indexing
- CLI tool for easier configuration
- Support for other documentation formats
- Performance optimizations for large doc sets

## License

MIT License - feel free to use and modify as needed.

## Troubleshooting Common Setup Issues

### Poetry Not Found

Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Then add to PATH if needed:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Virtual Environment Issues

If you encounter issues with the Poetry virtual environment:

```bash
# Clear Poetry cache
poetry cache clear . --all

# Reinstall dependencies
poetry install --no-cache
```

### Claude Not Recognizing the Server

1. Ensure the MCP server command works: `poetry run rust-doc-mcp --version`
2. Check that the path in `claude.json` is correct
3. Restart Claude completely (close and reopen)
4. Check Claude's logs for startup errors

### Documentation Not Indexing

Verify the documentation structure:
```bash
ls /path/to/your/docs/
# Should show: index.html, *.html files, css/, js/, etc.
```

## Support

For issues, questions, or suggestions:
1. Check this README for solutions
2. Verify your configuration matches the examples
3. Review error messages carefully - they often indicate missing paths or misconfiguration
