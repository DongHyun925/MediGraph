from typing import Any, Dict, List, Optional
import re
from langchain_core.messages import HumanMessage
from src.state import AgentState
from src.utils.llm import llm

def medication_search_node(state: AgentState) -> Dict[str, Any]:
    """
    사용자 메시지에서 약물명을 추출합니다.
    (닥터 패스에 포함할 목적)
    """
    
    symptoms = state.get("symptoms", [])
    if symptoms is None:
        symptoms = []
    
    messages = state.get("messages", [])
    if messages is None:
        messages = []
    
    # 마지막 사용자 메시지 추출
    user_messages = []
    messages_to_check = messages if messages else []
    for msg in reversed(messages_to_check):
        if msg and hasattr(msg, 'type') and msg.type == 'human':
            msg_content = getattr(msg, 'content', '')
            if msg_content is None: msg_content = ""
            user_messages.append(msg_content)
        if len(user_messages) >= 3:  # 최근 3개 메시지만 확인
            break
    
    combined_text = " ".join(user_messages)
    
    # LLM을 사용하여 약물명 추출
    extraction_prompt = f"""다음 텍스트에서 약물명을 추출하세요. 추출된 약물명만 쉼표로 구분하여 나열하세요.
    약물명이 없으면 "없음"이라고만 답하세요.
    
    텍스트: {combined_text}
    
    약물명:"""
    
    try:
        medication_response = llm.invoke([HumanMessage(content=extraction_prompt)])
        medications_str = medication_response.content.strip()
        
        if medications_str == "없음" or not medications_str:
            return {}
        
        # 쉼표로 분리
        medications = []
        if medications_str:
            medications = [med.strip() for med in medications_str.split(',') if med and isinstance(med, str) and med.strip()]
        
        if not medications:
            return {}
        
        # 단순히 약물 목록만 반환 (검색 없이)
        medication_list = ", ".join(medications)
        
        return {
            "medications": medications,
            "medication_info": f"복용 약물: {medication_list}"
        }
        
    except Exception as e:
        print(f"Medication extraction error: {e}")
        return {}
    
    return {}

