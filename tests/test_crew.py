"""Unit Tests for CrewAI Multi-Agent Service.

Tests agent instantiation, fallback response generation, and workflow contracts.
"""

from app.models import NutritionSuggestionRequest, WorkoutSuggestionRequest
from app.services.crew_service import WorkoutCrewService


def test_crew_service_initialization() -> None:
    """Tests service instantiation with settings."""
    service = WorkoutCrewService()
    assert service.model_name is not None
    assert service.max_tokens > 0


def test_workout_plan_fallback() -> None:
    """Tests that workout generation produces structured content even on fallback."""
    service = WorkoutCrewService()
    req = WorkoutSuggestionRequest(
        goal="Hypertrophy",
        target_muscle_groups=["Chest", "Triceps"],
        fitness_level="Intermediate",
        available_equipment="Full Gym",
        duration_minutes=60,
    )
    res = service._fallback_workout_plan(req)
    assert res["status"] == "success"
    assert "Chest" in res["plan_markdown"]
    assert "Warm-Up" in res["plan_markdown"]
    assert "Compound Lift" in res["plan_markdown"]


def test_nutrition_plan_fallback() -> None:
    """Tests that nutrition generation produces structured meal and supplement content."""
    service = WorkoutCrewService()
    req = NutritionSuggestionRequest(
        goal="Muscle Gain",
        dietary_preference="Standard Omnivore",
        body_weight_kg=80.0,
        daily_calorie_target=2800,
        allergies_intolerances="None",
        training_frequency_per_week=4,
    )
    res = service._fallback_nutrition_plan(req)
    assert res["status"] == "success"
    assert "Protein:" in res["plan_markdown"]
    assert "Creatine" in res["plan_markdown"]
    assert "Meal Schedule" in res["plan_markdown"]
