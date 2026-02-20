"""
Pydantic data models for YouTube Analytics.
Provides type safety and validation for API responses.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, computed_field


class ContentType(str, Enum):
    """YouTube content type classification.

    Authoritative source: Analytics API creatorContentType dimension.
    Fallback: duration-based heuristic.
    """
    SHORTS = "SHORTS"
    VIDEO_ON_DEMAND = "VIDEO_ON_DEMAND"
    LIVE_STREAM = "LIVE_STREAM"
    STORY = "STORY"
    UNSPECIFIED = "UNSPECIFIED"


class Video(BaseModel):
    """Model for a YouTube video."""
    video_id: str
    title: str
    description: str = ""
    published_at: datetime
    channel_id: str
    channel_title: str
    thumbnail_url: str = ""
    tags: List[str] = Field(default_factory=list)
    category_id: Optional[str] = None
    duration_minutes: float
    duration_iso: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    content_type: ContentType = ContentType.UNSPECIFIED

    @computed_field
    @property
    def is_short(self) -> bool:
        """Determine if video is a Short.

        Uses content_type if classified by Analytics API, otherwise falls back
        to duration heuristic (<= 3 minutes, expanded from 60s in Oct 2024).
        """
        if self.content_type != ContentType.UNSPECIFIED:
            return self.content_type == ContentType.SHORTS
        return self.duration_minutes <= 3.0

    @computed_field
    @property
    def show_name(self) -> str:
        """Extract show name from title using PBS Wisconsin conventions."""
        if " | " not in self.title:
            return "Uncategorized"

        parts = self.title.split(" | ")

        # Wisconsin Life is reversed
        if parts[0].strip() == "Wisconsin Life":
            return "Wisconsin Life"

        return parts[-1].strip()

    @computed_field
    @property
    def days_since_publication(self) -> int:
        """Days since the video was published."""
        return (datetime.now() - self.published_at).days

    @computed_field
    @property
    def views_per_day(self) -> float:
        """Average views per day since publication."""
        days = self.days_since_publication or 1
        return self.views / days

    @computed_field
    @property
    def engagement_rate(self) -> float:
        """Engagement rate as percentage."""
        if self.views == 0:
            return 0.0
        return ((self.likes + self.comments) / self.views) * 100


class ChannelStats(BaseModel):
    """Model for channel-level statistics."""
    channel_id: str
    title: str
    description: str = ""
    subscriber_count: int = 0
    video_count: int = 0
    view_count: int = 0
    uploads_playlist_id: str
    published_at: str


class DailyAnalytics(BaseModel):
    """Model for daily channel analytics."""
    date: datetime
    views: int = 0
    engaged_views: Optional[int] = None
    watch_time_minutes: float = 0.0
    avg_view_duration_seconds: float = 0.0
    subscribers_gained: int = 0
    subscribers_lost: int = 0

    @computed_field
    @property
    def net_subscribers(self) -> int:
        """Net subscriber change."""
        return self.subscribers_gained - self.subscribers_lost


class VideoAnalytics(BaseModel):
    """Model for per-video analytics."""
    video_id: str
    views: int = 0
    engaged_views: Optional[int] = None
    watch_time_minutes: float = 0.0
    avg_view_duration_seconds: float = 0.0
    subscribers_gained: int = 0
    subscribers_lost: int = 0


class TrafficSource(BaseModel):
    """Model for traffic source data."""
    source: str
    views: int = 0
    watch_time_minutes: float = 0.0


class SubscriberSource(BaseModel):
    """Model for subscriber acquisition by video."""
    video_id: str
    subscribers_gained: int = 0
    subscribers_lost: int = 0

    @computed_field
    @property
    def net_subscribers(self) -> int:
        """Net subscriber change from this video."""
        return self.subscribers_gained - self.subscribers_lost


# === Database Models (SQLAlchemy compatible) ===

class VideoRecord(BaseModel):
    """Database record for video with all computed fields stored."""
    video_id: str
    title: str
    description: str = ""
    published_at: datetime
    channel_id: str
    channel_title: str
    show_name: str
    duration_minutes: float
    is_short: bool
    content_type: str = ContentType.UNSPECIFIED.value
    view_count_methodology: str = "legacy"
    views: int = 0
    likes: int = 0
    comments: int = 0
    engagement_rate: float = 0.0
    views_per_day: float = 0.0
    days_since_publication: int = 0
    last_updated: datetime = Field(default_factory=datetime.now)


class DailyStatsRecord(BaseModel):
    """Database record for daily video stats snapshot."""
    video_id: str
    date: datetime
    views: int = 0
    engaged_views: Optional[int] = None
    likes: int = 0
    comments: int = 0
    watch_time_minutes: float = 0.0
    subscribers_gained: int = 0


class ChannelSnapshotRecord(BaseModel):
    """Database record for daily channel snapshot."""
    channel_id: str
    date: datetime
    subscriber_count: int = 0
    video_count: int = 0
    view_count: int = 0
    daily_views: int = 0
    daily_watch_time_minutes: float = 0.0
    daily_subscribers_gained: int = 0
    daily_subscribers_lost: int = 0
