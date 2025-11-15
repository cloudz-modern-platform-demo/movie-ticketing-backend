"""FastAPI 애플리케이션 팩토리"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from movie_ticketing_backend.db.session import init_db
from movie_ticketing_backend.route.ticket_route import router as ticket_router


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 생성"""
    app = FastAPI(
        title="Movie Ticketing Backend",
        description="영화 티켓 발권 및 환불 API 백엔드 서비스",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    # CORS 미들웨어 추가
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 라우터 등록
    app.include_router(ticket_router)
    
    # 시작 이벤트
    @app.on_event("startup")
    async def startup_event():
        """애플리케이션 시작 시 데이터베이스 초기화"""
        init_db()
    
    # 헬스 체크 엔드포인트
    @app.get("/", tags=["health"])
    async def health_check():
        """헬스 체크"""
        return {"status": "ok", "message": "Movie Ticketing Backend is running"}
    
    return app
