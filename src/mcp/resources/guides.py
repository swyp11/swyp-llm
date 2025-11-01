"""MCP Resource: Body Measurement Guide"""


async def get_body_measurement_options() -> str:
    """웨딩 드레스 추천을 위한 체형 측정 옵션 정보"""
    return """
# 웨딩 드레스 추천 체형 옵션

## 팔 길이 (arm_length)
- 짧은: 어깨에서 손목까지의 길이가 평균보다 짧음
- 보통: 표준적인 팔 길이
- 긴: 평균보다 긴 팔 길이

## 다리 길이 (leg_length)
- 짧은: 상체 대비 다리가 짧은 편
- 보통: 균형잡힌 다리 길이
- 긴: 상체 대비 다리가 긴 편

## 목 길이 (neck_length)
- 짧은: 어깨와 턱 사이 거리가 짧음
- 보통: 표준적인 목 길이
- 긴: 긴 목선

## 얼굴형 (face_shape)
- 달걀: 이마와 턱이 둥글고 균형잡힌 타원형
- 넓은: 광대뼈가 발달하고 얼굴이 넓은 편
- 각진: 턱선이 각져있고 이마가 넓은 편
- 긴: 얼굴 길이가 긴 편

## 사용 예시
```json
{
  "arm_length": "보통",
  "leg_length": "긴",
  "neck_length": "보통",
  "face_shape": "달걀"
}
```
"""


def register_guide_resource(mcp):
    """Register guide resource with MCP server"""
    mcp.resource("wedding-dress://body-measurements")(get_body_measurement_options)
