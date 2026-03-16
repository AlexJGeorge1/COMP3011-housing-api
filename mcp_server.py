import httpx
from mcp.server.fastmcp import FastMCP

API_BASE = "http://localhost:8000"

mcp = FastMCP("UK Housing Affordability API")


@mcp.tool()
def get_affordability(region: str) -> dict:
    """Get housing affordability metrics for a UK region.
    Returns price-to-income ratio, rent-to-income %, and affordability band."""
    response = httpx.get(f"{API_BASE}/affordability/{region}")
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_trends(region: str) -> dict:
    """Get year-on-year house price trends for a UK region (2015-2024).
    Returns median prices per year, total % change, and CAGR."""
    response = httpx.get(f"{API_BASE}/trends/{region}")
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_rent_to_buy(region: str) -> dict:
    """Compare renting vs buying in a UK region.
    Returns estimated mortgage cost, deposit savings timeline, and a verdict."""
    response = httpx.get(f"{API_BASE}/rent-to-buy/{region}")
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_insights(region: str) -> dict:
    """Get an AI-generated housing market insight for a UK region.
    Powered by Llama 3 via Groq, grounded in real Land Registry and ONS data."""
    response = httpx.get(f"{API_BASE}/insights/{region}")
    response.raise_for_status()
    return response.json()


@mcp.tool()
def search_listings(query: str, region: str = None, limit: int = 10) -> dict:
    """Semantic search over property listings using natural language.
    Example queries: 'affordable flat in London', 'large detached house South East'."""
    params = {"q": query, "limit": limit}
    if region:
        params["region"] = region
    response = httpx.get(f"{API_BASE}/search", params=params)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def list_regions() -> dict:
    """List all UK regions available in the database."""
    response = httpx.get(f"{API_BASE}/regions")
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    mcp.run()
