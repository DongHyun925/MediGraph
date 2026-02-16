import React, { useState, useRef } from 'react';
import { Bot, User, AlertCircle, FileText, MapPin, Stethoscope, Camera } from 'lucide-react';
import html2canvas from 'html2canvas';

/**
 * 간단한 커스텀 마크다운 렌더러
 * 라이브러리 의존성 없이 안전하게 텍스트를 파싱하여 렌더링합니다.
 */
const renderContent = (text) => {
    if (!text) return null;

    // 1. 줄 단위로 분리
    const lines = text.split('\n');
    const elements = [];

    let currentList = [];

    lines.forEach((line, index) => {
        const key = `line-${index}`;

        // 볼드 처리 함수 (**text**)
        const processBold = (str) => {
            const parts = str.split(/(\*\*.*?\*\*)/g);
            return parts.map((part, i) => {
                if (part.startsWith('**') && part.endsWith('**')) {
                    return <strong key={i} className="text-green-700 font-semibold">{part.slice(2, -2)}</strong>;
                }
                return part;
            });
        };

        // 헤더 처리 (## )
        if (line.trim().startsWith('## ')) {
            if (currentList.length > 0) {
                elements.push(<ul key={`ul-${index}`} className="list-disc pl-5 mb-2 space-y-1">{currentList}</ul>);
                currentList = [];
            }
            if (line.trim().startsWith('## 🩺')) {
                elements.push(
                    <h3 key={key} className="text-xl font-bold text-slate-800 mt-6 mb-3 border-b border-slate-200 pb-2">
                        {line.replace('## ', '')}
                    </h3>
                );
            } else {
                elements.push(
                    <h3 key={key} className="text-lg font-bold text-green-800 mt-4 mb-2">
                        {line.replace('## ', '')}
                    </h3>
                );
            }
        }
        // 리스트 처리 (- )
        else if (line.trim().startsWith('- ')) {
            // 들여쓰기 감지 (공백 2칸 이상이면 중첩 리스트로 간주)
            const isNested = line.startsWith('  ') || line.startsWith('\t');

            currentList.push(
                <li key={key}
                    className={`text-slate-700 leading-relaxed ${isNested ? 'ml-6 list-[circle] text-sm' : ''}`}
                >
                    {processBold(line.trim().replace('- ', ''))}
                </li>
            );
        }
        // 일반 텍스트
        else {
            if (currentList.length > 0) {
                elements.push(<ul key={`ul-${index}`} className="list-disc pl-5 mb-2 space-y-1">{currentList}</ul>);
                currentList = [];
            }
            if (line.trim()) {
                elements.push(
                    <p key={key} className="mb-2 text-slate-700 leading-relaxed whitespace-pre-wrap">
                        {processBold(line)}
                    </p>
                );
            }
        }
    });

    // 남은 리스트 처리
    if (currentList.length > 0) {
        elements.push(<ul key="ul-last" className="list-disc pl-5 mb-2 space-y-1">{currentList}</ul>);
    }

    return elements;
};

/**
 * 개별 채팅 메시지를 렌더링하는 컴포넌트입니다.
 */
