"""Tabular Data Storage and Analytics Service.

Implements all tabular data processing, aggregation, filtering, and analytics
persistence using the Polars library in accordance with project rules.
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import polars as pl

from app.config import settings
from app.models import ExerciseItem, ExerciseSet, WorkoutSession
from app.services.math_engine import calculate_1rm_epley, calculate_volume_load


class WorkoutDataStore:
    """Manages workout data persistence and tabular analytics using Polars."""

    def __init__(self, data_file: Optional[Path] = None, analytics_dir: Optional[Path] = None) -> None:
        """Initializes the data store.

        Args:
            data_file: Path to the JSON persistence file for workouts.
            analytics_dir: Directory where analytics exports will be written.
        """
        self.data_file = data_file or settings.DATA_PATH
        self.analytics_dir = analytics_dir or settings.ANALYTICS_DIR
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_storage_initialized()

    def _ensure_storage_initialized(self) -> None:
        """Initializes storage file with starter records if non-existent."""
        if not self.data_file.exists():
            seed_data = self._generate_sample_workouts()
            self._save_raw_sessions(seed_data)

    def _generate_sample_workouts(self) -> List[Dict[str, Any]]:
        """Generates realistic sample workouts for initial visualization.

        Returns:
            List of dictionary workout session representations.
        """
        today = datetime.now()
        dates = [
            (today - timedelta(days=6)).strftime("%Y-%m-%d"),
            (today - timedelta(days=4)).strftime("%Y-%m-%d"),
            (today - timedelta(days=2)).strftime("%Y-%m-%d"),
            (today - timedelta(days=1)).strftime("%Y-%m-%d"),
        ]

        sample_sessions = [
            {
                "id": str(uuid.uuid4()),
                "date": dates[0],
                "title": "Push Day - Chest & Triceps",
                "duration_minutes": 55,
                "notes": "Solid session, felt strong on bench press.",
                "total_volume_kg": 4320.0,
                "exercises": [
                    {
                        "name": "Barbell Bench Press",
                        "muscle_group": "Chest",
                        "notes": "Focused on arch and controlled descent.",
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight_kg": 60.0, "rpe": 7.0},
                            {"set_number": 2, "reps": 8, "weight_kg": 70.0, "rpe": 8.0},
                            {"set_number": 3, "reps": 6, "weight_kg": 80.0, "rpe": 8.5},
                        ],
                    },
                    {
                        "name": "Incline Dumbbell Press",
                        "muscle_group": "Chest",
                        "notes": "Deep stretch at bottom.",
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight_kg": 24.0, "rpe": 7.5},
                            {"set_number": 2, "reps": 10, "weight_kg": 24.0, "rpe": 8.0},
                            {"set_number": 3, "reps": 8, "weight_kg": 26.0, "rpe": 9.0},
                        ],
                    },
                    {
                        "name": "Triceps Rope Pushdown",
                        "muscle_group": "Arms",
                        "notes": "Peak contraction held for 1s.",
                        "sets": [
                            {"set_number": 1, "reps": 12, "weight_kg": 25.0, "rpe": 7.0},
                            {"set_number": 2, "reps": 12, "weight_kg": 25.0, "rpe": 8.0},
                            {"set_number": 3, "reps": 10, "weight_kg": 30.0, "rpe": 8.5},
                        ],
                    },
                ],
            },
            {
                "id": str(uuid.uuid4()),
                "date": dates[1],
                "title": "Pull Day - Back & Biceps",
                "duration_minutes": 60,
                "notes": "Lat activation felt great.",
                "total_volume_kg": 4860.0,
                "exercises": [
                    {
                        "name": "Barbell Deadlift",
                        "muscle_group": "Back",
                        "notes": "Conventional stance, tight core.",
                        "sets": [
                            {"set_number": 1, "reps": 8, "weight_kg": 100.0, "rpe": 7.0},
                            {"set_number": 2, "reps": 6, "weight_kg": 120.0, "rpe": 8.0},
                            {"set_number": 3, "reps": 5, "weight_kg": 130.0, "rpe": 8.5},
                        ],
                    },
                    {
                        "name": "Lat Pulldown",
                        "muscle_group": "Back",
                        "notes": "Wide grip, smooth tempo.",
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight_kg": 55.0, "rpe": 7.5},
                            {"set_number": 2, "reps": 10, "weight_kg": 60.0, "rpe": 8.0},
                            {"set_number": 3, "reps": 8, "weight_kg": 65.0, "rpe": 8.5},
                        ],
                    },
                    {
                        "name": "Incline Dumbbell Curl",
                        "muscle_group": "Arms",
                        "notes": "Full bicep stretch.",
                        "sets": [
                            {"set_number": 1, "reps": 12, "weight_kg": 14.0, "rpe": 7.5},
                            {"set_number": 2, "reps": 10, "weight_kg": 14.0, "rpe": 8.0},
                            {"set_number": 3, "reps": 10, "weight_kg": 14.0, "rpe": 9.0},
                        ],
                    },
                ],
            },
            {
                "id": str(uuid.uuid4()),
                "date": dates[2],
                "title": "Leg Day - Quads & Hamstrings",
                "duration_minutes": 65,
                "notes": "High intensity leg training.",
                "total_volume_kg": 5780.0,
                "exercises": [
                    {
                        "name": "Barbell Back Squat",
                        "muscle_group": "Legs",
                        "notes": "Below parallel depth.",
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight_kg": 80.0, "rpe": 7.0},
                            {"set_number": 2, "reps": 8, "weight_kg": 95.0, "rpe": 8.0},
                            {"set_number": 3, "reps": 6, "weight_kg": 105.0, "rpe": 8.5},
                        ],
                    },
                    {
                        "name": "Romanian Deadlift",
                        "muscle_group": "Legs",
                        "notes": "Hamstring tension emphasis.",
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight_kg": 70.0, "rpe": 7.5},
                            {"set_number": 2, "reps": 10, "weight_kg": 80.0, "rpe": 8.0},
                            {"set_number": 3, "reps": 8, "weight_kg": 85.0, "rpe": 8.5},
                        ],
                    },
                    {
                        "name": "Standing Calf Raise",
                        "muscle_group": "Legs",
                        "notes": "Pause at top.",
                        "sets": [
                            {"set_number": 1, "reps": 15, "weight_kg": 40.0, "rpe": 7.5},
                            {"set_number": 2, "reps": 15, "weight_kg": 45.0, "rpe": 8.0},
                        ],
                    },
                ],
            },
            {
                "id": str(uuid.uuid4()),
                "date": dates[3],
                "title": "Upper Body Hypertrophy",
                "duration_minutes": 50,
                "notes": "High pump session.",
                "total_volume_kg": 3950.0,
                "exercises": [
                    {
                        "name": "Overhead Shoulder Press",
                        "muscle_group": "Shoulders",
                        "notes": "Standing strict press.",
                        "sets": [
                            {"set_number": 1, "reps": 8, "weight_kg": 45.0, "rpe": 7.5},
                            {"set_number": 2, "reps": 8, "weight_kg": 50.0, "rpe": 8.0},
                            {"set_number": 3, "reps": 6, "weight_kg": 52.5, "rpe": 8.5},
                        ],
                    },
                    {
                        "name": "Cable Lateral Raise",
                        "muscle_group": "Shoulders",
                        "notes": "Strict form, lateral delt isolation.",
                        "sets": [
                            {"set_number": 1, "reps": 15, "weight_kg": 10.0, "rpe": 8.0},
                            {"set_number": 2, "reps": 12, "weight_kg": 12.0, "rpe": 8.5},
                            {"set_number": 3, "reps": 12, "weight_kg": 12.0, "rpe": 9.0},
                        ],
                    },
                    {
                        "name": "Hanging Leg Raise",
                        "muscle_group": "Core",
                        "notes": "Full core engagement.",
                        "sets": [
                            {"set_number": 1, "reps": 12, "weight_kg": 0.0, "rpe": 7.5},
                            {"set_number": 2, "reps": 12, "weight_kg": 0.0, "rpe": 8.0},
                            {"set_number": 3, "reps": 10, "weight_kg": 0.0, "rpe": 8.5},
                        ],
                    },
                ],
            },
        ]
        return sample_sessions

    def _load_raw_sessions(self) -> List[Dict[str, Any]]:
        """Reads raw session list from storage file.

        Returns:
            List of session dictionaries.
        """
        if not self.data_file.exists():
            return []
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def _save_raw_sessions(self, sessions: List[Dict[str, Any]]) -> None:
        """Writes raw session list to storage file.

        Args:
            sessions: List of workout dictionaries.
        """
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(sessions, f, indent=2)

    def get_all_sessions(self) -> List[WorkoutSession]:
        """Retrieves all workout sessions as strongly-typed models.

        Returns:
            List of WorkoutSession instances sorted by date descending.
        """
        raw = self._load_raw_sessions()
        sessions = [WorkoutSession(**item) for item in raw]
        sessions.sort(key=lambda s: s.date, reverse=True)
        return sessions

    def add_session(self, session: WorkoutSession) -> WorkoutSession:
        """Appends a new workout session and computes its total volume load.

        Args:
            session: WorkoutSession instance to store.

        Returns:
            The stored WorkoutSession with ID and computed volume.
        """
        if not session.id:
            session.id = str(uuid.uuid4())

        # Compute volume load using JAX math engine
        all_weights: List[float] = []
        all_reps: List[int] = []
        for ex in session.exercises:
            for s in ex.sets:
                all_weights.append(s.weight_kg)
                all_reps.append(s.reps)

        session.total_volume_kg = calculate_volume_load(all_weights, all_reps)

        sessions = self._load_raw_sessions()
        sessions.append(session.model_dump())
        self._save_raw_sessions(sessions)

        # Trigger tabular analytics export (Rule 4 & 12)
        self.export_analytics()
        return session

    def delete_session(self, session_id: str) -> bool:
        """Deletes a workout session by ID.

        Args:
            session_id: UUID string of the session to remove.

        Returns:
            True if session existed and was removed, False otherwise.
        """
        sessions = self._load_raw_sessions()
        initial_len = len(sessions)
        updated = [s for s in sessions if s.get("id") != session_id]
        if len(updated) < initial_len:
            self._save_raw_sessions(updated)
            self.export_analytics()
            return True
        return False

    def to_polars_dataframe(self) -> pl.DataFrame:
        """Converts raw workout sessions into a tabular Polars DataFrame.

        Returns:
            Polars DataFrame with flattened sets, exercises, and sessions.
        """
        sessions = self._load_raw_sessions()
        records: List[Dict[str, Any]] = []

        for sess in sessions:
            sess_id = sess.get("id", "")
            sess_date = sess.get("date", "")
            sess_title = sess.get("title", "")
            sess_duration = sess.get("duration_minutes", 60)

            exercises = sess.get("exercises", [])
            for ex in exercises:
                ex_name = ex.get("name", "Unknown")
                muscle_group = ex.get("muscle_group", "General")
                sets = ex.get("sets", [])

                for s in sets:
                    reps = int(s.get("reps", 0))
                    weight = float(s.get("weight_kg", 0.0))
                    rpe = float(s.get("rpe", 0.0)) if s.get("rpe") is not None else 7.0
                    one_rm = calculate_1rm_epley(weight, reps)
                    vol = calculate_volume_load([weight], [reps])

                    records.append(
                        {
                            "session_id": sess_id,
                            "date": sess_date,
                            "title": sess_title,
                            "duration_minutes": sess_duration,
                            "exercise_name": ex_name,
                            "muscle_group": muscle_group,
                            "set_number": int(s.get("set_number", 1)),
                            "reps": reps,
                            "weight_kg": weight,
                            "rpe": rpe,
                            "estimated_1rm": one_rm,
                            "set_volume": vol,
                        }
                    )

        if not records:
            # Return empty structured Polars DataFrame
            return pl.DataFrame(
                schema={
                    "session_id": pl.Utf8,
                    "date": pl.Utf8,
                    "title": pl.Utf8,
                    "duration_minutes": pl.Int64,
                    "exercise_name": pl.Utf8,
                    "muscle_group": pl.Utf8,
                    "set_number": pl.Int64,
                    "reps": pl.Int64,
                    "weight_kg": pl.Float64,
                    "rpe": pl.Float64,
                    "estimated_1rm": pl.Float64,
                    "set_volume": pl.Float64,
                }
            )

        return pl.DataFrame(records)

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Calculates high-level workout analytics using Polars queries.

        Returns:
            Dictionary containing metrics like total sessions, total volume,
            muscle distribution, and personal best records.
        """
        df = self.to_polars_dataframe()

        if df.is_empty():
            return {
                "total_sessions": 0,
                "total_volume_kg": 0.0,
                "total_reps": 0,
                "avg_duration_minutes": 0.0,
                "muscle_distribution": [],
                "personal_records": [],
                "recent_volumes": [],
            }

        total_sessions = df.select(pl.col("session_id").n_unique()).item()
        total_volume = float(df.select(pl.col("set_volume").sum()).item())
        total_reps = int(df.select(pl.col("reps").sum()).item())

        # Average duration per unique session
        session_durations = (
            df.select(["session_id", "duration_minutes"])
            .unique()
            .select(pl.col("duration_minutes").mean())
            .item()
        )
        avg_duration = float(session_durations) if session_durations else 0.0

        # Muscle group breakdown using Polars group_by
        muscle_df = (
            df.group_by("muscle_group")
            .agg(
                [
                    pl.col("set_volume").sum().alias("volume"),
                    pl.col("reps").sum().alias("reps"),
                    pl.len().alias("sets_count"),
                ]
            )
            .sort("volume", descending=True)
        )
        muscle_distribution = muscle_df.to_dicts()

        # Personal Records (PRs) per exercise
        prs_df = (
            df.group_by("exercise_name")
            .agg(
                [
                    pl.col("muscle_group").first().alias("muscle_group"),
                    pl.col("weight_kg").max().alias("max_weight"),
                    pl.col("estimated_1rm").max().alias("max_1rm"),
                    pl.col("set_volume").sum().alias("total_volume"),
                ]
            )
            .sort("max_weight", descending=True)
            .limit(10)
        )
        personal_records = prs_df.to_dicts()

        # Recent session volume trend
        recent_df = (
            df.group_by(["session_id", "date", "title"])
            .agg(pl.col("set_volume").sum().alias("session_volume"))
            .sort("date", descending=False)
        )
        recent_volumes = recent_df.to_dicts()

        return {
            "total_sessions": total_sessions,
            "total_volume_kg": round(total_volume, 2),
            "total_reps": total_reps,
            "avg_duration_minutes": round(avg_duration, 1),
            "muscle_distribution": muscle_distribution,
            "personal_records": personal_records,
            "recent_volumes": recent_volumes,
        }

    def export_analytics(self) -> Path:
        """Exports analytics data tables to the analytics data directory.

        Satisfies Rule 4 and Rule 12 by using the analytics directory and Polars.

        Returns:
            Path to the written summary parquet file.
        """
        df = self.to_polars_dataframe()
        summary_path = self.analytics_dir / "workout_tabular_data.parquet"
        df.write_parquet(summary_path)

        # Export muscle group summary for visualization
        if not df.is_empty():
            muscle_df = (
                df.group_by("muscle_group")
                .agg(pl.col("set_volume").sum().alias("total_volume"))
                .sort("total_volume", descending=True)
            )
            muscle_json_path = self.analytics_dir / "muscle_distribution.json"
            with open(muscle_json_path, "w", encoding="utf-8") as f:
                json.dump(muscle_df.to_dicts(), f, indent=2)

        return summary_path
