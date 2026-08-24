"""
Data Collectors Package for Multi-Source Opportunity Discovery.
"""

from .base import BaseCollector
from .rss_collector import RSSCollector
from .youtube_collector import YouTubeCollector
from .platform_collector import PlatformCollector
from .academic_collector import AcademicCollector
from .africa_collector import AfricaCollector

__all__ = [
    "BaseCollector",
    "RSSCollector",
    "YouTubeCollector",
    "PlatformCollector",
    "AcademicCollector",
    "AfricaCollector",
]
