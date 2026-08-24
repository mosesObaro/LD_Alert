"""
Data models and type definitions for the Career Development Intelligence System.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime


class PricingType(str, Enum):
    FREE_CONTENT = "Free Content"
    FREE_AUDIT = "Course content: Free to audit (Certificate: Paid)"
    FREE_EVENT = "Free Event / Webinar"
    FREE_CERTIFICATE = "Free Certified Course"
    PAID_CONTENT = "Paid Resource"
    PAID_CERTIFICATE = "Paid Certificate"

    def __str__(self) -> str:
        return self.value


class ResourceType(str, Enum):
    COURSE = "Course"
    MINI_COURSE = "Mini-Course / Microlearning"
    LECTURE = "University / Expert Public Lecture"
    WEBINAR = "Webinar / Masterclass"
    WORKSHOP = "Workshop / Interactive Seminar"
    CONFERENCE = "Conference / Virtual Summit"
    REPORT = "Research Report / Whitepaper"
    TOOLKIT = "Toolkit / Practical Framework"
    PODCAST = "Podcast / Audio Masterclass"
    CAREER_OPPORTUNITY = "Fellowship / Leadership Programme"

    def __str__(self) -> str:
        return self.value


class PriorityLevel(str, Enum):
    CRITICAL = "CRITICAL (90-100)"
    HIGH = "HIGH (80-89)"
    GOOD = "GOOD (70-79)"
    LOW = "LOW (60-69)"
    IGNORE = "IGNORE (<60)"


class LearningStatus(str, Enum):
    NOT_STARTED = "NOT STARTED"
    IN_PROGRESS = "IN PROGRESS"
    COMPLETED = "COMPLETED"
    APPLIED = "APPLIED"
    SKIPPED = "SKIPPED"


@dataclass
class Resource:
    title: str
    provider: str
    type: ResourceType
    url: str
    date_published: str
    date_discovered: str
    duration: str
    cost: str
    pricing_type: PricingType
    topics: List[str]
    career_stage: str
    relevance_score: float = 0.0
    tier: int = 2
    summary: str = ""
    why_relevant: str = ""
    td_africa_application: str = ""
    practical_application: str = ""
    free_alternative: Optional[Dict[str, str]] = None
    status: LearningStatus = LearningStatus.NOT_STARTED
    difficulty: str = "Intermediate"
    event_date: Optional[str] = None
    registration_deadline: Optional[str] = None
    location: Optional[str] = "Virtual / Online"
    speaker_or_author: Optional[str] = None
    doi: Optional[str] = None
    canonical_hash: str = ""
    score_breakdown: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "provider": self.provider,
            "type": self.type.value if isinstance(self.type, ResourceType) else str(self.type),
            "url": self.url,
            "date_published": self.date_published,
            "date_discovered": self.date_discovered,
            "duration": self.duration,
            "cost": self.cost,
            "pricing_type": self.pricing_type.value if isinstance(self.pricing_type, PricingType) else str(self.pricing_type),
            "topics": self.topics,
            "career_stage": self.career_stage,
            "relevance_score": round(self.relevance_score, 1),
            "free": self.pricing_type in [PricingType.FREE_CONTENT, PricingType.FREE_AUDIT, PricingType.FREE_EVENT, PricingType.FREE_CERTIFICATE],
            "summary": self.summary,
            "why_relevant": self.why_relevant,
            "td_africa_application": self.td_africa_application,
            "practical_application": self.practical_application,
            "free_alternative": self.free_alternative,
            "status": self.status.value if isinstance(self.status, LearningStatus) else str(self.status),
            "difficulty": self.difficulty,
            "event_date": self.event_date,
            "registration_deadline": self.registration_deadline,
            "location": self.location,
            "speaker_or_author": self.speaker_or_author,
            "canonical_hash": self.canonical_hash,
            "score_breakdown": self.score_breakdown
        }


@dataclass
class Competency:
    id: str
    name: str
    category: str
    current_level: int  # 1 to 5
    target_level: int   # 1 to 5
    priority: str       # Critical, High, Medium, Low
    practical_evidence: str
    last_reviewed: str
    target_stage: str

    @property
    def gap(self) -> int:
        return max(0, self.target_level - self.current_level)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "current_level": self.current_level,
            "target_level": self.target_level,
            "gap": self.gap,
            "priority": self.priority,
            "practical_evidence": self.practical_evidence,
            "last_reviewed": self.last_reviewed,
            "target_stage": self.target_stage
        }


@dataclass
class PracticalChallenge:
    title: str
    estimated_time_minutes: int
    instructions: str
    deliverable: str
    related_competencies: List[str]


@dataclass
class PortfolioEvidence:
    artifact_type: str
    description: str
    example_templates: List[str]


@dataclass
class WeeklyIntelligencePlan:
    week_number: int
    theme: str
    why_matters: str
    core_ld_resource: Resource
    core_talent_management_resource: Resource
    core_broader_skill_resource: Resource
    practical_challenge: PracticalChallenge
    portfolio_evidence: PortfolioEvidence
    reflection_questions: List[str]
    next_action: str
    three_actions: Dict[str, str]
    optional_resources: List[Resource] = field(default_factory=list)
    upcoming_events: List[Resource] = field(default_factory=list)
    research_developments: List[Resource] = field(default_factory=list)
    career_opportunities: List[Resource] = field(default_factory=list)
    total_learning_time_minutes: int = 75


@dataclass
class ResearchItem:
    title: str
    authors_or_source: str
    date_published: str
    url: str
    research_question: str
    method: str
    key_finding: str
    why_it_matters: str
    how_to_apply: str


@dataclass
class TrendItem:
    topic: str
    direction: str  # "INCREASING" | "DECLINING" | "EMERGING"
    evidence_summary: str
