from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.state import AgentState
from src.utils.llm import get_llm

def specialist_router_node(state: AgentState):
    """
    추출된 증상의 심각도를 분석하여 다음 단계를 결정하는 분류(Router) 노드입니다.
    분류 카테고리: 'emergency' (응급), 'specialist_referral' (전문의 의뢰), 'general_advice' (일반 조언).
    """
    llm = get_llm()
    symptoms = state.get("symptoms", [])
    if symptoms is None:
        symptoms = []
    
    if not symptoms:
        # 증상이 발견되지 않은 경우, 더 많은 정보를 묻거나 일반적인 조언으로 넘어갑니다.
        # 여기서는 단순화를 위해 일반 조언으로 처리합니다.
        return {"next_step": "general_advice"}
        
    prompt = ChatPromptTemplate.from_template(
        """
        당신은 의료 분류(Triage) 시스템입니다. 다음 증상 목록을 분석하세요: {symptoms}
        
        심각도를 분석하여 다음 중 정확히 하나의 카테고리로 분류하세요:
        - "emergency": 생명을 위협하는 상태 (예: 심장마비 징후, 뇌졸중, 심한 출혈, 호흡 곤란).
        - "specialist_referral": 복잡하지만 안정적인 상태로, 의사의 진료가 필요한 경우 (예: 지속적인 통증, 피부 질환, 만성 질환).
        - "general_advice": 경미하거나 자가 치료가 가능한 상태 (예: 감기, 가벼운 두통, 피로).
        
        오직 카테고리 이름만 반환하세요.
        """
    )
    
    chain = prompt | llm | StrOutputParser()
    
    classification = chain.invoke({"symptoms": ", ".join(symptoms)})
    cleaned_classification = classification.strip().lower()
    
    # 결과 정규화 및 폴백(Fallback) 처리
    if "emergency" in cleaned_classification:
        return {"next_step": "emergency"}
    elif "specialist" in cleaned_classification:
        return {"next_step": "specialist_referral"}
    else:
        return {"next_step": "general_advice"}
