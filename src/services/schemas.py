"""Pydantic schemas for request/response"""
from pydantic import BaseModel, Field
from enum import Enum
from typing import List


class ArmLength(str, Enum):
    SHORT = "짧은"
    NORMAL = "보통"
    LONG = "긴"


class LegLength(str, Enum):
    SHORT = "짧은"
    NORMAL = "보통"
    LONG = "긴"


class NeckLength(str, Enum):
    SHORT = "짧은"
    NORMAL = "보통"
    LONG = "긴"


class FaceShape(str, Enum):
    OVAL = "달걀"
    WIDE = "넓은"
    ANGULAR = "각진"
    LONG = "긴"


class RecommendationRequest(BaseModel):
    """Wedding dress recommendation request"""
    arm_length: ArmLength = Field(..., description="팔 길이")
    leg_length: LegLength = Field(..., description="다리 길이")
    neck_length: NeckLength = Field(..., description="목 길이")
    face_shape: FaceShape = Field(..., description="얼굴형")
    num_recommendations: int = Field(
        default=3,
        ge=1,
        le=5,
        description="추천받을 스타일 개수 (1-5개)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "arm_length": "보통",
                "leg_length": "긴",
                "neck_length": "보통",
                "face_shape": "달걀",
                "num_recommendations": 3
            }
        }


class DressRecommendation(BaseModel):
    """Single dress recommendation"""
    style_name: str = Field(..., description="드레스 스타일 이름")
    description: str = Field(..., description="드레스 설명")
    why_recommended: str = Field(..., description="추천 이유")
    styling_tips: List[str] = Field(default_factory=list, description="스타일링 팁")


class RecommendationResponse(BaseModel):
    """Wedding dress recommendation response"""
    request_params: RecommendationRequest
    recommendations: List[DressRecommendation] = Field(..., description="드레스 추천 목록")
    overall_advice: str = Field(..., description="전체적인 조언")
    cached: bool = Field(default=False, description="캐시된 결과 여부")
    source: str = Field(default="ai_generated", description="결과 소스")
