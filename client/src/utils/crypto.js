/**
 * LocalStorage 암호화 유틸리티
 * AES-GCM을 사용한 클라이언트 측 암호화로 건강 정보 보호
 */

// Web Crypto API를 사용한 AES-GCM 암호화
const ALGORITHM = 'AES-GCM';
const KEY_LENGTH = 256;
const IV_LENGTH = 12; // 96 bits recommended for GCM

/**
 * 문자열로부터 암호화 키 생성
 * @param {string} password - 기본 비밀번호 (세션 ID 등)
 * @returns {Promise<CryptoKey>}
 */
async function deriveKey(password) {
    const encoder = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
        'raw',
        encoder.encode(password),
        { name: 'PBKDF2' },
        false,
        ['deriveKey']
    );

    return crypto.subtle.deriveKey(
        {
            name: 'PBKDF2',
            salt: encoder.encode('medilgraph-salt-2024'), // 고정 salt (실제로는 사용자별로 달라야 함)
            iterations: 100000,
            hash: 'SHA-256'
        },
        keyMaterial,
        { name: ALGORITHM, length: KEY_LENGTH },
        false,
        ['encrypt', 'decrypt']
    );
}

/**
 * 데이터 암호화
 * @param {string} plaintext - 암호화할 평문
 * @param {string} password - 암호화 키 생성용 비밀번호
 * @returns {Promise<string>} Base64 인코딩된 암호문
 */
export async function encryptData(plaintext, password = 'default-key-change-me') {
    try {
        const key = await deriveKey(password);
        const encoder = new TextEncoder();
        const data = encoder.encode(plaintext);

        // 랜덤 IV 생성
        const iv = crypto.getRandomValues(new Uint8Array(IV_LENGTH));

        // 암호화
        const ciphertext = await crypto.subtle.encrypt(
            { name: ALGORITHM, iv },
            key,
            data
        );

        // IV + ciphertext를 Base64로 인코딩
        const combined = new Uint8Array(iv.length + ciphertext.byteLength);
        combined.set(iv, 0);
        combined.set(new Uint8Array(ciphertext), iv.length);

        return btoa(String.fromCharCode.apply(null, combined));
    } catch (error) {
        console.error('암호화 실패:', error);
        throw error;
    }
}

/**
 * 데이터 복호화
 * @param {string} encryptedData - Base64 암호문
 * @param {string} password - 복호화 키 생성용 비밀번호
 * @returns {Promise<string>} 복호화된 평문
 */
export async function decryptData(encryptedData, password = 'default-key-change-me') {
    try {
        const key = await deriveKey(password);

        // Base64 디코딩
        const combined = Uint8Array.from(atob(encryptedData), c => c.charCodeAt(0));

        // IV와 ciphertext 분리
        const iv = combined.slice(0, IV_LENGTH);
        const ciphertext = combined.slice(IV_LENGTH);

        // 복호화
        const decrypted = await crypto.subtle.decrypt(
            { name: ALGORITHM, iv },
            key,
            ciphertext
        );

        const decoder = new TextDecoder();
        return decoder.decode(decrypted);
    } catch (error) {
        console.error('복호화 실패:', error);
        return null; // 복호화 실패 시 null 반환 (기존 데이터 호환성)
    }
}
