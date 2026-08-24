"""
RSS and Atom Feed Collector for Professional Bodies, Research, and Journals.
"""

from typing import List, Dict, Any, Optional
import feedparser
import requests
from datetime import datetime

from src.models import Resource, ResourceType, PricingType
from src.utils.logger import get_logger
from src.utils.dates import parse_date, to_iso_string
from src.utils.validator import sanitize_text, normalize_url
from .base import BaseCollector

logger = get_logger("collector.rss")


class RSSCollector(BaseCollector):
    def __init__(self, source_config: Dict[str, Any], timeout: int = 10):
        super().__init__(source_config)
        self.feed_url = source_config.get("feed_url") or source_config.get("url")
        self.timeout = timeout
        self.category = source_config.get("category", "general")
        self.default_topics = source_config.get("topics", [])
        self.pricing_bias = source_config.get("pricing_bias", "mostly_free")

    def collect(self) -> List[Resource]:
        if not self.feed_url:
            return []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LAndDAlert-CareerBot/1.0"
        }

        # Fetch feed content with requests to ensure custom timeout and headers
        resp = requests.get(self.feed_url, headers=headers, timeout=self.timeout)
        resp.raise_for_status()

        feed = feedparser.parse(resp.content)
        discovered: List[Resource] = []

        now_iso = to_iso_string()

        for entry in feed.entries[:25]:  # Process up to 25 latest entries
            title = sanitize_text(getattr(entry, "title", ""))
            link = getattr(entry, "link", "")
            summary = sanitize_text(getattr(entry, "summary", "") or getattr(entry, "description", ""))

            if not title or not link:
                continue

            # Determine published date
            pub_date_val = getattr(entry, "published", "") or getattr(entry, "updated", "")
            parsed_dt = parse_date(pub_date_val)
            date_published = to_iso_string(parsed_dt) if parsed_dt else now_iso

            # Infer ResourceType
            res_type = ResourceType.REPORT
            title_lower = title.lower()
            if any(w in title_lower for w in ["webinar", "virtual session", "live session"]):
                res_type = ResourceType.WEBINAR
            elif any(w in title_lower for w in ["masterclass", "workshop"]):
                res_type = ResourceType.WORKSHOP
            elif any(w in title_lower for w in ["course", "module", "training"]):
                res_type = ResourceType.COURSE
            elif any(w in title_lower for w in ["lecture", "keynote", "address"]):
                res_type = ResourceType.LECTURE
            elif any(w in title_lower for w in ["framework", "toolkit", "guide", "template"]):
                res_type = ResourceType.TOOLKIT
            elif any(w in title_lower for w in ["podcast", "audio", "episode"]):
                res_type = ResourceType.PODCAST

            # Infer PricingType based on pricing_bias and text
            pricing_type = PricingType.FREE_CONTENT
            if "webinar" in title_lower or res_type == ResourceType.WEBINAR:
                pricing_type = PricingType.FREE_EVENT
            elif self.pricing_bias == "always_free":
                pricing_type = PricingType.FREE_CONTENT
            elif self.pricing_bias == "free_audit":
                pricing_type = PricingType.FREE_AUDIT
            elif any(w in title_lower or w in summary.lower() for w in ["paid", "tuition", "fee required", "$"]):
                pricing_type = PricingType.PAID_CONTENT

            resource = Resource(
                title=title,
                provider=self.source_name,
                type=res_type,
                url=normalize_url(link),
                date_published=date_published,
                date_discovered=now_iso,
                duration="45-60 mins" if res_type in [ResourceType.WEBINAR, ResourceType.LECTURE] else "Self-paced",
                cost="100% Free" if pricing_type in [PricingType.FREE_CONTENT, PricingType.FREE_EVENT] else "Free Audit Available",
                pricing_type=pricing_type,
                topics=list(set(self.default_topics)),
                career_stage="Stage 3: Strategic Learning & Capability Development",
                tier=self.tier,
                summary=summary[:400] + ("..." if len(summary) > 400 else ""),
                why_relevant=f"Published by Tier-{self.tier} authority ({self.source_name}) addressing core capability areas."
            )
            discovered.append(resource)

        return discovered
