# 🔍 MCP Server - Vector Search

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.0+-green.svg)](https://neo4j.com)
[![FastMCP](https://img.shields.io/badge/FastMCP-Latest-orange.svg)](https://github.com/jlowin/fastmcp)
[![uv](https://img.shields.io/badge/uv-Package%20Manager-purple.svg)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A blazing-fast **Model Context Protocol (MCP) Server** built with **FastMCP** that seamlessly combines Neo4j's graph database capabilities with advanced vector search using embeddings. This server enables intelligent semantic search across your knowledge graph, allowing you to discover contextually relevant information through natural language queries with lightning speed.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │◄──►│   Vector Search  │◄──►│      Neo4j      │
│   (Claude AI)   │    │      Server      │    │     Database    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │    Embeddings    │
                       └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **[uv](https://github.com/astral-sh/uv)** 
- **Neo4j Database** (v5.0+) with APOC plugin
- **OpenAI API Key**

### Installation with uv

1. **Install uv** (if not already installed)
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone and setup the project**
   ```bash
   git clone https://github.com/omarguzmanm/mcp-server-vector-search.git
   cd mcp-server-vector-search
   
   # Create virtual environment and install dependencies
   uv venv
   uv pip install fastmcp neo4j openai python-dotenv sentence-transformers pydantic
   ```

3. **Environment Configuration**
   ```bash
   # Create .env file
   cp .env.example .env
   ```
   
   Edit `.env` with your configurations:
   ```env
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your_neo4j_password
   NEO4J_DATABASE=neo4j
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Neo4j Vector Index Setup**
   ```cypher
   // Create vector index for 1536-dimensional OpenAI embeddings
   // If does not works
   CREATE VECTOR INDEX embeddableIndex FOR (n:Document) ON (n.embedding)
   OPTIONS {indexConfig: {
     `vector.dimensions`: 1536,
     `vector.similarity_function`: 'cosine'
   }}
   ```

5. **Launch the Server**
   ```bash
   # Activate virtual environment
   source .venv/bin/activate  # On Linux/macOS
   # or
   .venv\Scripts\activate     # On Windows
   
   # Start the FastMCP server
   python main.py
   ```

## 🛠️ Tool

The server exposes a single, powerful tool optimized for vector search:

#### 🔍 Vector Search
```python
vector_search_neo4j(
    prompt="Find documents about machine learning and neural networks"
)
```

**What it does:**
- Converts your natural language query into a 1536-dimensional vector using OpenAI
- Searches your Neo4j vector index for the most semantically similar nodes
- Returns ranked results with similarity scores

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEO4J_URI` | Neo4j connection URI | ✅ | `bolt://localhost:7687` |
| `NEO4J_USERNAME` | Neo4j username | ✅ | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | ✅ | `password` |
| `NEO4J_DATABASE` | Neo4j database name | ✅ | `neo4j` |
| `OPENAI_API_KEY` | OpenAI API key | ❌ | `all-MiniLM-L6-v2 model` |

### Neo4j Requirements

1. **APOC Plugin**: Essential for advanced graph operations
2. **Vector Index**: Must support 1536 dimensions for OpenAI embeddings
3. **Node Structure**: Nodes should have `embedding` properties as vectors


### Performance Optimization

- **uv Benefits**: 10-100x faster dependency resolution compared to pip
- **FastMCP Advantages**: Minimal overhead, optimized for MCP protocol
- **Connection Pooling**: Automatic Neo4j connection management
- **Async Operations**: Non-blocking I/O for maximum throughput

## 🤝 Integration with Claude Desktop

### MCP Configuration
Add to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
      "mcp-neo4j-vector-search": {
      "command": "python",
      "args": [
        "you\\server.py",
        "--with",
        "mcp[cli]",
        "--with",
        "neo4j",
        "--with",
        "pydantic"
      ],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "your_password",
        "NEO4J_DATABASE": "neo4j",
        "OPENAI_API_KEY": "your_api_key"
      }
    }
  }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   # Reinstall dependencies with uv
   uv pip install --force-reinstall fastmcp neo4j openai
   ```

2. **"Vector index not found"**
   ```cypher
   // Check existing indexes
   SHOW INDEXES
   
   // Create if missing
   CREATE VECTOR INDEX embeddableIndex FOR (n:Document) ON (n.embedding)
   OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}}
   ```

3. **OpenAI API errors**
   ```bash
   # Verify API key
   uv run python -c "
   import os
   from openai import OpenAI
   client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
   print('API key is valid!' if client.api_key else 'API key missing!')
   "
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `uv pip install -e ".[dev]"`
4. Make your changes and add tests
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[FastMCP](https://github.com/jlowin/fastmcp)** - For the incredible MCP framework
- **[uv](https://github.com/astral-sh/uv)** - For blazing-fast Python package management
- **[Neo4j](https://neo4j.com)** - For powerful graph database capabilities
- **[OpenAI](https://openai.com)** - For state-of-the-art embedding models
- **[Model Context Protocol](https://github.com/modelcontextprotocol/python-sdk)** - For the protocol specification

---

<div align="center">
  <p>🚀 Made with ❤️ for the AI and Graph Database community</p>
  <p>
    <a href="#-mcp-server---vector-search">⬆️ Back to Top</a>
  </p>
</div>

