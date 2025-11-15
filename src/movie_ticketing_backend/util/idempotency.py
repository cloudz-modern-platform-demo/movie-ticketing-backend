"""Idempotency utility for handling duplicate requests."""

import hashlib
import json
from typing import Optional, Any
from datetime import datetime, timedelta


class IdempotencyCache:
    """
    In-memory cache for idempotency keys and request hashes.
    
    Stores the request hash and response for each idempotency key
    to prevent duplicate processing of requests.
    """
    
    def __init__(self, ttl_seconds: int = 86400):
        """
        Initialize the idempotency cache.
        
        Args:
            ttl_seconds: Time-to-live for cache entries in seconds (default: 24 hours)
        """
        self._cache: dict[str, dict[str, Any]] = {}
        self._ttl_seconds = ttl_seconds
    
    def _compute_request_hash(self, request_data: dict) -> str:
        """
        Compute a hash of the request data.
        
        Args:
            request_data: Dictionary representation of the request
            
        Returns:
            SHA256 hash of the request data
        """
        request_json = json.dumps(request_data, sort_keys=True)
        return hashlib.sha256(request_json.encode()).hexdigest()
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """
        Check if a cache entry has expired.
        
        Args:
            timestamp: Timestamp when the entry was created
            
        Returns:
            True if expired, False otherwise
        """
        return datetime.utcnow() - timestamp > timedelta(seconds=self._ttl_seconds)
    
    def _cleanup_expired(self):
        """Remove expired entries from the cache."""
        expired_keys = [
            key for key, value in self._cache.items()
            if self._is_expired(value["timestamp"])
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def check_and_store(
        self,
        idempotency_key: str,
        request_data: dict,
        response_data: Optional[dict] = None
    ) -> tuple[bool, Optional[dict]]:
        """
        Check if a request with the given idempotency key has been processed.
        
        Args:
            idempotency_key: Unique key for the request
            request_data: Dictionary representation of the request
            response_data: Response data to store (optional)
            
        Returns:
            Tuple of (is_duplicate, cached_response)
            - is_duplicate: True if this is a duplicate request
            - cached_response: The cached response if duplicate, None otherwise
            
        Raises:
            ValueError: If the idempotency key exists with different request data (conflict)
        """
        self._cleanup_expired()
        
        request_hash = self._compute_request_hash(request_data)
        
        if idempotency_key in self._cache:
            cached_entry = self._cache[idempotency_key]
            cached_hash = cached_entry["request_hash"]
            
            # Same idempotency key but different request data = conflict
            if cached_hash != request_hash:
                raise ValueError(
                    f"Idempotency key '{idempotency_key}' already used with different request data"
                )
            
            # Same key and same request = return cached response
            return True, cached_entry.get("response")
        
        # New request - store it
        if response_data is not None:
            self._cache[idempotency_key] = {
                "request_hash": request_hash,
                "response": response_data,
                "timestamp": datetime.utcnow(),
            }
        
        return False, None
    
    def store_response(self, idempotency_key: str, response_data: dict):
        """
        Store the response for a given idempotency key.
        
        Args:
            idempotency_key: Unique key for the request
            response_data: Response data to store
        """
        if idempotency_key in self._cache:
            self._cache[idempotency_key]["response"] = response_data
            self._cache[idempotency_key]["timestamp"] = datetime.utcnow()
    
    def clear(self):
        """Clear all entries from the cache."""
        self._cache.clear()


# Global idempotency cache instance
idempotency_cache = IdempotencyCache()

