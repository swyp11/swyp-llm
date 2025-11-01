"""SQLAlchemy database models"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Index, Text, DECIMAL, Boolean, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.session import Base


class WeddingDress(Base):
    """Wedding dress catalog"""
    __tablename__ = "wedding_dresses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2))
    style = Column(String(100), index=True)
    size = Column(String(50))
    color = Column(String(50))
    fabric = Column(String(100))
    availability = Column(Boolean, default=True, index=True)
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    surveys = relationship("Survey", back_populates="dress")


class Survey(Base):
    """Anonymous body measurement survey and dress recommendation"""
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)

    # Body measurements
    arm_length = Column(Enum('short', 'medium', 'long', name='arm_length_enum'), nullable=False)
    leg_length = Column(Enum('short', 'medium', 'long', name='leg_length_enum'), nullable=False)
    neck_length = Column(Enum('short', 'medium', 'long', name='neck_length_enum'), nullable=False)
    face_shape = Column(Enum('oval', 'wide', 'angular', 'long', name='face_shape_enum'), nullable=False)

    # Recommended dress
    dress_id = Column(Integer, ForeignKey('wedding_dresses.id', ondelete='SET NULL'), index=True)

    # Event information
    event_date = Column(Date)
    notes = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    dress = relationship("WeddingDress", back_populates="surveys")

    __table_args__ = (
        Index('idx_body_type', 'arm_length', 'leg_length', 'neck_length', 'face_shape'),
    )


class RecommendationQuery(Base):
    """Store recommendation queries and results (Legacy - for caching)"""
    __tablename__ = "recommendation_queries"

    id = Column(Integer, primary_key=True, index=True)
    query_hash = Column(String(64), unique=True, index=True, nullable=False)

    # Input parameters
    arm_length = Column(String(20), nullable=False)
    leg_length = Column(String(20), nullable=False)
    neck_length = Column(String(20), nullable=False)
    face_shape = Column(String(20), nullable=False)

    # Result
    recommendation = Column(JSON, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_query_params', 'arm_length', 'leg_length', 'neck_length', 'face_shape'),
    )
