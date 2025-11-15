"""Ticket ORM entity definition."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from movie_ticketing_backend.db.session import Base


class Ticket(Base):
    """
    Ticket ORM entity representing a movie ticket.
    
    Attributes:
        id: Unique ticket identifier (UUID)
        theater_name: Name of the theater
        user_id: User identifier who purchased the ticket
        movie_title: Title of the movie
        price_krw: Price in Korean Won (integer)
        status: Ticket status ('issued' or 'canceled')
        issued_at: Timestamp when the ticket was issued
        canceled_at: Timestamp when the ticket was canceled (nullable)
        memo: Optional memo or notes
    """
    
    __tablename__ = "tickets"
    
    id = Column(String, primary_key=True, index=True)
    theater_name = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    movie_title = Column(String, nullable=False, index=True)
    price_krw = Column(Integer, nullable=False)
    status = Column(String, nullable=False, index=True)  # 'issued' or 'canceled'
    issued_at = Column(DateTime, nullable=False)
    canceled_at = Column(DateTime, nullable=True)
    memo = Column(String, nullable=True)
    
    def __repr__(self) -> str:
        return (
            f"<Ticket(id={self.id}, theater={self.theater_name}, "
            f"movie={self.movie_title}, status={self.status})>"
        )

