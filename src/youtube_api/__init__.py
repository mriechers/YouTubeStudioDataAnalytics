"""
YouTube API integration module for PBS Wisconsin Analytics.
Replaces CSV-based data loading with live YouTube API data.
"""

from .client import YouTubeAPIClient
from .auth import get_authenticated_service, setup_oauth
from .data_loader import YouTubeAPIDataLoader
from .show_parser import extract_show_name
from .database import AnalyticsDatabase
from .models import Video, ChannelStats, DailyAnalytics, VideoAnalytics, ContentType

__all__ = [
    'YouTubeAPIClient',
    'YouTubeAPIDataLoader',
    'AnalyticsDatabase',
    'get_authenticated_service',
    'setup_oauth',
    'extract_show_name',
    'Video',
    'ChannelStats',
    'DailyAnalytics',
    'VideoAnalytics',
    'ContentType',
]
