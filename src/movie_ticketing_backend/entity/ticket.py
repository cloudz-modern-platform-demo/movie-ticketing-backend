"""
Ticket ORM 엔티티
SQLAlchemy ORM 모델 정의
"""
import uuid
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from movie_ticketing_backend.db.session import Base


class Ticket(Base):
    """
    티켓 테이블 ORM 모델
    """
    __tablename__ = "tickets"

    # 기본 키 - UUID 문자열
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 티켓 정보
    theater_name = Column(String(100), nullable=False)
    user_id = Column(String(100), nullable=False)
    movie_title = Column(String(200), nullable=False)
    price_krw = Column(Integer, nullable=False)
    
    # 상태: "issued" | "canceled"
    status = Column(String(20), nullable=False, default="issued")
    
    # 메모 (선택)
    memo = Column(String, nullable=True)
    
    # 생성 시간
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 업데이트 시간
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Ticket(id={self.id}, theater={self.theater_name}, movie={self.movie_title}, status={self.status})>"

