"""
티켓 라우트
REST API 엔드포인트 구현
"""
from typing import Optional, Annotated
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from movie_ticketing_backend.db.session import get_db
from movie_ticketing_backend.scheme.ticket import (
    IssueTicketRequest,
    IssueTicketResponse,
    RefundTicketRequest,
    RefundTicketResponse,
    TicketResponse,
    TicketListResponse
)
from movie_ticketing_backend.service.ticket_service import TicketService
from movie_ticketing_backend.util.idempotency import get_idempotency_cache


router = APIRouter(prefix="/tickets", tags=["tickets"])


def get_ticket_service(db: Session = Depends(get_db)) -> TicketService:
    """
    티켓 서비스 의존성 주입
    
    Args:
        db: 데이터베이스 세션
        
    Returns:
        TicketService 인스턴스
    """
    return TicketService(db, get_idempotency_cache())


@router.post(
    "/issue",
    response_model=IssueTicketResponse,
    status_code=201,
    summary="티켓 발권",
    description="티켓을 발권합니다. 수량만큼 티켓을 생성합니다."
)
async def issue_tickets(
    request: IssueTicketRequest,
    service: Annotated[TicketService, Depends(get_ticket_service)],
    idempotency_key: Annotated[Optional[str], Header()] = None
):
    """
    티켓 발권 엔드포인트
    
    Args:
        request: 발권 요청 데이터
        service: 티켓 서비스
        idempotency_key: 멱등성 키 (선택)
        
    Returns:
        발권 응답 데이터
        
    Raises:
        HTTPException: 400 (유효성 오류), 409 (멱등성 충돌), 500 (서버 오류)
    """
    try:
        response, status_code = service.issue_tickets(request, idempotency_key)
        # 멱등성 키가 있고 동일 요청인 경우 200 반환
        # 새 요청인 경우 201 반환
        if status_code == 200:
            return response
        return response
    except ValueError as e:
        # 멱등성 충돌
        if "Idempotency key conflict" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/refund",
    response_model=RefundTicketResponse,
    status_code=200,
    summary="티켓 환불",
    description="티켓을 환불합니다. 여러 티켓을 한 번에 환불할 수 있습니다."
)
async def refund_tickets(
    request: RefundTicketRequest,
    service: Annotated[TicketService, Depends(get_ticket_service)]
):
    """
    티켓 환불 엔드포인트
    
    Args:
        request: 환불 요청 데이터
        service: 티켓 서비스
        
    Returns:
        환불 응답 데이터
        
    Raises:
        HTTPException: 400 (유효성 오류), 500 (서버 오류)
    """
    try:
        return service.refund_tickets(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    status_code=200,
    summary="티켓 단일 조회",
    description="티켓 ID로 특정 티켓을 조회합니다."
)
async def get_ticket(
    ticket_id: str,
    service: Annotated[TicketService, Depends(get_ticket_service)]
):
    """
    티켓 단일 조회 엔드포인트
    
    Args:
        ticket_id: 티켓 ID
        service: 티켓 서비스
        
    Returns:
        티켓 응답 데이터
        
    Raises:
        HTTPException: 404 (티켓 없음), 500 (서버 오류)
    """
    try:
        ticket = service.get_ticket(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket not found: {ticket_id}")
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "",
    response_model=TicketListResponse,
    status_code=200,
    summary="티켓 목록 조회",
    description="필터 조건과 페이징을 사용하여 티켓 목록을 조회합니다."
)
async def list_tickets(
    service: Annotated[TicketService, Depends(get_ticket_service)],
    theater_name: Annotated[Optional[str], Query(description="극장명 필터")] = None,
    user_id: Annotated[Optional[str], Query(description="사용자 ID 필터")] = None,
    movie_title: Annotated[Optional[str], Query(description="영화명 필터")] = None,
    status: Annotated[Optional[str], Query(description="상태 필터 (issued | canceled)")] = None,
    limit: Annotated[int, Query(ge=1, le=1000, description="최대 조회 개수")] = 100,
    offset: Annotated[int, Query(ge=0, description="페이징 오프셋")] = 0
):
    """
    티켓 목록 조회 엔드포인트
    
    Args:
        service: 티켓 서비스
        theater_name: 극장명 필터 (선택)
        user_id: 사용자 ID 필터 (선택)
        movie_title: 영화명 필터 (선택)
        status: 상태 필터 (선택)
        limit: 최대 조회 개수
        offset: 페이징 오프셋
        
    Returns:
        티켓 목록 응답 데이터
        
    Raises:
        HTTPException: 400 (유효성 오류), 500 (서버 오류)
    """
    try:
        # 상태 필터 검증
        if status and status not in ["issued", "canceled"]:
            raise ValueError(f"Invalid status: {status}. Must be 'issued' or 'canceled'")

        return service.list_tickets(
            theater_name=theater_name,
            user_id=user_id,
            movie_title=movie_title,
            status=status,
            limit=limit,
            offset=offset
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

