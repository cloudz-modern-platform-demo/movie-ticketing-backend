"""
티켓 리포지토리
데이터베이스 CRUD 작업 및 트랜잭션 헬퍼
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from movie_ticketing_backend.entity.ticket import Ticket


class TicketRepository:
    """티켓 리포지토리 클래스"""

    def __init__(self, db: Session):
        self.db = db

    def create_ticket(
        self,
        theater_name: str,
        user_id: str,
        movie_title: str,
        price_krw: int,
        memo: Optional[str] = None
    ) -> Ticket:
        """
        티켓 생성
        
        Args:
            theater_name: 극장명
            user_id: 사용자 ID
            movie_title: 영화명
            price_krw: 가격 (KRW)
            memo: 메모 (선택)
            
        Returns:
            생성된 티켓 객체
        """
        ticket = Ticket(
            theater_name=theater_name,
            user_id=user_id,
            movie_title=movie_title,
            price_krw=price_krw,
            status="issued",
            memo=memo
        )
        self.db.add(ticket)
        self.db.flush()  # ID를 생성하기 위해 flush
        self.db.refresh(ticket)
        return ticket

    def get_ticket_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """
        ID로 티켓 조회
        
        Args:
            ticket_id: 티켓 ID
            
        Returns:
            티켓 객체 또는 None
        """
        return self.db.query(Ticket).filter(Ticket.id == ticket_id).first()

    def get_tickets_by_ids(self, ticket_ids: List[str]) -> List[Ticket]:
        """
        여러 ID로 티켓 조회
        
        Args:
            ticket_ids: 티켓 ID 목록
            
        Returns:
            티켓 객체 목록
        """
        return self.db.query(Ticket).filter(Ticket.id.in_(ticket_ids)).all()

    def cancel_ticket(self, ticket: Ticket) -> Ticket:
        """
        티켓 취소
        
        Args:
            ticket: 취소할 티켓 객체
            
        Returns:
            취소된 티켓 객체
        """
        ticket.status = "canceled"
        self.db.add(ticket)
        self.db.flush()
        self.db.refresh(ticket)
        return ticket

    def list_tickets(
        self,
        theater_name: Optional[str] = None,
        user_id: Optional[str] = None,
        movie_title: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Ticket], int]:
        """
        티켓 목록 조회 (필터링 및 페이징)
        
        Args:
            theater_name: 극장명 필터 (선택)
            user_id: 사용자 ID 필터 (선택)
            movie_title: 영화명 필터 (선택)
            status: 상태 필터 (선택)
            limit: 최대 조회 개수
            offset: 페이징 오프셋
            
        Returns:
            (티켓 목록, 전체 개수) 튜플
        """
        query = self.db.query(Ticket)

        # 필터 적용
        if theater_name:
            query = query.filter(Ticket.theater_name == theater_name)
        if user_id:
            query = query.filter(Ticket.user_id == user_id)
        if movie_title:
            query = query.filter(Ticket.movie_title == movie_title)
        if status:
            query = query.filter(Ticket.status == status)

        # 전체 개수 조회
        total = query.count()

        # 페이징 적용 및 조회
        tickets = query.order_by(Ticket.created_at.desc()).limit(limit).offset(offset).all()

        return tickets, total

    def commit(self):
        """트랜잭션 커밋"""
        self.db.commit()

    def rollback(self):
        """트랜잭션 롤백"""
        self.db.rollback()

