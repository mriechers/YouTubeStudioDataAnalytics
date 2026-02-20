"""Data refresh and status endpoints."""

import asyncio
import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from api.dependencies import get_db
from api.schemas import DataStatus, RefreshResult
from api.config import DATABASE_PATH

logger = logging.getLogger(__name__)

router = APIRouter()

_refresh_event: asyncio.Event = asyncio.Event()


@router.get("/data/status", response_model=DataStatus)
def data_status(db=Depends(get_db)):
    """Current data status: video count and database path."""
    videos = db.get_all_videos()
    return DataStatus(
        video_count=len(videos),
        database_path=str(DATABASE_PATH),
    )


@router.post("/data/refresh", response_model=RefreshResult)
def data_refresh():
    """Trigger a full data refresh from YouTube API."""
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

        from youtube_api import YouTubeAPIDataLoader, AnalyticsDatabase
        from api.config import load_channels_config, DATABASE_PATH

        config = load_channels_config()
        channels = config.get("channels", [])
        db = AnalyticsDatabase(db_path=DATABASE_PATH)

        total_videos = 0
        for ch in channels:
            loader = YouTubeAPIDataLoader(channel_id=ch["id"])
            videos_df, _ = loader.load_all_data()

            if videos_df is not None and not videos_df.empty:
                records = []
                for _, row in videos_df.iterrows():
                    records.append({
                        "video_id": row.get("video_id", ""),
                        "title": row.get("Title", ""),
                        "published_at": row.get("Publish Date"),
                        "channel_id": row.get("channel_id", ch["id"]),
                        "channel_title": row.get("channel_title", ch["name"]),
                        "show_name": row.get("Show Name", "Uncategorized"),
                        "duration_minutes": row.get("Duration (minutes)", 0),
                        "is_short": bool(row.get("Is Short", False)),
                        "content_type": row.get("Content Type", "UNSPECIFIED"),
                        "views": int(row.get("Views", 0)),
                        "likes": int(row.get("Likes", 0)),
                        "comments": int(row.get("Comments", 0)),
                        "engagement_rate": float(row.get("Engagement Rate (%)", 0)),
                        "views_per_day": float(row.get("Views per Day", 0)),
                        "days_since_publication": int(row.get("Days Since Publication", 0)),
                    })
                db.upsert_videos_bulk(records)
                total_videos += len(records)

        _refresh_event.set()
        _refresh_event.clear()

        return RefreshResult(
            success=True,
            videos_loaded=total_videos,
            message=f"Loaded {total_videos} videos from {len(channels)} channels",
        )

    except Exception as e:
        logger.error(f"Data refresh failed: {e}")
        return RefreshResult(success=False, message=str(e))


@router.get("/events")
async def event_stream():
    """SSE endpoint for data refresh notifications."""
    async def generate():
        while True:
            await _refresh_event.wait()
            yield {"event": "data-refreshed", "data": datetime.now().isoformat()}

    return EventSourceResponse(generate())
