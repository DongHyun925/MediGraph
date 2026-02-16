/**
 * LocalStorage 유틸리티
 * 대화 히스토리 관리 (저장, 불러오기, 삭제)
 */

const STORAGE_KEY = 'mediGraph_conversations';

/**
 * 모든 대화 목록 조회
 */
export const getConversations = () => {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        return stored ? JSON.parse(stored) : [];
    } catch (error) {
        console.error('Failed to load conversations:', error);
        return [];
    }
};

/**
 * 대화 저장
 * @param {Object} conversation - { id, title, messages, timestamp }
 */
export const saveConversation = (conversation) => {
    try {
        const conversations = getConversations();
        const existingIndex = conversations.findIndex(c => c.id === conversation.id);

        if (existingIndex >= 0) {
            // 기존 대화 업데이트
            conversations[existingIndex] = conversation;
        } else {
            // 새 대화 추가
            conversations.push(conversation);
        }

        localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
        return true;
    } catch (error) {
        console.error('Failed to save conversation:', error);
        return false;
    }
};

/**
 * 특정 대화 조회
 * @param {string} id - 대화 ID
 */
export const getConversationById = (id) => {
    const conversations = getConversations();
    return conversations.find(c => c.id === id);
};

/**
 * 대화 삭제
 * @param {string} id - 대화 ID
 */
export const deleteConversation = (id) => {
    try {
        const conversations = getConversations();
        const filtered = conversations.filter(c => c.id !== id);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
        return true;
    } catch (error) {
        console.error('Failed to delete conversation:', error);
        return false;
    }
};

/**
 * 대화 제목 자동 생성
 * @param {Array} messages - 메시지 배열
 */
export const generateConversationTitle = (messages) => {
    // 첫 번째 사용자 메시지에서 제목 추출 (최대 30자)
    const firstUserMsg = messages.find(m => m.role === 'user');
    if (firstUserMsg) {
        const content = firstUserMsg.content.trim();
        return content.length > 30 ? content.substring(0, 30) + '...' : content;
    }
    return '새 대화';
};

/**
 * 현재 대화 ID 생성
 */
export const generateConversationId = () => {
    return `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};
