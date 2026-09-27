"""Application Entrypoint Script.

Starts the Uvicorn ASGI server to host the PulseFit FastAPI application.
"""

import uvicorn
from app.config import settings


def main() -> None:
    """Runs the PulseFit server with hot reload."""
    print("=====================================================")
    print("  ⚡ PulseFit Workout & Nutrition Tracker Starting  ")
    print(f"  Host: {settings.HOST} | Port: {settings.PORT}")
    print(f"  CrewAI Model: {settings.CREWAI_MODEL}")
    print("=====================================================")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )


if __name__ == "__main__":
    main()
