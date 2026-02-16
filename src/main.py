from src.graph import create_graph
from langchain_core.messages import HumanMessage
import uuid

def main():
    # 그래프 생성 및 컴파일
    graph = create_graph()
    
    # 각 대화 세션을 구분하기 위한 고유 ID 생성
    thread_id = str(uuid.uuid4())
    
    print("🏥 MediGraph 에이전트가 초기화되었습니다. 종료하려면 'quit'을 입력하세요.")
    print("증상을 설명해주세요...")
    
    # LangGraph 설정 (스레드 ID)
    config = {"configurable": {"thread_id": thread_id}}
    
    while True:
        user_input = input("\n사용자: ")
        if user_input.lower() in ["quit", "exit"]:
            break
            
        # 초기 상태 설정: 사용자의 입력을 메시지 리스트에 담음
        initial_state = {"messages": [HumanMessage(content=user_input)]}
        
        print("\n🤖 분석 중...")
        
        # 그래프 스트리밍 실행 (단계별 진행 상황 확인)
        events = graph.stream(initial_state, config=config)
        
        for event in events:
            # 중간 단계 이벤트 출력
            for key, value in event.items():
                print(f"  -> 노드 실행 완료: {key}")
                if "diagnosis_hypothesis" in value:
                    # 너무 길면 100자까지만 출력
                    print(f"     진단 가설: {value['diagnosis_hypothesis'][:100]}...")
                if "next_step" in value:
                    print(f"     다음 단계 판단: {value['next_step']}")
        
if __name__ == "__main__":
    main()
