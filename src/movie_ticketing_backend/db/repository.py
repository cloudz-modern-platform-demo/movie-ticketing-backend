"""티켓 리포지토리"""
from typing import List, Optional
from sqlalchemy.orm import Session
from movie_ticketing_backend.entity.ticket import Ticket


class TicketRepository:
    """티켓 CRUD 작업을 담당하는 리포지토리"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, ticket: Ticket) -> Ticket:
        """티켓 생성"""
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
    
    def create_many(self, tickets: List[Ticket]) -> List[Ticket]:
        """여러 티켓 생성"""
        self.db.add_all(tickets)
        self.db.commit()
        for ticket in tickets:
            self.db.refresh(ticket)
        return tickets
    
    def get_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """ID로 티켓 조회"""
        return self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    def get_by_ids(self, ticket_ids: List[str]) -> List[Ticket]:
        """여러 ID로 티켓 조회"""
        return self.db.query(Ticket).filter(Ticket.id.in_(ticket_ids)).all()
    
    def get_list(
        self,
        theater_name: Optional[str] = None,
        user_id: Optional[str] = None,
        movie_title: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[Ticket], int]:
        """티켓 목록 조회 (필터링 및 페이징)"""
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
        
        # 페이징 적용
        tickets = query.limit(limit).offset(offset).all()
        
        return tickets, total
    
    def update(self, ticket: Ticket) -> Ticket:
        """티켓 업데이트"""
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
    
    def update_status(self, ticket_id: str, status: str) -> Optional[Ticket]:
        """티켓 상태 업데이트"""
        ticket = self.get_by_id(ticket_id)
        if ticket:
            ticket.status = status
            self.db.commit()
            self.db.refresh(ticket)
        return ticket
    
    def update_status_many(self, ticket_ids: List[str], status: str) -> List[Ticket]:
        """여러 티켓 상태 업데이트"""
        tickets = self.get_by_ids(ticket_ids)
        for ticket in tickets:
            ticket.status = status
        self.db.commit()
        for ticket in tickets:
            self.db.refresh(ticket)
        return tickets
