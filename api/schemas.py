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


# --- Insight Dashboard Schemas ---

class ChannelHealthKPIs(BaseModel):
    subscriber_count: int = 0
    avg_daily_views: float = 0.0
    total_watch_time_hours: float = 0.0
    avg_view_duration_seconds: float = 0.0
    views_trend_pct: Optional[float] = None
    watch_time_trend_pct: Optional[float] = None
    subscribers_trend_pct: Optional[float] = None

class ContentVelocity(BaseModel):
    new_uploads: int = 0
    avg_views_at_7d: Optional[float] = None
    avg_views_at_30d: Optional[float] = None
    catalog_view_pct: float = 0.0
    new_content_view_pct: float = 0.0

class ChannelHealthResponse(BaseModel):
    kpis: ChannelHealthKPIs
    timeseries: List[TimeseriesPoint]
    velocity: ContentVelocity
    publishing_cadence: List[Dict[str, Any]]
    watch_time_by_format: List[Dict[str, Any]]

class VideoWithContext(BaseModel):
    video_id: str
    title: str
    published_at: Optional[datetime] = None
    show_name: Optional[str] = None
    is_short: Optional[bool] = False
    views: int = 0
    likes: int = 0
    comments: int = 0
    engagement_rate: Optional[float] = 0.0
    views_per_day: Optional[float] = 0.0
    days_since_publication: Optional[int] = 0
    z_score: float = 0.0
    vs_show_multiplier: float = 0.0
    show_avg_vpd: float = 0.0
    subscribers_gained: Optional[int] = None

class ShowHitRate(BaseModel):
    show_name: str
    video_count: int
    hit_count: int
    hit_rate: float

class HitsResponse(BaseModel):
    hit_count: int
    avg_hit_multiplier: float
    top_sub_driver: Optional[str] = None
    best_show_hit_rate: Optional[str] = None
    top_performers: List[VideoWithContext]
    show_hit_rates: List[ShowHitRate]
    subscriber_drivers: List[Dict[str, Any]]

class ShowVariance(BaseModel):
    show_name: str
    video_count: int
    avg_views_per_day: float
    coeff_of_variation: float
    hit_count: int
    hit_rate: float

class FormatGapShow(BaseModel):
    show_name: str
    video_count: int
    total_views: Optional[int] = None
    avg_engagement: Optional[float] = None
    avg_views_per_day: Optional[float] = None
    channel_avg_views_per_day: Optional[float] = None
    ratio: Optional[float] = None

class OpportunitiesResponse(BaseModel):
    inconsistent_shows: List[ShowVariance]
    catalog_risers: List[Dict[str, Any]]
    no_shorts: List[FormatGapShow]
    underperforming: List[FormatGapShow]

class RecentResponse(BaseModel):
    videos: List[VideoWithContext]
    summary: Dict[str, Any]
