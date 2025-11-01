"""Wedding dress recommendation engine"""
import hashlib
import json
from openai import AsyncOpenAI
from src.config import settings
from src.services.styles_data import get_style_details, get_all_style_names


class DressRecommender:
    """AI-powered dress recommendation engine"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    @staticmethod
    def generate_hash(arm: str, leg: str, neck: str, face: str, num: int = 3) -> str:
        """Generate unique hash for request parameters"""
        params = f"{arm}_{leg}_{neck}_{face}_{num}"
        return hashlib.sha256(params.encode()).hexdigest()

    async def generate(
        self,
        arm_length: str,
        leg_length: str,
        neck_length: str,
        face_shape: str,
        num_recommendations: int = 3
    ) -> dict:
        """Generate AI recommendation with optimized token usage"""

        # Get available styles list
        available_styles = get_all_style_names()
        styles_list = ", ".join(available_styles)

        # Optimized prompt - only ask for style names and brief advice
        prompt = f"""신체 특징:
- 팔: {arm_length}
- 다리: {leg_length}
- 목: {neck_length}
- 얼굴형: {face_shape}

다음 스타일 중 가장 어울리는 {num_recommendations}가지를 추천하세요:
{styles_list}

JSON 형식 ({num_recommendations}개 추천):
{{
  "style_names": ["스타일1", "스타일2", ...],
  "overall_advice": "이 신부님께 드리는 한 줄 조언"
}}"""

        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "웨딩 드레스 스타일리스트. 체형에 맞는 스타일 이름만 간결하게 추천."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        # Parse GPT-4 response
        ai_result = json.loads(response.choices[0].message.content)
        style_names = ai_result.get("style_names", [])
        overall_advice = ai_result.get("overall_advice", "")

        # Get detailed information from local database
        detailed_styles = get_style_details(style_names)

        # Build final response with detailed information
        recommendations = []
        for style_info in detailed_styles:
            recommendations.append({
                "style_name": style_info["style_name"],
                "description": style_info["description"],
                "why_recommended": f"{arm_length} 팔, {leg_length} 다리, {neck_length} 목, {face_shape} 얼굴형에 잘 어울립니다.",
                "styling_tips": style_info["styling_tips"]
            })

        return {
            "recommendations": recommendations,
            "overall_advice": overall_advice
        }


# Global recommender instance
recommender = DressRecommender()
