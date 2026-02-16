from src.nodes.diagnosis_generator import diagnosis_generator_node
from langchain_core.messages import HumanMessage

def test_diagnosis_formatting():
    print("Testing Diagnosis Generator Formatting...")
    
    # Mock state
    state = {
        "symptoms": ["두통", "발열", "오한"],
        "medical_evidence": [
            "두통과 발열, 오한은 감기나 독감의 초기 증상일 수 있습니다.",
            "충분한 휴식과 수분 섭취가 권장됩니다."
        ]
    }
    
    try:
        result = diagnosis_generator_node(state)
        diagnosis = result.get("diagnosis_hypothesis", "")
        
        print("\n--- Generated Diagnosis ---")
        print(diagnosis)
        print("\n---------------------------")
        
        if "##" in diagnosis or "**" in diagnosis:
            print("SUCCESS: Markdown formatting detected.")
        else:
            print("WARNING: Markdown formatting NOT detected.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_diagnosis_formatting()
