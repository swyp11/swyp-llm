"""Statistics routes"""
from fastapi import APIRouter, HTTPException

from src.mcp.tools.stats import get_recommendation_stats

router = APIRouter(prefix="", tags=["statistics"])


@router.get("/stats")
async def get_statistics():
    """Get recommendation statistics"""
    try:
        stats = await get_recommendation_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mcp/tools")
async def list_mcp_tools():
    """List available MCP tools"""
    return {
        "tools": [
            {
                "name": "recommend_wedding_dress",
                "description": "신부의 체형 특징을 바탕으로 웨딩 드레스를 추천합니다"
            },
            {
                "name": "get_recommendation_stats",
                "description": "웨딩 드레스 추천 서비스의 통계 정보를 조회합니다"
            }
        ]
    }
