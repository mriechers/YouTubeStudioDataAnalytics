"""FastAPI application configuration."""

from pathlib import Path
from typing import List, Dict, Any

import yaml

PROJECT_ROOT = Path(__file__).parent.parent

# Paths
DATABASE_PATH = PROJECT_ROOT / "data" / "youtube_analytics.db"
CREDENTIALS_PATH = PROJECT_ROOT / "credentials" / "work" / "credentials.json"
TOKEN_PATH = PROJECT_ROOT / "credentials" / "work" / "token-analytics.json"
CHANNELS_CONFIG_PATH = PROJECT_ROOT / "config" / "channels.yaml"


def load_channels_config() -> Dict[str, Any]:
    """Load channel configuration from YAML."""
    if not CHANNELS_CONFIG_PATH.exists():
        return {"channels": [], "defaults": {}, "show_overrides": {}}
    with open(CHANNELS_CONFIG_PATH) as f:
        return yaml.safe_load(f) or {}
