"""Recommendation routes"""
from fastapi import APIRouter, HTTPException

from src.services.schemas import RecommendationRequest, RecommendationResponse, DressRecommendation
from src.services.recommender import recommender, DressRecommender
from src.database import AsyncSessionLocal
from src.database.repositories.recommendation import recommendation_repo
from src.config import redis_client

router = APIRouter(prefix="", tags=["recommendations"])


@router.post("/recommend", response_model=RecommendationResponse)
async def recommend_dress(request: RecommendationRequest):
    """
    Get wedding dress recommendations

    Parameters:
    - **arm_length**: 팔 길이 (짧은, 보통, 긴)
    - **leg_length**: 다리 길이 (짧은, 보통, 긴)
    - **neck_length**: 목 길이 (짧은, 보통, 긴)
    - **face_shape**: 얼굴형 (달걀, 넓은, 각진, 긴)
    - **num_recommendations**: 추천받을 스타일 개수 (1-5개, 기본값: 3)

    Returns wedding dress recommendations with styling tips
    """
    try:
        arm_length = request.arm_length.value
        leg_length = request.leg_length.value
        neck_length = request.neck_length.value
        face_shape = request.face_shape.value
        num_recommendations = request.num_recommendations

        # Generate query hash
        query_hash = DressRecommender.generate_hash(
            arm_length, leg_length, neck_length, face_shape, num_recommendations
        )

        # 1. Check Redis cache
        cached_result = await redis_client.get(f"recommendation:{query_hash}")
        if cached_result:
            return RecommendationResponse(
                request_params=request,
                recommendations=[
                    DressRecommendation(**rec)
                    for rec in cached_result["recommendations"]
                ],
                overall_advice=cached_result["overall_advice"],
                cached=True,
                source="redis_cache"
            )

        # 2. Check MySQL database
        async with AsyncSessionLocal() as db:
            db_record = await recommendation_repo.get_by_hash(db, query_hash)
            if db_record:
                result = db_record.recommendation
                # Save to Redis cache
                await redis_client.set(f"recommendation:{query_hash}", result)

                return RecommendationResponse(
                    request_params=request,
                    recommendations=[
                        DressRecommendation(**rec)
                        for rec in result["recommendations"]
                    ],
                    overall_advice=result["overall_advice"],
                    cached=True,
                    source="mysql_db"
                )

            # 3. Generate new recommendation
            recommendation = await recommender.generate(
                arm_length, leg_length, neck_length, face_shape, num_recommendations
            )

            # Save to database
            await recommendation_repo.create(
                db, query_hash, arm_length, leg_length, neck_length, face_shape, recommendation
            )

        # Save to cache
        await redis_client.set(f"recommendation:{query_hash}", recommendation)

        return RecommendationResponse(
            request_params=request,
            recommendations=[
                DressRecommendation(**rec)
                for rec in recommendation["recommendations"]
            ],
            overall_advice=recommendation["overall_advice"],
            cached=False,
            source="ai_generated"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
