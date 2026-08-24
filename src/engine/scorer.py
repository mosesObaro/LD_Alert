"""
Multi-Factor 0-100 Relevance Scoring Engine.
Calculates:
- Career Relevance (25%)
- Practical L&D Relevance to TD Africa (20%)
- Talent Management Relevance (15%)
- Quality & Credibility (15%)
- Free/Affordable Accessibility (10%)
- Recency (5%)
- Depth & Value (10%)
"""

from typing import Dict, Any, List, Optional
from src.models import Resource, PriorityLevel, PricingType, ResourceType
from src.utils.dates import days_since
from src.utils.logger import get_logger

logger = get_logger("scorer")


class Scorer:
    def __init__(self, config_weights: Optional[Dict[str, Any]] = None):
        self.weights = {
            "career_relevance": 0.25,
            "practical_ld_relevance": 0.20,
            "talent_management": 0.15,
            "quality_credibility": 0.15,
            "free_accessibility": 0.10,
            "recency": 0.05,
            "depth_value": 0.10
        }
        if config_weights and "weights" in config_weights:
            self.weights.update(config_weights["weights"])

    def calculate_score(self, resource: Resource, user_stage: str = "Stage 3", feedback_penalties: Optional[Dict[str, Any]] = None) -> float:
        """Calculates 0-100 score and attaches breakdown to resource."""
        text = f"{resource.title} {resource.summary} {' '.join(resource.topics)}".lower()

        # 1. Career Relevance (25%) - Progression towards Talent Management & Strategic HR
        s_career = 60.0
        if any(k in text for k in ["talent development", "strategic hr", "leadership pipeline", "competency", "succession", "hrbp"]):
            s_career = 95.0
        elif any(k in text for k in ["people analytics", "ai for hr", "organizational development", "change management"]):
            s_career = 90.0
        elif any(k in text for k in ["l&d strategy", "learning analytics", "capability"]):
            s_career = 85.0

        # 2. Practical L&D Relevance (20%) - Direct application to TD Africa Head/L&D Manager role
        s_practical = 50.0
        if any(k in text for k in ["tna", "training needs", "learning evaluation", "kirkpatrick", "microlearning", "lms", "roi", "certification"]):
            s_practical = 95.0
        elif any(k in text for k in ["adult learning", "learning culture", "facilitation", "power bi", "dashboard"]):
            s_practical = 85.0
        elif any(k in text for k in ["learning design", "instructional design", "onboarding"]):
            s_practical = 75.0

        # 3. Talent Management Relevance (15%) - 9-box, succession, critical roles, workforce planning
        s_tm = 40.0
        if any(k in text for k in ["succession planning", "talent review", "nine-box", "9-box", "critical role", "talent pool"]):
            s_tm = 100.0
        elif any(k in text for k in ["talent management", "talent development", "high-potential", "internal mobility"]):
            s_tm = 90.0
        elif any(k in text for k in ["performance management", "workforce planning", "retention"]):
            s_tm = 75.0

        # 4. Quality & Credibility (15%)
        # Tier 1 = 95, Tier 2 = 85, Tier 3 = 70, Tier 4 = 35
        tier_map = {1: 95.0, 2: 85.0, 3: 70.0, 4: 35.0}
        s_credibility = tier_map.get(resource.tier, 80.0)
        # Bonus for prestigious universities or CIPD / CIPM / SHRM
        if any(b in resource.provider.lower() for b in ["cipd", "cipm", "shrm", "atd", "harvard", "mit", "stanford", "mckinsey", "wef"]):
            s_credibility = min(100.0, s_credibility + 5.0)

        # 5. Free Accessibility (10%) - Free-First Rule
        pricing_map = {
            PricingType.FREE_CONTENT: 100.0,
            PricingType.FREE_CERTIFICATE: 100.0,
            PricingType.FREE_EVENT: 100.0,
            PricingType.FREE_AUDIT: 95.0,
            PricingType.PAID_CERTIFICATE: 70.0,
            PricingType.PAID_CONTENT: 30.0
        }
        s_free = pricing_map.get(resource.pricing_type, 85.0)

        # 6. Recency (5%)
        # < 7 days = 100, < 30 days = 85, < 90 days = 70, evergreen = 75
        days = days_since(resource.date_published)
        if days <= 7:
            s_recency = 100.0
        elif days <= 30:
            s_recency = 85.0
        elif days <= 90:
            s_recency = 70.0
        else:
            s_recency = 65.0  # Evergreen

        # 7. Depth & Value (10%)
        s_depth = 75.0
        if resource.type in [ResourceType.COURSE, ResourceType.LECTURE, ResourceType.WORKSHOP, ResourceType.REPORT]:
            s_depth = 90.0
        if "masterclass" in resource.title.lower() or "framework" in resource.title.lower():
            s_depth = 95.0

        # Weighted calculation
        total_score = (
            (self.weights["career_relevance"] * s_career) +
            (self.weights["practical_ld_relevance"] * s_practical) +
            (self.weights["talent_management"] * s_tm) +
            (self.weights["quality_credibility"] * s_credibility) +
            (self.weights["free_accessibility"] * s_free) +
            (self.weights["recency"] * s_recency) +
            (self.weights["depth_value"] * s_depth)
        )

        # Apply memory feedback penalties (e.g. if user repeatedly skipped topic)
        if feedback_penalties:
            skipped_topics = feedback_penalties.get("skipped_topics", {})
            for topic in resource.topics:
                if topic in skipped_topics and skipped_topics[topic] >= 2:
                    total_score = max(0.0, total_score - (skipped_topics[topic] * 5.0))

            rated_topics = feedback_penalties.get("highly_rated_topics", {})
            for topic in resource.topics:
                if topic in rated_topics:
                    total_score = min(100.0, total_score + 3.0)

        resource.relevance_score = round(total_score, 1)
        resource.score_breakdown = {
            "career_relevance": s_career,
            "practical_ld_relevance": s_practical,
            "talent_management": s_tm,
            "quality_credibility": s_credibility,
            "free_accessibility": s_free,
            "recency": s_recency,
            "depth_value": s_depth,
            "total_score": round(total_score, 1)
        }

        return resource.relevance_score

    @staticmethod
    def get_priority_level(score: float) -> PriorityLevel:
        if score >= 90.0:
            return PriorityLevel.CRITICAL
        elif score >= 80.0:
            return PriorityLevel.HIGH
        elif score >= 70.0:
            return PriorityLevel.GOOD
        elif score >= 60.0:
            return PriorityLevel.LOW
        else:
            return PriorityLevel.IGNORE
