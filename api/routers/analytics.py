"""Analytics endpoints for dashboard panels."""

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_db, get_api_client
from api.schemas import (
    ShowSummary, ShortsComparison, VideoSummary,
    OverviewKPIs, TimeseriesPoint,
    ChannelHealthResponse, ChannelHealthKPIs, ContentVelocity,
    HitsResponse, VideoWithContext, ShowHitRate,
    OpportunitiesResponse, ShowVariance, FormatGapShow,
    RecentResponse,
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


@router.get("/analytics/health", response_model=ChannelHealthResponse)
def get_health(
    channel_id: Optional[str] = Query(None),
    days: int = Query(90, ge=7, le=365),
    db=Depends(get_db),
):
    """Channel health dashboard data."""
    from datetime import datetime, timedelta

    if not channel_id:
        from api.config import load_channels_config
        config = load_channels_config()
        channels = config.get("channels", [])
        if channels:
            channel_id = channels[0]["id"]

    snapshots = db.get_channel_history(channel_id=channel_id, days=days) if channel_id else []
    timeseries = [
        TimeseriesPoint(
            date=s.get("date"),
            views=s.get("daily_views", 0),
            watch_time_minutes=s.get("daily_watch_time_minutes", 0),
            subscribers_gained=s.get("daily_subscribers_gained", 0),
            subscribers_lost=s.get("daily_subscribers_lost", 0),
        )
        for s in snapshots
    ]

    total_views = sum(s.get("daily_views", 0) for s in snapshots)
    total_watch_min = sum(s.get("daily_watch_time_minutes", 0) for s in snapshots)
    num_days = max(len(snapshots), 1)
    avg_daily_views = total_views / num_days

    prior_snapshots = db.get_channel_history(channel_id=channel_id, days=days * 2) if channel_id else []
    prior_only = [s for s in prior_snapshots if s not in snapshots]
    prior_views = sum(s.get("daily_views", 0) for s in prior_only)
    prior_days = max(len(prior_only), 1)
    prior_avg = prior_views / prior_days
    views_trend = ((avg_daily_views - prior_avg) / prior_avg * 100) if prior_avg > 0 else None

    sub_count = snapshots[-1].get("subscriber_count", 0) if snapshots else 0

    kpis = ChannelHealthKPIs(
        subscriber_count=sub_count,
        avg_daily_views=round(avg_daily_views, 1),
        total_watch_time_hours=round(total_watch_min / 60, 1),
        views_trend_pct=round(views_trend, 1) if views_trend is not None else None,
    )

    all_videos = db.get_all_videos(channel_id=channel_id)
    cutoff = datetime.now() - timedelta(days=days)
    new_videos = [v for v in all_videos if v.get("published_at") and v["published_at"] >= cutoff]
    old_videos = [v for v in all_videos if v.get("published_at") and v["published_at"] < cutoff]

    new_views = sum(v.get("views", 0) for v in new_videos)
    old_views = sum(v.get("views", 0) for v in old_videos)
    total_all_views = new_views + old_views

    velocity = ContentVelocity(
        new_uploads=len(new_videos),
        catalog_view_pct=round(old_views / max(total_all_views, 1) * 100, 1),
        new_content_view_pct=round(new_views / max(total_all_views, 1) * 100, 1),
    )

    from collections import Counter
    week_counts = Counter()
    for v in new_videos:
        pub = v.get("published_at")
        if pub:
            week_str = pub.strftime("%Y-W%W")
            week_counts[week_str] += 1
    cadence = [{"week": w, "count": c} for w, c in sorted(week_counts.items())]

    return ChannelHealthResponse(
        kpis=kpis,
        timeseries=timeseries,
        velocity=velocity,
        publishing_cadence=cadence,
        watch_time_by_format=[],
    )


@router.get("/analytics/hits", response_model=HitsResponse)
def get_hits(
    channel_id: Optional[str] = Query(None),
    days: int = Query(90, ge=7, le=365),
    db=Depends(get_db),
    client=Depends(get_api_client),
):
    """Hits & insights dashboard data."""
    videos = db.get_videos_with_show_context(channel_id=channel_id)

    hits = [v for v in videos if v.get("z_score", 0) > 2.0]
    hits.sort(key=lambda v: v.get("z_score", 0), reverse=True)

    hit_count = len(hits)
    avg_multiplier = (
        sum(h.get("vs_show_multiplier", 0) for h in hits) / max(hit_count, 1)
    )

    from collections import defaultdict
    show_totals = defaultdict(lambda: {"total": 0, "hits": 0})
    for v in videos:
        show = v.get("show_name") or "Uncategorized"
        show_totals[show]["total"] += 1
        if v.get("z_score", 0) > 2.0:
            show_totals[show]["hits"] += 1

    show_hit_rates = [
        ShowHitRate(
            show_name=name,
            video_count=data["total"],
            hit_count=data["hits"],
            hit_rate=round(data["hits"] / data["total"] * 100, 1),
        )
        for name, data in show_totals.items()
        if data["total"] >= 5
    ]
    show_hit_rates.sort(key=lambda x: x.hit_rate, reverse=True)

    best_show = show_hit_rates[0].show_name if show_hit_rates else None

    try:
        sub_sources = client.get_subscriber_sources()
    except Exception:
        sub_sources = []

    top_sub = sub_sources[0]["video_id"] if sub_sources else None
    top_sub_title = None
    if top_sub:
        for v in videos:
            if v.get("video_id") == top_sub:
                top_sub_title = v.get("title")
                break

    top_performers = [
        VideoWithContext(**{k: v.get(k) for k in VideoWithContext.model_fields})
        for v in hits[:50]
    ]

    return HitsResponse(
        hit_count=hit_count,
        avg_hit_multiplier=round(avg_multiplier, 1),
        top_sub_driver=top_sub_title,
        best_show_hit_rate=f"{best_show} ({show_hit_rates[0].hit_rate}%)" if best_show else None,
        top_performers=top_performers,
        show_hit_rates=show_hit_rates,
        subscriber_drivers=sub_sources[:10],
    )


@router.get("/analytics/opportunities", response_model=OpportunitiesResponse)
def get_opportunities(
    channel_id: Optional[str] = Query(None),
    db=Depends(get_db),
):
    """Opportunities dashboard data."""
    variance = db.get_show_variance_analysis(channel_id=channel_id)
    format_gaps = db.get_format_gaps(channel_id=channel_id)

    inconsistent = [
        ShowVariance(**{k: v for k, v in s.items() if k in ShowVariance.model_fields})
        for s in variance
    ]

    no_shorts = [FormatGapShow(**s) for s in format_gaps["no_shorts"]]
    underperforming = [FormatGapShow(**s) for s in format_gaps["underperforming"]]

    return OpportunitiesResponse(
        inconsistent_shows=inconsistent,
        catalog_risers=[],
        no_shorts=no_shorts,
        underperforming=underperforming,
    )


@router.get("/analytics/recent", response_model=RecentResponse)
def get_recent(
    channel_id: Optional[str] = Query(None),
    days: int = Query(30, ge=7, le=365),
    db=Depends(get_db),
):
    """Recent content lookup data."""
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=days)

    videos = db.get_videos_with_show_context(
        channel_id=channel_id,
        published_after=cutoff,
    )
    videos.sort(key=lambda v: v.get("views", 0), reverse=True)

    video_models = [
        VideoWithContext(**{k: v.get(k) for k in VideoWithContext.model_fields})
        for v in videos
    ]

    count = len(videos)
    total_views = sum(v.get("views", 0) for v in videos)
    avg_vpd = sum(v.get("views_per_day", 0) or 0 for v in videos) / max(count, 1)
    avg_eng = sum(v.get("engagement_rate", 0) or 0 for v in videos) / max(count, 1)

    return RecentResponse(
        videos=video_models,
        summary={
            "count": count,
            "total_views": total_views,
            "avg_views_per_day": round(avg_vpd, 1),
            "avg_engagement": round(avg_eng, 2),
        },
    )
