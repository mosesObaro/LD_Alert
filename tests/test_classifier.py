from src.engine.classifier import Classifier
from src.models import PricingType


def test_classify_pricing():
    # Coursera / edX
    assert Classifier.classify_pricing("Strategic Talent Management", "Great course", "Coursera") == PricingType.FREE_AUDIT
    assert Classifier.classify_pricing("Leading Change", "Audit available", "edX") == PricingType.FREE_AUDIT

    # Free certificate providers
    assert Classifier.classify_pricing("Leadership Principles", "Free statement", "OpenLearn") == PricingType.FREE_CERTIFICATE
    assert Classifier.classify_pricing("Power BI for HR", "Free modules", "Microsoft Learn") == PricingType.FREE_CERTIFICATE

    # YouTube / MIT OCW
    assert Classifier.classify_pricing("Executive Communication", "Video lecture", "YouTube") == PricingType.FREE_CONTENT
    assert Classifier.classify_pricing("Organizational Behavior", "Open courseware", "MIT OpenCourseWare") == PricingType.FREE_CONTENT

    # Webinars
    assert Classifier.classify_pricing("Future of Work Webinar 2026", "Live discussion", "CIPD") == PricingType.FREE_EVENT


def test_classify_topics():
    topics = Classifier.classify_topics(
        title="Predictive People Analytics & Retention Modeling",
        summary="Using Power BI and machine learning to forecast workforce attrition.",
        default_topics=[]
    )
    assert "People Analytics" in topics

    topics_tm = Classifier.classify_topics(
        title="Succession Planning and 9-Box Talent Review Calibration",
        summary="A practical guide to identifying high-potential talent pipelines.",
        default_topics=[]
    )
    assert "Talent Management" in topics_tm
    assert "Talent Development" in topics_tm


def test_classify_career_stage():
    stage_tm = Classifier.classify_career_stage(
        topics=["Talent Management", "Succession Planning"],
        title="Succession Planning & Talent Reviews"
    )
    assert stage_tm == "Stage 4: Talent Development & Talent Management"

    stage_ld = Classifier.classify_career_stage(
        topics=["L&D Strategy", "TNA"],
        title="Strategic Training Needs Analysis"
    )
    assert stage_ld == "Stage 3: Strategic Learning & Capability Development"
