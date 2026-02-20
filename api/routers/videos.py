"""Video listing and detail endpoints."""

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import get_db
from api.schemas import VideoSummary

router = APIRouter()


@router.get("/videos", response_model=List[VideoSummary])
def list_videos(
    channel_id: Optional[str] = Query(None),
    db=Depends(get_db),
):
    """List all videos, optionally filtered by channel."""
    return db.get_all_videos(channel_id=channel_id)


@router.get("/videos/{video_id}", response_model=VideoSummary)
def get_video(video_id: str, db=Depends(get_db)):
    """Get a single video by ID."""
    videos = db.get_all_videos()
    for v in videos:
        if v["video_id"] == video_id:
            return v
    raise HTTPException(status_code=404, detail="Video not found")
