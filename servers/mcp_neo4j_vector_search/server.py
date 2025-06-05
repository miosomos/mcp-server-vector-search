from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import json
import logging
from typing import Any
import mcp.types as types
from neo4j import (
    AsyncDriver,
    AsyncGraphDatabase,
    AsyncTransaction,
)
from pydantic import Field
import os
from openai import OpenAI

load_dotenv()

logger = logging.getLogger("mcp-neo4j-vector-search")

NEO4J_URI=os.getenv("NEO4J_URI")
NEO4J_USERNAME=os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD=os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE=os.getenv("NEO4J_DATABASE")

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embeddings(prompt:str) -> list:
    """
    Get the embedding for a given prompt.
    Args:
        prompt (str): The input text to be embedded.
    Returns:
        list: The embedding vector for the input text.
    """
    embeddings = model.encode(prompt)
    
    return embeddings.tolist()

def get_open_ai_embeddings(text: str, client: OpenAI) -> list:
    """
    Generates an embedding for a given text.
    Args:
        text (str): The input text to be embedded.
        Returns:
        list: The embedding vector for the input text.
    """
    response = client.embeddings.create(
        input=[text],
        model='text-embedding-3-small',
    )
    
    prompt_embeddings = response.data[0].embedding

    if not isinstance(prompt_embeddings, list) or len(prompt_embeddings) != 1536:
        raise ValueError("The embedding must be a list of 1536 numbers")

    return prompt_embeddings

async def _read(tx: AsyncTransaction, query: str, params: dict[str, Any]) -> str:
    raw_results = await tx.run(query, params)
    eager_results = await raw_results.to_eager_result()

    return json.dumps([r.data() for r in eager_results.records], default=str)


def create_mcp_server(neo4j_driver: AsyncDriver, api_key: str, database: str = "neo4j") -> FastMCP:
    mcp: FastMCP = FastMCP("mcp-neo4j-vector-search", dependencies=["neo4j", "pydantic"])
    openai_client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    async def vector_search_neo4j(
        prompt: str = Field(
            ..., description="The prompt to search for related nodes using similarity search"
        ),
    ) -> list[types.TextContent]:
        """Search for the most similar nodes in the neo4j database using vector search."""
        
        prompt_embeddings = get_open_ai_embeddings(prompt, openai_client)
        
        if len(prompt_embeddings) != 1536:  
            raise ValueError(
                f"Embedding dimension mismatch: Expected 1536, got {len(prompt_embeddings)}. "
                "Ensure the model and Neo4j index dimensions match."
            )
        query = """
            WITH $prompt_embeddings AS prompt_embeddings
            CALL db.index.vector.queryNodes('embeddableIndex', 10, prompt_embeddings)
            YIELD node, score
            RETURN node.name as name, node.description as description, score
            ORDER BY score DESC
        """
        
        async with neo4j_driver.session(database=database) as session:
            results = await session.execute_read(
                _read, query, {"prompt_embeddings": prompt_embeddings}
            )
        
        if not results:
            logger.warning("No results found for the given prompt.")
            return [types.TextContent(type="text", text="No results found.")]
        
        return results
        
    mcp.add_tool(vector_search_neo4j)

    return mcp

def main(
    db_url: str,
    username: str,
    password: str,
    database: str,
    api_key: str,
) -> None:
    logger.info("Starting MCP neo4j Server")

    neo4j_driver = AsyncGraphDatabase.driver(
        db_url,
        auth=(
            username,
            password,
        ),
    )

    mcp = create_mcp_server(neo4j_driver, api_key, database)

    mcp.run(transport="stdio")

if __name__ == "__main__":
    main(
        os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        os.getenv("NEO4J_USERNAME", "neo4j"),
        os.getenv("NEO4J_PASSWORD", "password"),
        os.getenv("NEO4J_DATABASE", "neo4j"),
        os.getenv("OPENAI_API_KEY", "your_openai_api_key")
    )