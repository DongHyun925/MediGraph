from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.state import AgentState
from src.nodes.symptom_analyzer import symptom_analyzer_node
from src.nodes.specialist_router import specialist_router_node
from src.nodes.medical_rag import medical_rag_node
from src.nodes.diagnosis_generator import diagnosis_generator_node
from src.nodes.fact_checker import fact_checker_node
from src.nodes.emergency import emergency_response_node
from src.nodes.question_generator import question_generator_node
from src.nodes.research_critic import research_critic_node
from src.nodes.medication_search import medication_search_node

def create_graph():
    # 그래프(워크플로우) 초기화
    workflow = StateGraph(AgentState)
    
    # 노드 추가
    workflow.add_node("symptom_analyzer", symptom_analyzer_node)
    workflow.add_node("question_generator", question_generator_node)
    workflow.add_node("specialist_router", specialist_router_node)
    workflow.add_node("medical_rag", medical_rag_node)
    workflow.add_node("research_critic", research_critic_node)
    workflow.add_node("diagnosis_generator", diagnosis_generator_node)
    workflow.add_node("medication_search", medication_search_node)
    workflow.add_node("fact_checker", fact_checker_node)
    workflow.add_node("emergency_response", emergency_response_node)
    
    # 진입점 설정
    workflow.set_entry_point("symptom_analyzer")
    
    # [조건부 엣지 1] Symptom Analyzer -> (질문 생성 or 전문의 라우터)
    def analyzer_condition(state):
        next_step = state.get("next_step")
        if next_step == "question_generator":
            return "ask_user"
        return "route"

    workflow.add_conditional_edges(
        "symptom_analyzer",
        analyzer_condition,
        {
            "ask_user": "question_generator",
            "route": "specialist_router"
        }
    )

    # [엣지] 질문 생성 후에는 사용자 입력 대기 (END)
    # 실제로는 Human-in-the-loop 패턴이지만 여기서는 응답 반환 후 종료로 처리
    workflow.add_edge("question_generator", END)
    
    # [조건부 엣지 2] Specialist Router -> (응급 or 검색)
    def router_condition(state):
        next_step = state.get("next_step")
        if next_step == "emergency":
            return "emergency"
        return "research"
            
    workflow.add_conditional_edges(
        "specialist_router",
        router_condition,
        {
            "emergency": "emergency_response",
            "research": "medical_rag"
        }
    )
    
    workflow.add_edge("emergency_response", END)
    
    # [엣지] RAG 검색 -> 리서치 크리틱 (평가)
    workflow.add_edge("medical_rag", "research_critic")

    # [조건부 엣지 3] Research Critic -> (재검색 or 진단 생성)
    def critic_condition(state):
        next_step = state.get("next_step")
        if next_step == "medical_rag":
            return "loop"
        return "diagnosis"

    workflow.add_conditional_edges(
        "research_critic",
        critic_condition,
        {
            "loop": "medical_rag", # 재검색 루프
            "diagnosis": "diagnosis_generator"
        }
    )
    
    # [조건부 엣지 4] Diagnosis Generator -> Medication Search (조건부)
    # 약물이 언급된 경우에만 medication_search 실행, 아니면 바로 fact_checker로
    def should_check_medication(state):
        """약물 검색 필요 여부 판단"""
        messages = state.get("messages", [])
        if messages is None:
            messages = []       # 최근 5개 메시지에서 약물 관련 키워드 확인
        medication_keywords = ["약", "먹", "복용", "타이레놀", "아스피린", "알약", "medicine", "medication"]
        
        for msg in messages[-5:]:
            if hasattr(msg, 'content') and msg.content:
                content = msg.content
                if isinstance(content, str):
                    content = content.lower()
                    if any(keyword in content for keyword in medication_keywords):
                        return "medication_search"
        
        return "fact_checker"
    
    workflow.add_conditional_edges(
        "diagnosis_generator",
        should_check_medication,
        {
            "medication_search": "medication_search",
            "fact_checker": "fact_checker"
        }
    )
    
    workflow.add_edge("medication_search", "fact_checker")
    
    # [조건부 엣지 5] Fact Checker -> 종료
    # (여기서도 검증 실패 시 재검색 루프를 넣을 수 있으나 복잡도 조절을 위해 생략)
    workflow.add_edge("fact_checker", END)
    
    # 체크포인터 설정 (In-Memory)
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)
