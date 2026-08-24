"""
Targeted Search Query Generator.
Generates multi-dimensional discovery queries: TOPIC + SKILL + RESOURCE TYPE + RECENCY.
"""

from typing import List, Dict, Any
from datetime import datetime
from src.utils.dates import get_lagos_now


class QueryGenerator:
    """Generates structured search queries tailored to career progression areas."""

    CORE_TOPICS = [
        # Learning & Development
        ("L&D Analytics", "Learning Measurement & ROI", "Free Course"),
        ("Instructional Design", "Microlearning Architecture", "Masterclass"),
        ("Training Needs Analysis", "Competency Gap Assessment", "Framework"),
        ("Learning Strategy", "Enterprise Capability", "Webinar"),
        ("Training Evaluation", "Kirkpatrick Model", "Lecture"),

        # Talent Development & Management
        ("Talent Management", "Succession Planning", "Webinar"),
        ("Talent Development", "High-Potential Pipelines", "Free Course"),
        ("Nine-Box Grid", "Talent Review Assessment", "Masterclass"),
        ("Competency Framework", "Skills-Based Organization", "Toolkit"),
        ("Career Pathing", "Internal Mobility", "Lecture"),

        # HRM & Strategic HR
        ("Strategic HRBP", "Business Partnering", "Masterclass"),
        ("Organizational Development", "Change Leadership", "Free Course"),
        ("Performance Enablement", "Continuous Feedback", "Webinar"),
        ("Employee Engagement", "Learning Culture", "Research Report"),

        # People Analytics & Future of Work
        ("People Analytics", "HR Dashboards Power BI", "Free Training"),
        ("AI for HR", "Generative AI in L&D", "Webinar"),
        ("AI Academy", "Digital Workforce Transformation", "Masterclass"),
        ("Workforce Planning", "Predictive Talent Analytics", "Lecture"),

        # Business & Financial Acumen
        ("Financial Literacy for HR", "Budgeting and ROI", "Masterclass"),
        ("Business Acumen for L&D", "Commercial Strategy", "Free Lecture"),

        # Africa & Nigeria HR
        ("CIPM Nigeria", "Talent Management in Africa", "Webinar"),
        ("African Workforce Trends", "Human Capital Development", "Report")
    ]

    RESOURCE_MODIFIERS = [
        "free course",
        "free lecture",
        "webinar",
        "masterclass",
        "toolkit",
        "whitepaper",
        "free certified training",
        "open courseware"
    ]

    @classmethod
    def generate_discovery_queries(cls, target_year: int = 2026) -> List[Dict[str, str]]:
        """
        Generates structured search queries combining:
        TOPIC + SKILL + RESOURCE TYPE + RECENCY
        """
        queries = []
        for topic, skill, res_type in cls.CORE_TOPICS:
            query_str = f"{topic} {skill} {res_type} {target_year}"
            queries.append({
                "topic": topic,
                "skill": skill,
                "resource_type": res_type,
                "year": str(target_year),
                "query": query_str
            })
        return queries

    @classmethod
    def generate_youtube_queries(cls) -> List[str]:
        """Generates specific queries targeted for university/expert public lectures."""
        return [
            "Talent Management succession planning free lecture university",
            "L&D analytics learning evaluation masterclass",
            "People analytics dashboard Power BI HR training free",
            "Strategic HR business partner executive lecture",
            "Generative AI for HR and L&D webinar 2026",
            "Skills based organization competency framework masterclass",
            "Executive presence leadership communication lecture Stanford Harvard"
        ]
