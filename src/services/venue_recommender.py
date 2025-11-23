"""Wedding venue recommendation engine"""
import hashlib
import json
from openai import AsyncOpenAI
from src.config import settings
from src.services.venues_data import get_venue_details, get_venues_with_suitability


class VenueRecommender:
    """AI-powered venue recommendation engine"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    @staticmethod
    def generate_hash(
        guest_count: str,
        budget: str,
        region: str,
        style: str,
        season: str,
        num: int = 3
    ) -> str:
        """Generate unique hash for request parameters"""
        params = f"{guest_count}_{budget}_{region}_{style}_{season}_{num}"
        return hashlib.sha256(params.encode()).hexdigest()

    async def generate(
        self,
        guest_count: str,
        budget: str,
        region: str,
        style_preference: str,
        season: str,
        num_recommendations: int = 3
    ) -> dict:
        """Generate AI venue recommendation"""

        # Get available venues with suitability info
        venues_with_info = get_venues_with_suitability()

        # Build requirements
        requirements = f"""예식 요구사항:
- 하객 수: {guest_count}
- 예산: {budget}
- 희망 지역: {region}
- 선호 스타일: {style_preference}
- 예식 시즌: {season}"""

        # Improved prompt with suitability information
        prompt = f"""{requirements}

다음 웨딩홀 목록에서 위 요구사항에 가장 잘 맞는 {num_recommendations}곳을 추천하세요.
각 웨딩홀 옆에 적합한 정보가 있으니 이를 참고하여 매칭하세요:

{venues_with_info}

중요: 요구사항과 각 웨딩홀의 적합성을 신중히 비교하여 최적의 조합을 선택하세요.
예산, 하객 수, 지역, 스타일, 시즌을 모두 고려하세요.

JSON 형식 ({num_recommendations}개 추천):
{{
  "venue_names": ["웨딩홀1", "웨딩홀2", ...],
  "overall_advice": "이 커플께 드리는 한 줄 조언"
}}"""

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "웨딩 플래너. 커플의 요구사항에 맞는 웨딩홀 이름만 간결하게 추천."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"}
        )

        # Parse GPT response
        ai_result = json.loads(response.choices[0].message.content)
        venue_names = ai_result.get("venue_names", [])
        overall_advice = ai_result.get("overall_advice", "")

        # Get detailed information from local database
        detailed_venues = get_venue_details(venue_names)

        # Build final response with detailed information
        recommendations = []
        for venue_info in detailed_venues:
            # Generate why_recommended based on requirements
            why_parts = []
            if guest_count:
                why_parts.append(f"{guest_count} 하객 수용")
            if budget:
                why_parts.append(f"{budget} 예산대")
            if region:
                why_parts.append(f"{region} 지역")
            if style_preference:
                why_parts.append(f"{style_preference} 스타일")
            if season:
                why_parts.append(f"{season} 예식")
            
            why_recommended = f"{', '.join(why_parts)}에 적합합니다."

            # Calculate estimated cost
            capacity_avg = (venue_info["capacity"]["min"] + venue_info["capacity"]["max"]) // 2
            price_multiplier = {"저": 15, "중": 25, "고": 40}
            base_price = price_multiplier.get(venue_info["price_range"], 25)
            estimated_cost = f"{capacity_avg * base_price // 100 * 100:,}만원 ~ {capacity_avg * (base_price + 10) // 100 * 100:,}만원"

            recommendations.append({
                "venue_name": venue_info["venue_name"],
                "description": venue_info["description"],
                "capacity": f"{venue_info['capacity']['min']}명 ~ {venue_info['capacity']['max']}명",
                "location": venue_info["location"],
                "price_range": venue_info["price_range"],
                "estimated_cost": estimated_cost,
                "why_recommended": why_recommended,
                "pros": venue_info.get("pros", []),
                "cons": venue_info.get("cons", []),
                "amenities": venue_info.get("amenities", []),
                "food_style": venue_info.get("food_style", []),
                "booking_tips": [
                    f"{season} 시즌은 최소 6개월 전 예약 권장",
                    "주말 예약 시 평일 대비 20-30% 할증",
                    "오프 시즌 할인 이벤트 확인"
                ]
            })

        return {
            "recommendations": recommendations,
            "overall_advice": overall_advice
        }


# Global recommender instance
venue_recommender = VenueRecommender()
