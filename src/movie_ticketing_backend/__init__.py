"""
Movie Ticketing Backend
영화 티켓팅 백엔드 패키지
"""
import uvicorn


def main():
    """
    메인 진입점
    uvicorn을 factory 모드로 실행 (포트 9000)
    """
    uvicorn.run(
        "movie_ticketing_backend.app:create_app",
        factory=True,
        host="0.0.0.0",
        port=9000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()

