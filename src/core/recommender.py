"""Wedding dress recommendation engine"""
import hashlib
import json
from openai import AsyncOpenAI
from src.config import settings


class DressRecommender:
    """AI-powered dress recommendation engine"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    @staticmethod
    def generate_hash(arm: str, leg: str, neck: str, face: str) -> str:
        """Generate unique hash for request parameters"""
        params = f"{arm}_{leg}_{neck}_{face}"
        return hashlib.sha256(params.encode()).hexdigest()

    async def generate(
        self,
        arm_length: str,
        leg_length: str,
        neck_length: str,
        face_shape: str
    ) -> dict:
        """Generate AI recommendation"""

        prompt = f"""당신은 전문 웨딩 드레스 스타일리스트입니다.
다음 신체 특징을 가진 신부에게 가장 어울리는 웨딩 드레스를 추천해주세요:

- 팔 길이: {arm_length}
- 다리 길이: {leg_length}
- 목 길이: {neck_length}
- 얼굴형: {face_shape}

3가지 드레스 스타일을 추천하고, 각각에 대해:
1. 스타일 이름
2. 상세한 설명
3. 이 신부에게 추천하는 이유
4. 스타일링 팁 (3-5가지)

그리고 전체적인 조언도 포함해주세요.

응답은 반드시 다음 JSON 형식으로만 제공해주세요:
{{
  "recommendations": [
    {{
      "style_name": "드레스 스타일 이름",
      "description": "드레스 설명",
      "why_recommended": "추천 이유",
      "styling_tips": ["팁1", "팁2", "팁3"]
    }}
  ],
  "overall_advice": "전체적인 조언"
}}"""

        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 전문 웨딩 드레스 스타일리스트입니다. 신부의 체형에 맞는 최적의 드레스를 추천합니다."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result


# Global recommender instance
recommender = DressRecommender()
