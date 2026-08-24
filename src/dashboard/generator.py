"""
Static Dashboard Data Generator.
Builds data/latest_summary.json powering the GitHub Pages interactive dashboard.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.models import WeeklyIntelligencePlan, Resource
from src.config_loader import ConfigLoader
from src.engine.career_engine import CareerEngine
from src.engine.memory_engine import MemoryEngine
from src.utils.dates import to_iso_string, format_lagos_time
from src.utils.logger import get_logger

logger = get_logger("dashboard_generator")


class DashboardGenerator:
    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent.parent
        self.data_dir = self.root_dir / "data"
        self.docs_dir = self.root_dir / "docs"
        self.config_loader = ConfigLoader(str(self.root_dir))
        self.career_engine = CareerEngine(self.config_loader)
        self.memory_engine = MemoryEngine(self.data_dir / "learning_history.json")

    def generate(
        self,
        weekly_plan: Optional[WeeklyIntelligencePlan] = None,
        ranked_resources: Optional[List[Resource]] = None
    ) -> Path:
        """Generates latest_summary.json in data/ and docs/ for GitHub Pages deployment."""
        profile = self.config_loader.load_profile()
        competencies = self.career_engine.get_priority_competencies()
        top_gaps = self.career_engine.get_top_gaps(limit=6)
        scorecard = self.career_engine.generate_monthly_scorecard()
        history_summary = self.memory_engine.data.get("summary", {})

        # Load portfolio
        portfolio_file = self.data_dir / "portfolio.json"
        portfolio_items = []
        if portfolio_file.exists():
            try:
                with open(portfolio_file, "r", encoding="utf-8") as f:
                    p_data = json.load(f)
                    portfolio_items = p_data.get("artifacts", [])
            except Exception as e:
                logger.debug(f"Could not load portfolio: {e}")

        # Top free learning catalog
        top_free = []
        if ranked_resources:
            top_free = [r.to_dict() for r in ranked_resources if r.relevance_score >= 75][:8]

        plan_dict = None
        if weekly_plan:
            plan_dict = {
                "week_number": weekly_plan.week_number,
                "theme": weekly_plan.theme,
                "why_matters": weekly_plan.why_matters,
                "core_ld": weekly_plan.core_ld_resource.to_dict(),
                "core_tm": weekly_plan.core_talent_management_resource.to_dict(),
                "core_broader": weekly_plan.core_broader_skill_resource.to_dict(),
                "challenge": {
                    "title": weekly_plan.practical_challenge.title,
                    "minutes": weekly_plan.practical_challenge.estimated_time_minutes,
                    "instructions": weekly_plan.practical_challenge.instructions,
                    "deliverable": weekly_plan.practical_challenge.deliverable
                },
                "portfolio_evidence": {
                    "artifact_type": weekly_plan.portfolio_evidence.artifact_type,
                    "description": weekly_plan.portfolio_evidence.description
                },
                "three_actions": weekly_plan.three_actions,
                "reflection_questions": weekly_plan.reflection_questions,
                "next_action": weekly_plan.next_action
            }

        user_info = dict(profile.get("user", {}))
        user_info.pop("email", None)  # Omit private email from public dashboard JSON

        payload = {
            "last_updated": to_iso_string(),
            "last_updated_lagos": format_lagos_time(),
            "user": user_info,
            "career_progression": profile.get("career_progression", {}),
            "weekly_plan": plan_dict,
            "competencies": [c.to_dict() for c in competencies],
            "top_gaps": [c.to_dict() for c in top_gaps],
            "scorecard": scorecard,
            "history_summary": history_summary,
            "portfolio_items": portfolio_items,
            "top_free_resources": top_free
        }

        # Write to data/latest_summary.json
        out_path = self.data_dir / "latest_summary.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        # Also mirror to docs/data.json so GitHub Pages can load it reliably via relative fetch
        docs_data_path = self.docs_dir / "data.json"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        with open(docs_data_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        logger.info(f"Dashboard data payload generated at {out_path} and {docs_data_path}")
        return out_path
