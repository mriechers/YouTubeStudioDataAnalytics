"""Show name extraction and normalization for PBS Wisconsin video titles."""

from pathlib import Path
from typing import Optional, Dict

import yaml

_SHOW_MAPPINGS_PATH = Path(__file__).parent.parent.parent / "config" / "show_mappings.yaml"
_show_mappings: Optional[Dict[str, str]] = None


def _get_show_mappings() -> Dict[str, str]:
    """Load and cache show name mappings from config."""
    global _show_mappings
    if _show_mappings is not None:
        return _show_mappings

    _show_mappings = {}
    if _SHOW_MAPPINGS_PATH.exists():
        with open(_SHOW_MAPPINGS_PATH) as f:
            config = yaml.safe_load(f) or {}
        raw = config.get("mappings", {})
        for variant, canonical in raw.items():
            _show_mappings[variant.lower()] = canonical
    return _show_mappings


def normalize_show_name(raw_name: str) -> str:
    """Apply show name mappings to a raw extracted name.

    Strips the legacy "WPT " prefix, then checks for explicit mappings.
    """
    name = raw_name
    if name.startswith("WPT "):
        name = name[4:]

    mappings = _get_show_mappings()
    return mappings.get(name.lower(), name)


def extract_show_name(title: str) -> str:
    """
    Extract show name from video title using PBS Wisconsin naming conventions.

    Formats (checked in order):
      1. Pipe (current):  "Video Title | SHOW NAME"  -> SHOW NAME
         Exception:       "Wisconsin Life | ..."      -> Wisconsin Life
      2. Colon (legacy):  "Show Name: Episode Title"  -> Show Name
      3. Dash (legacy):   "Show Name - Episode Title" -> Show Name

    After extraction, the raw name is normalized via config/show_mappings.yaml
    (strips "WPT " prefix, merges variant spellings).
    """
    raw = None

    if " | " in title:
        parts = title.split(" | ")
        if parts[0].strip() == "Wisconsin Life":
            raw = "Wisconsin Life"
        else:
            raw = parts[-1].strip()
    elif ": " in title:
        raw = title.split(": ", 1)[0].strip()
    elif " - " in title:
        raw = title.split(" - ", 1)[0].strip()

    if raw is None:
        return "Uncategorized"

    return normalize_show_name(raw)
