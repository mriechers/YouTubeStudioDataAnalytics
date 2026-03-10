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
sys.path.insert(0, str(Path(__file__).parent.parent))
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
                "avg_view_pct": row.get("avg_view_percentage", 0.0),
                "ctr": row.get("ctr", 0.0),
                "viewed_vs_swiped_pct": row.get("viewed_vs_swiped_pct", 0.0),
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
                    "avg_view_pct": analytics.get("avg_view_percentage", 0.0),
                    "ctr": analytics.get("ctr", 0.0),
                    "viewed_vs_swiped_pct": analytics.get("viewed_vs_swiped_pct", 0.0),
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
            "avg_view_pct": row.get("avg_view_percentage", 0.0),
            "ctr": row.get("ctr", 0.0),
            "viewed_vs_swiped_pct": row.get("viewed_vs_swiped_pct", 0.0),
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
                    "avg_view_pct": analytics.get("avg_view_percentage", 0.0),
                    "ctr": analytics.get("ctr", 0.0),
                    "viewed_vs_swiped_pct": analytics.get("viewed_vs_swiped_pct", 0.0),
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
