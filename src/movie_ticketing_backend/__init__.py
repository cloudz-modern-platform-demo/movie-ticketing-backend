"""Movie Ticketing Backend package."""

import uvicorn


def main():
    """
    Main entry point for the application.
    Runs the FastAPI application using uvicorn.
    """
    uvicorn.run(
        "movie_ticketing_backend.app:create_app",
        host="0.0.0.0",
        port=9000,
        factory=True,
        reload=False,
    )


if __name__ == "__main__":
    main()
