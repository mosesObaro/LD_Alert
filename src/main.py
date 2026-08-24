"""
Main CLI Entrypoint for L&D / Talent Management Career Intelligence System.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional

from src.config_loader import ConfigLoader
from src.models import Resource, PriorityLevel, LearningStatus, PricingType, ResourceType
from src.collectors import (
    RSSCollector,
    YouTubeCollector,
    PlatformCollector,
    AcademicCollector,
    AfricaCollector
)
from src.search.deduplicator import Deduplicator
from src.engine.classifier import Classifier
from src.engine.scorer import Scorer
from src.engine.career_engine import CareerEngine
from src.engine.memory_engine import MemoryEngine
from src.engine.synthesizer import Synthesizer
from src.engine.trend_detector import TrendDetector
from src.email.renderer import EmailRenderer
from src.email.sender import EmailSender
from src.dashboard.generator import DashboardGenerator
from src.utils.logger import setup_logger, get_logger
from src.utils.dates import get_week_number, get_lagos_now, format_lagos_time
from src.utils.validator import validate_url

logger = setup_logger("main")


def get_collectors(sources_config: List[dict]) -> List[any]:
    """Instantiates appropriate collectors for configured sources."""
    collectors = []
    for src in sources_config:
        if not src.get("enabled", True):
            continue
        src_type = src.get("type", "").lower()
        if src_type == "rss":
            collectors.append(RSSCollector(src))
        elif src_type == "youtube":
            collectors.append(YouTubeCollector(src))
        elif src_type == "platform":
            collectors.append(PlatformCollector(src))
        elif src.get("category") == "africa_nigeria":
            collectors.append(AfricaCollector(src))
        elif src.get("category") in ["research_consulting", "academic_journal"]:
            collectors.append(AcademicCollector(src))
        else:
            collectors.append(RSSCollector(src))
    return collectors


def harvest_and_rank_opportunities(config_loader: ConfigLoader, deduplicator: Deduplicator) -> List[Resource]:
    """Collects, classifies, verifies, and scores opportunities across all trusted sources."""
    sources_config = config_loader.load_sources()
    scoring_weights = config_loader.load_scoring_weights()
    memory_engine = MemoryEngine()
    penalties = memory_engine.get_feedback_penalties()

    collectors = get_collectors(sources_config)
    scorer = Scorer(scoring_weights)

    all_discovered: List[Resource] = []
    logger.info(f"Initiating multi-source collection across {len(collectors)} active sources...")

    for collector in collectors:
        items = collector.safe_collect()
        for item in items:
            # 1. Deduplication check
            is_dup, reason = deduplicator.is_duplicate(item)
            if is_dup:
                logger.debug(f"Skipping duplicate [{item.title}]: {reason}")
                continue

            # 2. Topic classification
            item.topics = Classifier.classify_topics(item.title, item.summary, item.topics)

            # 3. Pricing classification refinement
            item.pricing_type = Classifier.classify_pricing(item.title, item.summary, item.provider)

            # 4. Career stage classification
            item.career_stage = Classifier.classify_career_stage(item.topics, item.title)

            # 5. Scoring calculation
            scorer.calculate_score(item, feedback_penalties=penalties)

            all_discovered.append(item)

    # Sort descending by relevance score
    ranked = sorted(all_discovered, key=lambda r: r.relevance_score, reverse=True)
    logger.info(f"Harvest complete. {len(ranked)} unique opportunities ranked.")
    return ranked


def execute_weekly_workflow(dry_run: bool = False) -> None:
    """Executes the Monday 07:00 WAT weekly intelligence alert workflow."""
    logger.info(f"Starting Weekly Learning Alert Workflow (Dry-Run: {dry_run})...")
    config_loader = ConfigLoader()
    profile = config_loader.load_profile()
    deduplicator = Deduplicator()
    memory_engine = MemoryEngine()

    ranked = harvest_and_rank_opportunities(config_loader, deduplicator)

    week_num = get_week_number()
    weekly_plan = Synthesizer.synthesize_weekly_plan(ranked, week_num=week_num)

    # Record recommended core items into memory
    if not dry_run:
        for core in [weekly_plan.core_ld_resource, weekly_plan.core_talent_management_resource, weekly_plan.core_broader_skill_resource]:
            deduplicator.mark_seen(core)
            memory_engine.record_recommendation(core, week_num)
        deduplicator.save()
        memory_engine.save()

    # Render email templates
    renderer = EmailRenderer()
    subject, html_content, text_content = renderer.render_weekly_alert(weekly_plan, profile)

    # Send email
    recipient_email = os.environ.get("EMAIL_TO") or os.environ.get("RECIPIENT_EMAIL") or profile.get("user", {}).get("email")
    sender = EmailSender()
    success, msg = sender.send(
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        to_email=recipient_email,
        dry_run=dry_run
    )

    # Generate dashboard data
    dashboard_gen = DashboardGenerator()
    dashboard_gen.generate(weekly_plan=weekly_plan, ranked_resources=ranked)

    logger.info(f"Weekly workflow finished. Status: {msg}")


def execute_urgent_workflow(dry_run: bool = False) -> None:
    """Checks for newly published CRITICAL opportunities (Score >= 90)."""
    logger.info(f"Starting Urgent Critical Alert Check (Dry-Run: {dry_run})...")
    config_loader = ConfigLoader()
    profile = config_loader.load_profile()
    deduplicator = Deduplicator()
    memory_engine = MemoryEngine()

    ranked = harvest_and_rank_opportunities(config_loader, deduplicator)

    critical_items = [r for r in ranked if r.relevance_score >= 90.0]
    if not critical_items:
        logger.info("No new critical opportunities (score >= 90) discovered this cycle.")
        return

    logger.info(f"Discovered {len(critical_items)} critical opportunities!")
    top_critical = critical_items[0]

    if not dry_run:
        deduplicator.mark_seen(top_critical)
        deduplicator.save()
        memory_engine.record_recommendation(top_critical, get_week_number())
        memory_engine.save()

    renderer = EmailRenderer()
    subject, html_content, text_content = renderer.render_urgent_alert(top_critical, profile)

    recipient_email = os.environ.get("EMAIL_TO") or os.environ.get("RECIPIENT_EMAIL") or profile.get("user", {}).get("email")
    sender = EmailSender()
    success, msg = sender.send(
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        to_email=recipient_email,
        dry_run=dry_run
    )
    logger.info(f"Urgent alert workflow finished. Status: {msg}")


def execute_monthly_workflow(dry_run: bool = False) -> None:
    """Executes the 1st of month Career Intelligence Digest & Scorecard."""
    logger.info(f"Starting Monthly Career Digest Workflow (Dry-Run: {dry_run})...")
    config_loader = ConfigLoader()
    profile = config_loader.load_profile()
    deduplicator = Deduplicator()
    career_engine = CareerEngine(config_loader)
    memory_engine = MemoryEngine()

    ranked = harvest_and_rank_opportunities(config_loader, deduplicator)

    scorecard = career_engine.generate_monthly_scorecard()
    top_gaps = career_engine.get_top_gaps(limit=5)
    trends = TrendDetector.detect_monthly_trends(ranked)
    research_items = [r for r in ranked if r.type == ResourceType.REPORT][:2]
    upcoming_events = [r for r in ranked if r.type in [ResourceType.CONFERENCE, ResourceType.WEBINAR]][:3]

    now = get_lagos_now()
    month_name = now.strftime("%B")
    year = now.year

    renderer = EmailRenderer()
    subject, html_content, text_content = renderer.render_monthly_digest(
        month_name=month_name,
        year=year,
        scorecard=scorecard,
        history_summary=memory_engine.data.get("summary", {}),
        portfolio_count=len(memory_engine.data.get("history", [])),
        trends=trends,
        research_items=research_items,
        top_gaps=top_gaps,
        upcoming_events=upcoming_events,
        user_profile=profile
    )

    recipient_email = os.environ.get("EMAIL_TO") or os.environ.get("RECIPIENT_EMAIL") or profile.get("user", {}).get("email")
    sender = EmailSender()
    success, msg = sender.send(
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        to_email=recipient_email,
        dry_run=dry_run
    )

    # Generate dashboard data
    dashboard_gen = DashboardGenerator()
    dashboard_gen.generate(ranked_resources=ranked)

    logger.info(f"Monthly workflow finished. Status: {msg}")


def display_status() -> None:
    """Displays current system status, health, and competency summary."""
    config_loader = ConfigLoader()
    profile = config_loader.load_profile()
    career_engine = CareerEngine(config_loader)
    memory_engine = MemoryEngine()

    user = profile.get("user", {})
    print("\n" + "=" * 70)
    print(f"CAREER DEVELOPMENT INTELLIGENCE SYSTEM STATUS")
    print("=" * 70)
    print(f"User:             {user.get('name')} ({user.get('current_role')} at {user.get('organization')})")
    print(f"Timezone:         {user.get('timezone')} | Current Time: {format_lagos_time()}")
    print(f"Career Stage:     {profile.get('career_progression', {}).get('current_stage')}")
    print(f"Target Stage:     {profile.get('career_progression', {}).get('target_stage')}")
    print(f"Learning History: {memory_engine.data.get('summary', {})}")

    print("\nTOP PRIORITY COMPETENCY GAPS:")
    for comp in career_engine.get_top_gaps(limit=5):
        print(f"  - [{comp.priority.upper()}] {comp.name}: Level {comp.current_level} -> Target: {comp.target_level} (Gap: {comp.gap})")

    print("\n" + "=" * 70 + "\n")


def verify_sources() -> None:
    """Checks network and feed health for all configured sources."""
    config_loader = ConfigLoader()
    sources = config_loader.load_sources()
    print("\n" + "=" * 70)
    print("VERIFYING SOURCES HEALTH & CONNECTIVITY")
    print("=" * 70)

    for src in sources:
        sid = src.get("id")
        name = src.get("name")
        feed_url = src.get("feed_url") or src.get("url")
        ok, msg = validate_url(feed_url, timeout=5)
        status_str = "OK" if ok else "WARN/OFFLINE"
        print(f"[{status_str:12}] {name[:40]:40} | {msg}")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="L&D / Talent Management Career Development Intelligence System")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # run command
    run_parser = subparsers.add_parser("run", help="Run automated intelligence workflows")
    run_parser.add_argument("--type", choices=["weekly", "urgent", "monthly"], default="weekly", help="Workflow type")
    run_parser.add_argument("--dry-run", action="store_true", help="Execute without sending live emails or persisting state")

    # collect command
    collect_parser = subparsers.add_parser("collect", help="Harvest and rank opportunities")
    collect_parser.add_argument("--dry-run", action="store_true", help="Harvest without persisting seen database")

    # status command
    subparsers.add_parser("status", help="Show system status and competency overview")

    # verify sources command
    subparsers.add_parser("verify-sources", help="Check uptime and connectivity of all configured sources")

    # update-competency command
    comp_parser = subparsers.add_parser("update-competency", help="Update a competency level upon confirmed progress")
    comp_parser.add_argument("--id", required=True, help="Competency ID (e.g. succession_planning)")
    comp_parser.add_argument("--level", type=int, required=True, choices=[1, 2, 3, 4, 5], help="New confirmed level (1-5)")
    comp_parser.add_argument("--evidence", help="Practical evidence description")

    # record-learning command
    learn_parser = subparsers.add_parser("record-learning", help="Record completion, application, or feedback for a resource")
    learn_parser.add_argument("--url", required=True, help="Resource URL")
    learn_parser.add_argument("--status", choices=["NOT_STARTED", "IN_PROGRESS", "COMPLETED", "APPLIED", "SKIPPED"], required=True)
    learn_parser.add_argument("--rating", type=int, choices=[1, 2, 3, 4, 5], help="Rating from 1 to 5 stars")
    learn_parser.add_argument("--learning", help="Key learning summary")
    learn_parser.add_argument("--application", help="Workplace application notes")
    learn_parser.add_argument("--evidence", help="Portfolio evidence created")
    learn_parser.add_argument("--minutes", type=int, default=45, help="Learning time in minutes")

    args = parser.parse_args()

    if args.command == "run":
        if args.type == "weekly":
            execute_weekly_workflow(dry_run=args.dry_run)
        elif args.type == "urgent":
            execute_urgent_workflow(dry_run=args.dry_run)
        elif args.type == "monthly":
            execute_monthly_workflow(dry_run=args.dry_run)
    elif args.command == "collect":
        config_loader = ConfigLoader()
        deduplicator = Deduplicator()
        ranked = harvest_and_rank_opportunities(config_loader, deduplicator)
        print(f"\nTop {min(10, len(ranked))} Harvested Opportunities:")
        for idx, r in enumerate(ranked[:10], 1):
            print(f"{idx:2}. [{r.relevance_score:4.1f}/100] [{r.pricing_type.value[:14]}] {r.title} ({r.provider})")
    elif args.command == "status":
        display_status()
    elif args.command == "verify-sources":
        verify_sources()
    elif args.command == "update-competency":
        career_engine = CareerEngine()
        success = career_engine.update_competency_level(args.id, args.level, practical_evidence=args.evidence)
        if success:
            print(f"Successfully updated competency '{args.id}' to Level {args.level}.")
        else:
            print(f"Error: Competency '{args.id}' not found.")
            sys.exit(1)
    elif args.command == "record-learning":
        memory_engine = MemoryEngine()
        status_enum = LearningStatus[args.status]
        success = memory_engine.record_feedback(
            url=args.url,
            status=status_enum,
            rating=args.rating,
            key_learning=args.learning or "",
            application=args.application or "",
            evidence=args.evidence or "",
            duration_minutes=args.minutes
        )
        if success:
            print(f"Successfully recorded learning feedback for {args.url}.")
        else:
            print(f"Notice: Resource {args.url} was updated or logged into history.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
