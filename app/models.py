"""Data Models for Workout Tracker Application.

Defines Pydantic schemas for workout tracking, user parameters, and CrewAI
agent request and response contracts.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ExerciseSet(BaseModel):
    """Represents an individual set performed during an exercise."""

    set_number: int = Field(..., description="Sequential number of the set.")
    reps: int = Field(..., ge=1, description="Number of repetitions completed.")
    weight_kg: float = Field(
        ..., ge=0.0, description="Resistance weight in kilograms (0 for bodyweight)."
    )
    rpe: Optional[float] = Field(
        default=None,
        ge=1.0,
        le=10.0,
        description="Rating of Perceived Exertion (1-10 scale).",
    )


class ExerciseItem(BaseModel):
    """Represents a specific exercise within a workout session."""

    name: str = Field(..., description="Name of the exercise (e.g. Barbell Squat).")
    muscle_group: str = Field(
        ...,
        description="Primary muscle group targeted (e.g. Legs, Chest, Back, Shoulders, Arms, Core).",
    )
    sets: List[ExerciseSet] = Field(
        default_factory=list, description="List of sets completed."
    )
    notes: Optional[str] = Field(
        default="", description="Optional technique notes or sensations."
    )


class WorkoutSession(BaseModel):
    """Represents a full workout session log."""

    id: Optional[str] = Field(
        default=None, description="Unique identifier for the session."
    )
    date: str = Field(..., description="Date of the workout in YYYY-MM-DD format.")
    title: str = Field(..., description="Title or theme of the session (e.g. Leg Hypertrophy).")
    duration_minutes: int = Field(
        default=60, ge=1, description="Total duration of workout in minutes."
    )
    exercises: List[ExerciseItem] = Field(
        default_factory=list, description="List of exercises performed."
    )
    notes: Optional[str] = Field(
        default="", description="General session notes or fatigue rating."
    )
    total_volume_kg: Optional[float] = Field(
        default=0.0, description="Computed total volume load in kg."
    )


class WorkoutSuggestionRequest(BaseModel):
    """Parameters to guide CrewAI in generating new workout routines."""

    goal: str = Field(
        default="Hypertrophy",
        description="Primary training goal (Hypertrophy, Strength, Endurance, Fat Loss, General Fitness).",
    )
    target_muscle_groups: List[str] = Field(
        default_factory=lambda: ["Chest", "Triceps"],
        description="Muscle groups to emphasize in the suggested workout.",
    )
    fitness_level: str = Field(
        default="Intermediate",
        description="Current experience level (Beginner, Intermediate, Advanced).",
    )
    available_equipment: str = Field(
        default="Full Gym",
        description="Available gear (Full Gym, Barbell & Dumbbells, Dumbbells Only, Bodyweight Only).",
    )
    duration_minutes: int = Field(
        default=60,
        ge=15,
        le=180,
        description="Target workout duration in minutes.",
    )
    include_recent_history: bool = Field(
        default=True,
        description="Whether to incorporate recent workout logs to ensure progressive overload.",
    )


class NutritionSuggestionRequest(BaseModel):
    """Parameters to guide CrewAI in recommending meals and workout supplements."""

    goal: str = Field(
        default="Muscle Gain",
        description="Nutritional goal (Muscle Gain, Fat Loss, Maintenance, Recomposition).",
    )
    dietary_preference: str = Field(
        default="Standard Omnivore",
        description="Dietary style (Standard Omnivore, High-Protein, Vegetarian, Vegan, Ketogenic, Pescatarian).",
    )
    body_weight_kg: float = Field(
        default=75.0, ge=30.0, le=250.0, description="Current body weight in kilograms."
    )
    daily_calorie_target: Optional[int] = Field(
        default=2600, ge=1000, le=6000, description="Target daily caloric intake."
    )
    allergies_intolerances: Optional[str] = Field(
        default="None",
        description="Known food allergies or intolerances (e.g. Lactose, Gluten, Nuts).",
    )
    training_frequency_per_week: int = Field(
        default=4, ge=1, le=7, description="Number of weekly resistance training sessions."
    )


class FullPlanRequest(BaseModel):
    """Combined request for simultaneous workout, meal, and supplement regimen generation."""

    workout_params: WorkoutSuggestionRequest
    nutrition_params: NutritionSuggestionRequest
