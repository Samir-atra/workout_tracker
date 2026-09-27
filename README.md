# PulseFit &bull; Workout Tracker & AI Advisor

A web application powered by **CrewAI**, **FastAPI**, **Polars**, and **JAX** to track daily workouts, suggest personalized exercise routines, and recommend evidence-based meal plans and workout supplements.

## 🌟 Key Features

1. **Daily Workout Tracking**:
   - Log exercises, sets, resistance loads (kg), repetitions, and RPE scores.
   - Real-time session volume calculations and progressive overload tracking.

2. **JAX Mathematical Engine**:
   - Computes One-Rep Maximum (1RM) using Epley and Brzycki formulas using JAX arrays.
   - Calculates total volume load via vector dot products.
   - Computes session fatigue index and relative intensity percentages.

3. **Polars Tabular Analytics**:
   - Tabular storage and high-performance querying using Polars DataFrames (`pl.DataFrame`).
   - Group-by aggregations for volume by muscle group, personal records (PRs), and volume trends.
   - Direct export to Parquet format in `data/analytics/` for data science workflows.

4. **CrewAI Multi-Agent System**:
   - **Lead Exercise Physiologist & Strength Coach Agent**: Formulates periodized workout programs tailored to experience level, muscle groups, gear, and duration.
   - **Senior Clinical Sports Nutritionist Agent**: Formulates daily meal plans with precision macronutrient splits (protein, carbohydrates, healthy fats) and nutrient timing.
   - **Performance Ergogenics & Supplement Specialist Agent**: Evaluates and prescribes evidence-based workout supplements with clinical dosages, timing, and safety guidelines.

5. **Modern Responsive UI**:
   - Tabbed Single Page Application with dark fitness dashboard.
   - Interactive forms, dynamic exercise/set builder, and rendered Markdown outputs.

## 🚀 Quick Start

### 1. Requirements & Environment
Configure your `.env` file in the project root:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
CREWAI_MODEL=openrouter/google/gemini-2.5-flash
CREWAI_MAX_TOKENS=2048
HOST=0.0.0.0
PORT=8000
```

### 2. Run the Web Application
```bash
python run.py
```
Open your browser at `http://localhost:8000`.

### 3. Run Unit Tests
```bash
pytest tests/
```
