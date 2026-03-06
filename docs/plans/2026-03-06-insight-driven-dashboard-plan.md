# Insight-Driven Dashboard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the 5-tab data-type dashboard (Overview, Shows, Shorts, Archival, Subscribers) with a 4-tab insight-driven dashboard (Health, Hits, Opportunities, Recent) plus a data backfill script to populate channel_snapshots and daily_stats.

**Architecture:** Backend-first — add new database query methods and API endpoints, then build frontend pages. The backfill script runs independently. New API endpoints compute z-scores, coefficients of variation, and show-relative metrics server-side. Frontend is presentational.

**Tech Stack:** Python/FastAPI (backend), SQLAlchemy (queries), React/TypeScript (frontend), ECharts (charts), TanStack Table (tables), TanStack Query (data fetching)

**Design doc:** `docs/plans/2026-03-06-insight-driven-dashboard-design.md`

---

## Task 1: Backfill Script — Channel-Level Analytics

Populates `channel_snapshots` table with 18 months of daily channel metrics from YouTube Analytics API.

**Files:**
- Create: `scripts/backfill_analytics.py`

**Step 1: Create the backfill script**

```python
"""Backfill channel_snapshots and daily_stats from YouTube Analytics API.

Usage:
    python scripts/backfill_analytics.py --channel          # backfill channel snapshots (18 months)
    python scripts/backfill_analytics.py --daily            # fetch yesterday's data (cron mode)
    python scripts/backfill_analytics.py --videos --days 90 # backfill per-video daily stats
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Project imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from youtube_api import AnalyticsDatabase, YouTubeAPIClient
from api.config import DATABASE_PATH, CREDENTIALS_PATH, TOKEN_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def backfill_channel_snapshots(client: YouTubeAPIClient, db: AnalyticsDatabase, days: int = 540):
    """Backfill channel-level daily analytics.

    The Analytics API accepts date ranges, so we fetch in 90-day chunks
    to stay within response size limits. Each chunk is one API query.
    """
    channel_info = client.get_channel_info()
    channel_id = channel_info["id"]
    end = datetime.now() - timedelta(days=1)
    start = end - timedelta(days=days)

    chunk_size = 90
    current_start = start
    total_rows = 0

    while current_start < end:
        current_end = min(current_start + timedelta(days=chunk_size), end)
        start_str = current_start.strftime("%Y-%m-%d")
        end_str = current_end.strftime("%Y-%m-%d")

        logger.info(f"Fetching channel analytics: {start_str} to {end_str}")
        rows = client.get_channel_analytics(start_date=start_str, end_date=end_str)

        for row in rows:
            date = datetime.strptime(row["date"], "%Y-%m-%d")
            db.add_channel_snapshot(channel_id, date, {
                "subscriber_count": 0,  # not available from Analytics API daily
                "video_count": 0,
                "view_count": 0,
                "daily_views": row["views"],
                "daily_watch_time_minutes": row["watch_time_minutes"],
                "daily_subscribers_gained": row["subscribers_gained"],
                "daily_subscribers_lost": row["subscribers_lost"],
            })
            total_rows += 1

        current_start = current_end + timedelta(days=1)

    logger.info(f"Backfilled {total_rows} channel snapshot rows for {channel_id}")


def backfill_video_daily_stats(client: YouTubeAPIClient, db: AnalyticsDatabase, days: int = 90):
    """Backfill per-video daily stats.

    WARNING: Each video requires a separate API call. The Analytics API
    has a 200 queries/day limit. This function processes videos in batches
    and logs progress so it can be resumed.

    With 4,600 videos, full backfill takes ~23 days at quota.
    Focus on recent/active videos first.
    """
    all_videos = db.get_all_videos()
    # Sort by views desc — backfill the most important videos first
    all_videos.sort(key=lambda v: v.get("views", 0), reverse=True)

    end_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    start_str = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    processed = 0
    max_per_run = 180  # leave headroom under 200/day quota

    for video in all_videos[:max_per_run]:
        video_id = video["video_id"]
        try:
            analytics = client.get_video_analytics(
                video_id=video_id,
                start_date=start_str,
                end_date=end_str,
            )
            if analytics.get("views", 0) > 0:
                date = datetime.strptime(end_str, "%Y-%m-%d")
                db.add_daily_stats(video_id, date, {
                    "views": analytics["views"],
                    "engaged_views": analytics.get("engaged_views"),
                    "watch_time_minutes": analytics.get("watch_time_minutes", 0),
                    "subscribers_gained": analytics.get("subscribers_gained", 0),
                })
            processed += 1
            if processed % 20 == 0:
                logger.info(f"Processed {processed}/{max_per_run} videos")
        except Exception as e:
            logger.warning(f"Failed to fetch analytics for {video_id}: {e}")
            continue

    logger.info(f"Backfilled daily stats for {processed} videos")


def daily_update(client: YouTubeAPIClient, db: AnalyticsDatabase):
    """Fetch yesterday's data for channel + top videos. Designed for daily cron."""
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")

    # Channel snapshot
    logger.info(f"Fetching channel snapshot for {date_str}")
    rows = client.get_channel_analytics(start_date=date_str, end_date=date_str)
    channel_info = client.get_channel_info()

    if rows:
        row = rows[0]
        db.add_channel_snapshot(channel_info["id"], yesterday, {
            "subscriber_count": channel_info["subscriber_count"],
            "video_count": channel_info["video_count"],
            "view_count": channel_info["view_count"],
            "daily_views": row["views"],
            "daily_watch_time_minutes": row["watch_time_minutes"],
            "daily_subscribers_gained": row["subscribers_gained"],
            "daily_subscribers_lost": row["subscribers_lost"],
        })

    # Top 50 videos by recent views
    all_videos = db.get_all_videos()
    all_videos.sort(key=lambda v: v.get("views_per_day", 0), reverse=True)
    for video in all_videos[:50]:
        video_id = video["video_id"]
        try:
            analytics = client.get_video_analytics(
                video_id=video_id,
                start_date=date_str,
                end_date=date_str,
            )
            if analytics.get("views", 0) > 0:
                db.add_daily_stats(video_id, yesterday, {
                    "views": analytics["views"],
                    "engaged_views": analytics.get("engaged_views"),
                    "watch_time_minutes": analytics.get("watch_time_minutes", 0),
                    "subscribers_gained": analytics.get("subscribers_gained", 0),
                })
        except Exception as e:
            logger.warning(f"Failed for {video_id}: {e}")

    logger.info("Daily update complete")


def main():
    parser = argparse.ArgumentParser(description="Backfill YouTube analytics data")
    parser.add_argument("--channel", action="store_true", help="Backfill channel snapshots (18 months)")
    parser.add_argument("--videos", action="store_true", help="Backfill per-video daily stats")
    parser.add_argument("--daily", action="store_true", help="Fetch yesterday's data (cron mode)")
    parser.add_argument("--days", type=int, default=540, help="Days to look back (default: 540)")
    args = parser.parse_args()

    client = YouTubeAPIClient(
        credentials_path=str(CREDENTIALS_PATH),
        token_path=str(TOKEN_PATH),
    )
    db = AnalyticsDatabase(db_path=DATABASE_PATH)

    if args.daily:
        daily_update(client, db)
    elif args.channel:
        backfill_channel_snapshots(client, db, days=args.days)
    elif args.videos:
        backfill_video_daily_stats(client, db, days=args.days)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

**Step 2: Test with a dry run**

Run: `source venv/bin/activate && python scripts/backfill_analytics.py --channel --days 7`
Expected: Fetches 7 days of channel analytics, populates channel_snapshots table

**Step 3: Verify data landed**

Run: `source venv/bin/activate && python -c "from src.youtube_api import AnalyticsDatabase; db = AnalyticsDatabase(); print(f'channel_snapshots: {len(db.get_channel_history(\"CHANNEL_ID\", days=30))} rows')"`

**Step 4: Commit**

```bash
git add scripts/backfill_analytics.py
git commit -m "feat: add backfill script for channel snapshots and daily video stats"
```

---

## Task 2: Backend — New Database Query Methods

Add query methods that power the 4 dashboard tabs. These compute z-scores, coefficients of variation, and show-relative metrics in SQL where possible.

**Files:**
- Modify: `src/youtube_api/database.py`

**Step 1: Add `get_show_stats_for_scoring` method**

Returns per-show mean and stddev of views_per_day, needed for z-score computation. Add after the existing `get_show_summary` method.

```python
def get_show_stats_for_scoring(self, channel_id: Optional[str] = None) -> Dict[str, Dict[str, float]]:
    """Get per-show mean and stddev of views_per_day for z-score computation.

    Returns:
        Dict mapping show_name -> {'mean': float, 'stddev': float, 'count': int}
    """
    with self.get_session() as session:
        query = session.query(
            VideoTable.show_name,
            func.avg(VideoTable.views_per_day).label('mean'),
            func.count(VideoTable.video_id).label('count'),
        )
        if channel_id:
            query = query.filter(VideoTable.channel_id == channel_id)
        results = query.group_by(VideoTable.show_name).all()

        stats = {}
        for r in results:
            show = r.show_name or "Uncategorized"
            mean = r.mean or 0.0
            count = r.count or 0

            # Compute stddev in a second query (SQLite has no built-in stddev)
            sq = session.query(
                func.avg((VideoTable.views_per_day - mean) * (VideoTable.views_per_day - mean))
            ).filter(VideoTable.show_name == r.show_name)
            if channel_id:
                sq = sq.filter(VideoTable.channel_id == channel_id)
            variance = sq.scalar() or 0.0

            stats[show] = {
                'mean': round(mean, 4),
                'stddev': round(variance ** 0.5, 4),
                'count': count,
            }
        return stats
