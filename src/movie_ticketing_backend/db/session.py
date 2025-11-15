"""
데이터베이스 세션 및 엔진 설정
SQLAlchemy 엔진, 세션 팩토리, Base 클래스 제공
"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# 프로젝트 루트 경로 찾기
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "app.db"

# data 디렉토리가 없으면 생성
DATA_DIR.mkdir(exist_ok=True)

# SQLite 데이터베이스 URL
DATABASE_URL = f"sqlite:///{DB_PATH}"

# SQLAlchemy 엔진 생성
# check_same_thread=False: FastAPI에서 여러 스레드에서 접근 가능하도록 설정
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # SQL 로그 출력 비활성화 (필요시 True로 변경)
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 (모든 ORM 모델의 부모 클래스)
Base = declarative_base()


def get_db() -> Session:
    """
    데이터베이스 세션을 생성하고 반환하는 의존성 함수
    FastAPI 라우트에서 Depends로 사용
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    데이터베이스 초기화 - 모든 테이블 생성
    애플리케이션 시작 시 호출
    """
    Base.metadata.create_all(bind=engine)

