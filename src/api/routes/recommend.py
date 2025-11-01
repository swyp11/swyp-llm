"""Recommendation routes"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas import RecommendationRequest, RecommendationResponse, DressRecommendation
from src.mcp.tools.recommender import recommend_wedding_dress

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

    Returns wedding dress recommendations with styling tips
    """
    try:
        # Call MCP tool directly
        result = await recommend_wedding_dress(
            arm_length=request.arm_length.value,
            leg_length=request.leg_length.value,
            neck_length=request.neck_length.value,
            face_shape=request.face_shape.value
        )

        # Transform MCP response to API response
        return RecommendationResponse(
            request_params=request,
            recommendations=[
                DressRecommendation(**rec)
                for rec in result["recommendations"]
            ],
            overall_advice=result["overall_advice"],
            cached=result.get("cached", False),
            source=result.get("source", "ai_generated")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
