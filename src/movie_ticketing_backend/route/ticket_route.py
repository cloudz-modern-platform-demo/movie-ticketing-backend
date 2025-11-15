"""티켓 REST API 라우트"""
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from movie_ticketing_backend.db.session import get_db
from movie_ticketing_backend.service.ticket_service import TicketService
from movie_ticketing_backend.scheme.ticket import (
    TicketIssueRequest,
    TicketIssueResponse,
    TicketRefundRequest,
    TicketRefundResponse,
    TicketResponse,
    TicketListResponse,
)
from movie_ticketing_backend.util.idempotency import get_idempotency_cache


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/issue", response_model=TicketIssueResponse, status_code=status.HTTP_201_CREATED)
def issue_tickets(
    request: TicketIssueRequest,
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    """
    티켓 발권
    
    - **theater_name**: 극장명 (1~100자)
    - **user_id**: 사용자 ID (1~100자)
    - **movie_title**: 영화명 (1~200자)
    - **price_krw**: 가격 (1~1,000,000 KRW)
    - **quantity**: 수량 (1~10, 기본값: 1)
    - **memo**: 메모 (선택)
    
    멱등성 지원을 위해 `Idempotency-Key` 헤더를 사용할 수 있습니다.
    """
    service = TicketService(db)
    
    # 멱등성 키가 있으면 캐시 확인
    if idempotency_key:
        cache = get_idempotency_cache()
        request_data = request.model_dump()
        cached = cache.get(idempotency_key, request_data)
        
        if cached is not None:
            is_same, cached_response = cached
            if is_same:
                # 동일한 요청이면 캐시된 응답 반환
                return cached_response
            else:
                # 다른 요청이면 충돌
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="멱등성 키 충돌: 동일한 키로 다른 요청이 이미 처리되었습니다",
                )
    
    # 티켓 발권
    try:
        response = service.issue_tickets(request)
        
        # 멱등성 키가 있으면 캐시에 저장
        if idempotency_key:
            cache = get_idempotency_cache()
            cache.set(idempotency_key, request.model_dump(), response)
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"티켓 발권 실패: {str(e)}",
        )


@router.post("/refund", response_model=TicketRefundResponse, status_code=status.HTTP_200_OK)
def refund_tickets(
    request: TicketRefundRequest,
    db: Session = Depends(get_db),
):
    """
    티켓 환불
    
    - **ticket_ids**: 환불할 티켓 ID 목록
    - **reason**: 환불 사유 (선택)
    
    응답:
    - **refunded**: 성공적으로 환불된 티켓 ID 목록
    - **already_canceled**: 이미 취소된 티켓 ID 목록
    - **not_found**: 존재하지 않는 티켓 ID 목록
    """
    service = TicketService(db)
    
    try:
        return service.refund_tickets(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"티켓 환불 실패: {str(e)}",
        )


@router.get("/{ticket_id}", response_model=TicketResponse, status_code=status.HTTP_200_OK)
def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
):
    """
    티켓 단일 조회
    
    - **ticket_id**: 티켓 ID
    """
    service = TicketService(db)
    
    ticket = service.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"티켓을 찾을 수 없습니다: {ticket_id}",
        )
    
    return ticket


@router.get("", response_model=TicketListResponse, status_code=status.HTTP_200_OK)
def get_ticket_list(
    theater_name: Optional[str] = Query(None, description="극장명 필터"),
    user_id: Optional[str] = Query(None, description="사용자 ID 필터"),
    movie_title: Optional[str] = Query(None, description="영화명 필터"),
    status_filter: Optional[str] = Query(None, alias="status", description="상태 필터 (issued | canceled)"),
    limit: int = Query(100, ge=1, le=1000, description="페이지 크기 (최대 1000)"),
    offset: int = Query(0, ge=0, description="페이지 오프셋"),
    db: Session = Depends(get_db),
):
    """
    티켓 목록 조회
    
    필터링 및 페이징을 지원합니다.
    
    - **theater_name**: 극장명 필터 (선택)
    - **user_id**: 사용자 ID 필터 (선택)
    - **movie_title**: 영화명 필터 (선택)
    - **status**: 상태 필터 (issued | canceled, 선택)
    - **limit**: 페이지 크기 (1~1000, 기본값: 100)
    - **offset**: 페이지 오프셋 (기본값: 0)
    """
    service = TicketService(db)
    
    try:
        return service.get_ticket_list(
            theater_name=theater_name,
            user_id=user_id,
            movie_title=movie_title,
            status=status_filter,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"티켓 목록 조회 실패: {str(e)}",
        )
