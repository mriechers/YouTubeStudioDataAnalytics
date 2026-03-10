"""Analytics endpoints for dashboard panels."""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_db, get_api_client
from api.schemas import (
    ShowSummary, ShortsComparison, VideoSummary,
    OverviewKPIs, TimeseriesPoint,
    ShortsDetailVideo, ShortsOverviewKPIs, ShortsFullResponse,
    AudienceLoyaltyResponse, AudienceLoyaltyPoint,
)

router = APIRouter()


@router.get("/analytics/overview", response_model=OverviewKPIs)
def get_overview(
    channel_id: Optional[str] = Query(None),
    db=Depends(get_db),
):
    """KPI summary for the dashboard overview."""
    videos = db.get_all_videos(channel_id=channel_id)
    shorts_data = db.get_shorts_vs_longform(channel_id=channel_id)

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
def get_show_breakdown(
    channel_id: Optional[str] = Query(None),
    db=Depends(get_db),
):
    """Show breakdown for the show performance panel."""
    return db.get_show_summary(channel_id=channel_id)


@router.get("/analytics/shorts", response_model=ShortsFullResponse)
def get_shorts_comparison(
    channel_id: Optional[str] = Query(None),
    days: int = Query(90, ge=7, le=365),
    db=Depends(get_db),
):
    """Shorts full response: KPIs, comparison, video list with sparklines, timeseries."""
    comparison_data = db.get_shorts_vs_longform(channel_id=channel_id)
    shorts_videos = db.get_shorts_detail(channel_id=channel_id)
    aggregate = db.get_shorts_daily_aggregate(channel_id=channel_id, days=days)
    all_videos = db.get_all_videos(channel_id=channel_id)

    # channel_avg_views = total views of all videos / count of all videos
    total_all_views = sum(v.get("views", 0) for v in all_videos)
    total_all_count = len(all_videos)
    channel_avg_views = total_all_views / max(total_all_count, 1)

    # Build KPIs from shorts data
    shorts_count = len(shorts_videos)
    total_views = sum(v.get("views", 0) for v in shorts_videos)
    total_engaged = None
    avg_views = total_views / max(shorts_count, 1)
    avg_engagement = (
        sum(v.get("engagement_rate", 0) or 0 for v in shorts_videos) / max(shorts_count, 1)
    )
    avg_views_per_day = (
        sum(v.get("views_per_day", 0) or 0 for v in shorts_videos) / max(shorts_count, 1)
    )
    avg_viewed_vs_swiped = (
        sum(v.get("viewed_vs_swiped_pct", 0) or 0 for v in shorts_videos) / max(shorts_count, 1)
    )

    kpis = ShortsOverviewKPIs(
        count=shorts_count,
        total_views=total_views,
        total_engaged_views=total_engaged,
        avg_views=round(avg_views, 2),
        avg_engagement=round(avg_engagement, 4),
        avg_views_per_day=round(avg_views_per_day, 2),
        viewed_vs_swiped_pct=round(avg_viewed_vs_swiped, 2),
        channel_avg_views=round(channel_avg_views, 2),
    )

    # Build sparklines for top 20 shorts by views
    top20_ids = {v["video_id"] for v in shorts_videos[:20]}
    sparkline_map: dict = {}
    for vid in shorts_videos[:20]:
        vid_id = vid["video_id"]
        daily = db.get_video_daily_stats(vid_id, days=28)
        sparkline_map[vid_id] = [row["views"] for row in daily]

    videos = [
        ShortsDetailVideo(
            video_id=v["video_id"],
            title=v["title"],
            published_at=v.get("published_at"),
            show_name=v.get("show_name"),
            views=v.get("views", 0),
            likes=v.get("likes", 0),
            comments=v.get("comments", 0),
            engagement_rate=v.get("engagement_rate", 0.0),
            avg_view_pct=v.get("avg_view_pct", 0.0),
            ctr=v.get("ctr", 0.0),
            viewed_vs_swiped_pct=v.get("viewed_vs_swiped_pct", 0.0),
            views_per_day=v.get("views_per_day", 0.0),
            days_since_publication=v.get("days_since_publication", 0),
            sparkline=sparkline_map.get(v["video_id"]) if v["video_id"] in top20_ids else None,
        )
        for v in shorts_videos
    ]

    timeseries = [
        TimeseriesPoint(
            date=row["date"],
            views=row["views"],
            engaged_views=row.get("engaged_views"),
            watch_time_minutes=row.get("watch_time_minutes", 0.0),
            avg_view_pct=row.get("avg_view_pct", 0.0),
            ctr=row.get("ctr", 0.0),
            viewed_vs_swiped_pct=row.get("viewed_vs_swiped_pct", 0.0),
            subscribers_gained=row.get("subscribers_gained", 0),
        )
        for row in aggregate
    ]

    return ShortsFullResponse(
        kpis=kpis,
        comparison=ShortsComparison(**comparison_data),
        videos=videos,
        timeseries=timeseries,
    )


@router.get("/analytics/videos/{video_id}/daily", response_model=List[TimeseriesPoint])
def get_video_daily_stats(
    video_id: str,
    days: int = Query(28, ge=7, le=365),
    db=Depends(get_db),
):
    """Daily stats for a single video."""
    rows = db.get_video_daily_stats(video_id=video_id, days=days)
    return [
        TimeseriesPoint(
            date=row["date"],
            views=row["views"],
            engaged_views=row.get("engaged_views"),
            watch_time_minutes=row.get("watch_time_minutes", 0.0),
            subscribers_gained=row.get("subscribers_gained", 0),
        )
        for row in rows
    ]


@router.get("/analytics/archival", response_model=List[VideoSummary])
def get_archival_videos(
    months: int = Query(12, ge=3, le=60),
    channel_id: Optional[str] = Query(None),
    db=Depends(get_db),
):
    """Archival content older than threshold."""
    return db.get_archival_videos(months_threshold=months, channel_id=channel_id)


@router.get("/analytics/subscribers")
def get_subscriber_attribution(client=Depends(get_api_client)):
    """Subscriber attribution by video."""
    try:
        return client.get_subscriber_sources()
    except Exception:
        return []


@router.get("/analytics/matrix", response_model=List[VideoSummary])
def get_matrix(
    channel_id: Optional[str] = Query(None),
    db=Depends(get_db),
):
    """Data for CTR vs AVD scatter plot matrix."""
    return db.get_all_videos(channel_id=channel_id)
