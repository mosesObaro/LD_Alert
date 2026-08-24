"""
Pricing, Topic, and Career Stage Classifier.
"""

import re
from typing import List, Tuple
from src.models import Resource, PricingType, ResourceType


class Classifier:
    TOPIC_KEYWORDS = {
        "Learning & Development": [
            "l&d", "learning strategy", "training needs analysis", "tna", "instructional design",
            "adult learning", "andragogy", "facilitation", "training evaluation", "kirkpatrick",
            "learning effectiveness", "learning analytics", "learning roi", "microlearning",
            "lms", "simba spark", "blended learning", "learning culture"
        ],
        "Talent Development": [
            "talent development", "capability development", "competency framework", "skills framework",
            "career development", "career pathing", "internal mobility", "mentoring", "coaching",
            "high-potential", "hipo", "leadership pipeline", "skills-based organization"
        ],
        "Talent Management": [
            "talent management", "succession planning", "talent review", "nine-box", "9-box",
            "critical role", "workforce planning", "retention", "talent analytics"
        ],
        "Human Resource Management": [
            "hr strategy", "strategic hrbp", "business partnering", "performance management",
            "employee engagement", "employee experience", "organizational development", "change management",
            "hr policies", "people strategy", "cipm", "cipd", "shrm"
        ],
        "Leadership": [
            "leadership development", "executive presence", "stakeholder management", "influencing",
            "negotiation", "strategic communication", "presentation skills", "change leadership"
        ],
        "Business & Financial Acumen": [
            "financial literacy", "finance for hr", "business strategy", "commercial awareness",
            "budgeting", "business case", "roi calculation", "strategic planning"
        ],
        "People Analytics": [
            "people analytics", "hr analytics", "workforce analytics", "power bi", "dashboards",
            "data visualization", "hr metrics", "predictive analytics", "data storytelling"
        ],
        "Future of Work & AI": [
            "artificial intelligence", "generative ai", "ai for hr", "ai academy", "copilot",
            "digital transformation", "ai in l&d", "future skills", "human-ai collaboration"
        ],
        "Africa & Nigeria": [
            "nigeria", "africa", "lagos", "cipm", "african workforce", "emerging markets"
        ]
    }

    @classmethod
    def classify_pricing(cls, title: str, text: str, provider: str) -> PricingType:
        """
        Determines exact pricing classification:
        - FREE_CONTENT: 100% free course/toolkit/lecture
        - FREE_AUDIT: Free to audit course (Coursera, edX)
        - FREE_EVENT: Free webinar/conference registration
        - FREE_CERTIFICATE: Fully free certificate (OpenLearn, Microsoft Learn, IBM)
        - PAID_CONTENT: Requires payment
        - PAID_CERTIFICATE: Audit free, but certificate is paid
        """
        combined = f"{title} {text} {provider}".lower()

        # Platforms known for free audit
        if any(p in combined for p in ["coursera", "edx"]):
            if "certificate" in combined:
                return PricingType.FREE_AUDIT
            return PricingType.FREE_AUDIT

        # Platforms with 100% free certificates / badges
        if any(p in combined for p in ["openlearn", "microsoft learn", "ibm skillsbuild", "skillsbuild"]):
            return PricingType.FREE_CERTIFICATE

        # Events, webinars, masterclasses
        if any(w in combined for w in ["webinar", "virtual summit", "masterclass", "live session", "conference"]):
            if any(w in combined for w in ["$ ", "paid ticket", "tuition", "registration fee: $"]):
                return PricingType.PAID_CONTENT
            return PricingType.FREE_EVENT

        # YouTube and open courseware
        if any(p in combined for p in ["youtube", "mit opencourseware", "ocw", "stanford online free", "harvard online"]):
            return PricingType.FREE_CONTENT

        # Paid indicators
        if any(w in combined for w in ["subscription required", "buy now", "price: $", "enroll for $", "paid course"]):
            return PricingType.PAID_CONTENT

        # Default to free content
        return PricingType.FREE_CONTENT

    @classmethod
    def classify_topics(cls, title: str, summary: str, default_topics: List[str]) -> List[str]:
        """Extracts relevant topic tags from title and summary."""
        combined = f"{title} {summary}".lower()
        matched_categories = set(default_topics)

        for category, keywords in cls.TOPIC_KEYWORDS.items():
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", combined):
                    matched_categories.add(category)
                    break

        return list(matched_categories)

    @classmethod
    def classify_career_stage(cls, topics: List[str], title: str) -> str:
        """Assigns resource to the most appropriate career stage (1 to 5)."""
        text = (title + " " + " ".join(topics)).lower()

        if any(k in text for k in ["executive", "enterprise", "c-suite", "board", "strategic hr leadership", "org design"]):
            return "Stage 5: Enterprise Talent / Strategic HR Leadership"
        elif any(k in text for k in ["talent management", "succession", "9-box", "career path", "hipo", "competency framework"]):
            return "Stage 4: Talent Development & Talent Management"
        elif any(k in text for k in ["learning strategy", "capability development", "learning analytics", "roi", "microlearning", "tna"]):
            return "Stage 3: Strategic Learning & Capability Development"
        elif any(k in text for k in ["management", "facilitation", "evaluation", "kirkpatrick", "instructional design"]):
            return "Stage 2: Effective L&D Management"
        else:
            return "Stage 1: L&D Foundations"
