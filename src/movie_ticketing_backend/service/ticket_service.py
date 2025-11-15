"""
티켓 서비스
비즈니스 로직: 발권, 환불, 조회, 멱등성 처리
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from movie_ticketing_backend.db.repository import TicketRepository
from movie_ticketing_backend.entity.ticket import Ticket
from movie_ticketing_backend.scheme.ticket import (
    IssueTicketRequest,
    IssueTicketResponse,
    IssueTicketSummary,
    RefundTicketRequest,
    RefundTicketResponse,
    TicketResponse,
    TicketListResponse
)
from movie_ticketing_backend.util.idempotency import IdempotencyCache


class TicketService:
    """티켓 서비스 클래스"""

    def __init__(self, db: Session, idempotency_cache: IdempotencyCache):
        self.repository = TicketRepository(db)
        self.idempotency_cache = idempotency_cache

    def issue_tickets(
        self,
        request: IssueTicketRequest,
        idempotency_key: Optional[str] = None
    ) -> Tuple[IssueTicketResponse, int]:
        """
        티켓 발권
        
        Args:
            request: 발권 요청 데이터
            idempotency_key: 멱등성 키 (선택)
            
        Returns:
            (응답 데이터, 상태 코드) 튜플
            
        Raises:
            ValueError: 멱등성 충돌 시
        """
        # 멱등성 체크 (키가 제공된 경우)
        if idempotency_key:
            is_duplicate, conflict_type, cached_response = \
                self.idempotency_cache.check_and_store(
                    idempotency_key,
                    request.model_dump()
                )

            if is_duplicate:
                if conflict_type == "match" and cached_response:
                    # 동일한 요청 - 캐시된 응답 반환
                    return cached_response, 200
                elif conflict_type == "conflict":
                    # 다른 요청인데 같은 키 - 충돌
                    raise ValueError("Idempotency key conflict: different request body")

        try:
            # 수량만큼 티켓 생성
            created_tickets = []
            for _ in range(request.quantity):
                ticket = self.repository.create_ticket(
                    theater_name=request.theater_name,
                    user_id=request.user_id,
                    movie_title=request.movie_title,
                    price_krw=request.price_krw,
                    memo=request.memo
                )
                created_tickets.append(ticket)

            # 커밋
            self.repository.commit()

            # 응답 생성
            response = IssueTicketResponse(
                ticket_ids=[ticket.id for ticket in created_tickets],
                count=len(created_tickets),
                summary=IssueTicketSummary(
                    theater_name=request.theater_name,
                    movie_title=request.movie_title,
                    price_krw=request.price_krw
                )
            )

            # 멱등성 캐시에 응답 저장
            if idempotency_key:
                self.idempotency_cache.update_response(idempotency_key, response)

            return response, 201

        except Exception as e:
            # 롤백
            self.repository.rollback()
            raise e

    def refund_tickets(self, request: RefundTicketRequest) -> RefundTicketResponse:
        """
        티켓 환불
        
        Args:
            request: 환불 요청 데이터
            
        Returns:
            환불 응답 데이터
        """
        try:
            # 티켓 조회
            tickets = self.repository.get_tickets_by_ids(request.ticket_ids)
            found_ticket_ids = {ticket.id for ticket in tickets}

            refunded = []
            already_canceled = []
            not_found = []

            # 각 티켓 상태 확인 및 처리
            for ticket_id in request.ticket_ids:
                if ticket_id not in found_ticket_ids:
                    # 존재하지 않는 티켓
                    not_found.append(ticket_id)
                else:
                    # 티켓 찾기
                    ticket = next(t for t in tickets if t.id == ticket_id)
                    
                    if ticket.status == "canceled":
                        # 이미 취소된 티켓
                        already_canceled.append(ticket_id)
                    elif ticket.status == "issued":
                        # 환불 처리
                        self.repository.cancel_ticket(ticket)
                        refunded.append(ticket_id)

            # 커밋
            self.repository.commit()

            return RefundTicketResponse(
                refunded=refunded,
                already_canceled=already_canceled,
                not_found=not_found
            )

        except Exception as e:
            # 롤백
            self.repository.rollback()
            raise e

    def get_ticket(self, ticket_id: str) -> Optional[TicketResponse]:
        """
        티켓 단일 조회
        
        Args:
            ticket_id: 티켓 ID
            
        Returns:
            티켓 응답 데이터 또는 None
        """
        ticket = self.repository.get_ticket_by_id(ticket_id)
        if ticket:
            return TicketResponse.model_validate(ticket)
        return None

    def list_tickets(
        self,
        theater_name: Optional[str] = None,
        user_id: Optional[str] = None,
        movie_title: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> TicketListResponse:
        """
        티켓 목록 조회
        
        Args:
            theater_name: 극장명 필터 (선택)
            user_id: 사용자 ID 필터 (선택)
            movie_title: 영화명 필터 (선택)
            status: 상태 필터 (선택)
            limit: 최대 조회 개수
            offset: 페이징 오프셋
            
        Returns:
            티켓 목록 응답 데이터
        """
        tickets, total = self.repository.list_tickets(
            theater_name=theater_name,
            user_id=user_id,
            movie_title=movie_title,
            status=status,
            limit=limit,
            offset=offset
        )

        return TicketListResponse(
            tickets=[TicketResponse.model_validate(ticket) for ticket in tickets],
            total=total,
            limit=limit,
            offset=offset
        )

