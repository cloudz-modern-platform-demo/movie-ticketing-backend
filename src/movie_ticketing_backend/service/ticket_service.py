"""티켓 비즈니스 로직 서비스"""
import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from movie_ticketing_backend.db.repository import TicketRepository
from movie_ticketing_backend.entity.ticket import Ticket
from movie_ticketing_backend.scheme.ticket import (
    TicketIssueRequest,
    TicketIssueResponse,
    TicketIssueSummary,
    TicketRefundRequest,
    TicketRefundResponse,
    TicketResponse,
    TicketListResponse,
)


class TicketService:
    """티켓 비즈니스 로직을 담당하는 서비스"""
    
    def __init__(self, db: Session):
        self.repository = TicketRepository(db)
    
    def issue_tickets(self, request: TicketIssueRequest) -> TicketIssueResponse:
        """
        티켓 발권
        
        Args:
            request: 발권 요청
            
        Returns:
            발권 응답
        """
        # 티켓 엔티티 생성
        tickets = []
        for _ in range(request.quantity):
            ticket = Ticket(
                id=str(uuid.uuid4()),
                theater_name=request.theater_name,
                user_id=request.user_id,
                movie_title=request.movie_title,
                price_krw=request.price_krw,
                status="issued",
                memo=request.memo,
            )
            tickets.append(ticket)
        
        # 데이터베이스에 저장
        created_tickets = self.repository.create_many(tickets)
        
        # 응답 생성
        return TicketIssueResponse(
            ticket_ids=[ticket.id for ticket in created_tickets],
            count=len(created_tickets),
            summary=TicketIssueSummary(
                theater_name=request.theater_name,
                movie_title=request.movie_title,
                price_krw=request.price_krw,
            ),
        )
    
    def refund_tickets(self, request: TicketRefundRequest) -> TicketRefundResponse:
        """
        티켓 환불
        
        Args:
            request: 환불 요청
            
        Returns:
            환불 응답
        """
        # 티켓 조회
        tickets = self.repository.get_by_ids(request.ticket_ids)
        ticket_map = {ticket.id: ticket for ticket in tickets}
        
        refunded = []
        already_canceled = []
        not_found = []
        
        # 각 티켓 처리
        for ticket_id in request.ticket_ids:
            if ticket_id not in ticket_map:
                # 존재하지 않는 티켓
                not_found.append(ticket_id)
            else:
                ticket = ticket_map[ticket_id]
                if ticket.status == "canceled":
                    # 이미 취소된 티켓
                    already_canceled.append(ticket_id)
                elif ticket.status == "issued":
                    # 환불 가능한 티켓
                    ticket.status = "canceled"
                    refunded.append(ticket_id)
        
        # 환불된 티켓 업데이트
        if refunded:
            self.repository.update_status_many(refunded, "canceled")
        
        return TicketRefundResponse(
            refunded=refunded,
            already_canceled=already_canceled,
            not_found=not_found,
        )
    
    def get_ticket(self, ticket_id: str) -> Optional[TicketResponse]:
        """
        티켓 단일 조회
        
        Args:
            ticket_id: 티켓 ID
            
        Returns:
            티켓 응답 또는 None
        """
        ticket = self.repository.get_by_id(ticket_id)
        if ticket is None:
            return None
        
        return TicketResponse.model_validate(ticket)
    
    def get_ticket_list(
        self,
        theater_name: Optional[str] = None,
        user_id: Optional[str] = None,
        movie_title: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> TicketListResponse:
        """
        티켓 목록 조회
        
        Args:
            theater_name: 극장명 필터
            user_id: 사용자 ID 필터
            movie_title: 영화명 필터
            status: 상태 필터
            limit: 페이지 크기
            offset: 페이지 오프셋
            
        Returns:
            티켓 목록 응답
        """
        tickets, total = self.repository.get_list(
            theater_name=theater_name,
            user_id=user_id,
            movie_title=movie_title,
            status=status,
            limit=limit,
            offset=offset,
        )
        
        return TicketListResponse(
            tickets=[TicketResponse.model_validate(ticket) for ticket in tickets],
            total=total,
            limit=limit,
            offset=offset,
        )
