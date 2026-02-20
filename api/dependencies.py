"""FastAPI dependency injection providers."""

import sys
from functools import lru_cache
from pathlib import Path

# Ensure src/ is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from youtube_api import AnalyticsDatabase, YouTubeAPIClient
from .config import DATABASE_PATH, CREDENTIALS_PATH, TOKEN_PATH


@lru_cache
def get_db() -> AnalyticsDatabase:
    """Shared database instance (created once per process)."""
    return AnalyticsDatabase(db_path=DATABASE_PATH)


@lru_cache
def get_api_client() -> YouTubeAPIClient:
    """Shared API client instance (lazy-authenticated)."""
    return YouTubeAPIClient(
        credentials_path=str(CREDENTIALS_PATH),
        token_path=str(TOKEN_PATH),
    )
