"""
간단한 LRU 캐시 구현
의학 검색 결과를 캐싱하여 성능 향상
"""
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any, Optional
import threading

class LRUCache:
    """
    TTL(Time To Live)이 있는 LRU 캐시
    """
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """
        Args:
            max_size: 최대 캐시 항목 수
            ttl_seconds: 캐시 유효 시간 (초), 기본 1시간
        """
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = timedelta(seconds=ttl_seconds)
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        캐시에서 값을 가져옴
        
        Args:
            key: 캐시 키
            
        Returns:
            캐시된 값 또는 None (만료되었거나 없는 경우)
        """
        with self.lock:
            if key not in self.cache:
                return None
            
            value, timestamp = self.cache[key]
            
            # TTL 확인
            if datetime.now() - timestamp > self.ttl:
                # 만료됨
                del self.cache[key]
                return None
            
            # LRU: 최근 사용으로 이동
            self.cache.move_to_end(key)
            return value
    
    def set(self, key: str, value: Any) -> None:
        """
        캐시에 값을 저장
        
        Args:
            key: 캐시 키
            value: 저장할 값
        """
        with self.lock:
            # 이미 존재하면 업데이트
            if key in self.cache:
                del self.cache[key]
            
            # 새 항목 추가
            self.cache[key] = (value, datetime.now())
            self.cache.move_to_end(key)
            
            # 크기 제한 확인
            if len(self.cache) > self.max_size:
                # 가장 오래된 항목 제거
                self.cache.popitem(last=False)
    
    def clear(self) -> None:
        """캐시 전체 삭제"""
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        """현재 캐시 크기"""
        with self.lock:
            return len(self.cache)


# 전역 캐시 인스턴스
medical_search_cache = LRUCache(max_size=100, ttl_seconds=3600)
