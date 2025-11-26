"""Statistics routes"""
from fastapi import APIRouter, HTTPException

from src.database import AsyncSessionLocal
from src.database.repositories.dress import recommendation_repo

router = APIRouter(prefix="", tags=["statistics"])


@router.get("/stats")
async def get_statistics():
    """Get recommendation statistics"""
    try:
        async with AsyncSessionLocal() as db:
            stats = await recommendation_repo.get_stats(db)
            return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
