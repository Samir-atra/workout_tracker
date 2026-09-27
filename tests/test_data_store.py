"""Unit Tests for Polars Tabular Data Store.

Tests DataFrame conversions, group_by aggregations, PR computation, and
Parquet export.
"""

from pathlib import Path
import polars as pl
import pytest
from app.models import ExerciseItem, ExerciseSet, WorkoutSession
from app.services.data_store import WorkoutDataStore


@pytest.fixture
def temp_store(tmp_path: Path) -> WorkoutDataStore:
    """Fixture providing a temporary isolated WorkoutDataStore."""
    data_file = tmp_path / "test_workouts.json"
    analytics_dir = tmp_path / "analytics"
    return WorkoutDataStore(data_file=data_file, analytics_dir=analytics_dir)


def test_add_session_and_volume(temp_store: WorkoutDataStore) -> None:
    """Tests session storage and automated volume calculation."""
    session = WorkoutSession(
        date="2026-09-27",
        title="Test Chest Session",
        duration_minutes=45,
        exercises=[
            ExerciseItem(
                name="Dumbbell Press",
                muscle_group="Chest",
                sets=[
                    ExerciseSet(set_number=1, reps=10, weight_kg=30.0, rpe=8.0),
                    ExerciseSet(set_number=2, reps=10, weight_kg=30.0, rpe=8.5),
                ],
            )
        ],
    )
    saved = temp_store.add_session(session)
    assert saved.id is not None
    # Volume: (10*30) + (10*30) = 600.0 kg
    assert saved.total_volume_kg == 600.0


def test_to_polars_dataframe(temp_store: WorkoutDataStore) -> None:
    """Tests conversion of sessions into a tabular Polars DataFrame."""
    df = temp_store.to_polars_dataframe()
    assert isinstance(df, pl.DataFrame)
    assert not df.is_empty()
    assert "muscle_group" in df.columns
    assert "set_volume" in df.columns
    assert "estimated_1rm" in df.columns


def test_summary_metrics(temp_store: WorkoutDataStore) -> None:
    """Tests Polars summary metric computation."""
    metrics = temp_store.get_summary_metrics()
    assert metrics["total_sessions"] > 0
    assert metrics["total_volume_kg"] > 0
    assert len(metrics["muscle_distribution"]) > 0
    assert len(metrics["personal_records"]) > 0


def test_delete_session(temp_store: WorkoutDataStore) -> None:
    """Tests session deletion."""
    sessions = temp_store.get_all_sessions()
    first_id = sessions[0].id
    assert first_id is not None

    deleted = temp_store.delete_session(first_id)
    assert deleted is True

    updated_sessions = temp_store.get_all_sessions()
    assert not any(s.id == first_id for s in updated_sessions)


def test_export_analytics(temp_store: WorkoutDataStore) -> None:
    """Tests Parquet export to analytics directory (Rule 4 & Rule 12)."""
    parquet_path = temp_store.export_analytics()
    assert parquet_path.exists()
    assert parquet_path.suffix == ".parquet"

    # Verify written parquet can be read by Polars
    read_df = pl.read_parquet(parquet_path)
    assert isinstance(read_df, pl.DataFrame)
    assert read_df.shape[0] > 0
