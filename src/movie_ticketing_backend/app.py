"""
FastAPI 애플리케이션 팩토리
앱 생성, 라우터 마운트, 시작 훅 설정
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from movie_ticketing_backend.db.session import init_db
from movie_ticketing_backend.route.ticket_route import router as ticket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 생명주기 관리
    시작 시 데이터베이스 초기화
    """
    # 시작 시 실행
    print("Initializing database...")
    init_db()
    print("Database initialized successfully")
    
    yield
    
    # 종료 시 실행 (필요한 경우)
    print("Shutting down...")


def create_app() -> FastAPI:
    """
    FastAPI 애플리케이션 생성 팩토리 함수
    
    Returns:
        FastAPI 애플리케이션 인스턴스
    """
    app = FastAPI(
        title="Movie Ticketing Backend API",
        description="영화 티켓 발권 및 환불 API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # 라우터 등록
    app.include_router(ticket_router)

    # 루트 엔드포인트
    @app.get("/", tags=["health"])
    async def root():
        """헬스 체크 엔드포인트"""
        return {
            "status": "ok",
            "message": "Movie Ticketing Backend API is running",
            "version": "0.1.0"
        }

    return app

