"""
Validation, URL Normalization, and Content Sanitization Utilities.
"""

import hashlib
import re
import html
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import Tuple, Optional
import requests

from .logger import get_logger

logger = get_logger("validator")

# Tracking parameters to strip during URL normalization
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "msclkid", "ref", "source", "feature", "si", "trk"
}


def normalize_url(raw_url: str) -> str:
    """
    Normalizes URLs to ensure reliable deduplication:
    - Lowercases scheme and host
    - Removes common tracking query parameters (utm_*, gclid, etc.)
    - Removes trailing slashes
    - Removes fragments (#section)
    """
    if not raw_url:
        return ""

    try:
        parsed = urlparse(raw_url.strip())
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()

        # Remove default port
        if ":80" in netloc and scheme == "http":
            netloc = netloc.replace(":80", "")
        elif ":443" in netloc and scheme == "https":
            netloc = netloc.replace(":443", "")

        path = parsed.path.rstrip("/")
        if not path:
            path = "/"

        # Filter out tracking query params
        query_params = parse_qs(parsed.query, keep_blank_values=False)
        filtered_params = {
            k: v for k, v in query_params.items()
            if k.lower() not in TRACKING_PARAMS
        }
        # Sort query keys for consistent hashing
        clean_query = urlencode(filtered_params, doseq=True)

        return urlunparse((scheme, netloc, path, "", clean_query, ""))
    except Exception as e:
        logger.debug(f"Failed to normalize URL {raw_url}: {e}")
        return raw_url.strip()


def compute_hash(text: str) -> str:
    """Computes SHA-256 hash of normalized text."""
    clean = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(clean.encode("utf-8")).hexdigest()


def sanitize_text(text: Optional[str]) -> str:
    """Strips HTML tags, decodes HTML entities, and removes excess whitespace."""
    if not text:
        return ""
    # Decode HTML entities (&amp; -> &, &quot; -> ", etc.)
    decoded = html.unescape(text)
    # Strip HTML tags
    no_html = re.sub(r"<[^>]+>", " ", decoded)
    # Collapse multiple whitespaces
    cleaned = re.sub(r"\s+", " ", no_html).strip()
    return cleaned


def validate_url(url: str, timeout: int = 6) -> Tuple[bool, str]:
    """
    Verifies that a URL is well-formed and responds with a 2xx or 3xx HTTP status code.
    Gracefully handles network restrictions without crashing.
    """
    if not url or not url.startswith(("http://", "https://")):
        return False, "Invalid URL scheme"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LAndDAlert-CareerBot/1.0"
        }
        # First try a lightweight HEAD request
        response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        if response.status_code < 400:
            return True, f"HTTP {response.status_code}"

        # If HEAD is blocked (some servers return 405 Method Not Allowed), fallback to GET with stream
        response = requests.get(url, headers=headers, timeout=timeout, stream=True, allow_redirects=True)
        if response.status_code < 400:
            return True, f"HTTP {response.status_code}"
        return False, f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        logger.debug(f"URL validation failed for {url}: {e}")
        return False, str(e)
