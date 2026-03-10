"""Analytics endpoints for dashboard panels."""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_db, get_api_client
from api.schemas import (
    ShowSummary, ShortsComparison, VideoSummary,
    OverviewKPIs, TimeseriesPoint,
)

router = APIRouter()


@router.get("/analytics/overview", response_model=OverviewKPIs)
def get_overview(db=Depends(get_db)):
    """KPI summary for the dashboard overview."""
    videos = db.get_all_videos()
    shorts_data = db.get_shorts_vs_longform()

    total_views = sum(v.get("views", 0) for v in videos)
    total_videos = len(videos)
    shorts_count = shorts_data["shorts"]["count"]
    longform_count = shorts_data["longform"]["count"]

    avg_engagement = 0.0
    if total_videos > 0:
        avg_engagement = sum(
            v.get("engagement_rate", 0) or 0 for v in videos
        ) / total_videos

    return OverviewKPIs(
        total_videos=total_videos,
        total_views=total_views,
        total_subscribers=0,
        shorts_count=shorts_count,
        longform_count=longform_count,
        shorts_ratio=shorts_count / max(total_videos, 1) * 100,
        avg_engagement=round(avg_engagement, 2),
    )


@router.get("/analytics/timeseries", response_model=List[TimeseriesPoint])
def get_timeseries(
    channel_id: Optional[str] = Query(None),
    days: int = Query(90, ge=7, le=365),
    db=Depends(get_db),
):
    """Daily metrics time series for line charts."""
    if not channel_id:
        from api.config import load_channels_config
        config = load_channels_config()
        channels = config.get("channels", [])
        if channels:
            channel_id = channels[0]["id"]

    if not channel_id:
        return []

    snapshots = db.get_channel_history(channel_id=channel_id, days=days)
    return [
        TimeseriesPoint(
            date=s.get("date"),
            views=s.get("daily_views", 0),
            watch_time_minutes=s.get("daily_watch_time_minutes", 0),
            subscribers_gained=s.get("daily_subscribers_gained", 0),
            subscribers_lost=s.get("daily_subscribers_lost", 0),
        )
        for s in snapshots
    ]


@router.get("/analytics/shows", response_model=List[ShowSummary])
def get_show_breakdown(db=Depends(get_db)):
    """Show breakdown for the show performance panel."""
    return db.get_show_summary()


@router.get("/analytics/shorts", response_model=ShortsComparison)
def get_shorts_comparison(db=Depends(get_db)):
    """Shorts vs longform comparison."""
    return db.get_shorts_vs_longform()


@router.get("/analytics/archival", response_model=List[VideoSummary])
def get_archival_videos(
    months: int = Query(12, ge=3, le=60),
    db=Depends(get_db),
):
    """Archival content older than threshold."""
    return db.get_archival_videos(months_threshold=months)


@router.get("/analytics/subscribers")
def get_subscriber_attribution(client=Depends(get_api_client)):
    """Subscriber attribution by video."""
    try:
        return client.get_subscriber_sources()
    except Exception:
        return []
