"""
HTTP Client for Wedding Dress API
"""
import asyncio
import httpx
from typing import Optional


class WeddingDressHTTPClient:
    """HTTP Client for Wedding Dress API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.aclose()

    async def health_check(self) -> dict:
        """Check server health"""
        response = await self.client.get("/health")
        response.raise_for_status()
        return response.json()

    async def recommend_dress(
        self,
        arm_length: str,
        leg_length: str,
        neck_length: str,
        face_shape: str
    ) -> dict:
        """Get wedding dress recommendations"""
        payload = {
            "arm_length": arm_length,
            "leg_length": leg_length,
            "neck_length": neck_length,
            "face_shape": face_shape
        }

        response = await self.client.post("/recommend", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_statistics(self) -> dict:
        """Get recommendation statistics"""
        response = await self.client.get("/stats")
        response.raise_for_status()
        return response.json()


async def main():
    """Example usage"""
    async with WeddingDressHTTPClient() as client:
        # Health check
        print("🏥 Health Check...")
        health = await client.health_check()
        print(f"Status: {health['status']}\n")

        # Get recommendation
        print("👰 Getting Recommendation...")
        result = await client.recommend_dress(
            arm_length="보통",
            leg_length="긴",
            neck_length="보통",
            face_shape="달걀"
        )

        print(f"\n✨ Recommendations (Cached: {result['cached']}):")
        print(f"\n{result['overall_advice']}\n")

        for idx, rec in enumerate(result['recommendations'], 1):
            print(f"{idx}. {rec['style_name']}")
            print(f"   {rec['description']}")
            print(f"   Tips:")
            for tip in rec['styling_tips']:
                print(f"     • {tip}")
            print()

        # Get statistics
        print("📊 Statistics:")
        stats = await client.get_statistics()
        print(f"Total queries: {stats['total_unique_queries']}")
        print(f"Cache hit rate: {stats['cache_hit_rate']:.2%}")


if __name__ == "__main__":
    asyncio.run(main())
