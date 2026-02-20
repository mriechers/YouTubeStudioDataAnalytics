"""Channel configuration and stats endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException

from api.config import load_channels_config
from api.schemas import ChannelConfig, ChannelStats
from api.dependencies import get_api_client

router = APIRouter()


@router.get("/channels", response_model=List[ChannelConfig])
def list_channels():
    """List configured channels from channels.yaml."""
    config = load_channels_config()
    channels = config.get("channels") or []
    return [
        ChannelConfig(id=ch["id"], name=ch["name"], type=ch.get("type", "main"))
        for ch in channels
    ]


@router.get("/channels/{channel_id}/stats", response_model=ChannelStats)
def get_channel_stats(channel_id: str, client=Depends(get_api_client)):
    """Get live channel statistics from YouTube API."""
    try:
        info = client.get_channel_info(channel_id)
        return ChannelStats(
            id=info["id"],
            title=info["title"],
            subscriber_count=info["subscriber_count"],
            video_count=info["video_count"],
            view_count=info["view_count"],
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"YouTube API error: {e}")
