import pytest
from src.models import Resource, ResourceType, PricingType
from src.search.deduplicator import Deduplicator


def test_deduplication(tmp_path):
    temp_file = tmp_path / "seen.json"
    dedup = Deduplicator(data_file=temp_file)

    res1 = Resource(
        title="Predictive People Analytics with Power BI",
        provider="Microsoft",
        type=ResourceType.COURSE,
        url="https://example.com/course?utm_source=twitter&utm_medium=social",
        date_published="2026-08-20",
        date_discovered="2026-08-24",
        duration="2 hours",
        cost="100% Free",
        pricing_type=PricingType.FREE_CONTENT,
        topics=["People Analytics"],
        career_stage="Stage 3"
    )

    is_dup, _ = dedup.is_duplicate(res1)
    assert not is_dup

    dedup.mark_seen(res1)
    dedup.save()

    # Test exact URL duplicate (with different tracking param)
    res2 = Resource(
        title="Predictive People Analytics with Power BI",
        provider="Microsoft",
        type=ResourceType.COURSE,
        url="https://example.com/course?utm_campaign=summer",
        date_published="2026-08-20",
        date_discovered="2026-08-24",
        duration="2 hours",
        cost="100% Free",
        pricing_type=PricingType.FREE_CONTENT,
        topics=["People Analytics"],
        career_stage="Stage 3"
    )

    is_dup2, reason2 = dedup.is_duplicate(res2)
    assert is_dup2
    assert "Duplicate URL" in reason2

    # Test title similarity duplicate
    res3 = Resource(
        title="Predictive People Analytics in Power BI Masterclass",
        provider="Other",
        type=ResourceType.COURSE,
        url="https://different-domain.com/another-link",
        date_published="2026-08-20",
        date_discovered="2026-08-24",
        duration="2 hours",
        cost="100% Free",
        pricing_type=PricingType.FREE_CONTENT,
        topics=["People Analytics"],
        career_stage="Stage 3"
    )

    is_dup3, reason3 = dedup.is_duplicate(res3)
    assert is_dup3
    assert "similarity" in reason3.lower() or "title" in reason3.lower()
