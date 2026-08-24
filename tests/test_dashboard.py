import json
from pathlib import Path
from src.dashboard.generator import DashboardGenerator
from src.models import Resource, ResourceType, PricingType
from src.engine.synthesizer import Synthesizer


def test_dashboard_generation(tmp_path):
    # Copy config files to temp_dir first
    src_config = Path(__file__).resolve().parent.parent / "config"
    dest_config = tmp_path / "config"
    dest_config.mkdir(parents=True, exist_ok=True)
    for f in src_config.glob("*.yaml"):
        (dest_config / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")

    generator = DashboardGenerator(root_dir=tmp_path)

    # Mock sample plan
    resources = [
        Resource(
            title="Strategic Learning Analytics",
            provider="OpenLearn",
            type=ResourceType.COURSE,
            url="https://open.edu/test",
            date_published="2026-08-20",
            date_discovered="2026-08-24",
            duration="45 mins",
            cost="100% Free",
            pricing_type=PricingType.FREE_CONTENT,
            topics=["Learning & Development", "Learning Analytics"],
            career_stage="Stage 3"
        )
    ]
    plan = Synthesizer.synthesize_weekly_plan(resources, week_num=34)

    out_file = generator.generate(weekly_plan=plan, ranked_resources=resources)
    assert out_file.exists()

    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "user" in data
    assert "weekly_plan" in data
    assert data["weekly_plan"]["week_number"] == 34
    assert "competencies" in data
    assert len(data["competencies"]) == 27
