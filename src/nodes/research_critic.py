from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from src.state import AgentState
from src.utils.llm import llm

def research_critic_node(state: AgentState) -> Dict[str, Any]:
    """
    검색된 의학 정보(medical_evidence)가 충분한지 평가(Critique)하고,
    부족하다면 재검색을 위한 쿼리를 제안하거나, 검색을 종료시킵니다.
    """
    
    symptoms = state.get("symptoms", [])
    if symptoms is None: symptoms = []
    
    evidence = state.get("medical_evidence", [])
    if evidence is None: evidence = []
    
    search_count = state.get("search_count", 0)
    if search_count is None: search_count = 0
    
    # 최대 검색 횟수 제한 (예: 3회)
    if search_count >= 3:
        return {"next_step": "diagnosis_generator"} # 충분하지 않더라도 강제 진행

    # 증거가 아예 없으면 무조건 재검색 (혹은 검색 실패 처리)
    if not evidence:
         # 사실 evidence는 리스트이므로 내용이 있는지 확인해야 함.
         # 여기서는 간단히 카운트만 증가시키고 rag로 보냄 (rag에서 쿼리 생성 로직이 있으므로)
         return {"search_count": search_count + 1, "next_step": "medical_rag"}

    # 프롬프트: 검색 결과 평가
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 엄격한 의학 연구 평가자(Medical Research Critic)입니다.
        현재 환자의 증상: {symptoms}
        
        지금까지 수집된 의학적 근거(Evidence):
        {evidence}
        
        이 정보들이 환자의 증상 원인을 추론하고 진단을 내리기에 충분한지 평가하세요.
        
        규칙:
        1. 정보가 충분하면 'SUFFICIENT'라고만 출력하세요.
        2. 정보가 부족하거나, 엉뚱한 정보라면 'INSUFFICIENT'라고 출력하고, 
           어떤 정보가 더 필요한지 구체적인 검색 키워드(Query)를 제안하세요.
           형식: INSUFFICIENT: [추천 검색어]
        """),
        ("human", "평가를 시작해주세요.")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "symptoms": ", ".join(symptoms),
        "evidence": "\n".join(evidence) if evidence else "없음"
    })
    
    content = response.content.strip()
    
    if content.startswith("SUFFICIENT"):
        return {"next_step": "diagnosis_generator"}
    else:
        # 재검색 결정
        # 여기서 쿼리를 파싱해서 state에 넣어주면 RAG 노드가 그걸 쓸 수 있게 개선해야 함.
        # 현재는 RAG 노드가 매번 쿼리를 생성하므로, search_count를 늘려서 다시 보내면 더 나은 쿼리를 생성하도록 유도될 수 있음.
        # (더 정교하게 하려면 RAG 노드에 previous_search_failures 같은걸 전달해야 함)
        
        return {
            "search_count": search_count + 1,
            "next_step": "medical_rag"
        }
