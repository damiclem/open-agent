import os
import sys
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

# LanceDB
import lancedb
import lance

# LangChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

# MCP
import mcp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configuration
LANCEDB_PATH = os.environ.get("LANCEDB_PATH", "./lancedb")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_SIZE = 512
CHUNK_OVERLAP = 128
SIMILARITY_THRESHOLD = 0.7

# Initialize MCP server
server = Server("rag-mcp-server")


class RAGServer:
    def __init__(self):
        self.db_path = Path(LANCEDB_PATH)
        self.db_path.mkdir(exist_ok=True)
        self.lancedb = lancedb.connect(str(self.db_path))
        self.embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.chunker = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len
        )
        self._initialized = False

    def _get_table(self):
        """Get or create LanceDB table."""
        if not self._initialized:
            table_name = "rag_chunks"
            if table_name not in self.lancedb:
                self.lancedb.create_table(table_name).create(
                    schema=[
                        ("chunk_id", "uuid"),
                        ("embedding", "vector"),
                        ("content", "text"),
                        ("document_id", "string"),
                        ("metadata", "json")
                    ],
                    mode="overwrite"
                )
            self._initialized = True
        return self.lancedb.open_table("rag_chunks")

    def add_document(self, document_id: str, content: str, metadata: Optional[Dict] = None):
        """Add a document to the knowledge base."""
        table = self._get_table()
        
        # Split document into chunks
        chunks = self.chunker.split_text(content)
        
        # Generate embeddings and insert into database
        embeddings = self.embedding_model.embed_documents(chunks)
        
        insert_data = []
        for chunk, embedding in zip(chunks, embeddings):
            chunk_data = {
                "chunk_id": str(uuid.uuid4()),
                "embedding": embedding,
                "content": chunk,
                "document_id": document_id,
                "metadata": metadata or {}
            }
            insert_data.append(chunk_data)
        
        # Upsert into LanceDB
        if insert_data:
            table.add(insert_data)
        
        return len(insert_data)

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant chunks."""
        table = self._get_table()
        
        # Generate query embedding
        query_embedding = self.embedding_model.embed_query(query)
        
        # Perform similarity search
        results = table.search(query_embedding).limit(top_k).to_pandas()
        
        if results.empty:
            return []
        
        # Convert to list of dicts
        results_list = []
        for _, row in results.iterrows():
            result = {
                "chunk_id": row["chunk_id"],
                "content": row["content"],
                "document_id": row["document_id"],
                "score": float(row["distance"])
            }
            results_list.append(result)
        
        return results_list

    def list_documents(self) -> List[Dict]:
        """List all unique documents."""
        table = self._get_table()
        
        if table is None or table.schema is None:
            return []
        
        # Get unique document IDs
        doc_ids = table.search().select(["document_id"]).to_pandas()["document_id"].unique()
        
        return [{"document_id": doc_id.decode() if isinstance(doc_id, bytes) else doc_id} 
                for doc_id in doc_ids]

    def delete_document(self, document_id: str) -> bool:
        """Delete all chunks from a document."""
        table = self._get_table()
        
        if table is None:
            return False
        
        # Delete chunks matching document_id
        try:
            table.delete(f"document_id = '{document_id}'")
            return True
        except Exception:
            return False


# Create global instance
rag_server = RAGServer()


def create_tools() -> List[Tool]:
    """Create MCP tools for RAG operations."""
    return [
        Tool(
            name="rag_add_document",
            description="Add a document to the RAG knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "Unique identifier for the document"
                    },
                    "content": {
                        "type": "string",
                        "description": "The document content"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata for the document"
                    }
                },
                "required": ["document_id", "content"]
            }
        ),
        Tool(
            name="rag_search",
            description="Search for relevant context in the knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 3)",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="rag_list_documents",
            description="List all documents in the knowledge base",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="rag_delete_document",
            description="Delete a document from the knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "The document ID to delete"
                    }
                },
                "required": ["document_id"]
            }
        ),
        Tool(
            name="rag_get_context",
            description="Get context for a specific query with metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to get context for"
                    }
                },
                "required": ["query"]
            }
        )
    ]


@server.list_tools()
async def handle_list_tools():
    """List available tools."""
    return create_tools()


@server.call_tool()
async def handle_call_tool(names: List[str], arguments: Dict[str, Any]):
    """Handle tool calls."""
    results = []
    
    if "rag_add_document" in names:
        doc_id = arguments.get("document_id")
        content = arguments.get("content")
        metadata = arguments.get("metadata", {})
        
        try:
            chunk_count = rag_server.add_document(doc_id, content, metadata)
            results.append(TextContent(
                type="text",
                text=f"Added {chunk_count} chunks to document '{doc_id}'"
            ))
        except Exception as e:
            results.append(TextContent(
                type="text",
                text=f"Error adding document: {str(e)}"
            ))
    
    elif "rag_search" in names:
        query = arguments.get("query")
        top_k = arguments.get("top_k", 3)
        
        try:
            results = rag_server.search(query, top_k)
            context = "\n\n".join([
                f"Document: {r['document_id']}\nScore: {r['score']}\nContent: {r['content']}"
                for r in results
            ])
            results.append(TextContent(
                type="text",
                text=context
            ))
        except Exception as e:
            results.append(TextContent(
                type="text",
                text=f"Error searching: {str(e)}"
            ))
    
    elif "rag_list_documents" in names:
        try:
            docs = rag_server.list_documents()
            docs_str = json.dumps(docs, indent=2)
            results.append(TextContent(
                type="text",
                text=docs_str
            ))
        except Exception as e:
            results.append(TextContent(
                type="text",
                text=f"Error listing documents: {str(e)}"
            ))
    
    elif "rag_delete_document" in names:
        doc_id = arguments.get("document_id")
        
        try:
            success = rag_server.delete_document(doc_id)
            results.append(TextContent(
                type="text",
                text=f"Deleted document '{doc_id}' successfully" if success else f"Error deleting document '{doc_id}'"
            ))
        except Exception as e:
            results.append(TextContent(
                type="text",
                text=f"Error deleting document: {str(e)}"
            ))
    
    elif "rag_get_context" in names:
        query = arguments.get("query")
        
        try:
            results = rag_server.search(query, top_k=5)
            context = "\n\n".join([
                f"[{r['document_id']} (score: {r['score']:.3f)}]\n{r['content']}"
                for r in results
            ])
            results.append(TextContent(
                type="text",
                text=context
            ))
        except Exception as e:
            results.append(TextContent(
                type="text",
                text=f"Error getting context: {str(e)}"
            ))
    
    return results


@asynccontextmanager
async def server_lifespan(server: Server):
    """Manage server lifespan."""
    try:
        yield
    finally:
        # Cleanup on shutdown
        pass


if __name__ == "__main__":
    import asyncio
    
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server_lifespan(server)
            )
    
    asyncio.run(main())