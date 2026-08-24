from src.email.renderer import EmailRenderer
from src.engine.synthesizer import Synthesizer
from src.config_loader import ConfigLoader
from src.models import Resource, ResourceType, PricingType


def test_render_weekly_alert():
    loader = ConfigLoader()
    profile = loader.load_profile()
    renderer = EmailRenderer()

    resources = [
        Resource(
            title="Strategic Training Evaluation with Kirkpatrick Level 4",
            provider="OpenLearn",
            type=ResourceType.COURSE,
            url="https://open.edu/evaluation",
            date_published="2026-08-20",
            date_discovered="2026-08-24",
            duration="45 mins",
            cost="100% Free",
            pricing_type=PricingType.FREE_CONTENT,
            topics=["Learning & Development", "Training Evaluation"],
            career_stage="Stage 3"
        ),
        Resource(
            title="Succession Planning and Nine-Box Grids",
            provider="Coursera",
            type=ResourceType.COURSE,
            url="https://coursera.org/succession",
            date_published="2026-08-20",
            date_discovered="2026-08-24",
            duration="50 mins",
            cost="Course content: Free to audit",
            pricing_type=PricingType.FREE_AUDIT,
            topics=["Talent Management", "Succession Planning"],
            career_stage="Stage 4"
        ),
        Resource(
            title="Power BI Executive Dashboards for HR",
            provider="Microsoft Learn",
            type=ResourceType.COURSE,
            url="https://learn.microsoft.com/powerbi",
            date_published="2026-08-20",
            date_discovered="2026-08-24",
            duration="35 mins",
            cost="100% Free",
            pricing_type=PricingType.FREE_CERTIFICATE,
            topics=["People Analytics"],
            career_stage="Stage 3"
        )
    ]

    plan = Synthesizer.synthesize_weekly_plan(resources, week_num=34)
    subject, html_content, text_content = renderer.render_weekly_alert(plan, profile)

    assert "MY TALENT GROWTH PLAN | Week 34" in subject
    assert "HELLO EMUESIRI" in text_content
    assert "1. IMMEDIATE L&D SKILL" in text_content
    assert "TD AFRICA APPLICATION" in text_content
    assert "THIS WEEK'S PRACTICAL CHALLENGE" in text_content
    assert "THIS WEEK'S 3 ACTIONS" in text_content
    assert "<html" in html_content
    assert "Emuesiri Jessica Agbabune" in html_content


def test_render_urgent_alert():
    loader = ConfigLoader()
    profile = loader.load_profile()
    renderer = EmailRenderer()

    res = Resource(
        title="Harvard Executive Masterclass: Strategic Talent Leadership",
        provider="Harvard University",
        type=ResourceType.LECTURE,
        url="https://harvard.edu/live",
        date_published="2026-08-24",
        date_discovered="2026-08-24",
        duration="60 mins",
        cost="100% Free Virtual Masterclass",
        pricing_type=PricingType.FREE_EVENT,
        topics=["Leadership", "Talent Management"],
        career_stage="Stage 4",
        relevance_score=96.5,
        summary="Live masterclass with Harvard faculty on designing succession pipelines."
    )

    subject, html_content, text_content = renderer.render_urgent_alert(res, profile)
    assert "CRITICAL CAREER ALERT" in subject
    assert "Harvard Executive Masterclass" in text_content
    assert "96.5" in html_content
