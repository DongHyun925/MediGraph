from langchain_community.tools.tavily_search import TavilySearchResults
from src.state import AgentState
from src.utils.cache import medical_search_cache
import hashlib

def medical_rag_node(state: AgentState):
    """
    추출된 증상을 바탕으로 외부 의학 정보를 검색하는 RAG(Retrieval Augmented Generation) 노드입니다.
    Tavily API를 사용하여 신뢰할 수 있는 정보를 검색합니다.
    결과를 캐싱하여 동일한 증상에 대한 반복 검색을 방지합니다.
    """
    symptoms = state.get("symptoms", [])
    if symptoms is None:
        symptoms = []
        
    if not symptoms:
        return {"medical_evidence": ["검색할 구체적인 증상 정보가 없습니다."]}
        
    # 검색 쿼리 생성
    query = f"medical diagnosis and treatment for symptoms: {', '.join(symptoms)} (official medical guidelines or research paper)"
    
    # 캐시 키 생성 (쿼리의 해시값)
    cache_key = hashlib.md5(query.encode()).hexdigest()
    
    # 캐시 확인
    cached_result = medical_search_cache.get(cache_key)
    if cached_result is not None:
        print(f"[Cache HIT] 캐시에서 의학 정보 로드: {symptoms}")
        return {"medical_evidence": cached_result}
    
    print(f"[Cache MISS] Tavily 검색 실행: {symptoms}")
    
    # Tavily 검색 도구 초기화
    exclude_domains = [
        "naver.com", "blog.naver.com", "tistory.com", "velog.io", 
        "brunch.co.kr", "medium.com", "reddit.com", "dcinside.com", 
        "namu.wiki", "youtube.com", "facebook.com", "instagram.com", "twitter.com"
    ]
    
    search = TavilySearchResults(
        max_results=5,
        exclude_domains=exclude_domains,
    )
    
    try:
        results = search.invoke(query)
        
        # results가 None인 경우 빈 리스트로 처리
        if results is None:
            results = []
            
        evidence = [res.get("content", "") for res in results if res is not None]
        
        # 결과를 캐시에 저장
        medical_search_cache.set(cache_key, evidence)
        
        return {"medical_evidence": evidence}
    except Exception as e:
        print(f"medical_rag 검색 오류: {e}")
        return {"medical_evidence": ["의학 정보를 검색하는 중 오류가 발생했습니다."]}
