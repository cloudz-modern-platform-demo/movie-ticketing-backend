"""티켓 ORM 엔티티"""
import uuid
from sqlalchemy import Column, String, Integer
from movie_ticketing_backend.db.session import Base


class Ticket(Base):
    """티켓 테이블 ORM 모델"""
    
    __tablename__ = "tickets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    theater_name = Column(String(100), nullable=False)
    user_id = Column(String(100), nullable=False)
    movie_title = Column(String(200), nullable=False)
    price_krw = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="issued")  # issued | canceled
    memo = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, theater={self.theater_name}, movie={self.movie_title}, status={self.status})>"

