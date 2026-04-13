"""Custom RAG MCP server for code retrieval"""
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import TextContent
from mcp import ServerSession

from lancedb import (
    DBConnection, 
    Table as DBTable,
    connect as DBConnect
)

from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator

@dataclass
class AppContext:
    """Application context with typed dependencies."""
    # Define DB connection for RAG
    lancedb: DBConnection
    lancedb_table: DBTable 

@asynccontextmanager
async def app_lifespan(mcp: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context."""
    # Initialize on startup
    lancedb = DBConnect("/path/to/your/db")  # Database.connect()
    lancedb_table = lancedb.open_table('code_chunks')
    try:
        yield AppContext(
            lancedb=lancedb,
            lancedb_table=lancedb_table
        )
    finally:
        # # Cleanup on shutdown
        # await lancedb
        pass


mcp = FastMCP("RAG server", lifespan=app_lifespan)


@mcp.tool()
async def search_codebase(query: str, ctx: Context[ServerSession, AppContext], limit: int = 10) -> list[TextContent]:
    """
    Search the codebase using vector similarity.
    
    Args:
        query: The search query
        limit: Maximum number of results to return
    """
    # Define LanceDB table
    lancedb_table = ctx.request_context.lifespan_context.lancedb_table
    # Query your vector database
    results = lancedb_table.search(query) \
        .limit(limit) \
        .to_list()
    
    # Format results for Continue
    formatted_results = []
    for result in results:
        formatted_results.append(TextContent(
            type="text",
            text=f"File: {result['filename']}\n\n{result['text']}"
        ))
    
    return formatted_results


@mcp.tool()
async def get_file_context(filename: str, ctx: Context[ServerSession, AppContext]) -> list[TextContent]:
    """
    Get all chunks from a specific file.
    
    Args:
        filename: The name of the file to retrieve
    """
    # Define LanceDB table
    lancedb_table = ctx.request_context.lifespan_context.lancedb_table
    # Fetch results
    results = lancedb_table.search() \
        .where(f"filename = '{filename}'") \
        .to_list()
    
    return [TextContent(
        type="text",
        text="\n".join([r['text'] for r in results])
    )]


def main():
    """Execute FastMCP server"""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
