/**
 * PulseFit Frontend Application Logic.
 * Handles UI interactions, API calls to FastAPI, and dynamic rendering.
 */

// State
let exerciseBlockCount = 0;

// Initialize on DOM Load
document.addEventListener("DOMContentLoaded", () => {
  setupNavigation();
  loadDashboardData();
  initializeWorkoutForm();
});

/**
 * Sets up tab navigation listeners.
 */
function setupNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  navItems.forEach((btn) => {
    btn.addEventListener("click", () => {
      const tabId = btn.getAttribute("data-tab");
      switchTab(tabId);
    });
  });
}

/**
 * Switches the active tab view.
 * @param {string} tabId - Target tab identifier.
 */
function switchTab(tabId) {
  // Update sidebar active buttons
  document.querySelectorAll(".nav-item").forEach((btn) => {
    if (btn.getAttribute("data-tab") === tabId) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  // Update tab pane visibility
  document.querySelectorAll(".tab-pane").forEach((pane) => {
    pane.classList.remove("active");
  });

  const targetPane = document.getElementById(`tab-${tabId}`);
  if (targetPane) {
    targetPane.classList.add("active");
  }

  // Update header titles
  const titles = {
    dashboard: ["Dashboard Overview", "Track your training volume, review records, and consult multi-agent AI specialists."],
    "log-workout": ["Log Daily Workout", "Record exercises, resistance loads, reps, and RPE scores evaluated with JAX."],
    "ai-workout": ["CrewAI Workout Architect", "Exercise Physiologist agent designs routines adapted to your history and gear."],
    "ai-nutrition": ["Nutrition & Supplements", "Sports Nutritionist and Biochemist agents recommend personalized meal & supplement stacks."],
    analytics: ["Polars Tabular Analytics", "High-performance data queries and statistics exported to data/analytics."],
  };

  if (titles[tabId]) {
    document.getElementById("page-title").textContent = titles[tabId][0];
    document.getElementById("page-subtitle").textContent = titles[tabId][1];
  }

  if (tabId === "dashboard" || tabId === "analytics") {
    loadDashboardData();
  }
}

/**
 * Loads analytics and sessions from FastAPI backend.
 */
async function loadDashboardData() {
  try {
    const res = await fetch("/api/analytics");
    if (!res.ok) throw new Error("Failed to fetch analytics");
    const data = await res.json();

    // Populate KPI Cards
    document.getElementById("metric-sessions").textContent = data.total_sessions || 0;
    document.getElementById("metric-volume").innerHTML = `${Number(data.total_volume_kg || 0).toLocaleString()} <small>kg</small>`;
    document.getElementById("metric-reps").textContent = Number(data.total_reps || 0).toLocaleString();
    document.getElementById("metric-duration").innerHTML = `${data.avg_duration_minutes || 0} <small>min</small>`;

    // Populate Muscle Distribution Bars
    renderMuscleDistribution(data.muscle_distribution || []);

    // Populate Personal Records Table
    renderPersonalRecords(data.personal_records || []);

    // Populate Recent Workouts
    loadRecentWorkouts();
  } catch (err) {
    console.error("Dashboard error:", err);
  }
}

/**
 * Renders muscle distribution progress bars.
 * @param {Array} muscles - List of muscle group metrics.
 */
function renderMuscleDistribution(muscles) {
  const container = document.getElementById("muscle-bars");
  if (!muscles || muscles.length === 0) {
    container.innerHTML = '<p class="placeholder-text">No workout data logged yet.</p>';
    return;
  }

  const maxVol = Math.max(...muscles.map((m) => m.volume || 1));
  let html = "";

  muscles.forEach((m) => {
    const pct = Math.round((m.volume / maxVol) * 100);
    html += `
      <div class="muscle-bar-item">
        <div class="muscle-bar-meta">
          <span class="group-name">${m.muscle_group}</span>
          <span class="group-val">${Math.round(m.volume).toLocaleString()} kg (${m.sets_count} sets)</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width: ${pct}%"></div>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

/**
 * Renders personal records table.
 * @param {Array} prs - List of exercise PR records.
 */
function renderPersonalRecords(prs) {
  const tbody = document.getElementById("prs-tbody");
  const analyticsTbody = document.getElementById("analytics-tbody");

  if (!prs || prs.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No records found.</td></tr>';
    if (analyticsTbody) {
      analyticsTbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No records found.</td></tr>';
    }
    return;
  }

  let htmlDashboard = "";
  let htmlAnalytics = "";

  prs.forEach((pr) => {
    htmlDashboard += `
      <tr>
        <td><strong>${pr.exercise_name}</strong></td>
        <td><span class="badge">${pr.muscle_group}</span></td>
        <td>${pr.max_weight} kg</td>
        <td><strong style="color: #60a5fa;">${Math.round(pr.max_1rm)} kg</strong></td>
      </tr>
    `;

    htmlAnalytics += `
      <tr>
        <td><strong>${pr.exercise_name}</strong></td>
        <td><span class="badge">${pr.muscle_group}</span></td>
        <td>${pr.max_weight} kg</td>
        <td><strong style="color: #60a5fa;">${Math.round(pr.max_1rm)} kg</strong></td>
        <td>${Math.round(pr.total_volume).toLocaleString()} kg</td>
      </tr>
    `;
  });

  tbody.innerHTML = htmlDashboard;
  if (analyticsTbody) {
    analyticsTbody.innerHTML = htmlAnalytics;
  }
}

/**
 * Loads recent workout sessions.
 */
async function loadRecentWorkouts() {
  const container = document.getElementById("recent-workouts-list");
  try {
    const res = await fetch("/api/workouts");
    const sessions = await res.json();

    if (!sessions || sessions.length === 0) {
      container.innerHTML = '<p class="placeholder-text">No workouts logged yet.</p>';
      return;
    }

    let html = "";
    sessions.forEach((s) => {
      const exerciseCount = s.exercises ? s.exercises.length : 0;
      html += `
        <div class="workout-card">
          <div class="workout-card-header">
            <div>
              <div class="workout-card-title">${s.title}</div>
              <div class="workout-card-date">📅 ${s.date} &bull; ⏱️ ${s.duration_minutes} min</div>
            </div>
          </div>
          <div class="workout-stats-row">
            <div>Exercises: <strong>${exerciseCount}</strong></div>
            <div>Volume: <strong>${Math.round(s.total_volume_kg || 0).toLocaleString()} kg</strong></div>
          </div>
          ${s.notes ? `<div style="font-size: 0.8rem; color: var(--text-dim);">${s.notes}</div>` : ""}
          <div class="workout-card-actions">
            <button class="btn btn-danger-outline" onclick="deleteWorkoutSession('${s.id}')">Delete</button>
          </div>
        </div>
      `;
    });

    container.innerHTML = html;
  } catch (err) {
    console.error("Error loading workouts:", err);
  }
}

/**
 * Deletes a workout session by ID.
 * @param {string} id - Session ID.
 */
async function deleteWorkoutSession(id) {
  if (!confirm("Are you sure you want to delete this workout session?")) return;
  try {
    const res = await fetch(`/api/workouts/${id}`, { method: "DELETE" });
    if (res.ok) {
      loadDashboardData();
    }
  } catch (err) {
    console.error("Delete error:", err);
  }
}

/**
 * Initializes the workout logger form with today's date and a starter exercise block.
 */
function initializeWorkoutForm() {
  const dateInput = document.getElementById("workout-date");
  if (dateInput) {
    dateInput.value = new Date().toISOString().split("T")[0];
  }
  const container = document.getElementById("exercises-container");
  if (container && container.children.length === 0) {
    addExerciseBlock("Barbell Bench Press", "Chest");
  }
}

/**
 * Adds an interactive exercise block to the workout logging form.
 * @param {string} defaultName - Initial exercise name.
 * @param {string} defaultGroup - Initial muscle group.
 */
function addExerciseBlock(defaultName = "", defaultGroup = "Chest") {
  exerciseBlockCount++;
  const blockId = `ex-block-${exerciseBlockCount}`;
  const container = document.getElementById("exercises-container");

  const block = document.createElement("div");
  block.className = "exercise-block";
  block.id = blockId;

  block.innerHTML = `
    <div class="exercise-block-header">
      <div style="font-weight: 600; font-size: 0.95rem;">Exercise #${exerciseBlockCount}</div>
      <button type="button" class="btn btn-danger-outline" onclick="removeExerciseBlock('${blockId}')">Remove Exercise</button>
    </div>
    <div class="form-row">
      <div class="form-group" style="flex: 2;">
        <label>Exercise Name</label>
        <input type="text" class="input-ex-name" required placeholder="e.g. Barbell Squat" value="${defaultName}">
      </div>
      <div class="form-group" style="flex: 1;">
        <label>Muscle Group</label>
        <select class="input-ex-group">
          <option value="Chest" ${defaultGroup === "Chest" ? "selected" : ""}>Chest</option>
          <option value="Back" ${defaultGroup === "Back" ? "selected" : ""}>Back</option>
          <option value="Legs" ${defaultGroup === "Legs" ? "selected" : ""}>Legs</option>
          <option value="Shoulders" ${defaultGroup === "Shoulders" ? "selected" : ""}>Shoulders</option>
          <option value="Arms" ${defaultGroup === "Arms" ? "selected" : ""}>Arms</option>
          <option value="Core" ${defaultGroup === "Core" ? "selected" : ""}>Core</option>
        </select>
      </div>
    </div>

    <!-- Sets Container -->
    <div class="sets-container" id="sets-${blockId}">
      <!-- Dynamic Sets -->
    </div>
    <div style="margin-top: 0.5rem;">
      <button type="button" class="btn btn-secondary btn-sm" onclick="addSetRow('${blockId}')">+ Add Set</button>
    </div>
  `;

  container.appendChild(block);

  // Add 3 default set rows
  addSetRow(blockId, 1, 10, 60, 7.5);
  addSetRow(blockId, 2, 8, 70, 8.0);
  addSetRow(blockId, 3, 6, 80, 8.5);
}

/**
 * Removes an exercise block.
 * @param {string} blockId - Block element ID.
 */
function removeExerciseBlock(blockId) {
  const el = document.getElementById(blockId);
  if (el) el.remove();
}

/**
 * Adds a set row inside an exercise block.
 * @param {string} blockId - Parent exercise block ID.
 * @param {number} setNum - Sequential set number.
 * @param {number} reps - Reps count.
 * @param {number} weight - Weight in kg.
 * @param {number} rpe - RPE rating.
 */
function addSetRow(blockId, setNum = null, reps = 10, weight = 60, rpe = 8.0) {
  const setsContainer = document.getElementById(`sets-${blockId}`);
  if (!setsContainer) return;

  const currentCount = setsContainer.children.length + 1;
  const num = setNum || currentCount;

  const row = document.createElement("div");
  row.className = "set-row";
  row.innerHTML = `
    <span class="set-label">Set ${num}</span>
    <input type="number" class="set-reps" placeholder="Reps" min="1" max="100" value="${reps}" style="width: 80px;" required>
    <input type="number" step="0.5" class="set-weight" placeholder="Weight kg" min="0" max="500" value="${weight}" style="width: 100px;" required>
    <input type="number" step="0.5" class="set-rpe" placeholder="RPE (1-10)" min="1" max="10" value="${rpe}" style="width: 90px;">
    <button type="button" class="btn btn-danger-outline" style="padding: 0.35rem 0.5rem;" onclick="this.parentElement.remove()">✕</button>
  `;
  setsContainer.appendChild(row);
}

/**
 * Handles workout session creation.
 * @param {Event} e - Submit event.
 */
async function handleSaveWorkout(e) {
  e.preventDefault();

  const title = document.getElementById("workout-title").value.trim();
  const date = document.getElementById("workout-date").value;
  const duration = parseInt(document.getElementById("workout-duration").value, 10);
  const notes = document.getElementById("workout-notes").value.trim();

  const exerciseBlocks = document.querySelectorAll(".exercise-block");
  const exercises = [];

  exerciseBlocks.forEach((block) => {
    const name = block.querySelector(".input-ex-name").value.trim();
    const muscle = block.querySelector(".input-ex-group").value;
    const setRows = block.querySelectorAll(".set-row");
    const sets = [];

    setRows.forEach((row, idx) => {
      const reps = parseInt(row.querySelector(".set-reps").value, 10);
      const weight = parseFloat(row.querySelector(".set-weight").value);
      const rpeInput = row.querySelector(".set-rpe").value;
      const rpe = rpeInput ? parseFloat(rpeInput) : null;

      sets.push({
        set_number: idx + 1,
        reps: reps,
        weight_kg: weight,
        rpe: rpe,
      });
    });

    if (name && sets.length > 0) {
      exercises.push({
        name: name,
        muscle_group: muscle,
        sets: sets,
      });
    }
  });

  if (exercises.length === 0) {
    alert("Please add at least one exercise with sets.");
    return;
  }

  const payload = {
    title: title,
    date: date,
    duration_minutes: duration,
    notes: notes,
    exercises: exercises,
  };

  try {
    const res = await fetch("/api/workouts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error("Failed to save workout");

    alert("Workout successfully recorded!");
    switchTab("dashboard");
  } catch (err) {
    alert("Error saving workout: " + err.message);
  }
}

/**
 * Handles AI workout routine generation with CrewAI.
 * @param {Event} e - Submit event.
 */
async function handleGenerateWorkout(e) {
  e.preventDefault();

  const btn = document.getElementById("btn-generate-workout");
  const spinner = btn.querySelector(".btn-spinner");
  const btnText = btn.querySelector(".btn-text");
  const statusBadge = document.getElementById("workout-plan-status");
  const resultContainer = document.getElementById("ai-workout-result");

  const goal = document.getElementById("ai-workout-goal").value;
  const level = document.getElementById("ai-fitness-level").value;
  const equipment = document.getElementById("ai-equipment").value;
  const duration = parseInt(document.getElementById("ai-duration").value, 10);
  const includeHistory = document.getElementById("ai-include-history").checked;

  const targetMuscles = [];
  document.querySelectorAll('input[name="target-muscle"]:checked').forEach((cb) => {
    targetMuscles.push(cb.value);
  });

  if (targetMuscles.length === 0) {
    alert("Please select at least one target muscle group.");
    return;
  }

  const payload = {
    goal: goal,
    target_muscle_groups: targetMuscles,
    fitness_level: level,
    available_equipment: equipment,
    duration_minutes: duration,
    include_recent_history: includeHistory,
  };

  // UI Loading State
  btn.disabled = true;
  spinner.classList.remove("hidden");
  btnText.textContent = "Agent Crew Analyzing & Structuring...";
  statusBadge.textContent = "CrewAI Active";
  statusBadge.style.background = "rgba(59, 130, 246, 0.2)";
  statusBadge.style.color = "#60a5fa";

  resultContainer.innerHTML = `
    <div class="empty-state">
      <div class="btn-spinner" style="width: 32px; height: 32px; margin-bottom: 1rem;"></div>
      <p>The <strong>Exercise Physiologist & Strength Coach</strong> agent is synthesizing progressive overload, biomechanics, and exercise selection...</p>
    </div>
  `;

  try {
    const res = await fetch("/api/crew/suggest-workout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    resultContainer.innerHTML = marked.parse(data.plan_markdown || "No plan generated.");
    statusBadge.textContent = "Plan Generated";
    statusBadge.style.background = "rgba(16, 185, 129, 0.2)";
    statusBadge.style.color = "#34d399";
  } catch (err) {
    resultContainer.innerHTML = `<p style="color: var(--danger);">Failed to generate workout: ${err.message}</p>`;
    statusBadge.textContent = "Error";
  } finally {
    btn.disabled = false;
    spinner.classList.add("hidden");
    btnText.textContent = "⚡ Generate Custom Workout with CrewAI";
  }
}

/**
 * Handles AI meals and supplements recommendation with CrewAI.
 * @param {Event} e - Submit event.
 */
async function handleGenerateNutrition(e) {
  e.preventDefault();

  const btn = document.getElementById("btn-generate-nutrition");
  const spinner = btn.querySelector(".btn-spinner");
  const btnText = btn.querySelector(".btn-text");
  const statusBadge = document.getElementById("nutrition-plan-status");
  const resultContainer = document.getElementById("ai-nutrition-result");

  const goal = document.getElementById("nut-goal").value;
  const diet = document.getElementById("nut-diet").value;
  const bw = parseFloat(document.getElementById("nut-bw").value);
  const calories = parseInt(document.getElementById("nut-calories").value, 10);
  const freq = parseInt(document.getElementById("nut-frequency").value, 10);
  const allergies = document.getElementById("nut-allergies").value.trim() || "None";

  const payload = {
    goal: goal,
    dietary_preference: diet,
    body_weight_kg: bw,
    daily_calorie_target: calories,
    allergies_intolerances: allergies,
    training_frequency_per_week: freq,
  };

  btn.disabled = true;
  spinner.classList.remove("hidden");
  btnText.textContent = "Dietitian & Biochemist Collaborating...";
  statusBadge.textContent = "CrewAI Active";
  statusBadge.style.background = "rgba(139, 92, 246, 0.2)";
  statusBadge.style.color = "#c4b5fd";

  resultContainer.innerHTML = `
    <div class="empty-state">
      <div class="btn-spinner" style="width: 32px; height: 32px; margin-bottom: 1rem;"></div>
      <p>The <strong>Sports Nutritionist</strong> and <strong>Supplement Biochemist</strong> agents are formulating your macronutrients, timing, and evidence-based supplement stack...</p>
    </div>
  `;

  try {
    const res = await fetch("/api/crew/recommend-nutrition", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    resultContainer.innerHTML = marked.parse(data.plan_markdown || "No plan generated.");
    statusBadge.textContent = "Protocol Ready";
    statusBadge.style.background = "rgba(16, 185, 129, 0.2)";
    statusBadge.style.color = "#34d399";
  } catch (err) {
    resultContainer.innerHTML = `<p style="color: var(--danger);">Failed to recommend nutrition: ${err.message}</p>`;
    statusBadge.textContent = "Error";
  } finally {
    btn.disabled = false;
    spinner.classList.add("hidden");
    btnText.textContent = "🥗 Recommend Meals & Supplements with CrewAI";
  }
}

/**
 * Triggers Polars parquet export.
 */
async function exportAnalyticsData() {
  try {
    const res = await fetch("/api/analytics/export", { method: "POST" });
    const data = await res.json();
    alert(`Success: Tabular data exported via Polars to: ${data.export_path}`);
  } catch (err) {
    alert("Export failed: " + err.message);
  }
}
