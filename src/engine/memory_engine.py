"""
Recommendation Memory & Learning History Engine.
Maintains persistent memory of recommendations, completed courses, skipped items, and feedback.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.models import Resource, LearningStatus
from src.utils.logger import get_logger
from src.utils.dates import to_iso_string
from src.utils.validator import normalize_url

logger = get_logger("memory_engine")


class MemoryEngine:
    def __init__(self, history_file: Optional[Path] = None):
        if history_file is None:
            self.history_file = Path(__file__).resolve().parent.parent.parent / "data" / "learning_history.json"
        else:
            self.history_file = Path(history_file)
        self.data = self._load()

    def _get_default_state(self) -> Dict[str, Any]:
        return {
            "user": "Emuesiri Jessica Agbabune",
            "last_updated": to_iso_string(),
            "summary": {
                "total_recommended": 0,
                "completed": 0,
                "in_progress": 0,
                "applied": 0,
                "skipped": 0,
                "total_learning_minutes": 0
            },
            "history": [],
            "feedback_penalties": {
                "skipped_topics": {},
                "skipped_providers": {},
                "highly_rated_topics": {}
            }
        }

    def _load(self) -> Dict[str, Any]:
        if not self.history_file.exists():
            return self._get_default_state()
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load learning history: {e}. Reinitializing default state.")
            return self._get_default_state()

    def save(self) -> None:
        """Persists learning history to JSON file."""
        self.data["last_updated"] = to_iso_string()
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get_feedback_penalties(self) -> Dict[str, Any]:
        return self.data.setdefault("feedback_penalties", {
            "skipped_topics": {},
            "skipped_providers": {},
            "highly_rated_topics": {}
        })

    def is_recently_recommended(self, resource: Resource) -> bool:
        """Checks if a resource has been recommended in the past."""
        norm = normalize_url(resource.url)
        for entry in self.data.get("history", []):
            if normalize_url(entry.get("url", "")) == norm:
                return True
        return False

    def record_recommendation(self, resource: Resource, week_number: int) -> None:
        """Logs a recommended resource into persistent history."""
        norm = normalize_url(resource.url)
        history = self.data.setdefault("history", [])

        # Check if already present
        for entry in history:
            if normalize_url(entry.get("url", "")) == norm:
                entry["last_recommended_week"] = week_number
                return

        history.append({
            "title": resource.title,
            "provider": resource.provider,
            "url": norm,
            "type": resource.type.value if hasattr(resource.type, "value") else str(resource.type),
            "pricing_type": resource.pricing_type.value if hasattr(resource.pricing_type, "value") else str(resource.pricing_type),
            "topics": resource.topics,
            "career_stage": resource.career_stage,
            "relevance_score": resource.relevance_score,
            "week_recommended": week_number,
            "date_recommended": to_iso_string(),
            "status": LearningStatus.NOT_STARTED.value,
            "rating": None,
            "key_learning": "",
            "workplace_application": "",
            "portfolio_evidence": ""
        })
        self.data["summary"]["total_recommended"] = len(history)

    def record_feedback(
        self,
        url: str,
        status: LearningStatus,
        rating: Optional[int] = None,
        key_learning: str = "",
        application: str = "",
        evidence: str = "",
        duration_minutes: int = 0
    ) -> bool:
        """
        Updates learning status, rating, and notes for a resource.
        Adjusts topic penalties and summary statistics.
        """
        norm = normalize_url(url)
        found = False
        penalties = self.get_feedback_penalties()

        for entry in self.data.get("history", []):
            if normalize_url(entry.get("url", "")) == norm:
                old_status = entry.get("status")
                entry["status"] = status.value
                if rating is not None:
                    entry["rating"] = rating
                if key_learning:
                    entry["key_learning"] = key_learning
                if application:
                    entry["workplace_application"] = application
                if evidence:
                    entry["portfolio_evidence"] = evidence
                if status in [LearningStatus.COMPLETED, LearningStatus.APPLIED]:
                    entry["date_completed"] = to_iso_string()
                    self.data["summary"]["total_learning_minutes"] += duration_minutes

                # Handle penalties & boosts
                topics = entry.get("topics", [])
                if status == LearningStatus.SKIPPED:
                    for t in topics:
                        penalties["skipped_topics"][t] = penalties["skipped_topics"].get(t, 0) + 1
                elif rating and rating >= 4:
                    for t in topics:
                        penalties["highly_rated_topics"][t] = penalties["highly_rated_topics"].get(t, 0) + 1

                found = True
                break

        if found:
            # Recompute summary counts
            counts = {
                "completed": 0, "in_progress": 0, "applied": 0, "skipped": 0, "not_started": 0
            }
            for entry in self.data.get("history", []):
                st = entry.get("status", "").lower()
                if "completed" in st:
                    counts["completed"] += 1
                elif "in progress" in st:
                    counts["in_progress"] += 1
                elif "applied" in st:
                    counts["applied"] += 1
                elif "skipped" in st:
                    counts["skipped"] += 1
                else:
                    counts["not_started"] += 1

            self.data["summary"]["completed"] = counts["completed"]
            self.data["summary"]["in_progress"] = counts["in_progress"]
            self.data["summary"]["applied"] = counts["applied"]
            self.data["summary"]["skipped"] = counts["skipped"]
            self.save()
            return True
        return False
