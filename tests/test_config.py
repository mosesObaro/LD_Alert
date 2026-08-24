import pytest
from pathlib import Path
from src.config_loader import ConfigLoader


def test_load_profile():
    loader = ConfigLoader()
    profile = loader.load_profile()

    assert "user" in profile
    assert profile["user"]["name"] == "Emuesiri Jessica Agbabune"
    assert profile["user"]["organization"] == "TD Africa"
    assert profile["user"]["timezone"] == "Africa/Lagos"
    assert "career_progression" in profile
    assert "learning_preferences" in profile


def test_load_sources():
    loader = ConfigLoader()
    sources = loader.load_sources()

    assert isinstance(sources, list)
    assert len(sources) >= 15

    # Verify key sources exist
    source_ids = [s["id"] for s in sources]
    assert "cipd_news" in source_ids
    assert "cipm_nigeria" in source_ids
    assert "mit_ocw" in source_ids
    assert "openlearn_ou" in source_ids


def test_load_competencies():
    loader = ConfigLoader()
    competencies = loader.load_competencies()

    assert isinstance(competencies, list)
    assert len(competencies) == 27

    comp_ids = [c.id for c in competencies]
    assert "succession_planning" in comp_ids
    assert "talent_management" in comp_ids
    assert "learning_roi" in comp_ids
    assert "ai_for_hr" in comp_ids

    # Check gap calculation
    for c in competencies:
        assert 1 <= c.current_level <= 5
        assert 1 <= c.target_level <= 5
        assert c.gap == max(0, c.target_level - c.current_level)


def test_load_scoring_weights():
    loader = ConfigLoader()
    weights_data = loader.load_scoring_weights()

    assert "weights" in weights_data
    w = weights_data["weights"]
    total_weights = sum(w.values())
    assert pytest.approx(total_weights, 0.01) == 1.0
