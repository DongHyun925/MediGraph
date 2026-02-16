from typing import Any, Dict, List, Optional
from langchain_core.messages import HumanMessage
from src.state import AgentState
from src.utils.llm import llm
import base64
from langchain_google_genai import ChatGoogleGenerativeAI
import os

def image_analyzer_node(state: AgentState) -> Dict[str, Any]:
    """
    업로드된 이미지를 Gemini Vision API로 분석하는 노드입니다.
    피부 발진, 부종, 상처 등 시각적 증상을 설명으로 변환합니다.
    """
    
    images = state.get("images", [])
    
    if not images:
        # 이미지가 없으면 건너뜀
        return {}
    
    # Gemini Vision 모델 초기화
    vision_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.3,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # 프롬프트: 이미지 분석 요청
    prompt_text = """당신은 전문 의료 이미지 분석가입니다. 
    업로드된 이미지에서 보이는 증상을 의학적으로 정확하게 설명해주세요.
    
    다음 측면을 집중적으로 보고해주세요:
    - 위치 (신체 어느 부위인지)
    - 색상 (발적, 창백, 변색 등)
    - 형태 및 크기
    - 특이사항 (부종, 발진, 상처, 멍 등)
    
    간결하고 명확하게 작성하세요. 진단명은 제시하지 말고 관찰된 증상만 기술하세요."""
    
    # 이미지 분석 결과 수집
    image_descriptions = []
    
    for idx, img_base64 in enumerate(images):
        try:
            # Gemini Vision API는 base64 이미지를 직접 처리 가능
            # 이미지 메시지 구성
            message_content = [
                {"type": "text", "text": prompt_text},
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{img_base64}"
                }
            ]
            
            response = vision_llm.invoke([HumanMessage(content=message_content)])
            description = response.content
            image_descriptions.append(f"이미지 {idx + 1}: {description}")
            
        except Exception as e:
            print(f"Image analysis error for image {idx + 1}: {e}")
            image_descriptions.append(f"이미지 {idx + 1}: 분석 실패")
    
    # 이미지 분석 결과를 증상에 추가
    combined_description = "\n\n".join(image_descriptions)
    
    # 기존 symptoms에 이미지 분석 결과 추가
    existing_symptoms = state.get("symptoms", [])
    updated_symptoms = existing_symptoms + [f"[이미지 분석] {combined_description}"]
    
    return {
        "symptoms": updated_symptoms
    }
