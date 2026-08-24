"""
Weekly Plan Synthesizer & TD Africa Application Generator.
Constructs the personalized 3-Core Weekly Intelligence Plan, Practical Challenge, and Portfolio Artifact.
"""

from typing import List, Dict, Any, Optional, Tuple
from src.models import (
    Resource,
    WeeklyIntelligencePlan,
    PracticalChallenge,
    PortfolioEvidence,
    ResourceType,
    PricingType
)
from src.utils.dates import get_week_number
from src.utils.logger import get_logger

logger = get_logger("synthesizer")


class Synthesizer:
    THEMES = [
        ("Transforming L&D into Enterprise Talent Architecture", "Connecting training evaluation directly to high-potential retention and succession slates."),
        ("Data-Driven Capability & Predictive People Analytics", "Transitioning from attendance metrics to skill-gap velocity and Power BI talent dashboards."),
        ("Modernizing Microlearning & Continuous Digital Culture", "Leveraging SIMBA Spark and bite-sized learning to drive enterprise adoption and daily engagement."),
        ("AI-Augmented Workforce & Digital Talent Transformation", "Building the AI Academy curriculum, responsible AI governance, and prompt fluency for HR."),
        ("Succession Planning & Critical-Role Risk Mitigation", "Implementing 9-box talent review boards and multi-tier leadership pipelines across business units."),
        ("Kirkpatrick Level 4 Evaluation & Phillips L&D ROI", "Quantifying the commercial business impact and revenue enablement of technical and OEM certifications."),
        ("Executive Presence & Strategic HR Business Partnering", "Enhancing C-suite persuasion, financial acumen, and commercial alignment in executive presentations.")
    ]

    PRACTICAL_CHALLENGES = [
        PracticalChallenge(
            title="Draft a 9-Box Talent Review Calibration Grid for One Strategic Department",
            estimated_time_minutes=45,
            instructions="Map 5-8 key roles across Performance (Low/Med/High) vs Potential (Low/Med/High). Define one specific development action for each quadrant.",
            deliverable="1-Page 9-Box Calibration Matrix & Succession Slate Draft",
            related_competencies=["succession_planning", "talent_management"]
        ),
        PracticalChallenge(
            title="Build an Automated Power BI / Excel L&D Executive KPI Dashboard",
            estimated_time_minutes=50,
            instructions="Connect LMS completion and evaluation data to visualize: 1) Monthly Completion Rate, 2) Kirkpatrick Level 2 Skill Gain, 3) Cost per Learning Hour.",
            deliverable="Interactive L&D Executive Dashboard File (.pbix / .xlsx)",
            related_competencies=["learning_analytics", "people_analytics"]
        ),
        PracticalChallenge(
            title="Design a Microlearning Campaign Blueprint for SIMBA Spark",
            estimated_time_minutes=40,
            instructions="Create a 5-day microlearning sequence (3 minutes/day) focusing on a critical workplace skill with knowledge-check quizzes and reflection prompts.",
            deliverable="SIMBA Spark Microlearning Journey Sequence Document",
            related_competencies=["adult_learning", "digital_hr"]
        ),
        PracticalChallenge(
            title="Construct a Commercial Business Case for an Advanced Certification Programme",
            estimated_time_minutes=45,
            instructions="Formulate a financial justification deck detailing: Problem Statement, Target Cohort, Direct Cost, Productivity Enablement, and Projected ROI over 12 months.",
            deliverable="L&D Commercial Business Case Executive Deck (PowerPoint / PDF)",
            related_competencies=["learning_roi", "business_acumen", "financial_acumen"]
        )
    ]

    PORTFOLIO_ARTIFACTS = [
        PortfolioEvidence(
            artifact_type="Succession Planning & 9-Box Review Template",
            description="A standardized executive framework for identifying critical talent, flight risks, and succession readiness.",
            example_templates=["9-Box Grid Matrix.xlsx", "Talent Review Meeting Protocol.docx"]
        ),
        PortfolioEvidence(
            artifact_type="L&D Executive Analytics Dashboard",
            description="An executive-ready dashboard communicating learning effectiveness, adoption velocity, and training ROI.",
            example_templates=["TD_Africa_LD_Dashboard.pbix", "Executive_Summary_Deck.pptx"]
        ),
        PortfolioEvidence(
            artifact_type="Competency & Skill-Gap Audit Model",
            description="Role-based competency dictionary with behavioral indicators and self/manager assessment rubrics.",
            example_templates=["Competency_Dictionary_v2.xlsx", "TNA_Survey_Instrument.pdf"]
        ),
        PortfolioEvidence(
            artifact_type="Strategic AI in HR & L&D Capability Roadmap",
            description="Strategic blueprint outlining the rollout of AI tools, microlearning integrations, and digital workforce capability.",
            example_templates=["AI_Academy_Curriculum.pdf", "AI_Governance_HR_Checklist.docx"]
        )
    ]

    @classmethod
    def synthesize_weekly_plan(
        cls,
        ranked_resources: List[Resource],
        week_num: Optional[int] = None
    ) -> WeeklyIntelligencePlan:
        """
        Selects exactly 3 core learning resources and synthesizes the personalized weekly intelligence plan.
        """
        if week_num is None:
            week_num = get_week_number()

        theme_idx = week_num % len(cls.THEMES)
        theme, why_matters = cls.THEMES[theme_idx]

        # 1. Select Core 1: Immediate L&D Skill
        core_ld = cls._select_resource_by_category(
            ranked_resources,
            ["Learning & Development", "Adult Learning", "L&D Strategy", "Training Evaluation"],
            fallback_title="Strategic Training Needs Analysis & Capability Mapping"
        )
        cls._enrich_td_africa_application(core_ld)

        # 2. Select Core 2: Talent Development / Talent Management
        used_urls = {core_ld.url}
        core_tm = cls._select_resource_by_category(
            ranked_resources,
            ["Talent Management", "Talent Development", "Succession Planning", "Career Development"],
            exclude_urls=used_urls,
            fallback_title="Mastering Succession Planning & 9-Box Calibration"
        )
        cls._enrich_tm_application(core_tm)
        used_urls.add(core_tm.url)

        # 3. Select Core 3: Broader HR / Business / Digital / AI Skill
        core_broader = cls._select_resource_by_category(
            ranked_resources,
            ["Future of Work & AI", "People Analytics", "Business & Financial Acumen", "Leadership", "Human Resource Management"],
            exclude_urls=used_urls,
            fallback_title="Building Predictive People Analytics Dashboards"
        )
        cls._enrich_broader_application(core_broader)
        used_urls.add(core_broader.url)

        # Challenge & Portfolio
        challenge = cls.PRACTICAL_CHALLENGES[week_num % len(cls.PRACTICAL_CHALLENGES)]
        portfolio = cls.PORTFOLIO_ARTIFACTS[week_num % len(cls.PORTFOLIO_ARTIFACTS)]

        # Secondary buckets (Optional max 5, Events max 3, Research max 3, Career max 3)
        optional_items = [r for r in ranked_resources if r.url not in used_urls and r.relevance_score >= 70][:5]
        for r in optional_items:
            used_urls.add(r.url)

        upcoming_events = [r for r in ranked_resources if r.type in [ResourceType.WEBINAR, ResourceType.CONFERENCE, ResourceType.WORKSHOP] and r.url not in used_urls][:3]
        for r in upcoming_events:
            used_urls.add(r.url)

        research_items = [r for r in ranked_resources if r.type == ResourceType.REPORT and r.url not in used_urls][:3]
        for r in research_items:
            used_urls.add(r.url)

        career_ops = [r for r in ranked_resources if r.type == ResourceType.CAREER_OPPORTUNITY and r.url not in used_urls][:3]

        reflection_questions = [
            "What critical insight from this week's resources challenges our current approach at TD Africa?",
            "How can the practical challenge deliverable be integrated into upcoming talent review or training cycles?",
            "What behavioral shift in leadership or capability development did this study reveal?"
        ]

        next_action = f"Complete the '{challenge.title}' and archive the evidence in your portfolio before next Monday."

        three_actions = {
            "learn": f"Complete '{core_ld.title}' and '{core_tm.title}' ({core_ld.duration} + {core_tm.duration}).",
            "apply": f"{challenge.title} ({challenge.estimated_time_minutes} mins).",
            "capture": f"Save '{portfolio.artifact_type}' to your professional career portfolio."
        }

        return WeeklyIntelligencePlan(
            week_number=week_num,
            theme=theme,
            why_matters=why_matters,
            core_ld_resource=core_ld,
            core_talent_management_resource=core_tm,
            core_broader_skill_resource=core_broader,
            practical_challenge=challenge,
            portfolio_evidence=portfolio,
            reflection_questions=reflection_questions,
            next_action=next_action,
            three_actions=three_actions,
            optional_resources=optional_items,
            upcoming_events=upcoming_events,
            research_developments=research_items,
            career_opportunities=career_ops,
            total_learning_time_minutes=75
        )

    @classmethod
    def _select_resource_by_category(
        cls,
        resources: List[Resource],
        categories: List[str],
        exclude_urls: Optional[set] = None,
        fallback_title: str = "Core Professional Opportunity"
    ) -> Resource:
        exclude_urls = exclude_urls or set()
        for r in resources:
            if r.url in exclude_urls:
                continue
            if any(c in r.topics for c in categories):
                return r

        # If not found directly in categories, return highest ranked available
        for r in resources:
            if r.url not in exclude_urls:
                return r

        # Fallback resource
        return Resource(
            title=fallback_title,
            provider="CIPD / Executive Learning Hub",
            type=ResourceType.COURSE,
            url="https://www.cipd.org/uk/knowledge/",
            date_published="2026-08-20",
            date_discovered="2026-08-24",
            duration="45 mins",
            cost="100% Free",
            pricing_type=PricingType.FREE_CONTENT,
            topics=categories,
            career_stage="Stage 3: Strategic Learning & Capability Development",
            tier=1,
            summary="Strategic professional resource exploring enterprise capability frameworks and practical tools.",
            why_relevant="Builds essential competencies for L&D and Talent Management leadership."
        )

    @classmethod
    def _enrich_td_africa_application(cls, resource: Resource) -> None:
        if not resource.td_africa_application:
            resource.td_africa_application = (
                f"Apply the frameworks from '{resource.title}' directly to refine TD Africa's annual TNA cycle, "
                "integrate modular lessons into SIMBA Spark microlearning, and deliver measurable capability metrics for executive reporting."
            )
        if not resource.summary:
            resource.summary = "Deep dive into operational and strategic methodologies for designing, executing, and evaluating high-impact workplace learning."

    @classmethod
    def _enrich_tm_application(cls, resource: Resource) -> None:
        if not resource.practical_application:
            resource.practical_application = (
                f"Use this resource to pilot a structured 9-Box talent assessment and succession slate across one critical department at TD Africa."
            )
        if not resource.why_relevant:
            resource.why_relevant = "Directly accelerates progression from L&D management into enterprise Talent Management leadership."

    @classmethod
    def _enrich_broader_application(cls, resource: Resource) -> None:
        if not resource.why_relevant:
            resource.why_relevant = "Expands strategic capability in People Analytics, AI adoption, and business acumen to influence executive stakeholders."
