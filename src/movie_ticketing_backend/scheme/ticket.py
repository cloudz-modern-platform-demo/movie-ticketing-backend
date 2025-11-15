"""티켓 Pydantic 스키마"""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class TicketIssueRequest(BaseModel):
    """티켓 발권 요청 스키마"""
    
    theater_name: str = Field(..., min_length=1, max_length=100, description="극장명")
    user_id: str = Field(..., min_length=1, max_length=100, description="사용자 ID")
    movie_title: str = Field(..., min_length=1, max_length=200, description="영화명")
    price_krw: int = Field(..., ge=1, le=1_000_000, description="가격(KRW)")
    quantity: int = Field(1, ge=1, le=10, description="수량")
    memo: Optional[str] = Field(None, description="메모")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "theater_name": "CGV 강남",
                    "user_id": "user123",
                    "movie_title": "인터스텔라",
                    "price_krw": 15000,
                    "quantity": 2,
                    "memo": "VIP석"
                }
            ]
        }
    }


class TicketIssueSummary(BaseModel):
    """티켓 발권 요약"""
    
    theater_name: str
    movie_title: str
    price_krw: int


class TicketIssueResponse(BaseModel):
    """티켓 발권 응답 스키마"""
    
    ticket_ids: List[str] = Field(..., description="생성된 티켓 ID 목록")
    count: int = Field(..., description="생성된 티켓 수")
    summary: TicketIssueSummary = Field(..., description="발권 요약")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ticket_ids": ["abc123", "def456"],
                    "count": 2,
                    "summary": {
                        "theater_name": "CGV 강남",
                        "movie_title": "인터스텔라",
                        "price_krw": 15000
                    }
                }
            ]
        }
    }


class TicketRefundRequest(BaseModel):
    """티켓 환불 요청 스키마"""
    
    ticket_ids: List[str] = Field(..., min_length=1, description="환불할 티켓 ID 목록")
    reason: Optional[str] = Field(None, description="환불 사유")
    
    @field_validator("ticket_ids")
    @classmethod
    def validate_ticket_ids(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("ticket_ids는 비어있을 수 없습니다")
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ticket_ids": ["abc123", "def456"],
                    "reason": "고객 요청"
                }
            ]
        }
    }


class TicketRefundResponse(BaseModel):
    """티켓 환불 응답 스키마"""
    
    refunded: List[str] = Field(..., description="환불된 티켓 ID 목록")
    already_canceled: List[str] = Field(..., description="이미 취소된 티켓 ID 목록")
    not_found: List[str] = Field(..., description="찾을 수 없는 티켓 ID 목록")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "refunded": ["abc123"],
                    "already_canceled": ["def456"],
                    "not_found": []
                }
            ]
        }
    }


class TicketResponse(BaseModel):
    """티켓 응답 스키마"""
    
    id: str = Field(..., description="티켓 ID")
    theater_name: str = Field(..., description="극장명")
    user_id: str = Field(..., description="사용자 ID")
    movie_title: str = Field(..., description="영화명")
    price_krw: int = Field(..., description="가격(KRW)")
    status: str = Field(..., description="상태 (issued | canceled)")
    memo: Optional[str] = Field(None, description="메모")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "abc123",
                    "theater_name": "CGV 강남",
                    "user_id": "user123",
                    "movie_title": "인터스텔라",
                    "price_krw": 15000,
                    "status": "issued",
                    "memo": "VIP석"
                }
            ]
        }
    }


class TicketListResponse(BaseModel):
    """티켓 목록 응답 스키마"""
    
    tickets: List[TicketResponse] = Field(..., description="티켓 목록")
    total: int = Field(..., description="전체 티켓 수")
    limit: int = Field(..., description="페이지 크기")
    offset: int = Field(..., description="페이지 오프셋")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tickets": [
                        {
                            "id": "abc123",
                            "theater_name": "CGV 강남",
                            "user_id": "user123",
                            "movie_title": "인터스텔라",
                            "price_krw": 15000,
                            "status": "issued",
                            "memo": "VIP석"
                        }
                    ],
                    "total": 1,
                    "limit": 10,
                    "offset": 0
                }
            ]
        }
    }
