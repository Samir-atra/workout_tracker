"""Main FastAPI Web Application Module.

Provides RESTful API endpoints and serves the modern Single Page Application
for workout tracking, tabular analytics (Polars & JAX), and multi-agent AI
generation (CrewAI).
"""

from pathlib import Path
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.models import (
    FullPlanRequest,
    NutritionSuggestionRequest,
    WorkoutSession,
    WorkoutSuggestionRequest,
)
from app.services.crew_service import WorkoutCrewService
from app.services.data_store import WorkoutDataStore

# Initialize FastAPI application
app = FastAPI(
    title="PulseFit Workout & Nutrition Tracker",
    description="CrewAI powered workout tracking, generation, and nutrition/supplement advisor.",
    version="1.0.0",
)

# Enable CORS for local integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Mount static files and templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Initialize services
data_store = WorkoutDataStore()
crew_service = WorkoutCrewService()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> HTMLResponse:
    """Renders the main dashboard Single Page Application.

    Args:
        request: Incoming HTTP request object.

    Returns:
        Rendered HTML template.
    """
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/workouts", response_model=List[WorkoutSession])
async def list_workouts() -> List[WorkoutSession]:
    """Retrieves all logged workout sessions.

    Returns:
        List of WorkoutSession items sorted by date descending.
    """
    return data_store.get_all_sessions()


@app.post("/api/workouts", response_model=WorkoutSession)
async def create_workout(session: WorkoutSession) -> WorkoutSession:
    """Logs a new workout session and computes its volume using JAX.

    Args:
        session: Workout session details.

    Returns:
        Saved WorkoutSession instance with computed volume load and ID.
    """
    return data_store.add_session(session)


@app.delete("/api/workouts/{workout_id}")
async def delete_workout(workout_id: str) -> Dict[str, Any]:
    """Deletes a workout session by ID.

    Args:
        workout_id: UUID of session to delete.

    Returns:
        Status confirmation message.

    Raises:
        HTTPException: If workout_id was not found.
    """
    success = data_store.delete_session(workout_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workout session not found.")
    return {"status": "deleted", "workout_id": workout_id}


@app.get("/api/analytics")
async def get_analytics() -> Dict[str, Any]:
    """Computes summary metrics and personal records using Polars.

    Returns:
        Dictionary of high-level workout and volume analytics.
    """
    return data_store.get_summary_metrics()


@app.post("/api/analytics/export")
async def export_analytics() -> Dict[str, Any]:
    """Exports tabular dataset to parquet format in the analytics data directory.

    Satisfies Rule 4 and Rule 12.

    Returns:
        Confirmation and export file path.
    """
    export_path = data_store.export_analytics()
    return {
        "status": "success",
        "export_path": str(export_path),
        "directory": str(settings.ANALYTICS_DIR),
    }


@app.post("/api/crew/suggest-workout")
async def suggest_workout(request: WorkoutSuggestionRequest) -> Dict[str, Any]:
    """Invokes CrewAI Workout Architect Agent to create a personalized routine.

    Args:
        request: Workout goals, muscle groups, gear, and duration.

    Returns:
        Structured workout plan formatted in Markdown.
    """
    recent_summary = data_store.get_summary_metrics()
    return crew_service.suggest_workout(request, recent_summary=recent_summary)


@app.post("/api/crew/recommend-nutrition")
async def recommend_nutrition(
    request: NutritionSuggestionRequest,
) -> Dict[str, Any]:
    """Invokes CrewAI Nutritionist and Supplement Specialist Agents.

    Args:
        request: Dietary goals, preferences, body weight, and restrictions.

    Returns:
        Structured meal plan and evidence-graded supplement stack.
    """
    return crew_service.recommend_nutrition(request)


@app.post("/api/crew/full-plan")
async def generate_full_plan(request: FullPlanRequest) -> Dict[str, Any]:
    """Executes full CrewAI pipeline for both workout and nutrition/supplements.

    Args:
        request: Combined workout and nutrition criteria.

    Returns:
        Consolidated training and nutrition protocol.
    """
    recent_summary = data_store.get_summary_metrics()
    workout_res = crew_service.suggest_workout(
        request.workout_params, recent_summary=recent_summary
    )
    nutrition_res = crew_service.recommend_nutrition(request.nutrition_params)

    return {
        "workout": workout_res,
        "nutrition": nutrition_res,
    }
