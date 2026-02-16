from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.graph import create_graph
from langchain_core.messages import HumanMessage
import uuid
import os
import sys
from typing import List, Optional, Dict, Any

app = FastAPI(title="MediGraph API", description="Medical Diagnostic Agent API")

# CORS 설정 (프론트엔드 통신 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 그래프 초기화
graph = create_graph()

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    steps: List[Dict[str, Any]]
    diagnosis: Optional[str] = None
    next_step: Optional[str] = None
    doctor_pass: Optional[str] = None
    recommended_department: Optional[str] = None
    medication_info: Optional[str] = None
    fact_check_confidence: Optional[int] = None
    fact_check_sources: Optional[List[str]] = None

@app.get("/")
async def root():
    return {"message": "MediGraph API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    사용자의 메시지를 받아 MediGraph 에이전트를 실행하고 결과를 반환합니다.
    """
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {"messages": [HumanMessage(content=request.message)]}
    
    steps_log = []
    final_response = None
    final_diagnosis = None
    final_next_step = None
    final_doctor_pass = None
    final_department = None
    final_medication_info = None
    final_fact_check_confidence = None
    final_fact_check_sources = None
    
    try:
        # 스트리밍을 통해 중간 단계 포착
        events = graph.stream(initial_state, config=config)
        
        for event in events:
            if event is None: continue
            for key, value in event.items():
                if value is None:
                    continue
                    
                # 단계별 로그 기록
                step_val = str(value)
                if isinstance(value, dict) and "messages" in value:
                     msgs = value["messages"]
                     if isinstance(msgs, list):
                         step_val = []
                         for m in msgs:
                             if m is None: continue
                             if hasattr(m, 'content'):
                                 step_val.append(m.content)
                             else:
                                 step_val.append(str(m))
                     else:
                         step_val = str(msgs)

                step_info = {
                    "node": key,
                    "content": step_val
                }
                
                if isinstance(value, dict):
                    if "diagnosis_hypothesis" in value:
                        step_info["diagnosis"] = value["diagnosis_hypothesis"]
                        final_diagnosis = value["diagnosis_hypothesis"]
                    
                    if "next_step" in value:
                        step_info["next_step"] = value["next_step"]
                        final_next_step = value["next_step"]
                        
                    if "doctor_pass" in value:
                        final_doctor_pass = value["doctor_pass"]
                    
                    if "recommended_department" in value:
                        final_department = value["recommended_department"]
                    
                    if "medication_info" in value:
                        final_medication_info = value["medication_info"]
                    
                    if "fact_check_confidence" in value:
                        final_fact_check_confidence = value["fact_check_confidence"]
                    
                    if "fact_check_sources" in value:
                        final_fact_check_sources = value["fact_check_sources"]
                        
                    if "messages" in value:
                        msgs = value["messages"]
                        if isinstance(msgs, (list, tuple)) and len(msgs) > 0:
                            last_msg = msgs[-1]
                            if last_msg is not None:
                                if hasattr(last_msg, 'content'):
                                    final_response = last_msg.content
                                elif isinstance(last_msg, dict) and 'content' in last_msg:
                                    final_response = last_msg['content']
                                elif isinstance(last_msg, str):
                                    final_response = last_msg
                        elif hasattr(msgs, 'content'):
                            final_response = msgs.content

                steps_log.append(step_info)
        
        if final_diagnosis:
             # String checks for safety
             if isinstance(final_diagnosis, str):
                 final_diagnosis = final_diagnosis.replace("```markdown", "").replace("```", "").strip()
             final_response = "증상 분석이 완료되었습니다. 아래 진단 리포트를 확인해주세요."
        elif final_next_step == "emergency":
             final_response = "응급 상황입니다! 즉시 병원을 방문하세요."
        
        if not final_response:
            final_response = "죄송합니다. 적절한 답변을 생성하지 못했습니다."
            
    except Exception as e:
        import traceback
        err_type, err_obj, err_tb = sys.exc_info()
        fname = os.path.split(err_tb.tb_frame.f_code.co_filename)[1]
        line_no = err_tb.tb_lineno
        print(f"!!! SERVER ERROR: {e} | Type: {err_type.__name__} | File: {fname} | Line: {line_no}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)} at {fname}:{line_no}")
    
    return ChatResponse(
        response=str(final_response) if final_response is not None else "",
        thread_id=thread_id,
        steps=steps_log,
        diagnosis=final_diagnosis,
        next_step=final_next_step,
        doctor_pass=final_doctor_pass,
        recommended_department=final_department,
        medication_info=final_medication_info,
        fact_check_confidence=final_fact_check_confidence,
        fact_check_sources=final_fact_check_sources if final_fact_check_sources is not None else []
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
