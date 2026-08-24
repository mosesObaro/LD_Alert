"""
Jinja2 Email Template Renderer for Weekly, Urgent, and Monthly Alerts.
"""

from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.models import WeeklyIntelligencePlan, Resource
from src.utils.logger import get_logger
from src.utils.dates import get_lagos_now

logger = get_logger("email_renderer")


class EmailRenderer:
    def __init__(self, templates_dir: Optional[Path] = None):
        if templates_dir is None:
            self.templates_dir = Path(__file__).resolve().parent / "templates"
        else:
            self.templates_dir = Path(templates_dir)

        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["html", "xml"])
        )

    def render_weekly_alert(self, plan: WeeklyIntelligencePlan, user_profile: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Renders weekly alert.
        Returns (subject, html_content, text_content).
        """
        subject = f"MY TALENT GROWTH PLAN | Week {plan.week_number} | {plan.theme.upper()}"

        user_info = user_profile.get("user", {})
        context = {
            "plan": plan,
            "user": user_info,
            "now_formatted": get_lagos_now().strftime("%A, %d %B %Y")
        }

        html_template = self.env.get_template("weekly_alert.html")
        text_template = self.env.get_template("weekly_alert.txt")

        html_content = html_template.render(**context)
        text_content = text_template.render(**context)

        return subject, html_content, text_content

    def render_urgent_alert(self, resource: Resource, user_profile: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Renders critical urgency alert.
        Returns (subject, html_content, text_content).
        """
        subject = f"CRITICAL CAREER ALERT | {resource.title[:60]}"

        user_info = user_profile.get("user", {})
        context = {
            "resource": resource,
            "user": user_info,
            "now_formatted": get_lagos_now().strftime("%A, %d %B %Y")
        }

        html_template = self.env.get_template("urgent_alert.html")
        text_template = self.env.get_template("urgent_alert.txt")

        html_content = html_template.render(**context)
        text_content = text_template.render(**context)

        return subject, html_content, text_content

    def render_monthly_digest(
        self,
        month_name: str,
        year: int,
        scorecard: Dict[str, Any],
        history_summary: Dict[str, Any],
        portfolio_count: int,
        trends: List[Any],
        research_items: List[Resource],
        top_gaps: List[Any],
        upcoming_events: List[Resource],
        user_profile: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """
        Renders monthly career intelligence digest.
        Returns (subject, html_content, text_content).
        """
        subject = f"MONTHLY CAREER INTELLIGENCE DIGEST | {month_name.upper()} {year}"

        user_info = user_profile.get("user", {})
        major_project = {
            "title": "Enterprise 9-Box Talent Review & Succession Framework Rollout",
            "objective": "Establish objective high-potential identification rubrics and pilot succession slates across 3 critical departments at TD Africa.",
            "deliverable": "Complete 9-Box Review Kit (Calibration Excel Guide + Meeting Protocol + Executive Board Deck)"
        }

        context = {
            "month_name": month_name,
            "year": year,
            "scorecard": scorecard,
            "history_summary": history_summary,
            "portfolio_count": portfolio_count,
            "trends": trends,
            "research_items": research_items,
            "major_project": major_project,
            "top_gaps": top_gaps,
            "upcoming_events": upcoming_events,
            "user": user_info
        }

        html_template = self.env.get_template("monthly_digest.html")
        text_template = self.env.get_template("monthly_digest.txt")

        html_content = html_template.render(**context)
        text_content = text_template.render(**context)

        return subject, html_content, text_content
