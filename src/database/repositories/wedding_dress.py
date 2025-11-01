"""Repository for wedding dress operations"""
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from src.database.models import WeddingDress
from src.services.schemas import WeddingDressCreate, WeddingDressUpdate


class WeddingDressRepository:
    """Handle database operations for wedding dresses"""

    @staticmethod
    async def get_by_id(db: AsyncSession, dress_id: int) -> Optional[WeddingDress]:
        """Get wedding dress by ID"""
        result = await db.execute(
            select(WeddingDress).where(WeddingDress.id == dress_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        available_only: bool = False
    ) -> List[WeddingDress]:
        """Get all wedding dresses with pagination"""
        query = select(WeddingDress)

        if available_only:
            query = query.where(WeddingDress.availability == True)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_style(
        db: AsyncSession,
        style: str,
        available_only: bool = False
    ) -> List[WeddingDress]:
        """Get wedding dresses by style"""
        query = select(WeddingDress).where(WeddingDress.style == style)

        if available_only:
            query = query.where(WeddingDress.availability == True)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, dress: WeddingDressCreate) -> WeddingDress:
        """Create new wedding dress"""
        db_dress = WeddingDress(**dress.model_dump())
        db.add(db_dress)
        await db.commit()
        await db.refresh(db_dress)
        return db_dress

    @staticmethod
    async def update(
        db: AsyncSession,
        dress_id: int,
        dress_update: WeddingDressUpdate
    ) -> Optional[WeddingDress]:
        """Update wedding dress"""
        # Get existing dress
        result = await db.execute(
            select(WeddingDress).where(WeddingDress.id == dress_id)
        )
        db_dress = result.scalar_one_or_none()

        if not db_dress:
            return None

        # Update only provided fields
        update_data = dress_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_dress, field, value)

        await db.commit()
        await db.refresh(db_dress)
        return db_dress

    @staticmethod
    async def delete(db: AsyncSession, dress_id: int) -> bool:
        """Delete wedding dress"""
        result = await db.execute(
            select(WeddingDress).where(WeddingDress.id == dress_id)
        )
        db_dress = result.scalar_one_or_none()

        if not db_dress:
            return False

        await db.delete(db_dress)
        await db.commit()
        return True

    @staticmethod
    async def get_available_count(db: AsyncSession) -> int:
        """Get count of available dresses"""
        result = await db.execute(
            select(func.count(WeddingDress.id)).where(
                WeddingDress.availability == True
            )
        )
        return result.scalar()

    @staticmethod
    async def get_styles(db: AsyncSession) -> List[str]:
        """Get unique dress styles"""
        result = await db.execute(
            select(WeddingDress.style)
            .distinct()
            .where(WeddingDress.style.isnot(None))
        )
        return [style for style in result.scalars().all() if style]


# Global repository instance
wedding_dress_repo = WeddingDressRepository()
