"""멱등성 캐시 유틸리티"""
import hashlib
import json
from typing import Dict, Optional, Tuple, Any


class IdempotencyCache:
    """멱등성 키를 기반으로 요청/응답을 캐싱하는 클래스"""
    
    def __init__(self):
        # key: idempotency_key, value: (request_hash, response)
        self._cache: Dict[str, Tuple[str, Any]] = {}
    
    def _hash_request(self, request_data: dict) -> str:
        """요청 데이터의 해시를 생성"""
        # 정렬된 JSON 문자열로 변환하여 일관된 해시 생성
        request_json = json.dumps(request_data, sort_keys=True)
        return hashlib.sha256(request_json.encode()).hexdigest()
    
    def get(self, idempotency_key: str, request_data: dict) -> Optional[Tuple[bool, Any]]:
        """
        캐시에서 응답을 조회
        
        Args:
            idempotency_key: 멱등성 키
            request_data: 요청 데이터
            
        Returns:
            - (True, response): 동일한 요청이면 캐시된 응답 반환
            - (False, None): 다른 요청이면 충돌
            - None: 캐시에 없음
        """
        if idempotency_key not in self._cache:
            return None
        
        cached_hash, cached_response = self._cache[idempotency_key]
        request_hash = self._hash_request(request_data)
        
        # 동일한 요청인지 확인
        if cached_hash == request_hash:
            return (True, cached_response)
        else:
            # 다른 요청이면 충돌
            return (False, None)
    
    def set(self, idempotency_key: str, request_data: dict, response: Any) -> None:
        """
        캐시에 응답을 저장
        
        Args:
            idempotency_key: 멱등성 키
            request_data: 요청 데이터
            response: 응답 데이터
        """
        request_hash = self._hash_request(request_data)
        self._cache[idempotency_key] = (request_hash, response)
    
    def clear(self) -> None:
        """캐시 초기화"""
        self._cache.clear()


# 전역 캐시 인스턴스
_idempotency_cache = IdempotencyCache()


def get_idempotency_cache() -> IdempotencyCache:
    """전역 멱등성 캐시 인스턴스 반환"""
    return _idempotency_cache
