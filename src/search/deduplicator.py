"""
Multi-Level Deduplicator.
Deduplicates resources by Normalized URL, Title Similarity, Canonical Hash, and DOI.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from difflib import SequenceMatcher

from src.models import Resource
from src.utils.validator import normalize_url, compute_hash, sanitize_text
from src.utils.logger import get_logger
from src.utils.dates import get_utc_now, to_iso_string

logger = get_logger("deduplicator")


class Deduplicator:
    def __init__(self, data_file: Optional[Path] = None):
        if data_file is None:
            self.data_file = Path(__file__).resolve().parent.parent.parent / "data" / "seen_resources.json"
        else:
            self.data_file = Path(data_file)
        self.seen_data: Dict[str, Any] = self._load_seen_data()

    def _load_seen_data(self) -> Dict[str, Any]:
        if not self.data_file.exists():
            return {
                "last_updated": to_iso_string(),
                "total_seen": 0,
                "seen_urls": {},
                "seen_hashes": {}
            }
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load seen resources file: {e}. Starting fresh.")
            return {
                "last_updated": to_iso_string(),
                "total_seen": 0,
                "seen_urls": {},
                "seen_hashes": {}
            }

    def save(self) -> None:
        """Persists updated deduplication state to JSON file."""
        self.seen_data["last_updated"] = to_iso_string()
        self.seen_data["total_seen"] = len(self.seen_data.get("seen_urls", {}))
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.seen_data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _normalize_title(title: str) -> str:
        """Normalizes titles for fuzzy comparison."""
        clean = sanitize_text(title).lower()
        # Remove punctuation and noise words
        clean = re.sub(r"[^\w\s]", " ", clean)
        clean = re.sub(r"\b(a|an|the|in|on|at|for|to|of|and|or|free|webinar|course|masterclass|2025|2026)\b", " ", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    def is_duplicate(self, resource: Resource, title_similarity_threshold: float = 0.85) -> Tuple[bool, str]:
        """
        Checks whether a resource has already been seen or recommended.
        Returns (is_dup, reason).
        """
        norm_url = normalize_url(resource.url)
        seen_urls = self.seen_data.setdefault("seen_urls", {})
        seen_hashes = self.seen_data.setdefault("seen_hashes", {})

        # 1. Exact normalized URL match
        if norm_url in seen_urls:
            return True, f"Duplicate URL previously seen on {seen_urls[norm_url].get('date_seen', 'unknown')}"

        # 2. Canonical title/content hash match
        title_hash = compute_hash(self._normalize_title(resource.title))
        resource.canonical_hash = title_hash
        if title_hash in seen_hashes:
            return True, f"Duplicate title hash: {seen_hashes[title_hash].get('title', '')}"

        # 3. DOI match (for research papers)
        if resource.doi:
            for url_key, info in seen_urls.items():
                if info.get("doi") and info.get("doi").lower() == resource.doi.lower():
                    return True, f"Duplicate DOI: {resource.doi}"

        # 4. Fuzzy title similarity match against recent seen titles
        norm_title = self._normalize_title(resource.title)
        if len(norm_title) > 10:
            for h, info in seen_hashes.items():
                past_norm_title = self._normalize_title(info.get("title", ""))
                if len(past_norm_title) > 10:
                    similarity = SequenceMatcher(None, norm_title, past_norm_title).ratio()
                    if similarity >= title_similarity_threshold:
                        return True, f"High title similarity ({similarity:.2f}) with: {info.get('title')}"

        return False, ""

    def mark_seen(self, resource: Resource) -> None:
        """Registers a resource in the seen database."""
        norm_url = normalize_url(resource.url)
        title_hash = resource.canonical_hash or compute_hash(self._normalize_title(resource.title))
        now_str = to_iso_string()

        self.seen_data.setdefault("seen_urls", {})[norm_url] = {
            "title": resource.title,
            "provider": resource.provider,
            "date_seen": now_str,
            "score": resource.relevance_score,
            "doi": resource.doi
        }

        self.seen_data.setdefault("seen_hashes", {})[title_hash] = {
            "title": resource.title,
            "url": norm_url,
            "date_seen": now_str
        }
