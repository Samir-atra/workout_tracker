"""Unit Tests for JAX Mathematical Engine.

Tests 1RM estimations, volume load dot products, and exertion metrics.
"""

import pytest
from app.services.math_engine import (
    calculate_1rm_brzycki,
    calculate_1rm_epley,
    calculate_average_intensity,
    calculate_fatigue_score,
    calculate_volume_load,
)


def test_calculate_1rm_epley_single_rep() -> None:
    """Tests 1RM with 1 repetition returns the lifted weight."""
    assert calculate_1rm_epley(100.0, 1) == 100.0


def test_calculate_1rm_epley_multiple_reps() -> None:
    """Tests Epley formula: 100 * (1 + 10 / 30) = 133.33 kg."""
    result = calculate_1rm_epley(100.0, 10)
    assert pytest.approx(result, rel=1e-2) == 133.33


def test_calculate_1rm_epley_zero_inputs() -> None:
    """Tests zero or negative inputs return 0.0."""
    assert calculate_1rm_epley(0.0, 10) == 0.0
    assert calculate_1rm_epley(100.0, 0) == 0.0


def test_calculate_1rm_brzycki() -> None:
    """Tests Brzycki formula: 100 * (36 / (37 - 10)) = 133.33 kg."""
    result = calculate_1rm_brzycki(100.0, 10)
    assert pytest.approx(result, rel=1e-2) == 133.33


def test_calculate_volume_load_jax() -> None:
    """Tests vector dot product volume calculation via JAX."""
    weights = [50.0, 60.0, 70.0]
    reps = [10, 8, 6]
    # Expected: (50*10) + (60*8) + (70*6) = 500 + 480 + 420 = 1400.0
    total = calculate_volume_load(weights, reps)
    assert total == 1400.0


def test_calculate_volume_load_empty() -> None:
    """Tests empty sequence returns 0.0."""
    assert calculate_volume_load([], []) == 0.0


def test_calculate_average_intensity() -> None:
    """Tests relative intensity computation with JAX."""
    weights = [80.0, 90.0, 100.0]
    one_rms = [100.0, 100.0, 100.0]
    # Mean: (80 + 90 + 100) / 3 = 90.0%
    intensity = calculate_average_intensity(weights, one_rms)
    assert pytest.approx(intensity, rel=1e-2) == 90.0


def test_calculate_fatigue_score() -> None:
    """Tests fatigue index generation."""
    score = calculate_fatigue_score(volume=5000.0, duration_minutes=60, avg_rpe=8.5)
    assert score > 0.0