```

**Step 2: Add `get_videos_with_show_context` method**

Returns all videos enriched with show-relative metrics. Used by Hits, Opportunities, and Recent tabs.

```python
def get_videos_with_show_context(
    self,
    channel_id: Optional[str] = None,
    published_after: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """Get all videos with show-relative performance context.

    Args:
        channel_id: Optional channel filter
        published_after: Optional date filter for recent content

    Returns:
        List of video dicts with added fields: show_avg_vpd, show_stddev_vpd,
        z_score, vs_show_multiplier
    """
    show_stats = self.get_show_stats_for_scoring(channel_id=channel_id)
    videos = self.get_all_videos(channel_id=channel_id)

    enriched = []
    for v in videos:
        if published_after and v.get("published_at"):
            if v["published_at"] < published_after:
                continue

        show = v.get("show_name") or "Uncategorized"
        ss = show_stats.get(show, {"mean": 0, "stddev": 0, "count": 0})
        vpd = v.get("views_per_day", 0) or 0
        mean = ss["mean"]
        stddev = ss["stddev"]

        z_score = (vpd - mean) / stddev if stddev > 0 else 0.0
        multiplier = vpd / mean if mean > 0 else 0.0

        v["show_avg_vpd"] = round(mean, 2)
        v["show_stddev_vpd"] = round(stddev, 2)
        v["z_score"] = round(z_score, 2)
        v["vs_show_multiplier"] = round(multiplier, 2)
        enriched.append(v)

    return enriched
```

**Step 3: Add `get_show_variance_analysis` method**

Powers the Opportunities "Inconsistent Shows" section.

```python
def get_show_variance_analysis(self, channel_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get shows ranked by coefficient of variation (stddev/mean of views_per_day).

    High CoV = inconsistent show where topic/title matters more than brand.

    Returns:
        List of show dicts with mean, stddev, coeff_of_variation, hit_rate
    """
    show_stats = self.get_show_stats_for_scoring(channel_id=channel_id)
    results = []
    for show_name, ss in show_stats.items():
        if ss["count"] < 5:  # skip shows with too few videos for meaningful stats
            continue
        mean = ss["mean"]
        stddev = ss["stddev"]
        cov = stddev / mean if mean > 0 else 0.0

        # Count hits (>2 sigma)
        hit_threshold = mean + 2 * stddev
        with self.get_session() as session:
            query = session.query(func.count(VideoTable.video_id)).filter(
                VideoTable.show_name == show_name,
                VideoTable.views_per_day > hit_threshold,
            )
            if channel_id:
                query = query.filter(VideoTable.channel_id == channel_id)
            hit_count = query.scalar() or 0

        results.append({
            "show_name": show_name,
            "video_count": ss["count"],
            "avg_views_per_day": round(mean, 2),
            "stddev_views_per_day": round(stddev, 2),
            "coeff_of_variation": round(cov, 2),
            "hit_count": hit_count,
            "hit_rate": round(hit_count / ss["count"] * 100, 1) if ss["count"] > 0 else 0.0,
        })

    results.sort(key=lambda x: x["coeff_of_variation"], reverse=True)
    return results
```

**Step 4: Add `get_format_gaps` method**

Powers the Opportunities "Format Gaps" section.

```python
def get_format_gaps(self, channel_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Identify shows with format opportunities.

    Returns:
        Dict with 'no_shorts' (longform shows with 0 Shorts) and
        'underperforming' (shows with below-average and declining views/day)
    """
    shows = self.get_show_summary(channel_id=channel_id)
    all_videos = self.get_all_videos(channel_id=channel_id)

    # Channel average views_per_day
    channel_avg_vpd = 0.0
    if all_videos:
        channel_avg_vpd = sum(v.get("views_per_day", 0) or 0 for v in all_videos) / len(all_videos)

    no_shorts = []
    underperforming = []

    for show in shows:
        name = show.get("show_name")
        count = show.get("video_count", 0)
        shorts = show.get("shorts_count", 0)

        if count >= 5 and shorts == 0:
            no_shorts.append({
                "show_name": name,
                "video_count": count,
                "total_views": show.get("total_views", 0),
                "avg_engagement": round(show.get("avg_engagement", 0), 2),
            })

        if count >= 5:
            # Compute show avg views/day
            show_vpd = sum(
                v.get("views_per_day", 0) or 0
                for v in all_videos
                if v.get("show_name") == name
            ) / max(count, 1)

            if show_vpd < channel_avg_vpd * 0.7:
                underperforming.append({
                    "show_name": name,
                    "video_count": count,
                    "avg_views_per_day": round(show_vpd, 2),
                    "channel_avg_views_per_day": round(channel_avg_vpd, 2),
                    "ratio": round(show_vpd / channel_avg_vpd, 2) if channel_avg_vpd > 0 else 0,
                })

    no_shorts.sort(key=lambda x: x["video_count"], reverse=True)
    underperforming.sort(key=lambda x: x["avg_views_per_day"])

    return {"no_shorts": no_shorts, "underperforming": underperforming}
```

**Step 5: Verify methods exist and import cleanly**

Run: `source venv/bin/activate && python -c "from src.youtube_api.database import AnalyticsDatabase; db = AnalyticsDatabase(); print('get_show_stats_for_scoring' in dir(db)); print('get_videos_with_show_context' in dir(db)); print('get_show_variance_analysis' in dir(db)); print('get_format_gaps' in dir(db))"`
Expected: Four `True` lines

**Step 6: Commit**

```bash
git add src/youtube_api/database.py
git commit -m "feat: add show-relative scoring, variance analysis, and format gap queries"
```

---

## Task 3: Backend — New API Schemas

Add Pydantic response models for the 4 new dashboard tabs.

**Files:**
- Modify: `api/schemas.py`

**Step 1: Add new schemas**

Add after the existing `ShortsFullResponse` class:

```python
# --- Insight Dashboard Schemas ---

class HealthKPIs(BaseModel):
    subscriber_count: int = 0
    avg_daily_views: float = 0.0
    total_watch_time_hours: float = 0.0
    avg_view_duration_seconds: float = 0.0
    views_trend_pct: Optional[float] = None  # period-over-period change
    watch_time_trend_pct: Optional[float] = None
    subscribers_trend_pct: Optional[float] = None

class ContentVelocity(BaseModel):
    new_uploads: int = 0
    avg_views_at_7d: Optional[float] = None
    avg_views_at_30d: Optional[float] = None
    catalog_view_pct: float = 0.0  # % of views from videos older than period
    new_content_view_pct: float = 0.0

class HealthResponse(BaseModel):
    kpis: HealthKPIs
    timeseries: List[TimeseriesPoint]
    velocity: ContentVelocity
    publishing_cadence: List[Dict[str, Any]]  # [{week: str, count: int}]
    watch_time_by_format: List[Dict[str, Any]]  # [{date, shorts_minutes, longform_minutes}]

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
    catalog_risers: List[Dict[str, Any]]  # placeholder until daily_stats populated
    no_shorts: List[FormatGapShow]
    underperforming: List[FormatGapShow]

class RecentResponse(BaseModel):
    videos: List[VideoWithContext]
    summary: Dict[str, Any]  # {count, total_views, avg_vpd, avg_engagement}
```

**Step 2: Verify imports**

Run: `source venv/bin/activate && python -c "from api.schemas import HealthResponse, HitsResponse, OpportunitiesResponse, RecentResponse; print('All schemas OK')"`

**Step 3: Commit**

```bash
git add api/schemas.py
git commit -m "feat: add Pydantic schemas for Health, Hits, Opportunities, Recent tabs"
```

---

## Task 4: Backend — New API Endpoints

Add 4 new endpoints for the dashboard tabs. Keep existing endpoints intact (they may be useful as general API surface).

**Files:**
- Modify: `api/routers/analytics.py`

**Step 1: Add `/analytics/health` endpoint**

```python
@router.get("/analytics/health", response_model=HealthResponse)
def get_health(
    channel_id: Optional[str] = Query(None),
    days: int = Query(90, ge=7, le=365),
    db=Depends(get_db),
):
    """Channel health dashboard data."""
    from datetime import timedelta

    if not channel_id:
        from api.config import load_channels_config
        config = load_channels_config()
        channels = config.get("channels", [])
        if channels:
            channel_id = channels[0]["id"]

    # Timeseries from channel_snapshots
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

    # KPIs from snapshots
    total_views = sum(s.get("daily_views", 0) for s in snapshots)
    total_watch_min = sum(s.get("daily_watch_time_minutes", 0) for s in snapshots)
    num_days = max(len(snapshots), 1)
    avg_daily_views = total_views / num_days

    # Period-over-period comparison
    prior_snapshots = db.get_channel_history(channel_id=channel_id, days=days * 2) if channel_id else []
    prior_only = [s for s in prior_snapshots if s not in snapshots]
    prior_views = sum(s.get("daily_views", 0) for s in prior_only)
    prior_days = max(len(prior_only), 1)
    prior_avg = prior_views / prior_days
    views_trend = ((avg_daily_views - prior_avg) / prior_avg * 100) if prior_avg > 0 else None

    # Subscriber count from most recent snapshot
    sub_count = snapshots[-1].get("subscriber_count", 0) if snapshots else 0

    kpis = HealthKPIs(
        subscriber_count=sub_count,
        avg_daily_views=round(avg_daily_views, 1),
        total_watch_time_hours=round(total_watch_min / 60, 1),
        views_trend_pct=round(views_trend, 1) if views_trend is not None else None,
    )

    # Content velocity
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

    # Publishing cadence (uploads per week)
    from collections import Counter
    week_counts = Counter()
    for v in new_videos:
        pub = v.get("published_at")
        if pub:
            week_str = pub.strftime("%Y-W%W")
            week_counts[week_str] += 1
    cadence = [{"week": w, "count": c} for w, c in sorted(week_counts.items())]

    return HealthResponse(
        kpis=kpis,
        timeseries=timeseries,
        velocity=velocity,
        publishing_cadence=cadence,
        watch_time_by_format=[],  # populated after daily_stats backfill
    )
```

**Step 2: Add `/analytics/hits` endpoint**

```python
@router.get("/analytics/hits", response_model=HitsResponse)
def get_hits(
    channel_id: Optional[str] = Query(None),
    days: int = Query(90, ge=7, le=365),
    db=Depends(get_db),
    client=Depends(get_api_client),
):
    """Hits & insights dashboard data."""
    videos = db.get_videos_with_show_context(channel_id=channel_id)

    # Filter hits (z_score > 2)
    hits = [v for v in videos if v.get("z_score", 0) > 2.0]
    hits.sort(key=lambda v: v.get("z_score", 0), reverse=True)

    # KPIs
    hit_count = len(hits)
    avg_multiplier = (
        sum(h.get("vs_show_multiplier", 0) for h in hits) / max(hit_count, 1)
    )

    # Show hit rates
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

    # Subscriber drivers (from API if available)
    try:
        sub_sources = client.get_subscriber_sources()
    except Exception:
        sub_sources = []

    top_sub = sub_sources[0]["video_id"] if sub_sources else None
    # Resolve video title for top sub driver
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
```

**Step 3: Add `/analytics/opportunities` endpoint**

```python
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
        catalog_risers=[],  # populated after daily_stats backfill
        no_shorts=no_shorts,
        underperforming=underperforming,
    )
```

**Step 4: Add `/analytics/recent` endpoint**

```python
@router.get("/analytics/recent", response_model=RecentResponse)
def get_recent(
    channel_id: Optional[str] = Query(None),
    days: int = Query(30, ge=7, le=365),
    db=Depends(get_db),
):
    """Recent content lookup data."""
    from datetime import timedelta
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
```

**Step 5: Add required imports at top of file**

Add to the imports block:
```python
from api.schemas import (
    ShowSummary, ShortsComparison, VideoSummary,
    OverviewKPIs, TimeseriesPoint,
    ShortsDetailVideo, ShortsOverviewKPIs, ShortsFullResponse,
    HealthResponse, HealthKPIs, ContentVelocity,
    HitsResponse, VideoWithContext, ShowHitRate,
    OpportunitiesResponse, ShowVariance, FormatGapShow,
    RecentResponse,
)
```

**Step 6: Verify endpoints load**

Run: `source venv/bin/activate && python -c "from api.routers.analytics import router; routes = [r.path for r in router.routes]; print(routes); assert '/analytics/health' in routes; assert '/analytics/hits' in routes; assert '/analytics/opportunities' in routes; assert '/analytics/recent' in routes; print('All 4 new endpoints registered')"`

**Step 7: Commit**

```bash
git add api/routers/analytics.py api/schemas.py
git commit -m "feat: add Health, Hits, Opportunities, Recent API endpoints"
```

---

## Task 5: Frontend — API Client & Hooks

Update the TypeScript API client and React Query hooks for the 4 new endpoints.

**Files:**
- Modify: `web/src/api/client.ts`
- Modify: `web/src/hooks/useAnalytics.ts`

**Step 1: Add interfaces to `client.ts`**

Add after the existing `ShortsFullResponse` interface:

```typescript
// --- Insight Dashboard Types ---

export interface HealthKPIs {
  subscriber_count: number;
  avg_daily_views: number;
  total_watch_time_hours: number;
  avg_view_duration_seconds: number;
  views_trend_pct?: number;
  watch_time_trend_pct?: number;
  subscribers_trend_pct?: number;
}

export interface ContentVelocity {
  new_uploads: number;
  avg_views_at_7d?: number;
  avg_views_at_30d?: number;
  catalog_view_pct: number;
  new_content_view_pct: number;
}

export interface HealthData {
  kpis: HealthKPIs;
  timeseries: TimeseriesPoint[];
  velocity: ContentVelocity;
  publishing_cadence: Array<{ week: string; count: number }>;
  watch_time_by_format: Array<Record<string, unknown>>;
}

export interface VideoWithContext {
  video_id: string;
  title: string;
  published_at?: string;
  show_name?: string;
  is_short?: boolean;
  views: number;
  likes: number;
  comments: number;
  engagement_rate?: number;
  views_per_day?: number;
  days_since_publication?: number;
  z_score: number;
  vs_show_multiplier: number;
  show_avg_vpd: number;
  subscribers_gained?: number;
}

export interface ShowHitRate {
  show_name: string;
  video_count: number;
  hit_count: number;
  hit_rate: number;
}

export interface HitsData {
  hit_count: number;
  avg_hit_multiplier: number;
  top_sub_driver?: string;
  best_show_hit_rate?: string;
  top_performers: VideoWithContext[];
  show_hit_rates: ShowHitRate[];
  subscriber_drivers: Array<Record<string, unknown>>;
}

export interface ShowVariance {
  show_name: string;
  video_count: number;
  avg_views_per_day: number;
  coeff_of_variation: number;
  hit_count: number;
  hit_rate: number;
}

export interface FormatGapShow {
  show_name: string;
  video_count: number;
  total_views?: number;
  avg_engagement?: number;
  avg_views_per_day?: number;
  channel_avg_views_per_day?: number;
  ratio?: number;
}

export interface OpportunitiesData {
  inconsistent_shows: ShowVariance[];
  catalog_risers: Array<Record<string, unknown>>;
  no_shorts: FormatGapShow[];
  underperforming: FormatGapShow[];
}

export interface RecentData {
  videos: VideoWithContext[];
  summary: {
    count: number;
    total_views: number;
    avg_views_per_day: number;
    avg_engagement: number;
  };
}
```

**Step 2: Add API methods to the `api` object**

```typescript
  getHealth: (days = 90, channelId?: string) =>
    fetchJson<HealthData>(
      `/analytics/health${qs(`days=${days}`, channelParam(channelId))}`
    ),
  getHits: (days = 90, channelId?: string) =>
    fetchJson<HitsData>(
      `/analytics/hits${qs(`days=${days}`, channelParam(channelId))}`
    ),
  getOpportunities: (channelId?: string) =>
    fetchJson<OpportunitiesData>(
      `/analytics/opportunities${qs(channelParam(channelId))}`
    ),
  getRecent: (days = 30, channelId?: string) =>
    fetchJson<RecentData>(
      `/analytics/recent${qs(`days=${days}`, channelParam(channelId))}`
    ),
```

**Step 3: Add hooks to `useAnalytics.ts`**

```typescript
export const useHealth = (days = 90) => {
  const { channelId } = useChannel();
  return useQuery({
    queryKey: ["health", days, channelId],
    queryFn: () => api.getHealth(days, channelId),
  });
};

export const useHits = (days = 90) => {
  const { channelId } = useChannel();
  return useQuery({
    queryKey: ["hits", days, channelId],
    queryFn: () => api.getHits(days, channelId),
  });
};

export const useOpportunities = () => {
  const { channelId } = useChannel();
  return useQuery({
    queryKey: ["opportunities", channelId],
    queryFn: () => api.getOpportunities(channelId),
  });
};

export const useRecent = (days = 30) => {
  const { channelId } = useChannel();
  return useQuery({
    queryKey: ["recent", days, channelId],
    queryFn: () => api.getRecent(days, channelId),
  });
};
```

**Step 4: Verify TypeScript compiles**

Run: `cd web && ./node_modules/.bin/tsc --noEmit`
Expected: 0 errors (hooks/client won't have consumers yet, but types must compile)

**Step 5: Commit**

```bash
git add web/src/api/client.ts web/src/hooks/useAnalytics.ts
git commit -m "feat: add API client interfaces and hooks for insight dashboard tabs"
```

---

## Task 6: Frontend — Health Page

**Files:**
- Create: `web/src/pages/Health.tsx`

**Step 1: Create the Health page**

Build a page with:
- PeriodSelector at top (30/90/180/365, default 90)
- 4 KpiCards: Subscribers, Avg Daily Views (with trend %), Watch Time (hours), Avg View Duration
- Growth Trends chart: dual-axis line (views left, subscribers right) with 30d moving average
- Content Velocity section: 4 stats (new uploads, avg views at 7d/30d, catalog vs new %)
- Publishing Cadence: bar chart (uploads per week)
- Watch Time by Format: stacked area (placeholder until data available)

Use: `useHealth(days)`, KpiCard (with trend prop), BaseChart (with ariaLabel), PeriodSelector, ChartSummary, EmptyState, rollingAverage from chartHelpers.

Follow patterns from the existing Shorts.tsx page structure.

**Step 2: Verify TypeScript compiles**

Run: `cd web && ./node_modules/.bin/tsc --noEmit`

**Step 3: Commit**

```bash
git add web/src/pages/Health.tsx
git commit -m "feat: add Health dashboard page"
```

---

## Task 7: Frontend — Hits Page

**Files:**
- Create: `web/src/pages/Hits.tsx`

**Step 1: Create the Hits page**

Build a page with:
- PeriodSelector at top
- 4 KpiCards: Hits Found, Avg Hit Multiplier, Top Sub Driver, Best Show Hit Rate
- Top Performers table (DataTable): Title, Show, Views, vs Show (colored multiplier), Eng%, Subs gained. Sorted by z_score desc. Add show filter dropdown and format toggle (All/Shorts/Long) using `useState` + client-side filtering.
- Show Hit Rates: horizontal bar chart (BaseChart) showing hit_rate per show
- Engagement vs Views scatter chart: BaseChart scatter with hits highlighted in a different color
- Subscriber Drivers: horizontal bar chart of top 10 sub-driving videos

Use: `useHits(days)`, KpiCard, BaseChart, DataTable, PeriodSelector, ChartSummary, EmptyState.

**Step 2: Verify TypeScript compiles**

Run: `cd web && ./node_modules/.bin/tsc --noEmit`

**Step 3: Commit**

```bash
git add web/src/pages/Hits.tsx
git commit -m "feat: add Hits & Insights dashboard page"
```

---

## Task 8: Frontend — Opportunities Page

**Files:**
- Create: `web/src/pages/Opportunities.tsx`

**Step 1: Create the Opportunities page**

Build a page with:
- Summary banner: counts of inconsistent shows, catalog risers, format gaps (clickable to scroll)
- Inconsistent Shows table: Show, Videos, Avg V/Day, Hit Rate, CoV (with lightning emoji for high CoV)
- Catalog Risers table: EmptyState placeholder ("Catalog risers will appear after daily stats backfill")
- Format Gaps: two-column layout. Left: shows with no Shorts. Right: underperforming shows.

Use: `useOpportunities()`, DataTable, EmptyState, KpiCard.

**Step 2: Verify TypeScript compiles**

Run: `cd web && ./node_modules/.bin/tsc --noEmit`

**Step 3: Commit**

```bash
git add web/src/pages/Opportunities.tsx
git commit -m "feat: add Opportunities dashboard page"
```

---

## Task 9: Frontend — Recent Content Page

**Files:**
- Create: `web/src/pages/Recent.tsx`

**Step 1: Create the Recent page**

Build a page with:
- PeriodSelector with 7/14/30/90 day presets, default 30
- Search input (text, client-side filtering on title)
- Show dropdown filter (populated from unique show_names in data)
- Format toggle (All/Shorts/Longform)
- 4 summary KpiCards that update with filters: Published count, Total Views, Avg V/Day, Avg Eng%
- Sortable DataTable: Title (full, wrapping), Show, Type (Short/Long badge), Views, V/Day, Eng%, vs Show (colored: green >1.5x, red <0.7x)

Use: `useRecent(days)`, KpiCard, KpiRow, DataTable, PeriodSelector, EmptyState.
Use `useState` for search text, show filter, and format filter. Apply filters client-side before rendering.

**Step 2: Verify TypeScript compiles**

Run: `cd web && ./node_modules/.bin/tsc --noEmit`

**Step 3: Commit**

```bash
git add web/src/pages/Recent.tsx
git commit -m "feat: add Recent Content dashboard page"
```

---

## Task 10: Frontend — Navigation & Routing Update

Replace old 5-tab navigation with new 4-tab structure.

**Files:**
- Modify: `web/src/App.tsx`
- Modify: `web/src/components/Layout.tsx`
- Delete: `web/src/pages/Overview.tsx`
- Delete: `web/src/pages/Shows.tsx`
- Delete: `web/src/pages/Shorts.tsx`
- Delete: `web/src/pages/Archival.tsx`
- Delete: `web/src/pages/Subscribers.tsx`

**Step 1: Update Layout.tsx nav items**

```typescript
const NAV_ITEMS = [
  { to: "/", label: "Health" },
  { to: "/hits", label: "Hits" },
  { to: "/opportunities", label: "Opportunities" },
  { to: "/recent", label: "Recent" },
];
```

**Step 2: Update App.tsx routes**

```typescript
import Health from "./pages/Health";
import Hits from "./pages/Hits";
import Opportunities from "./pages/Opportunities";
import Recent from "./pages/Recent";

// Remove old page imports

// In Routes:
<Route index element={<Health />} />
<Route path="hits" element={<Hits />} />
<Route path="opportunities" element={<Opportunities />} />
<Route path="recent" element={<Recent />} />
```

**Step 3: Delete old page files**

```bash
rm web/src/pages/Overview.tsx web/src/pages/Shows.tsx web/src/pages/Shorts.tsx web/src/pages/Archival.tsx web/src/pages/Subscribers.tsx
```

**Step 4: Verify TypeScript compiles**

Run: `cd web && ./node_modules/.bin/tsc --noEmit`
Expected: 0 errors

**Step 5: Verify Docker build**

Run: `docker compose up --build` (in background)
Verify: API starts on 8001, web on 3001, all 4 new endpoints return 200

**Step 6: Commit**

```bash
git add -A
git commit -m "feat: replace 5-tab layout with 4-tab insight-driven dashboard

Removes Overview, Shows, Shorts, Archival, Subscribers pages.
Adds Health, Hits, Opportunities, Recent pages."
```

---

## Task 11: Integration Verification

Final verification that everything works end-to-end.

**Step 1: Build and start containers**

Run: `docker compose up --build`

**Step 2: Test all API endpoints**

```bash
curl -s "http://localhost:8001/api/v1/analytics/health?days=90" | python3 -m json.tool | head -30
curl -s "http://localhost:8001/api/v1/analytics/hits?days=90" | python3 -m json.tool | head -30
curl -s "http://localhost:8001/api/v1/analytics/opportunities" | python3 -m json.tool | head -30
curl -s "http://localhost:8001/api/v1/analytics/recent?days=30" | python3 -m json.tool | head -30
```

**Step 3: Verify web frontend loads all 4 tabs**

Open http://localhost:3001/ — Health tab should load as default
Navigate to /hits, /opportunities, /recent — each should render

**Step 4: Run backfill (optional, depends on OAuth being set up)**

```bash
source venv/bin/activate
python scripts/backfill_analytics.py --channel --days 7
```

Verify channel_snapshots table has data, then refresh Health page to see trend charts populate.
