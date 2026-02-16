from src.graph import create_graph
from langchain_core.messages import HumanMessage

def run_test(scenario_name, user_input):
    print(f"\n--- 테스트 시나리오 실행: {scenario_name} ---")
    print(f"사용자 입력: {user_input}")
    
    # 그래프 재생성
    graph = create_graph()
    initial_state = {"messages": [HumanMessage(content=user_input)]}
    
    try:
        final_state = graph.invoke(initial_state)
        
        print(f"최종 노드 도달. 최종 상태 키(Keys): {final_state.keys()}")
        print(f"추출된 증상: {final_state.get('symptoms')}")
        print(f"진단 가설: {final_state.get('diagnosis_hypothesis')}")
        print(f"다음 단계 판단: {final_state.get('next_step')}")
        print(f"팩트 체크 결과: {final_state.get('critique')}")
    except Exception as e:
        print(f"테스트 실패: {e}")

if __name__ == "__main__":
    # 시나리오 1: 응급 상황 (심장마비 의심)
    run_test("Emergency (응급)", "I have a crushing chest pain and I can't breathe.")
    
    # 시나리오 2: 일반 문의 (두통/RAG 필요)
    run_test("General Inquiry (일반 문의)", "My head hurts a bit and I feel tired.")
