"""Ticket repository for database operations."""

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from movie_ticketing_backend.entity.ticket import Ticket


class TicketRepository:
    """Repository for ticket CRUD operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create_ticket(
        self,
        ticket_id: str,
        theater_name: str,
        user_id: str,
        movie_title: str,
        price_krw: int,
        memo: Optional[str] = None,
    ) -> Ticket:
        """
        Create a new ticket in the database.
        
        Args:
            ticket_id: Unique ticket identifier
            theater_name: Name of the theater
            user_id: User identifier
            movie_title: Title of the movie
            price_krw: Price in Korean Won
            memo: Optional memo
            
        Returns:
            Created Ticket instance
        """
        ticket = Ticket(
            id=ticket_id,
            theater_name=theater_name,
            user_id=user_id,
            movie_title=movie_title,
            price_krw=price_krw,
            status="issued",
            issued_at=datetime.utcnow(),
            canceled_at=None,
            memo=memo,
        )
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
    
    def get_ticket_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """
        Retrieve a ticket by its ID.
        
        Args:
            ticket_id: Ticket identifier
            
        Returns:
            Ticket instance if found, None otherwise
        """
        return self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    def get_tickets_by_ids(self, ticket_ids: list[str]) -> list[Ticket]:
        """
        Retrieve multiple tickets by their IDs.
        
        Args:
            ticket_ids: List of ticket identifiers
            
        Returns:
            List of Ticket instances
        """
        return self.db.query(Ticket).filter(Ticket.id.in_(ticket_ids)).all()
    
    def list_tickets(
        self,
        theater_name: Optional[str] = None,
        user_id: Optional[str] = None,
        movie_title: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Ticket], int]:
        """
        List tickets with optional filters and pagination.
        
        Args:
            theater_name: Filter by theater name
            user_id: Filter by user ID
            movie_title: Filter by movie title
            status: Filter by ticket status
            limit: Maximum number of tickets to return
            offset: Number of tickets to skip
            
        Returns:
            Tuple of (list of tickets, total count)
        """
        query = self.db.query(Ticket)
        
        if theater_name:
            query = query.filter(Ticket.theater_name == theater_name)
        if user_id:
            query = query.filter(Ticket.user_id == user_id)
        if movie_title:
            query = query.filter(Ticket.movie_title == movie_title)
        if status:
            query = query.filter(Ticket.status == status)
        
        total = query.count()
        tickets = query.order_by(Ticket.issued_at.desc()).offset(offset).limit(limit).all()
        
        return tickets, total
    
    def cancel_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """
        Cancel a ticket by updating its status.
        
        Args:
            ticket_id: Ticket identifier
            
        Returns:
            Updated Ticket instance if found and updated, None otherwise
        """
        ticket = self.get_ticket_by_id(ticket_id)
        if ticket and ticket.status == "issued":
            ticket.status = "canceled"
            ticket.canceled_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(ticket)
            return ticket
        return None
    
    def is_ticket_canceled(self, ticket_id: str) -> bool:
        """
        Check if a ticket is already canceled.
        
        Args:
            ticket_id: Ticket identifier
            
        Returns:
            True if ticket exists and is canceled, False otherwise
        """
        ticket = self.get_ticket_by_id(ticket_id)
        return ticket is not None and ticket.status == "canceled"

