"""
Base Collector Interface with Health Tracking & Resilient Error Handling.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import time

from src.models import Resource
from src.utils.logger import get_logger
from src.utils.dates import get_utc_now, to_iso_string

logger = get_logger("collector.base")


class BaseCollector(ABC):
    def __init__(self, source_config: Dict[str, Any], health_file: Optional[Path] = None):
        self.config = source_config
        self.source_id = source_config.get("id", "unknown_source")
        self.source_name = source_config.get("name", "Unknown Source")
        self.enabled = source_config.get("enabled", True)
        self.tier = source_config.get("tier", 2)
        if health_file is None:
            self.health_file = Path(__file__).resolve().parent.parent.parent / "data" / "source_health.json"
        else:
            self.health_file = Path(health_file)

    @abstractmethod
    def collect(self) -> List[Resource]:
        """Collects opportunities from the target source."""
        pass

    def record_health(self, success: bool, items_found: int = 0, error_msg: Optional[str] = None) -> None:
        """Updates persistent health log for this source."""
        try:
            health_data = {}
            if self.health_file.exists():
                with open(self.health_file, "r", encoding="utf-8") as f:
                    health_data = json.load(f)

            sources_log = health_data.setdefault("sources", {})
            sources_log[self.source_id] = {
                "name": self.source_name,
                "last_check": to_iso_string(),
                "status": "HEALTHY" if success else "ERROR",
                "items_found": items_found,
                "error": error_msg or ""
            }
            health_data["last_check"] = to_iso_string()

            self.health_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.health_file, "w", encoding="utf-8") as f:
                json.dump(health_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Failed to record source health: {e}")

    def safe_collect(self) -> List[Resource]:
        """Safely executes collect() without allowing exceptions to crash the application."""
        if not self.enabled:
            logger.debug(f"Source {self.source_id} is disabled. Skipping.")
            return []

        start_time = time.time()
        logger.info(f"Collecting from [{self.source_name}]...")
        try:
            resources = self.collect()
            elapsed = time.time() - start_time
            logger.info(f"[{self.source_name}] Discovered {len(resources)} items in {elapsed:.2f}s")
            self.record_health(success=True, items_found=len(resources))
            return resources
        except Exception as e:
            elapsed = time.time() - start_time
            error_str = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Failed to collect from [{self.source_name}] ({elapsed:.2f}s): {error_str}")
            self.record_health(success=False, error_msg=error_str)
            return []
