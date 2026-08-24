"""
Nigeria & Africa HR / Talent Development Collector.
Monitors CIPM Nigeria, African HR conferences, and local workforce trends.
"""

from typing import List, Dict, Any
import requests
import feedparser

from src.models import Resource, ResourceType, PricingType
from src.utils.logger import get_logger
from src.utils.dates import to_iso_string, parse_date
from src.utils.validator import sanitize_text, normalize_url
from .base import BaseCollector

logger = get_logger("collector.africa")


class AfricaCollector(BaseCollector):
    def __init__(self, source_config: Dict[str, Any], timeout: int = 10):
        super().__init__(source_config)
        self.feed_url = source_config.get("feed_url")
        self.timeout = timeout
        self.default_topics = source_config.get("topics", ["HR Strategy", "Talent Management", "Nigeria HR"])

    def collect(self) -> List[Resource]:
        discovered: List[Resource] = []
        now_iso = to_iso_string()

        if self.feed_url:
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LAndDAlert-CareerBot/1.0"}
                resp = requests.get(self.feed_url, headers=headers, timeout=self.timeout)
                if resp.status_code == 200:
                    feed = feedparser.parse(resp.content)
                    for entry in feed.entries[:15]:
                        title = sanitize_text(getattr(entry, "title", ""))
                        link = getattr(entry, "link", "")
                        summary = sanitize_text(getattr(entry, "summary", ""))
                        if not title or not link:
                            continue

                        # Check relevance for HR, talent, leadership, workplace in Nigeria/Africa
                        title_sum = (title + " " + summary).lower()
                        if not any(k in title_sum for k in ["hr", "talent", "training", "leadership", "workforce", "cipm", "learning", "skills", "management"]):
                            continue

                        pub_val = getattr(entry, "published", "") or getattr(entry, "updated", "")
                        parsed_dt = parse_date(pub_val)
                        date_pub = to_iso_string(parsed_dt) if parsed_dt else now_iso

                        discovered.append(
                            Resource(
                                title=title,
                                provider=self.source_name,
                                type=ResourceType.CONFERENCE if "conference" in title.lower() else ResourceType.WEBINAR,
                                url=normalize_url(link),
                                date_published=date_pub,
                                date_discovered=now_iso,
                                duration="Virtual / Hybrid",
                                cost="Free / CIPM Member Access",
                                pricing_type=PricingType.FREE_EVENT,
                                topics=self.default_topics,
                                career_stage="Stage 4: Talent Development & Talent Management",
                                tier=self.tier,
                                summary=summary[:350],
                                why_relevant=f"Directly relevant to Nigerian enterprise HR context and CIPM professional development.",
                                location="Lagos, Nigeria / Virtual"
                            )
                        )
                    if discovered:
                        return discovered
            except Exception as e:
                logger.debug(f"Feed error for {self.source_name}: {e}")

        # Seed catalog for CIPM Nigeria and African Management events
        curated_africa = self._get_curated_africa()
        for item in curated_africa:
            discovered.append(
                Resource(
                    title=item["title"],
                    provider=item.get("provider", self.source_name),
                    type=item.get("type", ResourceType.WEBINAR),
                    url=normalize_url(item["url"]),
                    date_published=now_iso,
                    date_discovered=now_iso,
                    duration=item.get("duration", "90 mins"),
                    cost=item.get("cost", "100% Free Virtual Registration"),
                    pricing_type=item.get("pricing_type", PricingType.FREE_EVENT),
                    topics=item.get("topics", self.default_topics),
                    career_stage="Stage 4: Talent Development & Talent Management",
                    tier=1,
                    summary=item.get("summary", ""),
                    why_relevant=item.get("why_relevant", ""),
                    location=item.get("location", "Lagos, Nigeria (WAT) / Virtual")
                )
            )

        return discovered

    def _get_curated_africa(self) -> List[Dict[str, Any]]:
        sid = self.source_id
        if sid == "cipm_nigeria":
            return [
                {
                    "title": "CIPM Nigeria Strategic HR & Talent Management Virtual Masterclass",
                    "url": "https://cipmnigeria.net/events/",
                    "type": ResourceType.WEBINAR,
                    "duration": "2 hours",
                    "cost": "Free for CIPM Members & Associates",
                    "pricing_type": PricingType.FREE_EVENT,
                    "topics": ["HR Strategy", "Talent Management", "Labor Relations", "Nigeria HR"],
                    "summary": "High-level panel on strategic talent retention, currency volatility impacts on compensation, and workforce capability building in Nigeria.",
                    "why_relevant": "Tailored to Nigerian operating environment; builds direct ACIPM professional currency."
                }
            ]
        elif sid == "african_management_institute":
            return [
                {
                    "title": "Building Resilient African Talent & Managerial Capability",
                    "url": "https://www.africanmanagers.org/insights/",
                    "type": ResourceType.REPORT,
                    "duration": "20 mins read",
                    "cost": "100% Free",
                    "pricing_type": PricingType.FREE_CONTENT,
                    "topics": ["African Talent Management", "Leadership Development", "Capability Development"],
                    "summary": "Case studies and toolkits on scaling practical middle-management capabilities across fast-growing African enterprises.",
                    "why_relevant": "Provides practical management development frameworks suited for TD Africa's regional expansion."
                }
            ]
        return []
