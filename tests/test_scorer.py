from src.models import Resource, ResourceType, PricingType, PriorityLevel
from src.engine.scorer import Scorer


def test_scorer_calculation():
    scorer = Scorer()

    resource = Resource(
        title="Strategic Talent Management & Succession Planning Masterclass",
        provider="Harvard Business School",
        type=ResourceType.COURSE,
        url="https://example.com/talent",
        date_published="2026-08-20",
        date_discovered="2026-08-24",
        duration="1 hour",
        cost="100% Free",
        pricing_type=PricingType.FREE_CONTENT,
        topics=["Talent Management", "Succession Planning", "Leadership Development"],
        career_stage="Stage 4: Talent Development & Talent Management",
        tier=1,
        summary="Deep dive into 9-box grids, talent reviews, and leadership pipeline building."
    )

    score = scorer.calculate_score(resource)
    assert 85.0 <= score <= 100.0
    assert resource.score_breakdown["talent_management"] >= 90.0
    assert resource.score_breakdown["free_accessibility"] == 100.0

    priority = scorer.get_priority_level(score)
    assert priority in [PriorityLevel.CRITICAL, PriorityLevel.HIGH]


def test_scorer_feedback_penalties():
    scorer = Scorer()
    resource = Resource(
        title="General Motivational Quotes",
        provider="Blog",
        type=ResourceType.REPORT,
        url="https://example.com/blog",
        date_published="2026-01-01",
        date_discovered="2026-08-24",
        duration="5 mins",
        cost="Paid",
        pricing_type=PricingType.PAID_CONTENT,
        topics=["General Motivation"],
        career_stage="Stage 1: L&D Foundations",
        tier=3
    )

    penalties = {"skipped_topics": {"General Motivation": 3}}
    score = scorer.calculate_score(resource, feedback_penalties=penalties)
    assert score < 60.0
    assert scorer.get_priority_level(score) == PriorityLevel.IGNORE
