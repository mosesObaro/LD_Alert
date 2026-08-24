from src.engine.career_engine import CareerEngine
from src.config_loader import ConfigLoader


def test_career_engine_priority_gaps():
    loader = ConfigLoader()
    engine = CareerEngine(loader)

    top_gaps = engine.get_top_gaps(limit=5)
    assert len(top_gaps) == 5

    # Gaps must be greater than 0
    for g in top_gaps:
        assert g.gap > 0

    # Ensure critical competencies like succession planning and talent management are present
    gap_ids = [g.id for g in top_gaps]
    assert "succession_planning" in gap_ids


def test_monthly_scorecard():
    loader = ConfigLoader()
    engine = CareerEngine(loader)

    scorecard = engine.generate_monthly_scorecard()
    assert "Learning & Development" in scorecard
    assert "Talent Management" in scorecard
    assert "Human Resource Management" in scorecard

    for cat, data in scorecard.items():
        assert 0.0 <= data["score"] <= 5.0
        assert data["competency_count"] > 0
