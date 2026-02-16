from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from src.state import AgentState
from src.utils.llm import llm
import json

def symptom_analyzer_node(state: AgentState) -> Dict[str, Any]:
    """
    사용자의 메시지에서 증상을 추출하고, 
    진단을 위해 정보가 충분한지 판단하는 노드입니다.
    """
    messages = state.get("messages", [])
    if not messages:
        return {"next_step": "end"}
        
    last_message_obj = messages[-1]
    last_message = getattr(last_message_obj, 'content', str(last_message_obj))
    
    existing_symptoms = state.get("symptoms", [])
    if existing_symptoms is None:
        existing_symptoms = []
    
    # 대화 내역 추출 (최근 5개만)
    conversation_history = []
    recent_messages = messages[-5:] if messages else []
    for msg in recent_messages:
        if msg and hasattr(msg, 'type'):
            msg_content = getattr(msg, 'content', '')
            if msg.type == 'human':
                conversation_history.append(f"환자: {msg_content}")
            elif msg.type == 'ai':
                conversation_history.append(f"AI: {msg_content}")
    
    conversation_text = "\n".join(conversation_history) if conversation_history else "없음"
    
    # 프롬프트 템플릿: 증상 업데이트 및 정보 부족 여부 판단
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 정밀한 의료 진단 보조 AI입니다.
        현재까지 파악된 증상 목록과 사용자의 새로운 입력을 바탕으로 증상 목록을 업데이트하고, 진단을 내리기에 정보가 충분한지 판단하세요.

        현재 파악된 증상: {current_symptoms}
        
        최근 대화 내역:
{conversation_history}

        작업 지침:
        1. 사용자의 새로운 입력({text})에서 새로운 증상을 추출하거나, 기존 증상의 세부 사항(위치, 양상, 지속시간 등)을 업데이트하세요.
        2. 예: 기존 "복통" + 입력 "아랫배가 찌르듯 아파" -> "찌르는 듯한 아랫배 통증"으로 구체화.
        3. 단순 인사나 관련 없는 말은 증상 목록에 영향을 주지 마세요.
        4. 업데이트된 **전체 증상 목록**을 반환하세요.
        5. **중요:** missing_info에는 반드시 다음을 확인하세요:
           - **대화 내역에서 이미 답변한 질문은 절대 다시 물어보지 마세요** (예: 약물 복용 여부를 이미 답변했으면 제외)
           - 증상의 구체적인 정보 (위치, 양상, 지속시간 등)
           - **모호한 용어 명확화**: "목"(목구멍 vs 경추), "배"(윗배 vs 아랫배), "머리"(두통 vs 외상) 등 모호한 표현이 있으면 정확한 위치 확인 필요
           - **현재 복용 중인 약물 여부** (아직 확인하지 않았다면 포함)
        
        **모호한 증상 예시:**
        - "목이 아파요" -> missing_info에 "목의 정확한 위치 (목구멍인지 경추/목 뒷부분인지)" 추가
        - "배가 아파요" -> missing_info에 "복통의 정확한 위치 (윗배/명치/아랫배)" 추가
        - "머리 다쳤어요" -> missing_info에 "머리 부상 위치와 원인" 추가
        
        출력 형식 (JSON string only):
        {{
            "symptoms": ["업데이트된 증상1", "업데이트된 증상2"],
            "missing_info": ["부족한 정보1", "목의 정확한 위치", "복용 중인 약물"],
            "is_sufficient": true/false
        }}

        판단 기준:
        - 핵심 증상의 구체적인 정보(위치, 양상, 지속 시간 등)가 파악되었으면 is_sufficient: true
        - 모호한 용어가 있어 정확한 위치를 알 수 없다면 is_sufficient: false
        - 약물 복용 여부를 아직 확인하지 않았다면 is_sufficient: false
        - 여전히 모호하다면 is_sufficient: false
        """),
        ("human", "{text}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "text": last_message, 
        "current_symptoms": ", ".join(existing_symptoms) if existing_symptoms else "없음",
        "conversation_history": conversation_text
    })
    
    # 응답 파싱
    try:
        content = response.content if hasattr(response, 'content') else str(response)
        content = content.replace("```json", "").replace("```", "").strip()
        if not content: content = "{}"
        
        result = json.loads(content)
        if result is None: result = {}
        
        symptoms = result.get("symptoms", existing_symptoms)
        if symptoms is None: symptoms = existing_symptoms
        
        missing_info = result.get("missing_info", [])
        if missing_info is None: missing_info = []
        
        is_sufficient_llm = result.get("is_sufficient", False)
        if is_sufficient_llm is None: is_sufficient_llm = False
        
        # 로직 보강: missing_info가 있으면 LLM이 True라고 해도 False로 처리 (더 신중하게)
        is_sufficient = is_sufficient_llm
        if missing_info and len(missing_info) > 0:
            is_sufficient = False
            
    except Exception as e:
        print(f"JSON Parsing Error: {e}")
        symptoms = existing_symptoms
        missing_info = []
        is_sufficient = True

    # 상태 업데이트
    next_step = None 
    
    # 질문 횟수 및 정보 충분성 판단
    ask_count = state.get("ask_count", 0)
    
    # 최소 2번은 물어보도록 유도 (정보가 아주 많지 않은 이상)
    if is_sufficient and ask_count < 1 and len(symptoms) < 3:
        print("정보가 아직 조금 부족합니다. 추가 질문을 생성합니다.")
        is_sufficient = False
        if not missing_info:
            missing_info = ["증상의 지속 시간", "최근 복용 약물"]

    # 최대 질문 횟수 제한
    MAX_ASK_COUNT = 3
    if ask_count >= MAX_ASK_COUNT:
        is_sufficient = True
    
    if not is_sufficient:
        next_step = "question_generator"
    else:
        next_step = "specialist_router"

    return {
        "symptoms": symptoms,
        "missing_info": missing_info,
        "next_step": next_step
    }
# Force reload
