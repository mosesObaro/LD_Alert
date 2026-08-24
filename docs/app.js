document.addEventListener("DOMContentLoaded", async () => {
  try {
    const res = await fetch("data.json");
    if (!res.ok) throw new Error("Could not load data.json");
    const data = await res.json();
    renderDashboard(data);
  } catch (e) {
    console.warn("Loading fallback preview data...", e);
    renderDashboard(getFallbackData());
  }
});

function renderDashboard(data) {
  // Update header meta
  const lastUpdatedEl = document.getElementById("last-updated");
  if (lastUpdatedEl && data.last_updated_lagos) {
    lastUpdatedEl.textContent = `Last Updated: ${data.last_updated_lagos}`;
  }

  // Update stats
  const statCompleted = document.getElementById("stat-completed");
  const statMinutes = document.getElementById("stat-minutes");
  const statStage = document.getElementById("stat-stage");
  const statArtifacts = document.getElementById("stat-artifacts");

  if (statCompleted) statCompleted.textContent = data.history_summary?.completed || 0;
  if (statMinutes) statMinutes.textContent = `${data.history_summary?.total_learning_minutes || 0}m`;
  if (statStage) statStage.textContent = data.career_progression?.current_stage?.split(":")[0] || "Stage 3";
  if (statArtifacts) statArtifacts.textContent = data.portfolio_items?.length || 2;

  // Render Weekly Plan
  const weeklyPlanContainer = document.getElementById("weekly-plan-container");
  if (weeklyPlanContainer && data.weekly_plan) {
    const plan = data.weekly_plan;
    weeklyPlanContainer.innerHTML = `
      <div style="background: #eff6ff; border-left: 4px solid #2563eb; padding: 1rem; border-radius: 0 8px 8px 0; margin-bottom: 1.5rem;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #1e40af; text-transform: uppercase;">Week ${plan.week_number} Theme</div>
        <h3 style="font-size: 1.15rem; color: #0f172a; margin: 0.2rem 0 0.4rem 0;">${plan.theme}</h3>
        <p style="font-size: 0.9rem; color: #475569; margin: 0;">${plan.why_matters}</p>
      </div>

      <div class="resource-item">
        <span class="badge badge-free">Immediate L&D Skill</span>
        <h3 style="margin-top: 0.4rem;">${plan.core_ld.title}</h3>
        <div class="resource-meta">Provider: <strong>${plan.core_ld.provider}</strong> &bull; Duration: <strong>${plan.core_ld.duration}</strong></div>
        <p style="font-size: 0.88rem; margin-bottom: 0.5rem;">${plan.core_ld.summary}</p>
        <div class="app-box">
          <strong>TD Africa Application:</strong> ${plan.core_ld.td_africa_application}
        </div>
        <a href="${plan.core_ld.url}" class="btn" target="_blank">Access Resource &rarr;</a>
      </div>

      <div class="resource-item">
        <span class="badge badge-audit">Talent Development / TM</span>
        <h3 style="margin-top: 0.4rem;">${plan.core_tm.title}</h3>
        <div class="resource-meta">Provider: <strong>${plan.core_tm.provider}</strong> &bull; Duration: <strong>${plan.core_tm.duration}</strong></div>
        <p style="font-size: 0.88rem; margin-bottom: 0.5rem;">${plan.core_tm.summary}</p>
        <div class="app-box" style="border-left-color: #9333ea;">
          <strong style="color: #7e22ce;">Practical Application:</strong> ${plan.core_tm.practical_application}
        </div>
        <a href="${plan.core_tm.url}" class="btn" target="_blank">Access Resource &rarr;</a>
      </div>

      <div class="resource-item">
        <span class="badge badge-free">Broader HR / Digital</span>
        <h3 style="margin-top: 0.4rem;">${plan.core_broader.title}</h3>
        <div class="resource-meta">Provider: <strong>${plan.core_broader.provider}</strong> &bull; Duration: <strong>${plan.core_broader.duration}</strong></div>
        <p style="font-size: 0.88rem;">${plan.core_broader.summary}</p>
        <a href="${plan.core_broader.url}" class="btn" target="_blank">Access Resource &rarr;</a>
      </div>

      <div style="background: #fdf4ff; border: 1px solid #f0abfc; border-radius: 8px; padding: 1.25rem; margin-top: 1.5rem;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #86198f; text-transform: uppercase;">Weekly Practical Challenge (${plan.challenge.minutes} mins)</div>
        <h4 style="margin: 0.25rem 0 0.5rem 0; color: #0f172a;">${plan.challenge.title}</h4>
        <p style="font-size: 0.88rem; margin-bottom: 0.5rem;">${plan.challenge.instructions}</p>
        <div style="font-size: 0.85rem; background: #ffffff; padding: 0.5rem 0.75rem; border-radius: 4px;"><strong>Deliverable:</strong> ${plan.challenge.deliverable}</div>
      </div>
    `;
  }

  // Render Competencies
  const compContainer = document.getElementById("competencies-container");
  if (compContainer && data.competencies) {
    compContainer.innerHTML = data.competencies.slice(0, 8).map(c => `
      <div class="comp-bar">
        <div class="comp-header">
          <span>${c.name}</span>
          <span style="color: #64748b; font-size: 0.8rem;">Level ${c.current_level} / ${c.target_level}</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width: ${(c.current_level / 5) * 100}%;"></div>
        </div>
      </div>
    `).join("");
  }

  // Render Portfolio Artifacts
  const portfolioContainer = document.getElementById("portfolio-container");
  if (portfolioContainer && data.portfolio_items) {
    portfolioContainer.innerHTML = data.portfolio_items.map(item => `
      <div style="border-bottom: 1px solid #e2e8f0; padding-bottom: 0.75rem; margin-bottom: 0.75rem;">
        <div style="font-weight: 700; font-size: 0.9rem; color: #0f172a;">${item.title}</div>
        <div style="font-size: 0.8rem; color: #64748b;">${item.category} &bull; ${item.date_created}</div>
        <p style="font-size: 0.82rem; color: #475569; margin-top: 0.2rem;">${item.impact_summary}</p>
      </div>
    `).join("");
  }
}

function getFallbackData() {
  return {
    last_updated_lagos: "Monday, 24 August 2026",
    user: { name: "Emuesiri Jessica Agbabune", role: "Head / L&D Manager", organization: "TD Africa" },
    career_progression: { current_stage: "Stage 3: Strategic Learning & Capability Development" },
    history_summary: { completed: 4, total_learning_minutes: 240 },
    portfolio_items: [
      { title: "TD Africa Enterprise TNA Framework & Audit Instrument", category: "Learning & Development", date_created: "2026-07-15", impact_summary: "Standardized annual skill-gap assessment across 6 departments." },
      { title: "SIMBA Spark Microlearning Architecture Playbook", category: "Digital HR", date_created: "2026-08-01", impact_summary: "Increased weekly active learning adoption through structured bite-sized modules." }
    ],
    competencies: [
      { name: "L&D Strategy", current_level: 4, target_level: 5 },
      { name: "Training Needs Analysis", current_level: 4, target_level: 5 },
      { name: "Succession Planning", current_level: 2, target_level: 5 },
      { name: "People Analytics", current_level: 2, target_level: 4 },
      { name: "AI for HR", current_level: 3, target_level: 5 }
    ]
  };
}
