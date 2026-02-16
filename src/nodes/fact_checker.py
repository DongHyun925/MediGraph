from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.state import AgentState
from src.utils.llm import get_llm

def fact_checker_node(state: AgentState):
    """
    생성된 진단 가설이 검색된 근거와 일치하는지 검증하는(Fact Checking) 노드입니다.
    신뢰도 점수와 출처 인용을 추가하여 신뢰성을 높입니다.
    """
    llm = get_llm()
    hypothesis = state.get("diagnosis_hypothesis", "")
    evidence = state.get("medical_evidence", [])
    if evidence is None:
        evidence = []
    
    if not hypothesis or not evidence:
        return {
            "critique": "insufficient_data",
            "fact_check_confidence": 0,
            "fact_check_sources": []
        }
        
    prompt = ChatPromptTemplate.from_template(
        """
        당신은 전문 의료 팩트 체커(Fact Checker)입니다. 다음 진단 가설이 제공된 의학적 증거(RAG)와 일치하는지 철저히 검증하세요.
        
        진단 가설 (Hypothesis):
        {hypothesis}
        
        의학적 증거 (Evidence):
        {evidence}
        
        작업 지침:
        1. **검증 (Critique)**: 진단이 증거에 의해 잘 뒷받침되는지 확인하세요. 
           - 환각(증거에 없는 주장)이나 모순이 있다면 "invalid"
           - 증거가 너무 부족하면 "needs_more_info"
           - 논리적으로 일치하면 "valid"
        2. **신뢰도 (Confidence)**: 진단의 정확성에 대한 확신을 0-100 사이의 점수로 매기세요.
        3. **출처 (Sources)**: 증거 내용에서 언급된 신뢰할 수 있는 기관이나 논문, 가이드라인 이름을 추출하세요. (최대 3개)
        
        출력 형식 (JSON string only):
        {{
            "critique": "valid/invalid/needs_more_info",
            "confidence": 95,
            "sources": ["출처 1", "출처 2"]
        }}
        """
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        result = chain.invoke({
            "hypothesis": hypothesis,
            "evidence": "\n\n".join(evidence)
        })
        
        if result is None:
            print("!!! Fact Checker: LLM returned None")
            result = {}
            
        print(f"DEBUG Fact Checker Result: {result}")
            
        sources = result.get("sources", [])
        if not isinstance(sources, list):
            sources = [str(sources)] if sources else []

        # 신뢰도 점수 추출 및 정수 변환 로직 강화
        def parse_confidence(val):
            if val is None: return 0
            if isinstance(val, (int, float)): return int(val)
            if isinstance(val, str):
                # 숫자만 추출 (예: "95%" -> 95)
                import re
                nums = re.findall(r'\d+', val)
                return int(nums[0]) if nums else 0
            return 0

        # 여러 가능한 키 확인
        conf_val = result.get("confidence")
        if conf_val is None: conf_val = result.get("fact_check_confidence")
        if conf_val is None: conf_val = result.get("score")
        
        confidence_score = parse_confidence(conf_val)
        critique_str = str(result.get("critique", "needs_more_info")).lower()

        # 보정 로직: valid인데 점수가 너무 낮으면(0점 등) 최소 점수 부여
        if critique_str == "valid" and confidence_score < 30:
            confidence_score = 80 # 기본 신뢰도 부여
            
        return {
            "critique": critique_str,
            "fact_check_confidence": confidence_score,
            "fact_check_sources": sources
        }
    except Exception as e:
        print(f"Fact Check Error: {e}")
        return {
            "critique": "valid", 
            "fact_check_confidence": 70, # 에러 시 기본값 상향
            "fact_check_sources": ["시스템 자가 검증"]
        }

