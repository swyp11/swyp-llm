"""MCP Tool: Wedding Dress Recommendation"""
from typing import Annotated

from src.core.recommender import DressRecommender, recommender
from src.database import AsyncSessionLocal
from src.database.repositories.recommendation import recommendation_repo
from src.config import redis_client


async def recommend_wedding_dress(
    arm_length: Annotated[str, "팔 길이 (짧은, 보통, 긴)"],
    leg_length: Annotated[str, "다리 길이 (짧은, 보통, 긴)"],
    neck_length: Annotated[str, "목 길이 (짧은, 보통, 긴)"],
    face_shape: Annotated[str, "얼굴형 (달걀, 넓은, 각진, 긴)"]
) -> dict:
    """
    신부의 체형 특징을 바탕으로 웨딩 드레스를 추천합니다.

    캐시된 결과가 있으면 즉시 반환하고, 없으면 AI가 새로 생성합니다.
    """
    # Generate query hash
    query_hash = DressRecommender.generate_hash(arm_length, leg_length, neck_length, face_shape)

    # 1. Check Redis cache
    cached_result = await redis_client.get(f"recommendation:{query_hash}")
    if cached_result:
        cached_result["cached"] = True
        cached_result["source"] = "redis_cache"
        return cached_result

    # 2. Check MySQL database
    async with AsyncSessionLocal() as db:
        db_record = await recommendation_repo.get_by_hash(db, query_hash)
        if db_record:
            result = db_record.recommendation
            # Save to Redis cache
            await redis_client.set(f"recommendation:{query_hash}", result)
            result["cached"] = True
            result["source"] = "mysql_db"
            return result

        # 3. Generate new recommendation
        recommendation = await recommender.generate(
            arm_length, leg_length, neck_length, face_shape
        )

        # Save to database
        await recommendation_repo.create(
            db, query_hash, arm_length, leg_length, neck_length, face_shape, recommendation
        )

    # Save to cache
    await redis_client.set(f"recommendation:{query_hash}", recommendation)

    recommendation["cached"] = False
    recommendation["source"] = "ai_generated"
    recommendation["request_params"] = {
        "arm_length": arm_length,
        "leg_length": leg_length,
        "neck_length": neck_length,
        "face_shape": face_shape
    }

    return recommendation


def register_recommendation_tool(mcp):
    """Register recommendation tool with MCP server"""
    mcp.tool()(recommend_wedding_dress)
