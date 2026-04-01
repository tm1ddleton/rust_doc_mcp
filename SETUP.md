# Quick Setup Guide

Get up and running with Rust Doc MCP Server in 10 minutes.

## Prerequisites

- Python 3.9+
- Poetry (install from https://python-poetry.org/docs/#installation)
- A Rust project or access to Rust documentation

## Step 1: Install the Server

```bash
cd ~/repos/rust_doc_mcp
poetry install
```

## Step 2: Generate Rust Documentation

Choose one of these options:

### Option 1: From Your Own Rust Project (Recommended)

If you have a Rust project that uses Polars or other crates:

```bash
cd ~/your-rust-project
cargo doc --package polars --no-deps
# Documentation is now at: target/doc/polars/
```

### Option 2: Generate in a Temporary Project

```bash
# Create a temp project
cargo new --bin temp_docs
cd temp_docs

# Add the crates you want to document
cargo add polars serde tokio

# Generate docs
cargo doc --no-deps
# Docs are at: target/doc/
```

## Step 3: Configure the Server

### Option A: Interactive Setup (Easiest)

```bash
poetry run rust-doc-mcp-init
```

Follow the prompts to add your crates.

### Option B: Manual Configuration

Create `~/.config/rust-doc-mcp/config.json`:

```json
{
  "crates": {
    "polars": {
      "name": "polars",
      "path": "/path/to/your/docs/polars",
      "description": "Fast DataFrame library"
    }
  }
}
```

**Make sure the path points to the documentation root** (it should contain `index.html`).

### Verify Your Setup

```bash
poetry run rust-doc-mcp-verify
```

This will check that all configured crates are accessible.

## Step 4: Configure Claude

### For Claude Desktop App

Edit/create `~/.claude/claude.json`:

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

Replace `/path/to/rust_doc_mcp` with the actual path (typically `~/repos/rust_doc_mcp`).

### Restart Claude

Close and reopen Claude for it to pick up the new MCP server.

## Step 5: Test It Out

In Claude, try:

```
Can you search the Polars documentation for "DataFrame"?
```

If Claude can use the `search_rust_docs` tool and return results, you're all set!

## Troubleshooting

### "Crate not found"

Check your configuration:
```bash
poetry run rust-doc-mcp-config
```

The path must exist and contain `.html` files.

### "No documentation indexed"

Verify the documentation path:
```bash
ls /path/to/your/polars/docs/index.html
# Should exist
```

### Claude doesn't see the server

1. Verify the path in `~/.claude/claude.json` is correct
2. Use absolute paths, not relative paths
3. Restart Claude completely
4. Check that `poetry run rust-doc-mcp` runs without errors

## Next Steps

- Add more crates to your configuration
- Generate documentation with `--all-features` for more complete docs
- See [README.md](README.md) for more advanced usage

## Common Paths

If you generated docs in a Rust project:

```bash
# After running cargo doc
/home/username/my-rust-project/target/doc/polars/
/home/username/my-rust-project/target/doc/serde/
```

The path should end with the crate name and contain an `index.html` file.
