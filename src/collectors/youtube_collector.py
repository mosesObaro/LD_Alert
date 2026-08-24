"""
YouTube Channel & University Public Lecture Collector.
Leverages direct YouTube Atom Feeds (zero API keys required).
"""

from typing import List, Dict, Any, Optional
import feedparser
import requests

from src.models import Resource, ResourceType, PricingType
from src.utils.logger import get_logger
from src.utils.dates import parse_date, to_iso_string
from src.utils.validator import sanitize_text, normalize_url
from .base import BaseCollector

logger = get_logger("collector.youtube")


class YouTubeCollector(BaseCollector):
    def __init__(self, source_config: Dict[str, Any], timeout: int = 10):
        super().__init__(source_config)
        self.channel_id = source_config.get("channel_id")
        self.timeout = timeout
        self.default_topics = source_config.get("topics", [])
        self.channel_feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={self.channel_id}" if self.channel_id else source_config.get("feed_url")

    def collect(self) -> List[Resource]:
        if not self.channel_feed_url:
            return []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LAndDAlert-CareerBot/1.0"
        }

        resp = requests.get(self.channel_feed_url, headers=headers, timeout=self.timeout)
        resp.raise_for_status()

        feed = feedparser.parse(resp.content)
        discovered: List[Resource] = []
        now_iso = to_iso_string()

        for entry in feed.entries[:20]:
            title = sanitize_text(getattr(entry, "title", ""))
            link = getattr(entry, "link", "")
            summary = sanitize_text(getattr(entry, "summary", ""))

            if not title or not link:
                continue

            # Check if relevant to leadership, talent, L&D, management, analytics, AI
            title_lower = title.lower()
            relevant_keywords = [
                "leadership", "talent", "management", "learning", "skills", "strategy",
                "analytics", "communication", "negotiation", "change", "culture", "ai",
                "hr", "people", "performance", "coaching", "executive", "organization",
                "future of work", "development"
            ]

            if not any(k in title_lower or k in summary.lower() for k in relevant_keywords):
                # Filter out irrelevant general video topics
                continue

            pub_date_val = getattr(entry, "published", "") or getattr(entry, "updated", "")
            parsed_dt = parse_date(pub_date_val)
            date_published = to_iso_string(parsed_dt) if parsed_dt else now_iso

            resource = Resource(
                title=f"{title} - [Public Lecture]",
                provider=f"{self.source_name} (YouTube)",
                type=ResourceType.LECTURE,
                url=normalize_url(link),
                date_published=date_published,
                date_discovered=now_iso,
                duration="30-45 mins",
                cost="100% Free Lecture",
                pricing_type=PricingType.FREE_CONTENT,
                topics=list(set(self.default_topics)),
                career_stage="Stage 3: Strategic Learning & Capability Development",
                tier=self.tier,
                summary=summary[:350] + ("..." if len(summary) > 350 else ""),
                why_relevant=f"High-caliber free academic lecture from {self.source_name} on executive capabilities.",
                difficulty="Advanced / Executive"
            )
            discovered.append(resource)

        return discovered
