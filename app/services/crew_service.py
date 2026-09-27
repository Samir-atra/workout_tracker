"""CrewAI Multi-Agent Service for Workout and Nutrition Intelligence.

Orchestrates collaborative AI agents to analyze training history, synthesize
custom workout routines, and generate evidence-based meal and supplement plans.
"""

import os
from typing import Any, Dict, List, Optional
from crewai import Agent, Crew, LLM, Process, Task

from app.config import settings
from app.models import NutritionSuggestionRequest, WorkoutSuggestionRequest


class WorkoutCrewService:
    """Service encapsulating CrewAI multi-agent workflows."""

    def __init__(self) -> None:
        """Initializes the CrewAI service with configured LLM parameters."""
        self.api_key = settings.OPENROUTER_API_KEY
        self.model_name = settings.CREWAI_MODEL
        self.base_url = settings.OPENROUTER_API_BASE
        self.max_tokens = settings.CREWAI_MAX_TOKENS

    def _get_llm(self) -> Optional[LLM]:
        """Creates and returns the configured CrewAI LLM instance.

        Returns:
            Configured LLM instance or None if API key is not configured.
        """
        if not self.api_key:
            return None

        return LLM(
            model=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            max_tokens=self.max_tokens,
            temperature=0.7,
        )

    def _create_workout_architect(self, llm: Optional[LLM]) -> Agent:
        """Instantiates the Workout Architect Agent.

        Args:
            llm: Optional CrewAI LLM instance.

        Returns:
            Configured Agent instance.
        """
        return Agent(
            role="Lead Exercise Physiologist & Strength Coach",
            goal=(
                "Design optimal, scientifically structured workout sessions "
                "incorporating progressive overload, optimal volume, and exercise selection."
            ),
            backstory=(
                "You are an elite strength and conditioning specialist with a deep "
                "background in biomechanics. You prescribe targeted exercise routines, "
                "specifying sets, reps, intensity (RPE), rest intervals, and cues."
            ),
            verbose=False,
            allow_delegation=False,
            llm=llm,
        )

    def _create_nutritionist(self, llm: Optional[LLM]) -> Agent:
        """Instantiates the Clinical Sports Nutritionist Agent.

        Args:
            llm: Optional CrewAI LLM instance.

        Returns:
            Configured Agent instance.
        """
        return Agent(
            role="Senior Clinical Sports Nutritionist",
            goal=(
                "Formulate comprehensive, delicious, and macronutrient-balanced daily "
                "meal plans optimized for athletic performance, recovery, and body composition."
            ),
            backstory=(
                "You are a registered sports dietitian specializing in nutrient timing, "
                "macronutrient distribution, and practical culinary meal plans tailored "
                "to individual dietary preferences and training demands."
            ),
            verbose=False,
            allow_delegation=False,
            llm=llm,
        )

    def _create_supplement_specialist(self, llm: Optional[LLM]) -> Agent:
        """Instantiates the Ergogenics & Supplement Specialist Agent.

        Args:
            llm: Optional CrewAI LLM instance.

        Returns:
            Configured Agent instance.
        """
        return Agent(
            role="Evidence-Based Performance Ergogenics Specialist",
            goal=(
                "Recommend safe, peer-reviewed, and highly effective workout supplements "
                "with precise clinical dosages, timing protocols, and safety considerations."
            ),
            backstory=(
                "You are a sports biochemist specializing in performance supplements. "
                "You only recommend supplements with robust scientific evidence (e.g. Creatine, "
                "Whey Protein, Beta-Alanine, Electrolytes) and always highlight safety guidelines."
            ),
            verbose=False,
            allow_delegation=False,
            llm=llm,
        )

    def suggest_workout(
        self, request: WorkoutSuggestionRequest, recent_summary: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Executes a CrewAI workflow to generate a tailored workout plan.

        Args:
            request: Workout suggestion criteria.
            recent_summary: Optional recent workout summary for progressive overload context.

        Returns:
            Dictionary containing structured workout recommendation and details.
        """
        llm = self._get_llm()
        if not llm:
            return self._fallback_workout_plan(request)

        try:
            coach = self._create_workout_architect(llm)

            history_context = ""
            if request.include_recent_history and recent_summary:
                history_context = (
                    f"User's recent activity: {recent_summary.get('total_sessions', 0)} sessions logged, "
                    f"Total volume: {recent_summary.get('total_volume_kg', 0)} kg. "
                    f"Muscle distribution: {recent_summary.get('muscle_distribution', [])}."
                )

            task_description = (
                f"Design a comprehensive, structured workout routine for an individual with the following profile:\n"
                f"- Primary Goal: {request.goal}\n"
                f"- Target Muscle Groups: {', '.join(request.target_muscle_groups)}\n"
                f"- Experience Level: {request.fitness_level}\n"
                f"- Available Equipment: {request.available_equipment}\n"
                f"- Available Time: {request.duration_minutes} minutes\n"
                f"- Training Context: {history_context}\n\n"
                f"Please provide:\n"
                f"1. Workout Title and Strategic Overview.\n"
                f"2. Dynamic Warm-Up (5-8 mins).\n"
                f"3. Main Resistance Training Routine: For each exercise, include Exercise Name, "
                f"Target Muscle, Sets, Reps range, Target RPE, Rest Period (seconds), and Technique Form Cue.\n"
                f"4. Cool-Down and Mobility Suggestions.\n"
                f"5. Progressive Overload Recommendation for the next session."
            )

            workout_task = Task(
                description=task_description,
                expected_output=(
                    "A fully structured, formatted markdown workout program with warm-up, "
                    "detailed exercises table/list, rest intervals, and coaching cues."
                ),
                agent=coach,
            )

            crew = Crew(
                agents=[coach],
                tasks=[workout_task],
                process=Process.sequential,
                verbose=False,
            )

            result = crew.kickoff()
            output_text = str(result)
            return {
                "status": "success",
                "goal": request.goal,
                "target_muscle_groups": request.target_muscle_groups,
                "plan_markdown": output_text,
                "model_used": self.model_name,
            }
        except Exception as e:
            # Fallback gracefully to ensure continuous reliability
            fallback = self._fallback_workout_plan(request)
            fallback["warning"] = f"AI agent service switched to fallback: {str(e)}"
            return fallback

    def recommend_nutrition(
        self, request: NutritionSuggestionRequest
    ) -> Dict[str, Any]:
        """Executes a CrewAI workflow to generate meal and supplement plans.

        Args:
            request: Nutrition and supplement parameters.

        Returns:
            Dictionary containing structured meal plans and supplement protocols.
        """
        llm = self._get_llm()
        if not llm:
            return self._fallback_nutrition_plan(request)

        try:
            nutritionist = self._create_nutritionist(llm)
            supplement_specialist = self._create_supplement_specialist(llm)

            meal_task_description = (
                f"Formulate a complete daily meal plan for a person with:\n"
                f"- Goal: {request.goal}\n"
                f"- Dietary Style: {request.dietary_preference}\n"
                f"- Body Weight: {request.body_weight_kg} kg\n"
                f"- Target Calories: {request.daily_calorie_target} kcal\n"
                f"- Allergies/Restrictions: {request.allergies_intolerances}\n"
                f"- Training Frequency: {request.training_frequency_per_week} days/week\n\n"
                f"Include:\n"
                f"1. Target Daily Macros (Protein g, Carbohydrates g, Fats g, Total Calories).\n"
                f"2. Breakfast, Lunch, Pre/Post-Workout Snack, and Dinner.\n"
                f"3. Practical hydration recommendation."
            )

            meal_task = Task(
                description=meal_task_description,
                expected_output="A structured markdown meal plan with macronutrient breakdown and specific food choices.",
                agent=nutritionist,
            )

            supp_task_description = (
                f"Based on the training goal ({request.goal}) and diet ({request.dietary_preference}), "
                f"recommend a targeted, evidence-based workout supplement protocol.\n"
                f"For each supplement recommended, provide:\n"
                f"- Supplement Name\n"
                f"- Evidence Grade (A/B/C)\n"
                f"- Exact Daily Clinical Dosage\n"
                f"- Optimal Timing (Pre-workout, Post-workout, With Meals, Morning)\n"
                f"- Scientific Mechanism & Benefit\n"
                f"- Safety / Hydration Considerations."
            )

            supp_task = Task(
                description=supp_task_description,
                expected_output="A bulleted supplement stack with dosages, timing, mechanisms, and safety precautions.",
                agent=supplement_specialist,
            )

            crew = Crew(
                agents=[nutritionist, supplement_specialist],
                tasks=[meal_task, supp_task],
                process=Process.sequential,
                verbose=False,
            )

            result = crew.kickoff()
            output_text = str(result)
            return {
                "status": "success",
                "goal": request.goal,
                "dietary_preference": request.dietary_preference,
                "plan_markdown": output_text,
                "model_used": self.model_name,
            }
        except Exception as e:
            fallback = self._fallback_nutrition_plan(request)
            fallback["warning"] = f"AI agent service switched to fallback: {str(e)}"
            return fallback

    def _fallback_workout_plan(
        self, request: WorkoutSuggestionRequest
    ) -> Dict[str, Any]:
        """Provides an evidence-based fallback routine when API is unavailable.

        Args:
            request: Workout suggestion criteria.

        Returns:
            Dictionary containing structured workout recommendation.
        """
        muscles = ", ".join(request.target_muscle_groups)
        content = f"""# Tailored {request.goal} Workout Routine
**Target Muscle Groups:** {muscles} | **Equipment:** {request.available_equipment} | **Duration:** {request.duration_minutes} min

### 1. Dynamic Warm-Up (6 Minutes)
- Arm circles & chest openers: 2 sets x 30 seconds
- Cat-cow & thoracic rotations: 2 sets x 10 reps
- Band pull-aparts / Light push-ups: 2 sets x 12 reps

### 2. Main Resistance Routine
1. **Primary Compound Lift**:
   - **Sets / Reps:** 4 sets x 6-8 reps
   - **Intensity:** RPE 8.0 (2 reps in reserve)
   - **Rest:** 120 seconds between sets
   - **Cues:** Control eccentric phase (3 seconds down), explode on concentric.

2. **Secondary Compound / Superset**:
   - **Sets / Reps:** 3 sets x 8-10 reps
   - **Intensity:** RPE 8.0
   - **Rest:** 90 seconds
   - **Cues:** Full range of motion, maintain steady tempo.

3. **Hypertrophy / Isolation Movement**:
   - **Sets / Reps:** 3 sets x 12-15 reps
   - **Intensity:** RPE 8.5
   - **Rest:** 60 seconds
   - **Cues:** Focus on muscular squeeze and mind-muscle connection.

4. **Finisher / Core Stability**:
   - **Sets / Reps:** 3 sets x 15-20 reps or 45s isometric hold
   - **Intensity:** RPE 9.0
   - **Rest:** 45 seconds

### 3. Progressive Overload Guidance
- Once you reach the top of the repetition range across all sets with proper form, increase resistance by 2.5% to 5% next session.
"""
        return {
            "status": "success",
            "goal": request.goal,
            "target_muscle_groups": request.target_muscle_groups,
            "plan_markdown": content,
            "model_used": "Evidence-Based Exercise Physiology Engine",
        }

    def _fallback_nutrition_plan(
        self, request: NutritionSuggestionRequest
    ) -> Dict[str, Any]:
        """Provides an evidence-based fallback nutrition plan when API is unavailable.

        Args:
            request: Nutrition suggestion criteria.

        Returns:
            Dictionary containing structured meal and supplement plan.
        """
        bw = request.body_weight_kg
        protein = round(bw * 2.0, 1)  # 2.0g per kg body weight
        protein_kcal = protein * 4.0
        total_kcal = request.daily_calorie_target or int(bw * 35)
        remaining_kcal = total_kcal - protein_kcal
        carbs = round((remaining_kcal * 0.55) / 4.0, 1)
        fats = round((remaining_kcal * 0.45) / 9.0, 1)

        content = f"""# Personalized Nutrition & Workout Supplement Plan
**Goal:** {request.goal} | **Diet Style:** {request.dietary_preference} | **Caloric Target:** {total_kcal} kcal

### 1. Macro Target Breakdown
- **Daily Protein:** {protein} g (~{int(protein_kcal)} kcal) — Crucial for muscle protein synthesis (MPS)
- **Daily Carbohydrates:** {carbs} g — Fuel for high-intensity glycolytic training
- **Daily Healthy Fats:** {fats} g — Essential for hormone production and joint health
- **Total Energy:** {total_kcal} kcal

---

### 2. Daily Meal Schedule
- **Breakfast:**
  - 3 whole eggs (or scrambled tofu for plant-based) + 1 cup oatmeal topped with fresh berries & chia seeds.
  - Greek yogurt or protein smoothie.
- **Lunch:**
  - 180g Grilled Chicken Breast (or Tempeh / Lentils) + 1.5 cups Brown Rice or Quinoa + Steamed Broccoli with Olive Oil.
- **Pre-Workout Fuel (60-90 min prior):**
  - 1 Banana + 1 scoop Whey Protein Isolate (or Pea Protein) mixed with water or almond milk.
- **Post-Workout Recovery (Within 60 min):**
  - High-protein meal or shake with fast-digesting carbohydrates (e.g. rice cakes with honey, whey shake).
- **Dinner:**
  - 200g Baked Salmon / Lean Beef (or Seitan / Edamame bowl) + Sweet potato wedges + Large mixed greens salad with avocado.

---

### 3. Evidence-Based Workout Supplements
1. **Creatine Monohydrate**:
   - **Dosage:** 5g daily (any consistent time, ideally post-workout with carbs).
   - **Evidence:** Grade A (enhances phosphocreatine replenishment, power output, and cell hydration).
2. **Whey / Plant Protein Isolate**:
   - **Dosage:** 25-30g post-workout or to hit daily protein goals.
   - **Evidence:** Grade A (high leucine content triggers muscle protein synthesis).
3. **Electrolytes (Sodium, Potassium, Magnesium)**:
   - **Dosage:** 1 serving during prolonged or intense training sessions.
   - **Evidence:** Grade A for neuromuscular contraction and fluid balance.
4. **Caffeine Anhydrous (Optional Pre-Workout)**:
   - **Dosage:** 3-5 mg/kg bodyweight taken 30-45 minutes before intense sessions.
   - **Evidence:** Grade A for acute focus, alertness, and delayed fatigue.
5. **Vitamin D3 & Omega-3 Fish Oil**:
   - **Dosage:** 2000-4000 IU Vitamin D3 + 1000mg EPA/DHA with morning meal.
   - **Evidence:** Supports immune health, bone density, and systemic inflammation reduction.
"""
        return {
            "status": "success",
            "goal": request.goal,
            "dietary_preference": request.dietary_preference,
            "plan_markdown": content,
            "model_used": "Evidence-Based Sports Nutrition Engine",
        }
