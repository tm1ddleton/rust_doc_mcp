"""MCP Server for Rust documentation"""

from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent

from rust_doc_mcp.config import get_config_path, load_config
from rust_doc_mcp.indexer import DocIndexer


class RustDocServer:
    """MCP Server for Rust documentation"""

    def __init__(self):
        self.server = Server("rust-doc-mcp")
        self.indexers: dict[str, DocIndexer] = {}
        self.config = load_config(get_config_path())
        self._load_indexers()
        self._register_tools()

    def _load_indexers(self) -> None:
        """Load indexers for all configured crates"""
        for crate_name, crate_config in self.config.crates.items():
            doc_path = Path(crate_config.path).expanduser().resolve()
            if doc_path.exists():
                self.indexers[crate_name] = DocIndexer(doc_path)

    def _register_tools(self) -> None:
        """Register MCP tools"""
        self.server.add_tool(
            Tool(
                name="search_rust_docs",
                description="Search Rust documentation for a specific crate",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "crate": {
                            "type": "string",
                            "description": "The name of the Rust crate to search (e.g., 'polars')",
                        },
                        "query": {
                            "type": "string",
                            "description": "Search query for documentation",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 10)",
                            "default": 10,
                        },
                    },
                    "required": ["crate", "query"],
                },
            )
        )

        self.server.add_tool(
            Tool(
                name="get_rust_doc",
                description="Get the full documentation for a specific item",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "crate": {
                            "type": "string",
                            "description": "The name of the Rust crate",
                        },
                        "path": {
                            "type": "string",
                            "description": "The documentation path/key (obtained from search results)",
                        },
                    },
                    "required": ["crate", "path"],
                },
            )
        )

        self.server.add_tool(
            Tool(
                name="list_rust_crates",
                description="List all available Rust crate documentations",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            )
        )

        self.server.add_tool(
            Tool(
                name="list_crate_docs",
                description="List all documentation files in a specific crate",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "crate": {
                            "type": "string",
                            "description": "The name of the Rust crate",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 50)",
                            "default": 50,
                        },
                    },
                    "required": ["crate"],
                },
            )
        )

        @self.server.call_tool
        async def handle_tool_call(name: str, arguments: dict) -> Any:
            if name == "search_rust_docs":
                return await self._search_docs(
                    arguments["crate"],
                    arguments["query"],
                    arguments.get("limit", 10),
                )
            elif name == "get_rust_doc":
                return await self._get_doc(arguments["crate"], arguments["path"])
            elif name == "list_rust_crates":
                return await self._list_crates()
            elif name == "list_crate_docs":
                return await self._list_crate_docs(
                    arguments["crate"], arguments.get("limit", 50)
                )
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

    async def _search_docs(self, crate: str, query: str, limit: int) -> Any:
        """Search documentation"""
        if crate not in self.indexers:
            return [
                TextContent(
                    type="text",
                    text=f"Crate '{crate}' not found. Available crates: {', '.join(self.indexers.keys())}",
                )
            ]

        indexer = self.indexers[crate]
        results = indexer.search(query, limit=limit)

        if not results:
            return [
                TextContent(
                    type="text",
                    text=f"No documentation found for '{query}' in {crate}",
                )
            ]

        response = f"Found {len(results)} results for '{query}' in {crate}:\n\n"
        for i, result in enumerate(results, 1):
            response += f"{i}. **{result['title']}** (path: `{result['key']}`)\n"
            response += f"   {result['preview'][:100]}...\n\n"

        return [TextContent(type="text", text=response)]

    async def _get_doc(self, crate: str, path: str) -> Any:
        """Get specific documentation"""
        if crate not in self.indexers:
            return [
                TextContent(
                    type="text",
                    text=f"Crate '{crate}' not found.",
                )
            ]

        indexer = self.indexers[crate]
        doc = indexer.get_doc(path)

        if not doc:
            return [
                TextContent(
                    type="text",
                    text=f"Documentation for '{path}' not found in {crate}",
                )
            ]

        # Return HTML content - Claude can render it
        return [TextContent(type="text", text=doc["html"])]

    async def _list_crates(self) -> Any:
        """List available crates"""
        crates = self.config.list_crates()
        if not crates:
            return [
                TextContent(
                    type="text",
                    text="No crates configured. See README for setup instructions.",
                )
            ]

        response = "Available Rust documentation:\n\n"
        for name, description in crates.items():
            status = "✓ Loaded" if name in self.indexers else "✗ Not found"
            response += f"- **{name}**: {description} [{status}]\n"

        return [TextContent(type="text", text=response)]

    async def _list_crate_docs(self, crate: str, limit: int) -> Any:
        """List documentation in a crate"""
        if crate not in self.indexers:
            return [
                TextContent(
                    type="text",
                    text=f"Crate '{crate}' not found.",
                )
            ]

        indexer = self.indexers[crate]
        docs = indexer.list_all(limit=limit)

        if not docs:
            return [
                TextContent(
                    type="text",
                    text=f"No documentation indexed for {crate}",
                )
            ]

        response = f"Documentation in {crate} ({len(docs)} total, showing {min(limit, len(docs))}):\n\n"
        for doc in docs:
            response += f"- **{doc['title']}** (`{doc['key']}`)\n"

        return [TextContent(type="text", text=response)]

    async def run(self) -> None:
        """Run the server"""
        async with self.server:
            pass


def main() -> None:
    """Entry point"""
    server = RustDocServer()
    import asyncio

    asyncio.run(server.run())


if __name__ == "__main__":
    main()
