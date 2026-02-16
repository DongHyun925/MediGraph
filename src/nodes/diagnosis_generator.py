from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from src.state import AgentState
from src.utils.llm import get_llm
from src.nodes.node_utils import clean_persona_fluff

def diagnosis_generator_node(state: AgentState):
    """
    증상과 검색된 의학적 근거(Evidence)를 종합하여 진단 가설과 조언을 생성하는 노드입니다.
    """
    llm = get_llm()
    symptoms = state.get("symptoms", [])
    if symptoms is None: symptoms = []
    
    evidence = state.get("medical_evidence", [])
    if evidence is None: evidence = []
    
    critique = state.get("critique", "")
    if critique is None: critique = ""
    
    messages = state.get("messages", [])
    if messages is None: messages = []
    
    medication_info = state.get("medication_info", "")
    if medication_info is None: medication_info = ""
    
    # 최근 대화 내역 추출
    recent_conversation = []
    for msg in messages[-10:]:
        if msg and hasattr(msg, 'type'):
            msg_content = getattr(msg, 'content', '')
            if msg_content is None: msg_content = ""
            if msg.type == 'human':
                recent_conversation.append(f"환자: {msg_content}")
            elif msg.type == 'ai':
                recent_conversation.append(f"AI: {msg_content}")
    
    conversation_text = "\n".join(recent_conversation) if recent_conversation else "대화 기록 없음"
    
    # 진단 생성 프롬프트
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 냉철하고 정확한 전문의입니다.
        환자의 증상과 의학적 근거를 바탕으로 데이터 중심의 최종 진단을 내리세요.
        
        **작성 지침:**
        1. **언어 설정**: **모든 답변은 반드시 한국어로 작성하십시오.** 전문 용어의 경우 괄호 안에 영어를 병기할 수 있으나, 기본 설명은 한국어로 이루어져야 합니다.
        2. **전문가적 품격**: 신뢰감 있는 의사의 말투를 유지하세요.
        3. **공감 멘트 제거**: "많이 불편하시겠어요" 등 위로의 말은 **절대 하지 마세요.** 
        4. **객관적 설명 (Explanation)**: 질환의 원인과 증상의 인과관계에 대해서만 사실 중심으로 기술하세요.
        5. **닥터 패스 (Doctor Pass) - 필수 규칙**: 
           - **오직 환자가 진술한 사실**(증상, 발병 시점, 통증 양상, 복용 약물 등)만 불렛 포인트로 요약하세요.
           - **AI의 의견이나 진단 추측을 절대 포함하지 마세요.**
           - 실제 의사에게 전달할 '환자 히스토리 요약'임을 명심하세요.
        
        입력 정보:
        - 환자 증상: {symptoms}
        - 의학적 근거: {evidence}
        - 전체 대화 내역:
{conversation}
        
        출력 형식 (JSON string only):
        {{
            "diagnosis": "질환명 (Korean)",
            "confidence": "95%",
            "explanation": "이 증상은 ~~때문에 발생하는 ~~일 가능성이 높습니다.",
            "differential_diagnosis": ["가능성 있는 질환 1", "가능성 있는 질환 2"],
            "recommendations": ["- 조치 1", "- 조치 2"],
            "doctor_pass": "- 이틀 전부터 둔한 허리 통증 발생\n- 아스피린 복용 중\n- 신경학적 이상 소견 없음",
            "recommended_department": "정형외과"
        }}
        """),
        ("human", "객관적 사실 중심의 닥터패스를 포함한 한국어 진단 리포트를 생성해주세요.")
    ])
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        result = chain.invoke({
            "symptoms": ", ".join(symptoms),
            "evidence": "\n".join(evidence),
            "critique": critique,
            "conversation": conversation_text
        })
        
        # 후처리: 공감 멘트 강제 제거
        result['explanation'] = clean_persona_fluff(result.get('explanation', ''))
        result['doctor_pass'] = clean_persona_fluff(result.get('doctor_pass', ''))
        if result.get('recommendations'):
            result['recommendations'] = [clean_persona_fluff(r) for r in result['recommendations']]

        # 결과 포맷팅 (Frontend에서 보여줄 Markdown)
        diagnosis_md = f"""
## 📋 AI 증상 분석 결과

**🔍 추정 가능 질환:** {result['diagnosis']} (AI 신뢰도: {result['confidence']})

{result['explanation']}

**⚖️ 다른 가능성이 있는 질환**
{', '.join(result.get('differential_diagnosis', [])) if result.get('differential_diagnosis') else '없음'}

**💡 자가 관리 권장사항**
{chr(10).join(result.get('recommendations', [])) if result.get('recommendations') else '없음'}

⚠️ **중요**: 이 분석은 참고용이며 의사의 진단을 대체할 수 없습니다. 증상이 지속되거나 악화되면 반드시 의료기관을 방문하세요.
"""
        return {
            "diagnosis_hypothesis": diagnosis_md,
            "doctor_pass": result.get("doctor_pass", ""),
            "recommended_department": result.get("recommended_department", "내과"),
            "next_step": "end"
        }
            
    except Exception as e:
        print(f"Diagnosis Generation Error: {e}")
        return {
            "diagnosis_hypothesis": "진단 생성 중 오류가 발생했습니다. 다시 시도해주세요.",
            "next_step": "end"
        }
