from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.state import AgentState
from src.utils.llm import get_llm
from src.nodes.node_utils import clean_persona_fluff

def emergency_response_node(state: AgentState):
    """
    응급 상황(Emergency)으로 판단되었을 때 즉각적인 안전 지침을 제공하는 노드입니다.
    """
    llm = get_llm()
    symptoms = state.get("symptoms", [])
    if symptoms is None:
        symptoms = []
    
    # 응급 상황 이유 추론 및 대처법 프롬프트
    prompt = ChatPromptTemplate.from_template(
        """
        당신은 냉철한 응급의학과 전문의입니다. 현재 환자의 증상은 '절대적 응급' 상황입니다.
        불필요한 위로나 공감 멘트 없이, 오직 생명과 직결된 정보만 신속하고 정확하게 전달하세요.
        
        **모든 답변은 반드시 한국어로 작성하십시오.**
        
        증상 목록: {symptoms}
        
        **작성 지침:**
        1. **직설적 통보**: "불편하시겠어요", "안타깝네요" 같은 말은 **절대 하지 마세요.**
        2. **의심 질환**: 가능성 있는 치명적 질환을 명시하세요.
        3. **즉각적 조치**: 구급차 도착 전까지 환자가 수행해야 할 행동 강령만 나열하세요.
        
        출력 형식:
        **의심 질환**: [한국어 질환명]
        
        **판단 근거**: [한국어 설명]
        
        **응급 조치 요령**:
        - [한국어 필수 조치 1]
        - [한국어 필수 조치 2]
        """
    )
    
    try:
        chain = prompt | llm | StrOutputParser()
        emergency_reason = chain.invoke({"symptoms": ", ".join(symptoms)})
        
        # 후처리: 공감 멘트 강제 제거
        emergency_reason = clean_persona_fluff(emergency_reason)
        
    except Exception as e:
        print(f"Emergency Reasoning Error: {e}")
        emergency_reason = "심각한 증상이 의심됩니다. 즉각적인 의료 조치가 필요합니다.\n\n**응급 조치**: 환자를 편안한 자세로 눕히고 즉시 119에 신고하세요."

    return {
        "diagnosis_hypothesis": f"🚨 **즉시 119에 신고하세요** 🚨\n\nCRITICAL EMERGENCY (심각한 응급 상황)\n\n{emergency_reason}",
        "next_step": "emergency",
        "critique": "valid", 
        "messages": [AIMessage(content="WARNING: 심각한 증상이 감지되었습니다. 즉시 응급 구조대에 연락하거나 병원 응급실을 방문하세요.")]
    }
