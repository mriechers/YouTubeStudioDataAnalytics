"""Pydantic response schemas for the API."""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str


class AuthStatusResponse(BaseModel):
    authenticated: bool
    expires_at: Optional[str] = None


class ChannelConfig(BaseModel):
    id: str
    name: str
    type: str


class ChannelStats(BaseModel):
    id: str
    title: str
    subscriber_count: int
    video_count: int
    view_count: int


class VideoSummary(BaseModel):
    video_id: str
    title: str
    published_at: Optional[datetime] = None
    channel_id: str
    channel_title: Optional[str] = None
    show_name: Optional[str] = None
    duration_minutes: Optional[float] = None
    is_short: Optional[bool] = False
    content_type: Optional[str] = "UNSPECIFIED"
    views: int = 0
    likes: int = 0
    comments: int = 0
    engagement_rate: Optional[float] = 0.0
    views_per_day: Optional[float] = 0.0
    days_since_publication: Optional[int] = 0


class ShowSummary(BaseModel):
    show_name: Optional[str] = None
    video_count: int
    total_views: int
    total_likes: int
    avg_engagement: float
    shorts_count: int


class ShortsComparison(BaseModel):
    shorts: Dict[str, Any]
    longform: Dict[str, Any]


class OverviewKPIs(BaseModel):
    total_videos: int
    total_views: int
    total_subscribers: int
    shorts_count: int
    longform_count: int
    shorts_ratio: float
    avg_engagement: float


class TimeseriesPoint(BaseModel):
    date: Optional[datetime] = None
    views: int = 0
    engaged_views: Optional[int] = None
    watch_time_minutes: float = 0.0
    subscribers_gained: int = 0
    subscribers_lost: int = 0


class DataStatus(BaseModel):
    last_refresh: Optional[str] = None
    video_count: int = 0
    database_path: str


class RefreshResult(BaseModel):
    success: bool
    videos_loaded: int = 0
    message: str = ""
