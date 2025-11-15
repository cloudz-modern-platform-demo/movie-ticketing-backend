"""
멱등성(Idempotency) 유틸리티
동일한 요청에 대한 중복 처리를 방지하기 위한 캐시 관리
"""
import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class IdempotencyCache:
    """
    멱등성 캐시 관리 클래스
    메모리 기반 캐시로 Idempotency-Key와 요청 해시를 저장
    """

    def __init__(self, ttl_minutes: int = 60):
        """
        Args:
            ttl_minutes: 캐시 유효 시간 (분)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = timedelta(minutes=ttl_minutes)

    def _compute_request_hash(self, request_data: dict) -> str:
        """
        요청 데이터의 해시 계산
        
        Args:
            request_data: 요청 데이터 딕셔너리
            
        Returns:
            요청 데이터의 SHA256 해시
        """
        # 딕셔너리를 정렬된 JSON 문자열로 변환하여 해시 계산
        request_str = json.dumps(request_data, sort_keys=True)
        return hashlib.sha256(request_str.encode()).hexdigest()

    def _cleanup_expired(self):
        """만료된 캐시 항목 제거"""
        now = datetime.now()
        expired_keys = [
            key for key, value in self._cache.items()
            if now - value["timestamp"] > self._ttl
        ]
        for key in expired_keys:
            del self._cache[key]

    def check_and_store(
        self,
        idempotency_key: str,
        request_data: dict,
        response: Optional[Any] = None
    ) -> tuple[bool, Optional[str], Optional[Any]]:
        """
        멱등성 키를 확인하고 저장
        
        Args:
            idempotency_key: 멱등성 키
            request_data: 요청 데이터
            response: 응답 데이터 (저장할 경우)
            
        Returns:
            (is_duplicate, conflict_type, cached_response) 튜플
            - is_duplicate: 중복 요청 여부
            - conflict_type: 충돌 타입 ("match": 동일 요청, "conflict": 다른 요청)
            - cached_response: 캐시된 응답 (동일 요청인 경우)
        """
        self._cleanup_expired()

        request_hash = self._compute_request_hash(request_data)

        if idempotency_key in self._cache:
            cached = self._cache[idempotency_key]
            cached_hash = cached["request_hash"]

            if cached_hash == request_hash:
                # 동일한 요청 - 캐시된 응답 반환
                return True, "match", cached.get("response")
            else:
                # 다른 요청인데 같은 키 사용 - 충돌
                return True, "conflict", None

        # 새로운 요청 - 캐시에 저장
        self._cache[idempotency_key] = {
            "request_hash": request_hash,
            "response": response,
            "timestamp": datetime.now()
        }

        return False, None, None

    def update_response(self, idempotency_key: str, response: Any):
        """
        캐시된 응답 업데이트
        
        Args:
            idempotency_key: 멱등성 키
            response: 응답 데이터
        """
        if idempotency_key in self._cache:
            self._cache[idempotency_key]["response"] = response

    def clear(self):
        """전체 캐시 삭제"""
        self._cache.clear()


# 전역 싱글톤 인스턴스
_idempotency_cache = IdempotencyCache()


def get_idempotency_cache() -> IdempotencyCache:
    """
    글로벌 멱등성 캐시 인스턴스 반환
    
    Returns:
        IdempotencyCache 인스턴스
    """
    return _idempotency_cache

