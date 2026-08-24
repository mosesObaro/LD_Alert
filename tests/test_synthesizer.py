from src.models import Resource, ResourceType, PricingType
from src.engine.synthesizer import Synthesizer


def test_synthesizer_weekly_plan():
    resources = [
        Resource(
            title="Strategic Training Needs Analysis Blueprint",
            provider="CIPD",
            type=ResourceType.COURSE,
            url="https://cipd.org/tna",
            date_published="2026-08-20",
            date_discovered="2026-08-24",
            duration="45 mins",
            cost="100% Free",
            pricing_type=PricingType.FREE_CONTENT,
            topics=["Learning & Development", "TNA"],
            career_stage="Stage 3"
        ),
        Resource(
            title="9-Box Talent Review & Succession Planning Masterclass",
            provider="HBR",
            type=ResourceType.LECTURE,
            url="https://hbr.org/talent",
            date_published="2026-08-20",
            date_discovered="2026-08-24",
            duration="40 mins",
            cost="Free Audit",
            pricing_type=PricingType.FREE_AUDIT,
            topics=["Talent Management", "Succession Planning"],
            career_stage="Stage 4"
        ),
        Resource(
            title="AI Tools & Microsoft Copilot for Enterprise HR",
            provider="Microsoft Learn",
            type=ResourceType.COURSE,
            url="https://learn.microsoft.com/ai",
            date_published="2026-08-20",
            date_discovered="2026-08-24",
            duration="30 mins",
            cost="Free",
            pricing_type=PricingType.FREE_CERTIFICATE,
            topics=["Future of Work & AI", "AI for HR"],
            career_stage="Stage 4"
        )
    ]

    plan = Synthesizer.synthesize_weekly_plan(resources, week_num=34)

    assert plan.week_number == 34
    assert plan.core_ld_resource is not None
    assert plan.core_talent_management_resource is not None
    assert plan.core_broader_skill_resource is not None

    # Check TD Africa enrichment
    assert "TD Africa" in plan.core_ld_resource.td_africa_application

    # Check challenge and portfolio
    assert plan.practical_challenge is not None
    assert 30 <= plan.practical_challenge.estimated_time_minutes <= 60
    assert plan.portfolio_evidence is not None
    assert len(plan.reflection_questions) == 3
    assert "learn" in plan.three_actions
    assert "apply" in plan.three_actions
    assert "capture" in plan.three_actions
