"""
Career Gap & Progression Engine.
Manages the 27-competency matrix, stages 1-5, and career gap prioritization.
"""

from typing import List, Dict, Any, Optional
from src.models import Competency, Resource
from src.config_loader import ConfigLoader
from src.utils.logger import get_logger
from src.utils.dates import to_iso_string

logger = get_logger("career_engine")


class CareerEngine:
    def __init__(self, config_loader: Optional[ConfigLoader] = None):
        self.config_loader = config_loader or ConfigLoader()
        self.competencies: List[Competency] = self.config_loader.load_competencies()

    def get_priority_competencies(self) -> List[Competency]:
        """Returns competencies sorted by largest gap and critical priority."""
        priority_weight = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
        # Sort by (gap * priority_weight) descending
        sorted_comps = sorted(
            self.competencies,
            key=lambda c: (c.gap * priority_weight.get(c.priority, 1)),
            reverse=True
        )
        return sorted_comps

    def get_top_gaps(self, limit: int = 5) -> List[Competency]:
        """Returns the top N competency gaps needing development focus."""
        return [c for c in self.get_priority_competencies() if c.gap > 0][:limit]

    def update_competency_level(self, comp_id: str, new_level: int, practical_evidence: Optional[str] = None) -> bool:
        """
        Updates a user's competency level (1-5) only upon explicit user confirmation.
        """
        found = False
        for c in self.competencies:
            if c.id.lower() == comp_id.lower():
                c.current_level = max(1, min(5, new_level))
                if practical_evidence:
                    c.practical_evidence = practical_evidence
                c.last_reviewed = to_iso_string()[:10]
                found = True
                break

        if found:
            self.config_loader.save_competencies(self.competencies)
            logger.info(f"Updated competency {comp_id} to Level {new_level}")
            return True
        return False

    def generate_monthly_scorecard(self) -> Dict[str, Any]:
        """Generates the monthly capability scorecard (0-5 scale across core categories)."""
        category_levels: Dict[str, List[int]] = {}
        for c in self.competencies:
            category_levels.setdefault(c.category, []).append(c.current_level)

        scorecard = {}
        for cat, levels in category_levels.items():
            avg_score = round(sum(levels) / len(levels), 1)
            scorecard[cat] = {
                "score": avg_score,
                "max_score": 5.0,
                "competency_count": len(levels)
            }
        return scorecard
