import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

def get_llm(model_name: str = "gpt-4o"):
    """
    설정된 ChatOpenAI 인스턴스를 반환하는 유틸리티 함수입니다.
    
    Args:
        model_name (str): 사용할 모델 이름 (기본값: "gpt-4o").
                          의료적 추론 능력을 위해 gpt-4o 사용을 권장합니다.
    
    Returns:
        ChatOpenAI: 설정된 LangChain ChatModel 객체.
        
    Raises:
        ValueError: OPENAI_API_KEY가 환경 변수에 설정되지 않은 경우 발생.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(".env 파일에서 OPENAI_API_KEY를 찾을 수 없습니다.")
        
    return ChatOpenAI(
        model=model_name,
        temperature=0, # 의료 분석의 일관성을 위해 무작위성을 0으로 설정 (Deterministic)
        api_key=api_key
    )

# 기본 LLM 인스턴스 (싱글톤처럼 사용)
try:
    llm = get_llm()
except Exception as e:
    print(f"LLM 초기화 경고: {e}")
    llm = None
