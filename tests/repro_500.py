import sys
import os
sys.path.append(os.getcwd())

from src.graph import create_graph
from langchain_core.messages import HumanMessage
import uuid

def test_graph():
    graph = create_graph()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # 여러 시나리오 테스트
    test_inputs = [
        "머리가 너무 아파요", 
        "약은 안 먹고 있어요",
        "타이레놀 먹었는데 효과가 없어요",
        "응급 상황인 것 같아요",
        "" # 빈 입력
    ]
    
    for text in test_inputs:
        print(f"\n--- Testing with input: '{text}' ---")
        try:
            initial_state = {"messages": [HumanMessage(content=text)]}
            # stream 테스트 (api.py와 유사한 방식)
            for event in graph.stream(initial_state, config=config):
                for key, value in event.items():
                    print(f"Node: {key}")
                    # 여기서 NoneType 반복 오류가 나는지 확인
                    if "messages" in value:
                        msgs = value["messages"]
                        if msgs is None:
                            print(f"ERROR: Node {key} returned messages=None")
                    
                    if "symptoms" in value and value["symptoms"] is None:
                        print(f"ERROR: Node {key} returned symptoms=None")

            print("SUCCESS: Graph execution completed.")
        except Exception as e:
            print(f"FAILED: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_graph()
