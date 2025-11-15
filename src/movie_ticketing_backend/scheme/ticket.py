"""
티켓 관련 Pydantic 스키마
요청 및 응답 데이터 모델
"""
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


# ===== 발권 API 스키마 =====
class IssueTicketRequest(BaseModel):
    """발권 요청 스키마"""
    theater_name: str = Field(..., min_length=1, max_length=100, description="극장명")
    user_id: str = Field(..., min_length=1, max_length=100, description="사용자 ID")
    movie_title: str = Field(..., min_length=1, max_length=200, description="영화명")
    price_krw: int = Field(..., gt=0, le=1_000_000, description="가격 (KRW)")
    quantity: int = Field(1, ge=1, le=10, description="수량")
    memo: Optional[str] = Field(None, description="메모")

    model_config = {
        "json_schema_extra": {
            "example": {
                "theater_name": "CGV 강남",
                "user_id": "user123",
                "movie_title": "영화 제목",
                "price_krw": 15000,
                "quantity": 2,
                "memo": "VIP석"
            }
        }
    }


class IssueTicketSummary(BaseModel):
    """발권 요약 정보"""
    theater_name: str
    movie_title: str
    price_krw: int


class IssueTicketResponse(BaseModel):
    """발권 응답 스키마"""
    ticket_ids: List[str] = Field(..., description="생성된 티켓 ID 목록")
    count: int = Field(..., description="생성된 티켓 개수")
    summary: IssueTicketSummary = Field(..., description="발권 요약")

    model_config = {
        "json_schema_extra": {
            "example": {
                "ticket_ids": ["abc123", "def456"],
                "count": 2,
                "summary": {
                    "theater_name": "CGV 강남",
                    "movie_title": "영화 제목",
                    "price_krw": 15000
                }
            }
        }
    }


# ===== 환불 API 스키마 =====
class RefundTicketRequest(BaseModel):
    """환불 요청 스키마"""
    ticket_ids: List[str] = Field(..., min_length=1, description="환불할 티켓 ID 목록")
    reason: Optional[str] = Field(None, description="환불 사유")

    model_config = {
        "json_schema_extra": {
            "example": {
                "ticket_ids": ["abc123", "def456"],
                "reason": "고객 요청"
            }
        }
    }


class RefundTicketResponse(BaseModel):
    """환불 응답 스키마"""
    refunded: List[str] = Field(..., description="환불 완료된 티켓 ID 목록")
    already_canceled: List[str] = Field(..., description="이미 취소된 티켓 ID 목록")
    not_found: List[str] = Field(..., description="존재하지 않는 티켓 ID 목록")

    model_config = {
        "json_schema_extra": {
            "example": {
                "refunded": ["abc123"],
                "already_canceled": ["def456"],
                "not_found": ["ghi789"]
            }
        }
    }


# ===== 티켓 조회 API 스키마 =====
class TicketResponse(BaseModel):
    """단일 티켓 응답 스키마"""
    id: str = Field(..., description="티켓 ID")
    theater_name: str = Field(..., description="극장명")
    user_id: str = Field(..., description="사용자 ID")
    movie_title: str = Field(..., description="영화명")
    price_krw: int = Field(..., description="가격 (KRW)")
    status: str = Field(..., description="상태 (issued | canceled)")
    memo: Optional[str] = Field(None, description="메모")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "abc123",
                "theater_name": "CGV 강남",
                "user_id": "user123",
                "movie_title": "영화 제목",
                "price_krw": 15000,
                "status": "issued",
                "memo": "VIP석",
                "created_at": "2025-11-15T10:00:00",
                "updated_at": "2025-11-15T10:00:00"
            }
        }
    }


class TicketListResponse(BaseModel):
    """티켓 목록 응답 스키마"""
    tickets: List[TicketResponse] = Field(..., description="티켓 목록")
    total: int = Field(..., description="전체 티켓 개수")
    limit: int = Field(..., description="적용된 limit")
    offset: int = Field(..., description="적용된 offset")

    model_config = {
        "json_schema_extra": {
            "example": {
                "tickets": [
                    {
                        "id": "abc123",
                        "theater_name": "CGV 강남",
                        "user_id": "user123",
                        "movie_title": "영화 제목",
                        "price_krw": 15000,
                        "status": "issued",
                        "memo": "VIP석",
                        "created_at": "2025-11-15T10:00:00",
                        "updated_at": "2025-11-15T10:00:00"
                    }
                ],
                "total": 1,
                "limit": 100,
                "offset": 0
            }
        }
    }

