const heroMetrics = document.getElementById("heroMetrics");
const programGrid = document.getElementById("programGrid");
const programSelect = document.getElementById("programSelect");
const categoryStats = document.getElementById("categoryStats");
const recentEnrollments = document.getElementById("recentEnrollments");

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Request failed.");
  }
  return data;
}

function setMessage(id, message, isError = false) {
  const node = document.getElementById(id);
  node.textContent = message;
  node.style.color = isError ? "#b42318" : "#115e59";
}

function renderMetrics(summary) {
  const cards = [
    ["Registered Students", summary.total_users],
    ["Active Programs", summary.total_programs],
    ["Total Enrollments", summary.total_enrollments],
    ["Occupancy Rate", `${summary.occupancy_rate}%`],
  ];
  heroMetrics.innerHTML = cards
    .map(
      ([label, value]) => `
        <div class="metric-card">
          <span>${label}</span>
          <strong>${value}</strong>
        </div>
      `,
    )
    .join("");
}

function renderPrograms(programs) {
  programGrid.innerHTML = programs
    .map((program) => {
      const occupancy = Math.round((program.enrolled_count / program.capacity) * 100);
      return `
        <article class="program-card">
          <p class="section-label">${program.category}</p>
          <h3>${program.name}</h3>
          <span class="program-meta">Coach: ${program.coach_name}</span>
          <span class="program-meta">Schedule: ${program.schedule}</span>
          <span class="program-meta">Skill: ${program.skill_level}</span>
          <span class="program-meta">Fee: Rs. ${program.fee}</span>
          <div class="capacity-meter"><div style="width:${occupancy}%"></div></div>
          <span class="program-meta">${program.enrolled_count}/${program.capacity} seats filled</span>
          <span class="pill">${program.seats_left} seats left</span>
        </article>
      `;
    })
    .join("");

  programSelect.innerHTML =
    '<option value="">Select sports program</option>' +
    programs
      .map(
        (program) =>
          `<option value="${program.id}">${program.name} (${program.seats_left} seats left)</option>`,
      )
      .join("");
}

function renderCategoryStats(rows) {
  categoryStats.innerHTML = rows
    .map(
      (row) => `
        <div class="stat-row">
          <strong>${row.category}</strong>
          <span>Programs: ${row.program_count}</span>
          <span>Enrollments: ${row.category_enrollment}/${row.category_capacity}</span>
        </div>
      `,
    )
    .join("");
}

function renderActivity(rows) {
  recentEnrollments.innerHTML = rows
    .map(
      (row) => `
        <div class="activity-row">
          <strong>${row.full_name}</strong>
          <span>${row.program_name} • ${row.category}</span>
          <span>Status: ${row.enrollment_status}</span>
          <span>${new Date(row.enrolled_on).toLocaleString()}</span>
        </div>
      `,
    )
    .join("");
}

async function loadDashboard() {
  const data = await fetchJson("/api/dashboard");
  renderMetrics(data.overview.summary);
  renderPrograms(data.programs);
  renderCategoryStats(data.overview.by_category);
  renderActivity(data.recent_enrollments);
}

document.getElementById("refreshButton").addEventListener("click", loadDashboard);

document.getElementById("registerForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  const payload = Object.fromEntries(form.entries());
  try {
    const data = await fetchJson("/api/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setMessage("registerMessage", data.message);
    event.target.reset();
    await loadDashboard();
  } catch (error) {
    setMessage("registerMessage", error.message, true);
  }
});

document.getElementById("loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  const payload = Object.fromEntries(form.entries());
  try {
    const data = await fetchJson("/api/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setMessage("loginMessage", `${data.message} Welcome, ${data.user.full_name}.`);
  } catch (error) {
    setMessage("loginMessage", error.message, true);
  }
});

document.getElementById("enrollForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  const payload = Object.fromEntries(form.entries());
  try {
    const data = await fetchJson("/api/enroll", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setMessage(
      "enrollMessage",
      `${data.message} ${data.result.student} joined ${data.result.program}. Seats left: ${data.result.seats_left}.`,
    );
    event.target.reset();
    await loadDashboard();
  } catch (error) {
    setMessage("enrollMessage", error.message, true);
  }
});

loadDashboard().catch((error) => {
  setMessage("enrollMessage", error.message, true);
});

