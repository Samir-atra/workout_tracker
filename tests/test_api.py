"""Unit Tests for FastAPI Endpoints.

Tests routing, CRUD operations for workouts, analytics retrieval, and AI endpoints.
"""

from fastapi.testclient import TestClient
import pytest
from app.main import app

client = TestClient(app)


def test_read_root() -> None:
    """Tests GET / returns HTML application."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "PulseFit" in response.text


def test_get_workouts() -> None:
    """Tests GET /api/workouts returns a list of sessions."""
    response = client.get("/api/workouts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_and_delete_workout() -> None:
    """Tests POST /api/workouts and subsequent DELETE /api/workouts/{id}."""
    payload = {
        "date": "2026-09-27",
        "title": "API Integration Test Session",
        "duration_minutes": 50,
        "notes": "FastAPI automated test.",
        "exercises": [
            {
                "name": "Overhead Press",
                "muscle_group": "Shoulders",
                "sets": [
                    {"set_number": 1, "reps": 10, "weight_kg": 40.0, "rpe": 8.0},
                    {"set_number": 2, "reps": 8, "weight_kg": 45.0, "rpe": 8.5},
                ],
            }
        ],
    }

    # Create
    create_res = client.post("/api/workouts", json=payload)
    assert create_res.status_code == 200
    session_data = create_res.json()
    session_id = session_data["id"]
    # (10*40) + (8*45) = 400 + 360 = 760.0 kg
    assert session_data["total_volume_kg"] == 760.0

    # Delete
    del_res = client.delete(f"/api/workouts/{session_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"


def test_get_analytics() -> None:
    """Tests GET /api/analytics returns Polars computed metrics."""
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_sessions" in data
    assert "total_volume_kg" in data
    assert "muscle_distribution" in data
    assert "personal_records" in data


def test_export_analytics() -> None:
    """Tests POST /api/analytics/export writes to analytics directory."""
    response = client.post("/api/analytics/export")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "workout_tabular_data.parquet" in data["export_path"]
