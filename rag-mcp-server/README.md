# RAG MCP Server for Continue.dev

A simple MCP server providing RAG functionality to Continue.dev using LanceDB as the vector database.

## Features

- **Document Management**: Add, list, and remove documents from knowledge base
- **RAG Search**: Retrieve relevant context for queries
- **LanceDB Backend**: Efficient vector storage and retrieval
- **Continue.dev Integration**: Seamless integration as an MCP server
- **Single File Architecture**: All code in one file for simplicity
- **Configurable**: Customizable chunk sizes, embedding models, and similarity thresholds

## Quick Start

### Installation

```bash
cd rag-mcp-server
poetry install
```

### Running the Server

```bash
poetry run python rag_mcp_server.py
```

The server will start listening for MCP connections via stdio.

### Configure Continue.dev

Add the following to your Continue.dev configuration (usually `~/.continue/config.json` or in your VS Code settings):

```json
{
  "mcpServers": {
    "rag-mcp-server": {
      "command": "poetry",
      "args": ["run", "python", "rag_mcp_server.py"],
      "cwd": "/path/to/rag-mcp-server"
    }
  }
}
```

Replace `/path/to/rag-mcp-server` with the actual path to your project directory.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LANCEDB_PATH` | `./lancedb` | Directory to store LanceDB database |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace embedding model name |

## Available Tools

### 1. `rag_add_document`

Add documents to the RAG knowledge base.

**Parameters:**
- `document_id` (string, required): Unique identifier for the document
- `content` (string, required): The document content to index
- `metadata` (object, optional): Additional metadata (e.g., author, date, tags)

**Example:**
```json
{
  "name": "rag_add_document",
  "arguments": {
    "document_id": "my-doc-1",
    "content": "This is the document content...",
    "metadata": {
      "author": "John Doe",
      "date": "2024-01-15",
      "category": "technical"
    }
  }
}
```

### 2. `rag_search`

Search for relevant context in the knowledge base.

**Parameters:**
- `query` (string, required): The search query
- `top_k` (integer, optional): Number of results to return (default: 3)

**Example:**
```json
{
  "name": "rag_search",
  "arguments": {
    "query": "What is the main topic?",
    "top_k": 5
  }
}
```

### 3. `rag_list_documents`

List all documents currently in the knowledge base.

**Parameters:** None

**Example:**
```json
{
  "name": "rag_list_documents",
  "arguments": {}
}
```

### 4. `rag_delete_document`

Remove a document from the knowledge base.

**Parameters:**
- `document_id` (string, required): The document ID to delete

**Example:**
```json
{
  "name": "rag_delete_document",
  "arguments": {
    "document_id": "my-doc-1"
  }
}
```

### 5. `rag_get_context`

Get enriched context for a specific query with scores and metadata.

**Parameters:**
- `query` (string, required): The query to get context for

**Example:**
```json
{
  "name": "rag_get_context",
  "arguments": {
    "query": "Explain this concept"
  }
}
```

## Configuration

### Chunking Settings

The server uses the following default chunking configuration:

- **Chunk Size**: 512 tokens
- **Chunk Overlap**: 128 tokens
- **Embedding Model**: `all-MiniLM-L6-v2` (768-dimensional vectors)
- **Similarity Threshold**: 0.7

These can be modified in `rag_mcp_server.py` by changing the constants at the top of the file:

```python
CHUNK_SIZE = 512
CHUNK_OVERLAP = 128
SIMILARITY_THRESHOLD = 0.7
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
```

### Database Path

By default, the LanceDB database is stored in `./lancedb` relative to the server location. You can change this by setting the `LANCEDB_PATH` environment variable before starting the server:

```bash
LANCEDB_PATH=/custom/path poetry run python rag_mcp_server.py
```

## Use Cases

1. **Code Documentation**: Index your project's README files, documentation, and code comments
2. **Research Papers**: Store and query research papers for context-aware assistance
3. **Meeting Notes**: Create a searchable knowledge base from meeting transcripts
4. **Technical Support**: Build a FAQ system for troubleshooting common issues
5. **Personal Knowledge Management**: Organize your notes and documents for quick retrieval

## Troubleshooting

### Server Not Starting

If the server fails to start, check:
- Python version is 3.10 or higher
- Poetry dependencies are installed (`poetry install`)
- No port conflicts (MCP uses stdio, so no ports are needed)

### Empty Search Results

If searches return no results:
- Verify documents have been added using `rag_list_documents`
- Check that the query is relevant to the indexed content
- Try lowering `top_k` to see if there are matches with lower scores

### Memory Issues

The embedding model loads into memory when first used. If you experience memory issues:
- Use a smaller embedding model (e.g., `sentence-transformers/all-mpnet-base-v2` is larger, consider alternatives)
- Limit the number of documents indexed
- Close other memory-intensive applications

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Continue.dev                          │
├─────────────────────────────────────────────────────────┤
│                  MCP Protocol                            │
├─────────────────────────────────────────────────────────┤
│              rag_mcp_server.py                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  RAGServer Class                                 │  │
│  │  ├─ LanceDB Integration                          │  │
│  │  ├─ Chunking (RecursiveCharacterTextSplitter)   │  │
│  │  ├─ Embeddings (SentenceTransformers)           │  │
│  │  └─ Search (Vector Similarity)                  │  │
│  └──────────────────────────────────────────────────┘  │
│                  MCP Tools                               │
│  ├─ rag_add_document                                   │
│  ├─ rag_search                                         │
│  ├─ rag_list_documents                                 │
│  ├─ rag_delete_document                                │
│  └─ rag_get_context                                    │
└─────────────────────────────────────────────────────────┘
```

## License

MIT License - Feel free to modify and use as needed.