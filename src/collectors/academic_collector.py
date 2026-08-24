"""
Academic & Strategic Research Collector.
Monitors newly published HR research, whitepapers, and surveys from WEF, McKinsey, Deloitte, and Journals.
"""

from typing import List, Dict, Any, Optional
import feedparser
import requests

from src.models import Resource, ResourceType, PricingType
from src.utils.logger import get_logger
from src.utils.dates import to_iso_string, parse_date
from src.utils.validator import sanitize_text, normalize_url
from .base import BaseCollector

logger = get_logger("collector.academic")


class AcademicCollector(BaseCollector):
    def __init__(self, source_config: Dict[str, Any], timeout: int = 10):
        super().__init__(source_config)
        self.feed_url = source_config.get("feed_url")
        self.timeout = timeout
        self.default_topics = source_config.get("topics", [])

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

                        # Check relevance for people, talent, leadership, future of work, AI, L&D
                        title_summary = (title + " " + summary).lower()
                        keywords = [
                            "talent", "skills", "learning", "workforce", "future of work",
                            "leadership", "people analytics", "generative ai", "organization",
                            "employee", "capability", "human capital", "productivity"
                        ]

                        if not any(k in title_summary for k in keywords):
                            continue

                        pub_val = getattr(entry, "published", "") or getattr(entry, "updated", "")
                        parsed_dt = parse_date(pub_val)
                        date_pub = to_iso_string(parsed_dt) if parsed_dt else now_iso

                        discovered.append(
                            Resource(
                                title=title,
                                provider=self.source_name,
                                type=ResourceType.REPORT,
                                url=normalize_url(link),
                                date_published=date_pub,
                                date_discovered=now_iso,
                                duration="25-35 mins read",
                                cost="100% Free Research",
                                pricing_type=PricingType.FREE_CONTENT,
                                topics=self.default_topics,
                                career_stage="Stage 4: Talent Development & Talent Management",
                                tier=self.tier,
                                summary=summary[:400],
                                why_relevant=f"Authoritative industry research by {self.source_name} on enterprise workforce transformation.",
                                difficulty="Strategic / Advanced"
                            )
                        )
                    if discovered:
                        return discovered
            except Exception as e:
                logger.debug(f"Feed error for {self.source_name}: {e}")

        # Seed research catalog fallback
        curated_research = self._get_curated_research()
        for item in curated_research:
            discovered.append(
                Resource(
                    title=item["title"],
                    provider=self.source_name,
                    type=ResourceType.REPORT,
                    url=normalize_url(item["url"]),
                    date_published=now_iso,
                    date_discovered=now_iso,
                    duration="30 mins read",
                    cost="100% Free Whitepaper",
                    pricing_type=PricingType.FREE_CONTENT,
                    topics=item.get("topics", self.default_topics),
                    career_stage="Stage 4: Talent Development & Talent Management",
                    tier=1,
                    summary=item.get("summary", ""),
                    why_relevant=item.get("why_relevant", ""),
                    difficulty="Executive / Strategic"
                )
            )

        return discovered

    def _get_curated_research(self) -> List[Dict[str, Any]]:
        sid = self.source_id
        if sid == "wef_future_of_jobs":
            return [
                {
                    "title": "Future of Jobs Report: Skills & Capability Transformation",
                    "url": "https://www.weforum.org/publications/the-future-of-jobs-report-2023/",
                    "topics": ["Future of Work", "Skills-based organizations", "AI in HR"],
                    "summary": "Global macroeconomic analysis of emerging and declining roles, top skills in demand, and enterprise reskilling strategies.",
                    "why_relevant": "Provides benchmark data for TD Africa TNA, capability blueprints, and executive presentations."
                }
            ]
        elif sid == "deloitte_insights":
            return [
                {
                    "title": "Global Human Capital Trends: Leading in a Boundaryless Workplace",
                    "url": "https://www2.deloitte.com/us/en/insights/focus/human-capital-trends.html",
                    "topics": ["Human Capital Trends", "Talent Management", "Internal Mobility"],
                    "summary": "Explores how leading organizations are transitioning to skills-based operating models and unlocking talent mobility.",
                    "why_relevant": "Directly guides the design of TD Africa internal mobility and succession frameworks."
                }
            ]
        elif sid == "mckinsey_org":
            return [
                {
                    "title": "The State of Organizations: Ten Shifts Transforming Workplace Leadership",
                    "url": "https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/the-state-of-organizations-2023",
                    "topics": ["Organizational Development", "Leadership Development", "AI Transformation"],
                    "summary": "Empirical survey across global organizations identifying key leadership, agility, and talent capability gaps.",
                    "why_relevant": "Provides executive arguments and benchmarks to justify strategic L&D budget allocations."
                }
            ]
        return []
