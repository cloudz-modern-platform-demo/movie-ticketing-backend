"""Movie Ticketing Backend - 메인 진입점"""
import uvicorn


def main():
    """메인 진입점 - uvicorn을 factory 모드로 실행"""
    uvicorn.run(
        "movie_ticketing_backend.app:create_app",
        host="0.0.0.0",
        port=9000,
        factory=True,
        reload=False,
    )


if __name__ == "__main__":
    main()
