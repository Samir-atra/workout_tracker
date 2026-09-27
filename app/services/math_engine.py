"""Mathematical Engine for Workout Analytics.

Implements all mathematical, biomechanical, and statistical computations using
the JAX library in accordance with project standards.
"""

from typing import List, Sequence, Tuple
import jax
import jax.numpy as jnp


def calculate_1rm_epley(weight: float, reps: int) -> float:
    """Calculates estimated One-Rep Max (1RM) using the Epley formula.

    Formula: 1RM = weight * (1 + reps / 30.0)

    Args:
        weight: Lifted resistance in kilograms.
        reps: Number of successful repetitions performed.

    Returns:
        Estimated 1RM in kilograms as a Python float.
    """
    if reps <= 0 or weight <= 0.0:
        return 0.0
    if reps == 1:
        return float(weight)

    w = jnp.asarray(weight, dtype=jnp.float32)
    r = jnp.asarray(reps, dtype=jnp.float32)
    one_rm = w * (1.0 + r / 30.0)
    return float(jax.device_get(one_rm))


def calculate_1rm_brzycki(weight: float, reps: int) -> float:
    """Calculates estimated One-Rep Max (1RM) using the Brzycki formula.

    Formula: 1RM = weight * (36.0 / (37.0 - reps))

    Args:
        weight: Lifted resistance in kilograms.
        reps: Number of successful repetitions performed.

    Returns:
        Estimated 1RM in kilograms as a Python float.
    """
    if reps <= 0 or weight <= 0.0:
        return 0.0
    if reps >= 37:
        # Fallback to Epley when reps approach or exceed 37 to avoid division by zero
        return calculate_1rm_epley(weight, reps)
    if reps == 1:
        return float(weight)

    w = jnp.asarray(weight, dtype=jnp.float32)
    r = jnp.asarray(reps, dtype=jnp.float32)
    one_rm = w * (36.0 / (37.0 - r))
    return float(jax.device_get(one_rm))


def calculate_volume_load(
    weights: Sequence[float], reps: Sequence[int]
) -> float:
    """Calculates total volume load across sets using JAX vector operations.

    Formula: Volume = sum(weight_i * reps_i)

    Args:
        weights: Sequence of resistance weights per set.
        reps: Sequence of repetitions completed per set.

    Returns:
        Total volume load in kilograms as a Python float.
    """
    if not weights or not reps or len(weights) != len(reps):
        return 0.0

    w_arr = jnp.asarray(weights, dtype=jnp.float32)
    r_arr = jnp.asarray(reps, dtype=jnp.float32)
    total_vol = jnp.dot(w_arr, r_arr)
    return float(jax.device_get(total_vol))


def calculate_average_intensity(
    weights: Sequence[float], one_rms: Sequence[float]
) -> float:
    """Computes the mean relative training intensity (% of 1RM) across sets.

    Args:
        weights: Sequence of lifted weights.
        one_rms: Corresponding 1RM values for the exercises.

    Returns:
        Average intensity percentage (0.0 to 100.0).
    """
    if not weights or not one_rms or len(weights) != len(one_rms):
        return 0.0

    w_arr = jnp.asarray(weights, dtype=jnp.float32)
    orm_arr = jnp.asarray(one_rms, dtype=jnp.float32)

    # Avoid zero division using safe masking
    valid_mask = orm_arr > 0.0
    safe_orm = jnp.where(valid_mask, orm_arr, 1.0)
    intensities = jnp.where(valid_mask, (w_arr / safe_orm) * 100.0, 0.0)

    count = jnp.sum(valid_mask.astype(jnp.float32))
    avg_intensity = jnp.where(count > 0.0, jnp.sum(intensities) / count, 0.0)
    return float(jax.device_get(avg_intensity))


def calculate_fatigue_score(
    volume: float, duration_minutes: int, avg_rpe: float
) -> float:
    """Calculates a composite session fatigue index using JAX operations.

    Args:
        volume: Total volume load in kilograms.
        duration_minutes: Workout duration in minutes.
        avg_rpe: Average Rating of Perceived Exertion (1 to 10).

    Returns:
        Normalized fatigue score index.
    """
    vol_j = jnp.asarray(max(volume, 0.0), dtype=jnp.float32)
    dur_j = jnp.asarray(max(duration_minutes, 1), dtype=jnp.float32)
    rpe_j = jnp.asarray(max(min(avg_rpe, 10.0), 1.0), dtype=jnp.float32)

    # Work density = volume / duration
    work_density = vol_j / dur_j
    # Non-linear RPE scaling using jnp.power
    fatigue = (work_density / 100.0) * jnp.power(rpe_j / 10.0, 1.5) * 10.0
    return float(jax.device_get(fatigue))
