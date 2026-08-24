"""
Configuration Loader for Profile, Sources, Competencies, and Weights.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.models import Competency


def _env_subst(val: str) -> str:
    """Substitutes ${VAR:-default} and ${VAR} patterns with environment variables."""
    pattern = re.compile(r"\$\{([A-Za-z0-9_]+)(?::-(.*?))?\}")

    def replace_match(match):
        var_name = match.group(1)
        default_val = match.group(2) if match.group(2) is not None else ""
        return os.environ.get(var_name, default_val)

    return pattern.sub(replace_match, val)


def _deep_subst(obj: Any) -> Any:
    if isinstance(obj, str):
        return _env_subst(obj)
    elif isinstance(obj, dict):
        return {k: _deep_subst(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_deep_subst(item) for item in obj]
    return obj


class ConfigLoader:
    def __init__(self, root_dir: Optional[str] = None):
        if root_dir is None:
            self.root_dir = Path(__file__).resolve().parent.parent
        else:
            self.root_dir = Path(root_dir)
        self.config_dir = self.root_dir / "config"
        self.data_dir = self.root_dir / "data"

    def load_profile(self) -> Dict[str, Any]:
        path = self.config_dir / "profile.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Profile configuration not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return _deep_subst(data)

    def load_sources(self) -> List[Dict[str, Any]]:
        path = self.config_dir / "sources.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Sources configuration not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        sources = data.get("sources", [])
        return _deep_subst(sources)

    def load_competencies(self) -> List[Competency]:
        path = self.config_dir / "competencies.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Competencies configuration not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        raw_list = data.get("competencies", [])
        competencies = []
        for item in raw_list:
            competencies.append(
                Competency(
                    id=item["id"],
                    name=item["name"],
                    category=item.get("category", "General"),
                    current_level=int(item.get("current_level", 1)),
                    target_level=int(item.get("target_level", 5)),
                    priority=item.get("priority", "Medium"),
                    practical_evidence=item.get("practical_evidence", ""),
                    last_reviewed=item.get("last_reviewed", ""),
                    target_stage=item.get("target_stage", "Stage 4: Talent Development & Talent Management")
                )
            )
        return competencies

    def load_scoring_weights(self) -> Dict[str, Any]:
        path = self.config_dir / "scoring_weights.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Scoring weights configuration not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return _deep_subst(data)

    def save_competencies(self, competencies: List[Competency]) -> None:
        path = self.config_dir / "competencies.yaml"
        payload = {
            "stages": {
                "stage_1": "L&D Foundations",
                "stage_2": "Effective L&D Management",
                "stage_3": "Strategic Learning & Capability Development",
                "stage_4": "Talent Development & Talent Management",
                "stage_5": "Enterprise Talent / Strategic HR Leadership"
            },
            "competencies": [c.to_dict() for c in competencies]
        }
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(payload, f, default_flow_style=False, sort_keys=False)
