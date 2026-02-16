import sys
import os

from src.graph import create_graph
from langchain_core.messages import HumanMessage

from src.graph import create_graph
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

def test_graph_multiturn():
    print("Initializing Graph with Memory Checkpointer...")
    memory = MemorySaver()
    # create_graph() needs to be modified to accept checkpointer if it doesn't already?
    # Actually create_graph returns a compiled graph.
    # I need to compile it with checkpointer.
    # In src/graph.py: return workflow.compile() -> return workflow.compile(checkpointer=memory) if I want.
    # But usually we pass checkpointer to compile().
    # Let's modify src/graph.py to accept an optional checkpointer or just do it here.
    # I cannot modify create_graph easily without editing the file.
    
    # Alternative: Instantiate workflow here.
    # But that requires importing all nodes.
    
    # Let's just run the graph for Turn 1, get the result, and manually construct state for Turn 2.
    # This proves the logic works.
    
    graph = create_graph()
    
    print("\n--- Turn 1: '배가 아파' ---")
    state_v1 = {"messages": [HumanMessage(content="배가 아파")]}
    
    # We need to capture the 'symptoms' output from the graph execution.
    # Since the graph might hit 'question_generator' and END.
    
    symptoms_v1 = []
    
    events = graph.stream(state_v1)
    for event in events:
        for key, value in event.items():
            if "symptoms" in value:
                symptoms_v1 = value["symptoms"]
                print(f"Turn 1 Symptoms: {symptoms_v1}")
                
    print(f"\nCaptured Symptoms after Turn 1: {symptoms_v1}")
    
    print("\n--- Turn 2: '아랫배가 콕콕 찔러' (User answers follow-up) ---")
    # Manually pass the symptoms from Turn 1 into Turn 2 state
    state_v2 = {
        "messages": [HumanMessage(content="배가 아파"), HumanMessage(content="아랫배가 콕콕 찔러")],
        "symptoms": symptoms_v1 # This is crucial. The API does this via checkpointing.
    }
    
    events = graph.stream(state_v2)
    for event in events:
         for key, value in event.items():
            if "symptoms" in value:
                print(f"Turn 2 Symptoms: {value['symptoms']}")
                print(f"Turn 2 Missing Info: {value.get('missing_info')}")

if __name__ == "__main__":
    test_graph_multiturn()
