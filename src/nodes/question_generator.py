from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from src.state import AgentState
from src.utils.llm import llm
from src.nodes.node_utils import clean_persona_fluff

def question_generator_node(state: AgentState) -> Dict[str, Any]:
    """
    사용자에게 부족한 정보를 묻는 질문을 생성하는 노드입니다.
    """
    
    missing_info = state.get("missing_info", [])
    if missing_info is None: missing_info = []
    
    symptoms = state.get("symptoms", [])
    if symptoms is None: symptoms = []
    
    current_ask_count = state.get("ask_count", 0)
    
    messages = state.get("messages", [])
    if messages is None: messages = []
    
    if not missing_info:
        return {"next_step": "end"}

    # 최근 대화 내역 추출
    recent_conversation = []
    recent_messages = messages[-10:] if messages else []
    for msg in recent_messages:
        if msg and hasattr(msg, 'type'):
            msg_content = getattr(msg, 'content', '')
            if msg_content is None: msg_content = ""
            if msg.type == 'human':
                recent_conversation.append(f"환자: {msg_content}")
            elif msg.type == 'ai':
                recent_conversation.append(f"AI: {msg_content}")
    
    conversation_context = "\n".join(recent_conversation) if recent_conversation else "없음"

    # 프롬프트 템플릿 정의
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 유능하고 꼼꼼한 전문 의사입니다.
        현재 환자가 호소한 증상({symptoms})에 대해 전문가로서의 품격 있는 어조를 유지하되, 불필요한 공감 멘트나 수식어는 생략하고 핵심 질문만 던지세요.
        
        부족한 정보 목록: {missing_info}
        
        **질문 작성 가이드:**
        1. **전문가적 어조**: 친절하고 신뢰감 있는 의사의 말투를 사용하세요. 
        2. **종결 어미**: 질문 시 "~까?" 쓰지 말고 **"~한가요?", "~인가요?"**와 같은 정중하고 부드러운 말투를 사용하세요.
        3. **공감 멘트 제거**: "많이 불편하시겠어요" 등 상투적인 공감 구절은 **절대 사용하지 마세요.**
        4. **핵심 질문**: 인사말 없이 바로 증상을 파악하기 위한 핵심 질문을 하나만 던지세요.
        5. **중복 질문 금지**: 최근 대화({conversation_context})를 확인하여 이미 확인된 정보는 다시 묻지 마세요."""),
        ("human", "부족한 정보 중 가장 중요한 한 가지에 대해 핵심 질문을 던져주세요.")
    ])
    
    # 체인 실행
    chain = prompt | llm
    response = chain.invoke({
        "symptoms": ", ".join(symptoms), 
        "missing_info": ", ".join(missing_info),
        "conversation_context": conversation_context
    })
    
    # 응답 후처리: 불필요한 문구 강제 제거
    if hasattr(response, 'content'):
        response.content = clean_persona_fluff(response.content)
    
    return {
        "messages": [response],
        "ask_count": current_ask_count + 1,
        "next_step": "user_input"
    }