const ChatMessage = ({ role, content, steps, diagnosis, nextStep, doctorPass, recommendedDepartment, medicationInfo, factCheckConfidence, factCheckSources }) => {
    const isAi = role === 'ai';
    const doctorPassRef = useRef(null);

    // 닥터 패스 스크린샷 함수
    const handleScreenshot = async () => {
        if (!doctorPassRef.current) return;

        try {
            const canvas = await html2canvas(doctorPassRef.current, {
                backgroundColor: '#f0f9ff',
                scale: 2, // 고해상도
                logging: false,
            });

            // 이미지를 다운로드
            const link = document.createElement('a');
            link.download = `doctor-pass-${new Date().getTime()}.png`;
            link.href = canvas.toDataURL();
            link.click();
        } catch (error) {
            console.error('Screenshot failed:', error);
            alert('스크린샷 생성에 실패했습니다.');
        }
    };

    return (
        <div className={`flex w-full mb-6 ${isAi ? 'justify-start' : 'justify-end'}`}>
            <div className={`flex max-w-[80%] ${isAi ? 'flex-row' : 'flex-row-reverse'} gap-3`}>
                {/* 아바타 영역 */}
                <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 
          ${isAi ? 'bg-medical/20 text-green-700' : 'bg-slate-200 text-slate-600'}`}>
                    {isAi ? <Bot size={20} /> : <User size={20} />}
                </div>

                {/* 메시지 본문 영역 */}
                <div className="flex flex-col gap-2 min-w-0">
                    <div className={`p-4 rounded-2xl shadow-sm 
            ${isAi ? 'bg-white border border-medical/40' : 'bg-slate-100 text-slate-800'}`}>
                        {isAi ? (
                            <div className="text-sm">
                                {renderContent(content)}
                            </div>
                        ) : (
                            <div className="whitespace-pre-wrap">{content}</div>
                        )}
                    </div>

                    {/* 진단 가설 카드 (AI 메시지일 경우에만 표시) */}
                    {isAi && diagnosis && (
                        <div className="bg-white border border-green-200 p-5 rounded-xl mt-2 shadow-sm text-sm">
                            <div className="flex items-center justify-between mb-4 border-b border-green-100 pb-2">
                                <div className="flex items-center gap-2">
                                    <FileText size={20} className="text-green-600" />
                                    <span className="font-bold text-lg text-green-800">진단 상세 리포트</span>
                                </div>
                                {factCheckConfidence != null && (
                                    <div className="flex flex-col items-end">
                                        <div className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${factCheckConfidence >= 80 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                                            근거 신뢰도 {factCheckConfidence}%
                                        </div>
                                        {factCheckSources && factCheckSources.length > 0 && (
                                            <div className="text-[9px] text-slate-400 mt-0.5">
                                                {factCheckSources.length}개 출처 검증 완료
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                            <div className="text-slate-800">
                                {renderContent(diagnosis)}
                            </div>

                            {/* 검증 출처 표시 */}
                            {factCheckSources && factCheckSources.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-dotted border-green-100">
                                    <div className="text-[10px] text-green-700 font-semibold mb-1 flex items-center gap-1">
                                        <span>✅ 검증 출처:</span>
                                        <span className="font-normal text-slate-500 italic">
                                            {factCheckSources.join(', ')}
                                        </span>
                                    </div>
                                </div>
                            )}

                            {/* 약물 정보 카드 */}
                            {medicationInfo && (
                                <div className="mt-4 bg-blue-50 border border-blue-200 p-4 rounded-xl">
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="text-xl">💊</span>
                                        <span className="font-bold text-blue-900">복용 중인 약물</span>
                                    </div>
                                    <div className="text-sm text-blue-800 whitespace-pre-line leading-relaxed">
                                        {medicationInfo}
                                    </div>
                                </div>
                            )}

                            {/* 닥터 패스 (의사 소견서) */}
                            {doctorPass && (
                                <div
                                    ref={doctorPassRef}
                                    className="mt-6 bg-blue-50 border border-blue-200 p-4 rounded-xl"
                                >
                                    <div className="flex items-center justify-between mb-3">
                                        <div className="flex items-center gap-2 text-blue-800 font-bold">
                                            <Stethoscope size={18} />
                                            <span>Doctor Pass (의료진용 요약)</span>
                                        </div>
                                        <button
                                            onClick={handleScreenshot}
                                            className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition-colors shadow-sm"
                                            title="닥터 패스 저장"
                                        >
                                            <Camera size={14} />
                                            <span>저장</span>
                                        </button>
                                    </div>
                                    <div className="bg-white/70 p-4 rounded-lg border border-blue-100 space-y-3">
                                        {/* 환자 호소 섹션 */}
                                        {doctorPass.includes('환자 호소:') && (
                                            <div>
                                                <div className="text-xs font-bold text-blue-700 mb-2">📝 환자 호소</div>
                                                <div className="text-sm text-blue-900 leading-relaxed whitespace-pre-line">
                                                    {doctorPass.split('환자 호소:')[1]?.split('의학적 해석:')[0]?.trim() || doctorPass}
                                                </div>
                                            </div>
                                        )}

                                        {/* 구분선 */}
                                        {doctorPass.includes('의학적 해석:') && (
                                            <div className="border-t border-blue-200 my-2"></div>
                                        )}

                                        {/* 의학적 해석 섹션 */}
                                        {doctorPass.includes('의학적 해석:') && (
                                            <div>
                                                <div className="text-xs font-bold text-blue-700 mb-2">🔬 의학적 해석</div>
                                                <div className="text-sm text-blue-900 font-medium leading-relaxed">
                                                    {doctorPass.split('의학적 해석:')[1]?.trim()}
                                                </div>
                                            </div>
                                        )}

                                        {/* 포맷이 없는 경우 원본 표시 */}
                                        {!doctorPass.includes('환자 호소:') && !doctorPass.includes('의학적 해석:') && (
                                            <div className="text-sm text-blue-900 font-medium whitespace-pre-line">
                                                {doctorPass}
                                            </div>
                                        )}
                                    </div>
                                    <p className="text-xs text-blue-400 mt-2">
                                        * 병원 방문 시 의사 선생님께 이 화면을 보여주세요.
                                    </p>
                                </div>
                            )}

                            {/* 병원 찾기 버튼 */}
                            {recommendedDepartment && (
                                <div className="mt-4">
                                    <a
                                        href={`https://map.kakao.com/link/search/${recommendedDepartment}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="flex items-center justify-center gap-2 w-full bg-green-500 hover:bg-green-600 text-white py-3 rounded-xl font-bold transition-colors shadow-md transform hover:scale-[1.02] active:scale-95 duration-200"
                                    >
                                        <MapPin size={18} />
                                        <span>내 주변 {recommendedDepartment} 찾기</span>
                                    </a>
                                </div>
                            )}
                        </div>
                    )}

                    {/* 다음 단계 배지 */}
                    {isAi && nextStep && (
                        <div className={`text-xs font-bold uppercase tracking-wider px-2 py-1 rounded inline-block self-start
              ${nextStep === 'emergency' ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'}`}>
                            다음 단계: {nextStep}
                        </div>
                    )}

                    {/* 사고 과정 (Thinking Process) */}
                    {isAi && steps && steps.length > 0 && (
                        <div className="mt-2 text-xs text-slate-400 bg-slate-50 p-2 rounded border border-slate-100">
                            <div className="font-semibold mb-2 flex items-center gap-1">
                                <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></div>
                                사고 과정 (Thinking Process)
                            </div>
                            {steps.map((step, idx) => (
                                <div key={idx} className="mb-1 pl-2 border-l-2 border-slate-200">
                                    <span className="font-mono text-green-600 text-[10px] uppercase">Node: {step.node}</span>
                                    <p className="line-clamp-1 opacity-70">{step.content}</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ChatMessage;
