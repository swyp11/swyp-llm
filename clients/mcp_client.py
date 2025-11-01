"""
MCP Client for Wedding Dress Recommendations
"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack


class WeddingDressMCPClient:
    """MCP Client for Wedding Dress Recommendations"""

    def __init__(self, server_script_path: str = "src/mcp/server.py"):
        self.server_script_path = server_script_path
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()

    async def __aenter__(self):
        """Connect to MCP server"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "src.mcp.server"],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()
        print("✅ MCP Client connected")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Disconnect from MCP server"""
        await self.exit_stack.aclose()
        print("👋 MCP Client disconnected")

    async def list_tools(self) -> list:
        """List available tools"""
        response = await self.session.list_tools()
        return response.tools

    async def list_resources(self) -> list:
        """List available resources"""
        response = await self.session.list_resources()
        return response.resources

    async def recommend_dress(
        self,
        arm_length: str,
        leg_length: str,
        neck_length: str,
        face_shape: str
    ) -> dict:
        """Get wedding dress recommendations"""
        result = await self.session.call_tool(
            "recommend_wedding_dress",
            arguments={
                "arm_length": arm_length,
                "leg_length": leg_length,
                "neck_length": neck_length,
                "face_shape": face_shape
            }
        )

        if result.content:
            import json
            return json.loads(result.content[0].text)
        return {}

    async def get_statistics(self) -> dict:
        """Get recommendation statistics"""
        result = await self.session.call_tool(
            "get_recommendation_stats",
            arguments={}
        )

        if result.content:
            import json
            return json.loads(result.content[0].text)
        return {}

    async def get_body_measurement_guide(self) -> str:
        """Get body measurement options guide"""
        result = await self.session.read_resource(
            uri="wedding-dress://body-measurements"
        )

        if result.contents:
            return result.contents[0].text
        return ""


async def main():
    """Example usage"""
    async with WeddingDressMCPClient() as client:
        print("\n" + "="*60)
        print("🎀 Wedding Dress MCP Client")
        print("="*60)

        # List tools
        print("\n📋 Available Tools:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"  • {tool.name}")

        # Get recommendation
        print("\n👰 Getting Recommendation...")
        recommendation = await client.recommend_dress(
            arm_length="보통",
            leg_length="긴",
            neck_length="보통",
            face_shape="달걀"
        )

        print(f"\n{'💾 Cached: ' + str(recommendation.get('cached', False))}")
        print(f"{'🎯 Source: ' + recommendation.get('source', 'unknown')}")
        print(f"\n💡 Overall Advice:")
        print(f"  {recommendation.get('overall_advice', 'N/A')}")

        print(f"\n✨ Recommendations:")
        for idx, rec in enumerate(recommendation.get('recommendations', []), 1):
            print(f"\n  {idx}. {rec['style_name']}")
            print(f"     {rec['description']}")

        # Get statistics
        print("\n📊 Statistics:")
        stats = await client.get_statistics()
        print(f"  Total queries: {stats.get('total_unique_queries', 0)}")
        print(f"  Cache hit rate: {stats.get('cache_hit_rate', 0):.2%}")


if __name__ == "__main__":
    asyncio.run(main())
