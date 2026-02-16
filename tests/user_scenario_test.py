import sys
import os
sys.path.append(os.getcwd())

from src.graph import create_graph
from langchain_core.messages import HumanMessage, AIMessage
import uuid

def test_user_scenario():
    graph = create_graph()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    messages = []
    
    # 순차적 대화 테스트
    inputs = [
        "속이 쓰려요",
        "명치",
        "소화제 먹었어요"
    ]
    
    for text in inputs:
        print(f"\n>>> User: {text}")
        try:
            # LangGraph는 state를 유지하므로 순차적으로 invoke
            # 또는 초기 state에 전체 history를 넣어서 테스트
            messages.append(HumanMessage(content=text))
            inputs_state = {"messages": messages}
            
            # 스트리밍 실행 (api.py 방식)
            events = graph.stream(inputs_state, config=config)
            for event in events:
                for key, value in event.items():
                    print(f"Node: [{key}]")
                    # 여기서 value가 None인지, 또는 value 안에 None이 있는지 체크
                    if value is None:
                        print(f"!!! CRITICAL: Node {key} returned None as value")
                    else:
                        if "messages" in value:
                            msgs = value["messages"]
                            if msgs is None:
                                print(f"!!! CRITICAL: Node {key} returned messages=None")
                            else:
                                # msgs가 리스트인지 확인
                                if not isinstance(msgs, list):
                                    msgs = [msgs]
                                for m in msgs:
                                    if hasattr(m, 'content'):
                                        if m.content is None:
                                            print(f"!!! CRITICAL: Node {key} returned message with content=None")
                                        else:
                                            # AI 응답이면 history에 추가 (다음 턴을 위해)
                                            if isinstance(m, AIMessage):
                                                messages.append(m)

            print("--- Step completed successfully ---")
            
        except Exception as e:
            print(f"!!! FAILED with error: {e}")
            import traceback
            traceback.print_exc()
            return

    print("\n✅ User scenario completed without crash.")

if __name__ == "__main__":
    test_user_scenario()
