from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """
    에이전트의 상태를 정의하는 TypedDict 클래스입니다.
    LangGraph의 각 노드 간에 이 상태 객체가 공유됩니다.
    """
    
    # messages: 대화 기록을 저장합니다. operator.add reducer를 사용하여
    # 새로운 메시지가 리스트에 추가(append)되는 방식으로 업데이트됩니다.
    messages: Annotated[List[BaseMessage], operator.add]
    
    # symptoms: LLM이 사용자의 발화에서 추출한 증상 목록입니다. (예: ['두통', '구토'])
    symptoms: List[str]
    
    # diagnosis_hypothesis: 검색된 정보(RAG)를 바탕으로 생성된 1차 진단 가설입니다.
    diagnosis_hypothesis: Optional[str]
    
    # medical_evidence: 외부 검색 도구(Medical RAG)를 통해 수집된 의학적 근거 자료들입니다.
    medical_evidence: List[str]
    
    # critique: Fact Checker(팩트 체크) 노드가 수행한 검증 결과입니다.
    # ('valid' 또는 'invalid' 등의 값을 가짐)
    critique: Optional[str]
    
    # next_step: 라우터(Router)가 결정한 다음 단계입니다.
    # ('emergency', 'specialist_referral', 'general_advice', 'ask_user' 등)
    next_step: Optional[str]

    # search_count: 검색 반복 횟수 제어 (무한 루프 방지) - 검색 품질 향상을 위한 Agentic Loop
    search_count: int

    # doctor_pass: 의사에게 보여줄 환자 진술 요약 (의학 용어 병기)
    doctor_pass: Optional[str]

    # recommended_department: 증상에 따른 추천 진료과 (예: 신경과, 내과)
    recommended_department: Optional[str]

    # missing_info: 진단을 위해 부족한 정보 목록 (역질문 생성용)
    missing_info: Optional[List[str]]
    
    # ask_count: 사용자에게 질문한 횟수 (반복 질문 방지)
    ask_count: int

    # images: 사용자가 업로드한 이미지 (base64 인코딩)
    images: Optional[List[str]]

    # medications: 사용자가 복용 중인 약물 목록
    medications: Optional[List[str]]
    
    # medication_info: 약물 상호작용, 부작용 등 약물 정보
    medication_info: Optional[str]

    # fact_check_confidence: 팩트 체크 신뢰도 점수 (0-100)
    fact_check_confidence: Optional[int]

    # fact_check_sources: 검증에 사용된 출처 목록
    fact_check_sources: Optional[List[str]]
