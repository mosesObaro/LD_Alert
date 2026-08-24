"""
Platform Collector for Open Educational Resources, University Courseware, and Tech Academies.
(OpenLearn, MIT OCW, Harvard Online, Coursera Free Audit, edX, Microsoft Learn, IBM SkillsBuild)
"""

from typing import List, Dict, Any
import requests
import feedparser

from src.models import Resource, ResourceType, PricingType
from src.utils.logger import get_logger
from src.utils.dates import to_iso_string, parse_date
from src.utils.validator import sanitize_text, normalize_url
from .base import BaseCollector

logger = get_logger("collector.platform")


class PlatformCollector(BaseCollector):
    def __init__(self, source_config: Dict[str, Any], timeout: int = 10):
        super().__init__(source_config)
        self.feed_url = source_config.get("feed_url")
        self.timeout = timeout
        self.pricing_bias = source_config.get("pricing_bias", "always_free")
        self.default_topics = source_config.get("topics", [])

    def collect(self) -> List[Resource]:
        discovered: List[Resource] = []
        now_iso = to_iso_string()

        # If a direct feed URL is available, parse it
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

                        pub_val = getattr(entry, "published", "") or getattr(entry, "updated", "")
                        parsed_dt = parse_date(pub_val)
                        date_pub = to_iso_string(parsed_dt) if parsed_dt else now_iso

                        pricing_type = PricingType.FREE_CONTENT
                        cost_str = "100% Free"
                        if self.pricing_bias == "free_audit":
                            pricing_type = PricingType.FREE_AUDIT
                            cost_str = "Course content: Free to audit (Certificate: Paid)"

                        discovered.append(
                            Resource(
                                title=title,
                                provider=self.source_name,
                                type=ResourceType.COURSE,
                                url=normalize_url(link),
                                date_published=date_pub,
                                date_discovered=now_iso,
                                duration="2-4 hours/week",
                                cost=cost_str,
                                pricing_type=pricing_type,
                                topics=self.default_topics,
                                career_stage="Stage 3: Strategic Learning & Capability Development",
                                tier=self.tier,
                                summary=summary[:350],
                                why_relevant=f"Structured curriculum from {self.source_name} supporting target competency growth."
                            )
                        )
                    if discovered:
                        return discovered
            except Exception as e:
                logger.debug(f"Feed fetch for platform {self.source_name} failed: {e}. Falling back to curated catalog.")

        # Fallback to high-value curated seed catalog if feeds are dynamic/sitemap-based
        curated_catalog = self._get_platform_curated_catalog()
        for item in curated_catalog:
            pricing_type = PricingType.FREE_AUDIT if self.pricing_bias == "free_audit" else PricingType.FREE_CONTENT
            cost_str = "Course content: Free to audit (Certificate: Paid)" if pricing_type == PricingType.FREE_AUDIT else "100% Free"
            discovered.append(
                Resource(
                    title=item["title"],
                    provider=item.get("provider", self.source_name),
                    type=item.get("type", ResourceType.COURSE),
                    url=normalize_url(item["url"]),
                    date_published=now_iso,
                    date_discovered=now_iso,
                    duration=item.get("duration", "4-6 hours"),
                    cost=cost_str,
                    pricing_type=pricing_type,
                    topics=item.get("topics", self.default_topics),
                    career_stage=item.get("career_stage", "Stage 3: Strategic Learning & Capability Development"),
                    tier=self.tier,
                    summary=item.get("summary", ""),
                    why_relevant=item.get("why_relevant", ""),
                    difficulty=item.get("difficulty", "Intermediate")
                )
            )

        return discovered

    def _get_platform_curated_catalog(self) -> List[Dict[str, Any]]:
        """Curated high-value open learning resources mapped to the user's specific development areas."""
        sid = self.source_id
        if sid == "openlearn_ou":
            return [
                {
                    "title": "Developing Leadership Character and Capability",
                    "url": "https://www.open.edu/openlearn/money-business/leadership-management/developing-leadership-practice/content-section-0",
                    "duration": "15 hours (Self-paced)",
                    "topics": ["Leadership Development", "Executive Presence", "Adult Learning"],
                    "summary": "Free open course examining the psychological foundations of leadership, behavioral transformation, and team empowerment.",
                    "why_relevant": "Provides rigorous academic frameworks on leadership capability development with free statement of participation."
                },
                {
                    "title": "Workplace Learning and Capability Development",
                    "url": "https://www.open.edu/openlearn/education-development/learning-workplace/content-section-0",
                    "duration": "12 hours (Self-paced)",
                    "topics": ["L&D Strategy", "Adult Learning", "Learning Culture"],
                    "summary": "Explores how organizations build collective capability, foster informal learning networks, and embed continuous workplace learning.",
                    "why_relevant": "Directly supports TD Africa learning culture transformation and microlearning strategy."
                }
            ]
        elif sid == "mit_ocw":
            return [
                {
                    "title": "People and Organizations (MIT Sloan Management)",
                    "url": "https://ocw.mit.edu/courses/15-668-people-and-organizations-fall-2010/",
                    "duration": "Full Semester Courseware",
                    "topics": ["Organizational Development", "Talent Management", "Strategic HR"],
                    "summary": "MIT Sloan master's level course covering organizational sociology, strategic human resource systems, and talent management.",
                    "why_relevant": "World-class curriculum on how high-performance enterprise talent systems drive commercial execution."
                }
            ]
        elif sid == "harvard_online_free":
            return [
                {
                    "title": "Exercising Leadership: Foundational Principles",
                    "url": "https://pll.harvard.edu/course/exercising-leadership-foundational-principles",
                    "duration": "4 weeks (2-3 hrs/week)",
                    "topics": ["Leadership Development", "Change Leadership", "Stakeholder Management"],
                    "summary": "Harvard Kennedy School executive framework on navigating complex change, stakeholder politics, and adaptive leadership.",
                    "why_relevant": "Equips L&D managers with executive change-management influence tools."
                }
            ]
        elif sid == "microsoft_learn_ai_hr":
            return [
                {
                    "title": "Empower Workforce Productivity with Microsoft 365 Copilot & AI",
                    "url": "https://learn.microsoft.com/en-us/training/modules/empower-workforce-copilot/",
                    "duration": "1 hour module",
                    "topics": ["AI for HR", "Generative AI", "Digital HR"],
                    "summary": "Practical training on leveraging AI assistants to streamline workplace workflows, synthesize HR documents, and accelerate learning.",
                    "why_relevant": "Directly applicable to TD Africa AI Academy and modern digital HR workflow design."
                },
                {
                    "title": "Build Interactive Dashboards in Power BI for People Analytics",
                    "url": "https://learn.microsoft.com/en-us/training/paths/create-use-analytics-reports-power-bi/",
                    "duration": "3 hours",
                    "topics": ["People Analytics", "Learning Analytics", "L&D Dashboards"],
                    "summary": "Step-by-step guidance on connecting HR datasets, building DAX measures, and visualizing talent metrics in executive dashboards.",
                    "why_relevant": "Provides the technical foundation to build automated TD Africa L&D and Talent Management dashboards."
                }
            ]
        elif sid == "ibm_skillsbuild":
            return [
                {
                    "title": "Artificial Intelligence Fundamentals & Responsible AI",
                    "url": "https://skillsbuild.org/students/course-catalog/artificial-intelligence",
                    "duration": "2.5 hours",
                    "topics": ["AI for HR", "Digital HR", "AI Governance"],
                    "summary": "Foundational certification on AI concepts, natural language processing, and ethical considerations in enterprise AI deployment.",
                    "why_relevant": "Critical background for spearheading AI-driven talent development and TD Africa AI Academy."
                }
            ]
        elif sid == "coursera_hr_ld":
            return [
                {
                    "title": "Strategic Talent Management (University of Michigan)",
                    "url": "https://www.coursera.org/learn/talent-management",
                    "duration": "4 weeks (Free to audit lectures and readings)",
                    "topics": ["Talent Management", "Succession Planning", "Talent Reviews", "Nine-Box Grid"],
                    "summary": "Comprehensive university course on identifying critical talent, running talent review boards, and building succession slates.",
                    "why_relevant": "Directly prepares the user for Stage 4: Talent Development & Talent Management leadership."
                },
                {
                    "title": "People Analytics: Transforming HR with Data (Wharton)",
                    "url": "https://www.coursera.org/learn/wharton-people-analytics",
                    "duration": "4 weeks (Free to audit)",
                    "topics": ["People Analytics", "Learning Analytics", "Workforce Planning"],
                    "summary": "Wharton executive programme on using data science to manage performance, predict attrition, and optimize capability development.",
                    "why_relevant": "Equips the user to build data-driven business cases and executive talent scorecards."
                }
            ]
        elif sid == "edx_hr_leadership":
            return [
                {
                    "title": "Leading Organizational Change (Columbia University)",
                    "url": "https://www.edx.org/learn/business-administration/columbia-university-leading-organizational-change",
                    "duration": "4 weeks (Free to audit)",
                    "topics": ["Change Management", "Organizational Development", "Leadership"],
                    "summary": "Columbia University framework for diagnosing organizational friction, architecting change coalitions, and sustaining new behaviors.",
                    "why_relevant": "Essential executive capability for driving enterprise-wide LMS adoption and learning culture shifts."
                }
            ]
        return []
