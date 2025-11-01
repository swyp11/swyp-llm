"""MCP Tool: Statistics"""
from src.database import AsyncSessionLocal
from src.database.repositories.recommendation import recommendation_repo


async def get_recommendation_stats() -> dict:
    """
    웨딩 드레스 추천 서비스의 통계 정보를 조회합니다.

    전체 쿼리 수, 총 액세스 수, 캐시 히트율, 인기 있는 체형 조합 등을 반환합니다.
    """
    async with AsyncSessionLocal() as db:
        stats = await recommendation_repo.get_stats(db)
        return stats


def register_stats_tool(mcp):
    """Register stats tool with MCP server"""
    mcp.tool()(get_recommendation_stats)
