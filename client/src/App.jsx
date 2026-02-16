import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Activity, ShieldCheck, HeartPulse, Bot, Stethoscope, MapPin, History, Trash2, Plus } from 'lucide-react';
import ChatMessage from './components/ChatMessage';
import { saveConversation, getConversations, deleteConversation, generateConversationId, generateConversationTitle } from './utils/storage';

// Axios API Base URL 설정 (백엔드 서버 주소)
const api = axios.create({
  baseURL: 'http://localhost:8000',
});

function App() {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      content: '안녕하세요! MediGraph입니다. 😊\n\n병원 가기 전에 **의사 선생님께 무슨 말을 해야 할지**, 그리고 **어떤 과를 찾아가야 할지** 고민이신가요?\n\n증상을 말씀해 주시면:\n✅ 의사에게 전달할 요약 카드 (닥터 패스)\n✅ 적합한 진료과 추천 및 병원 찾기\n✅ 증상 분석 및 자가 관리 팁\n\n을 제공해드립니다. 편하게 증상을 이야기해 주세요!',
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const [threadId, setThreadId] = useState(null); // 대화 세션 ID
  const [currentConvId, setCurrentConvId] = useState(generateConversationId()); // 현재 대화 ID
  const [savedConversations, setSavedConversations] = useState(getConversations()); // 저장된 대화 목록

  // 메시지 목록이 업데이트될 때마다 스크롤을 최하단으로 이동
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  // 메시지가 변경될 때마다 현재 대화 자동 저장
  useEffect(() => {
    if (messages.length > 1) { // 초기 AI 메시지 이상일 때만 저장
      const conversation = {
        id: currentConvId,
        title: generateConversationTitle(messages),
        messages: messages,
        timestamp: Date.now()
      };
      saveConversation(conversation);
      setSavedConversations(getConversations()); // 목록 갱신
    }
  }, [messages, currentConvId]);

  // 메시지 전송 핸들러
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    // 사용자 메시지 추가
    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // 백엔드 API 호출
      const response = await api.post('/chat', {
        message: userMsg.content,
        thread_id: threadId
      });

      const data = response.data;
      if (data.thread_id) setThreadId(data.thread_id);

      // AI 응답 메시지 구성
      const aiMsg = {
        role: 'ai',
        content: data.response,
        steps: data.steps,     // 사고 과정
        diagnosis: data.diagnosis, // 진단 요약
        nextStep: data.next_step, // 다음 단계
        doctorPass: data.doctor_pass, // 닥터 패스 (의사 소견서)
        recommendedDepartment: data.recommended_department, // 추천 진료과
        medicationInfo: data.medication_info, // 약물 정보
        factCheckConfidence: data.fact_check_confidence, // 팩트체크 신뢰도
        factCheckSources: data.fact_check_sources // 검증 출처
      };

      setMessages(prev => [...prev, aiMsg]);
    } catch (error) {
      console.error('Error:', error);

      // 에러 타입 세분화
      let errorMessage = '오류가 발생했습니다. ';
      if (error.response) {
        // 서버 응답이 있는 경우
        errorMessage += `서버 오류: ${error.response.status} \n`;
        if (error.response.data?.detail) {
          errorMessage += `상세: ${JSON.stringify(error.response.data.detail)} `;
        }
      } else if (error.request) {
        // 요청이 전송되었으나 응답 없음
        errorMessage += '서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인해주세요.';
      } else {
        // 요청 생성 중 오류
        errorMessage += error.message;
      }

      setMessages(prev => [
        ...prev,
        { role: 'ai', content: errorMessage }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // 새 대화 시작
  const handleNewConversation = () => {
    setCurrentConvId(generateConversationId());
    setThreadId(null);
    setMessages([
      {
        role: 'ai',
        content: '안녕하세요! MediGraph입니다. 😊\n\n병원 가기 전에 **의사 선생님께 무슨 말을 해야 할지**, 그리고 **어떤 과를 찾아가야 할지** 고민이신가요?\n\n증상을 말씀해 주시면:\n✅ 의사에게 전달할 요약 카드 (닥터 패스)\n✅ 적합한 진료과 추천 및 병원 찾기\n✅ 증상 분석 및 자가 관리 팁\n\n을 제공해드립니다. 편하게 증상을 이야기해 주세요!',
      }
    ]);
  };

  // 저장된 대화 불러오기
  const handleLoadConversation = (conv) => {
    setCurrentConvId(conv.id);
    setMessages(conv.messages);
    setThreadId(null); // 새 thread 시작
  };

  // 대화 삭제
  const handleDeleteConversation = (convId) => {
    deleteConversation(convId);
    setSavedConversations(getConversations());

    // 현재 보고 있는 대화를 삭제한 경우 새 대화 시작
    if (convId === currentConvId) {
      handleNewConversation();
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-50 to-slate-100">

      {/* 사이드바 / 데스크탑용 패널 */}
      <div className="hidden md:flex md:w-80 bg-white border-r border-slate-200 flex-col p-6">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-medical/30 rounded-xl flex items-center justify-center text-green-700">
            <Activity size={24} />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-800">MediGraph</h1>
        </div>

        <div className="space-y-6">
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
            <h3 className="font-semibold text-sm mb-2 text-slate-500 uppercase tracking-wider">시스템 상태</h3>
            <div className="flex items-center gap-2 text-sm text-green-600 font-medium">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              정상 작동 중 (All Systems Operational)
            </div>
          </div>

          <div className="space-y-4 break-keep">
            <div className="flex items-start gap-3 text-sm text-slate-700 font-medium bg-blue-50 p-3 rounded-lg border border-blue-100">
              <Stethoscope className="text-blue-600 flex-shrink-0 mt-0.5" size={18} />
              <p><strong className="text-blue-700">닥터 패스:</strong> 의사에게 전달할 증상 요약 카드 자동 생성</p>
            </div>
            <div className="flex items-start gap-3 text-sm text-slate-700 font-medium bg-green-50 p-3 rounded-lg border border-green-100">
              <MapPin className="text-green-600 flex-shrink-0 mt-0.5" size={18} />
              <p><strong className="text-green-700">진료과 추천:</strong> 증상에 맞는 진료과 안내 및 주변 병원 검색</p>
            </div>
            <div className="flex items-start gap-3 text-sm text-slate-600">
              <ShieldCheck className="text-medical flex-shrink-0" size={18} />
              <p>의학 정보 검색 및 검증 (LangGraph 기반)</p>
            </div>
            <div className="flex items-start gap-3 text-sm text-slate-600">
              <HeartPulse className="text-red-400 flex-shrink-0" size={18} />
              <p>응급 증상 실시간 감지 및 대응</p>
            </div>
          </div>
        </div>

        {/* 대화 히스토리 */}
        <div className="mt-6 flex-1 flex flex-col overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <History className="text-slate-600" size={16} />
              <h3 className="font-semibold text-sm text-slate-600">이전 대화</h3>
            </div>
            <button
              onClick={handleNewConversation}
              className="flex items-center gap-1 text-xs bg-medical/20 hover:bg-medical/30 text-green-700 px-2 py-1 rounded-lg transition-colors"
              title="새 대화 시작"
            >
              <Plus size={14} />
              <span>새 대화</span>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 pr-2">
            {savedConversations.length === 0 ? (
              <p className="text-xs text-slate-400 text-center py-4">저장된 대화가 없습니다</p>
            ) : (
              savedConversations
                .sort((a, b) => b.timestamp - a.timestamp) // 최신 대화가 위로
                .map((conv) => (
                  <div
                    key={conv.id}
                    className={`group p-2 rounded-lg border transition-colors cursor-pointer ${conv.id === currentConvId
                      ? 'bg-medical/10 border-medical/30'
                      : 'bg-slate-50 border-slate-200 hover:bg-slate-100'
                      }`}
                  >
                    <div className="flex items-start gap-2">
                      <div
                        onClick={() => handleLoadConversation(conv)}
                        className="flex-1 min-w-0"
                      >
                        <p className="text-xs font-medium text-slate-700 truncate">
                          {conv.title}
                        </p>
                        <p className="text-xs text-slate-400">
                          {new Date(conv.timestamp).toLocaleDateString('ko-KR', {
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteConversation(conv.id);
                        }}
                        className="opacity-0 group-hover:opacity-100 transition-opacity text-red-400 hover:text-red-600"
                        title="삭제"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                ))
            )}
          </div>
        </div>

        <div className="mt-auto pt-6 border-t border-slate-100">
          <p className="text-xs text-slate-400 leading-relaxed">
            면책 조항: 이 서비스는 의학적 조언을 대체하지 않습니다. 응급 상황 시 즉시 119에 연락하세요.
          </p>
        </div>
      </div>

      {/* 메인 채팅 영역 */}
      <div className="flex-1 flex flex-col max-w-5xl mx-auto w-full shadow-xl bg-white/50 backdrop-blur-sm sm:my-4 sm:rounded-2xl sm:border sm:border-slate-200 overflow-hidden">

        {/* 모바일 헤더 */}
        <div className="md:hidden flex items-center p-4 bg-white border-b border-slate-100 sticky top-0 z-10">
          <Activity className="text-medical mr-2" size={24} />
          <h1 className="font-bold text-lg">MediGraph</h1>
        </div>

        {/* 메시지 리스트 */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 scroll-smooth">
          {messages.map((msg, idx) => (
            <ChatMessage key={idx} {...msg} />
          ))}

          {/* 로딩 인디케이터 */}
          {loading && (
            <div className="flex w-full mb-6 justify-start">
              <div className="flex max-w-[80%] flex-row gap-3">
                <div className="w-10 h-10 rounded-full bg-medical/20 text-green-700 flex items-center justify-center flex-shrink-0">
                  <Bot size={20} />
                </div>
                <div className="bg-white border border-medical/40 p-4 rounded-2xl shadow-sm flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <span className="text-sm text-slate-500 ml-2">증상 분석 및 의학 정보 검색 중...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 입력 영역 */}
        <div className="p-4 bg-white border-t border-slate-100">
          <form onSubmit={handleSubmit} className="relative flex items-center max-w-4xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="증상을 입력하세요 (예: 머리가 아프고 메스꺼움이 있어요)"
              className="w-full pl-5 pr-14 py-4 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-medical/50 focus:border-medical transition-all shadow-inner text-slate-800 placeholder-slate-400"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="absolute right-2 p-2 bg-medical text-white rounded-lg hover:bg-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md"
            >
              <Send size={20} />
            </button>
          </form>
          <div className="text-center mt-2">
            <span className="text-xs text-slate-400">MediGraph AI can make mistakes. Please verify important information.</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
