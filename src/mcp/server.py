"""
MCP Server using fastmcp
"""
from fastmcp import FastMCP
from src.mcp.tools.recommender import register_recommendation_tool
from src.mcp.tools.stats import register_stats_tool
from src.mcp.resources.guides import register_guide_resource
from src.database import init_db
from src.config import redis_client

# Initialize MCP server
mcp = FastMCP("Wedding Dress Recommender")


# Register tools
register_recommendation_tool(mcp)
register_stats_tool(mcp)

# Register resources
register_guide_resource(mcp)


@mcp.on_startup()
async def on_startup():
    """Initialize database and Redis connections"""
    await init_db()
    await redis_client.connect()
    print("✅ MCP Server initialized")


@mcp.on_shutdown()
async def on_shutdown():
    """Cleanup connections"""
    await redis_client.disconnect()
    print("👋 MCP Server shutdown")


if __name__ == "__main__":
    mcp.run()
