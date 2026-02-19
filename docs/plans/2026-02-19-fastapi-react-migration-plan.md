# FastAPI + React Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a FastAPI + React stack alongside the existing Streamlit app, porting all 4 PBS panels + overview to React with ECharts.

**Architecture:** FastAPI backend wraps existing `src/youtube_api/` classes (thin routing layer). React frontend consumes JSON endpoints via TanStack Query. Both stacks share the same SQLite database. Docker Compose for deployment.

**Tech Stack:** FastAPI, uvicorn, sse-starlette (backend); React 18, TypeScript, Vite, ECharts, TanStack Query, TanStack Table, Tailwind CSS (frontend); Docker Compose (deployment).

---

## Batch 1: FastAPI Backend Foundation (Tasks 1-4)

### Task 1: FastAPI Project Setup

**Files:**
- Create: `api/__init__.py`
- Create: `api/main.py`
- Create: `api/config.py`
- Create: `api/dependencies.py`
- Create: `api/schemas.py`
- Modify: `requirements.txt`
- Test: `tests/test_api.py`

**Step 1: Add FastAPI dependencies to requirements.txt**

Add these lines to the end of `requirements.txt`:

```
# FastAPI backend
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
sse-starlette>=2.0.0
httpx>=0.27.0  # for testing
```

**Step 2: Install dependencies**

Run: `source venv/bin/activate && pip install fastapi "uvicorn[standard]" sse-starlette httpx`

**Step 3: Create `api/config.py`**

```python
"""FastAPI application configuration."""

from pathlib import Path
from typing import List, Dict, Any

import yaml

PROJECT_ROOT = Path(__file__).parent.parent

# Paths
DATABASE_PATH = PROJECT_ROOT / "data" / "youtube_analytics.db"
CREDENTIALS_PATH = PROJECT_ROOT / "credentials" / "credentials.json"
TOKEN_PATH = PROJECT_ROOT / "credentials" / "token.json"
CHANNELS_CONFIG_PATH = PROJECT_ROOT / "config" / "channels.yaml"


def load_channels_config() -> Dict[str, Any]:
    """Load channel configuration from YAML."""
    if not CHANNELS_CONFIG_PATH.exists():
        return {"channels": [], "defaults": {}, "show_overrides": {}}
    with open(CHANNELS_CONFIG_PATH) as f:
        return yaml.safe_load(f) or {}
```

**Step 4: Create `api/dependencies.py`**

```python
"""FastAPI dependency injection providers."""

import sys
from functools import lru_cache
from pathlib import Path

# Ensure src/ is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from youtube_api import AnalyticsDatabase, YouTubeAPIClient
from .config import DATABASE_PATH, CREDENTIALS_PATH, TOKEN_PATH


@lru_cache
def get_db() -> AnalyticsDatabase:
    """Shared database instance (created once per process)."""
    return AnalyticsDatabase(db_path=DATABASE_PATH)


@lru_cache
def get_api_client() -> YouTubeAPIClient:
    """Shared API client instance (lazy-authenticated)."""
    return YouTubeAPIClient(
        credentials_path=str(CREDENTIALS_PATH),
        token_path=str(TOKEN_PATH),
    )
```

**Step 5: Create `api/schemas.py`**

```python
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
```

**Step 6: Create `api/main.py`**

```python
"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, channels, videos, analytics, data


def create_app() -> FastAPI:
    app = FastAPI(
        title="PBS Wisconsin YouTube Analytics API",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
    app.include_router(channels.router, prefix="/api/v1", tags=["channels"])
    app.include_router(videos.router, prefix="/api/v1", tags=["videos"])
    app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
    app.include_router(data.router, prefix="/api/v1", tags=["data"])

    @app.get("/api/v1/health")
    def health_check():
        return {"status": "ok", "version": "0.1.0"}

    return app


app = create_app()
```

**Step 7: Create `api/__init__.py`**

```python
```

(Empty file.)

**Step 8: Create stub routers so the app can import**

Create these 5 files with minimal content:

`api/routers/__init__.py`:
```python
```

`api/routers/auth.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

`api/routers/channels.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

`api/routers/videos.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

`api/routers/analytics.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

`api/routers/data.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

**Step 9: Write the test**

Create `tests/test_api.py`:

```python
"""Tests for the FastAPI backend."""

import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
```

**Step 10: Run the test**

Run: `venv/bin/python -m pytest tests/test_api.py -v`
Expected: PASS

**Step 11: Verify the server starts**

Run: `cd /Users/mriechers/Developer/pbswi-youtube-analytics && venv/bin/python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &`
Then: `curl http://localhost:8000/api/v1/health`
Expected: `{"status":"ok","version":"0.1.0"}`
Then kill the server.

**Step 12: Commit**

```bash
git add api/ tests/test_api.py requirements.txt
git commit -m "feat(api): scaffold FastAPI backend with health endpoint"
```

---

### Task 2: Auth Router

**Files:**
- Modify: `api/routers/auth.py`
- Test: `tests/test_api.py`

**Step 1: Write the test**

Add to `tests/test_api.py`:

```python
class TestAuthEndpoints:
    def test_auth_status_returns_structure(self):
        """Auth status should return authenticated bool regardless of token state."""
        response = client.get("/api/v1/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert "authenticated" in data
        assert isinstance(data["authenticated"], bool)
```

**Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/test_api.py::TestAuthEndpoints -v`
Expected: FAIL (404 — route doesn't exist yet)

**Step 3: Implement `api/routers/auth.py`**

```python
"""Auth status and refresh endpoints."""

from pathlib import Path

from fastapi import APIRouter

from api.config import TOKEN_PATH
from api.schemas import AuthStatusResponse

router = APIRouter()


@router.get("/auth/status", response_model=AuthStatusResponse)
def auth_status():
    """Check if OAuth token exists and is potentially valid."""
    token_exists = TOKEN_PATH.exists()

    expires_at = None
    if token_exists:
        try:
            import json
            with open(TOKEN_PATH) as f:
                token_data = json.load(f)
            expires_at = token_data.get("expiry")
        except Exception:
            pass

    return AuthStatusResponse(
        authenticated=token_exists,
        expires_at=expires_at,
    )


@router.post("/auth/refresh")
def auth_refresh():
    """Attempt to refresh the OAuth token."""
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        from youtube_api.auth import get_credentials
        get_credentials()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

**Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/test_api.py::TestAuthEndpoints -v`
Expected: PASS

**Step 5: Commit**

```bash
git add api/routers/auth.py tests/test_api.py
git commit -m "feat(api): add auth status and refresh endpoints"
```

---

### Task 3: Channels Router

**Files:**
- Modify: `api/routers/channels.py`
- Test: `tests/test_api.py`

**Step 1: Write the test**

Add to `tests/test_api.py`:

```python
class TestChannelsEndpoints:
    def test_channels_list_returns_array(self):
        response = client.get("/api/v1/channels")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_channels_list_has_expected_fields(self):
        response = client.get("/api/v1/channels")
        data = response.json()
        if len(data) > 0:
            channel = data[0]
            assert "id" in channel
            assert "name" in channel
            assert "type" in channel
```

**Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/test_api.py::TestChannelsEndpoints -v`
Expected: FAIL (404)

**Step 3: Implement `api/routers/channels.py`**

```python
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
    return [
        ChannelConfig(id=ch["id"], name=ch["name"], type=ch.get("type", "main"))
        for ch in config.get("channels", [])
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
```

**Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/test_api.py::TestChannelsEndpoints -v`
Expected: PASS

**Step 5: Commit**

```bash
git add api/routers/channels.py tests/test_api.py
git commit -m "feat(api): add channels list and stats endpoints"
```

---

### Task 4: Videos Router

**Files:**
- Modify: `api/routers/videos.py`
- Test: `tests/test_api.py`

**Step 1: Write the test**

Add to `tests/test_api.py`:

```python
class TestVideosEndpoints:
    def test_videos_list_returns_array(self):
        response = client.get("/api/v1/videos")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_videos_list_supports_channel_filter(self):
        response = client.get("/api/v1/videos?channel_id=test123")
        assert response.status_code == 200

    def test_video_detail_not_found(self):
        response = client.get("/api/v1/videos/nonexistent_id")
        assert response.status_code == 404
```

**Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/test_api.py::TestVideosEndpoints -v`
Expected: FAIL (404)

**Step 3: Implement `api/routers/videos.py`**

```python
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
```

**Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/test_api.py::TestVideosEndpoints -v`
Expected: PASS

**Step 5: Commit**

```bash
git add api/routers/videos.py tests/test_api.py
git commit -m "feat(api): add videos list and detail endpoints"
```

---

## Batch 2: Analytics + Data Routes (Tasks 5-6)

### Task 5: Analytics Router

**Files:**
- Modify: `api/routers/analytics.py`
- Test: `tests/test_api.py`

**Step 1: Write the tests**

Add to `tests/test_api.py`:

```python
class TestAnalyticsEndpoints:
    def test_shows_returns_array(self):
        response = client.get("/api/v1/analytics/shows")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_shorts_returns_comparison(self):
        response = client.get("/api/v1/analytics/shorts")
        assert response.status_code == 200
        data = response.json()
        assert "shorts" in data
        assert "longform" in data

    def test_archival_returns_array(self):
        response = client.get("/api/v1/analytics/archival")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_archival_accepts_months_param(self):
        response = client.get("/api/v1/analytics/archival?months=24")
        assert response.status_code == 200

    def test_overview_returns_kpis(self):
        response = client.get("/api/v1/analytics/overview")
        assert response.status_code == 200
        data = response.json()
        assert "total_videos" in data

    def test_timeseries_returns_array(self):
        response = client.get("/api/v1/analytics/timeseries")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
```

**Step 2: Run tests to verify they fail**

Run: `venv/bin/python -m pytest tests/test_api.py::TestAnalyticsEndpoints -v`
Expected: FAIL (404s)

**Step 3: Implement `api/routers/analytics.py`**

```python
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
        total_subscribers=0,  # Populated when channel snapshot exists
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
        # Use first configured channel
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
```

**Step 4: Run tests to verify they pass**

Run: `venv/bin/python -m pytest tests/test_api.py::TestAnalyticsEndpoints -v`
Expected: PASS

**Step 5: Commit**

```bash
git add api/routers/analytics.py tests/test_api.py
git commit -m "feat(api): add analytics endpoints (overview, shows, shorts, archival, subscribers)"
```

---

### Task 6: Data Management Router (refresh, status, SSE)

**Files:**
- Modify: `api/routers/data.py`
- Test: `tests/test_api.py`

**Step 1: Write the test**

Add to `tests/test_api.py`:

```python
class TestDataEndpoints:
    def test_data_status_returns_structure(self):
        response = client.get("/api/v1/data/status")
        assert response.status_code == 200
        data = response.json()
        assert "video_count" in data
        assert "database_path" in data
```

**Step 2: Run test to verify it fails**

Run: `venv/bin/python -m pytest tests/test_api.py::TestDataEndpoints -v`
Expected: FAIL (404)

**Step 3: Implement `api/routers/data.py`**

```python
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

# Simple event bus for SSE
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

        # Signal SSE listeners
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
```

**Step 4: Run test to verify it passes**

Run: `venv/bin/python -m pytest tests/test_api.py::TestDataEndpoints -v`
Expected: PASS

**Step 5: Run ALL backend tests**

Run: `venv/bin/python -m pytest tests/test_api.py -v`
Expected: ALL PASS

**Step 6: Commit**

```bash
git add api/routers/data.py tests/test_api.py
git commit -m "feat(api): add data refresh, status, and SSE endpoints"
```

---

## Batch 3: React Frontend Foundation (Tasks 7-9)

### Task 7: Vite + React + TypeScript Scaffold

**Files:**
- Create: `web/` directory (via Vite scaffold)
- Create: `web/vite.config.ts` (customize proxy)

**Step 1: Scaffold the React project**

Run:
```bash
cd /Users/mriechers/Developer/pbswi-youtube-analytics
npm create vite@latest web -- --template react-ts
```

**Step 2: Install dependencies**

Run:
```bash
cd web && npm install
npm install echarts echarts-for-react @tanstack/react-query @tanstack/react-table react-router-dom
npm install -D tailwindcss @tailwindcss/vite
```

**Step 3: Configure Vite proxy**

Replace `web/vite.config.ts`:

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
```

**Step 4: Add Tailwind to CSS**

Replace `web/src/index.css`:

```css
@import "tailwindcss";
```

**Step 5: Verify it builds**

Run: `cd web && npm run build`
Expected: Build succeeds

**Step 6: Commit**

```bash
git add web/
git commit -m "feat(web): scaffold React + TypeScript + Vite frontend"
```

---

### Task 8: ECharts Theme + BaseChart Component

**Files:**
- Create: `web/src/theme/echarts.ts`
- Create: `web/src/components/BaseChart.tsx`

**Step 1: Create the Okabe-Ito theme**

Create `web/src/theme/echarts.ts`:

```typescript
import * as echarts from "echarts/core";

// Okabe-Ito colorblind-safe palette
const OKABE_ITO = [
  "#E69F00", // orange
  "#56B4E9", // sky blue
  "#009E73", // bluish green
  "#F0E442", // yellow
  "#0072B2", // blue
  "#D55E00", // vermilion
  "#CC79A7", // reddish purple
  "#999999", // grey
];

export const THEME_NAME = "pbs-dark";

echarts.registerTheme(THEME_NAME, {
  color: OKABE_ITO,
  backgroundColor: "transparent",
  textStyle: { color: "#e5e7eb" },
  title: { textStyle: { color: "#f9fafb" } },
  legend: { textStyle: { color: "#d1d5db" } },
  categoryAxis: {
    axisLine: { lineStyle: { color: "#4b5563" } },
    axisLabel: { color: "#9ca3af" },
    splitLine: { lineStyle: { color: "#374151" } },
  },
  valueAxis: {
    axisLine: { lineStyle: { color: "#4b5563" } },
    axisLabel: { color: "#9ca3af" },
    splitLine: { lineStyle: { color: "#374151" } },
  },
  tooltip: {
    backgroundColor: "#1f2937",
    borderColor: "#374151",
    textStyle: { color: "#f9fafb" },
  },
});
```

**Step 2: Create the BaseChart component**

Create `web/src/components/BaseChart.tsx`:

```tsx
import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "echarts";
import { THEME_NAME } from "../theme/echarts";

interface BaseChartProps {
  option: EChartsOption;
  height?: string;
  className?: string;
}

export default function BaseChart({
  option,
  height = "400px",
  className = "",
}: BaseChartProps) {
  return (
    <ReactECharts
      option={option}
      theme={THEME_NAME}
      style={{ height, width: "100%" }}
      className={className}
      opts={{ renderer: "canvas" }}
    />
  );
}
```

**Step 3: Verify it compiles**

Run: `cd web && npx tsc --noEmit`
Expected: No errors

**Step 4: Commit**

```bash
git add web/src/theme/ web/src/components/BaseChart.tsx
git commit -m "feat(web): add Okabe-Ito ECharts theme and BaseChart component"
```

---

### Task 9: Layout, Routing, API Client, and Hooks

**Files:**
- Create: `web/src/components/Layout.tsx`
- Create: `web/src/components/KpiCard.tsx`
- Create: `web/src/components/KpiRow.tsx`
- Create: `web/src/components/DataTable.tsx`
- Create: `web/src/api/client.ts`
- Create: `web/src/hooks/useAnalytics.ts`
- Create: `web/src/hooks/useSSE.ts`
- Modify: `web/src/App.tsx`
- Modify: `web/src/main.tsx`

**Step 1: Create `web/src/api/client.ts`**

```typescript
const BASE = "/api/v1";

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json();
}

export interface ChannelConfig {
  id: string;
  name: string;
  type: string;
}

export interface VideoSummary {
  video_id: string;
  title: string;
  published_at: string | null;
  show_name: string | null;
  duration_minutes: number | null;
  is_short: boolean;
  content_type: string;
  views: number;
  likes: number;
  comments: number;
  engagement_rate: number;
  views_per_day: number;
  days_since_publication: number;
}

export interface ShowSummary {
  show_name: string | null;
  video_count: number;
  total_views: number;
  total_likes: number;
  avg_engagement: number;
  shorts_count: number;
}

export interface ShortsComparison {
  shorts: Record<string, number>;
  longform: Record<string, number>;
}

export interface OverviewKPIs {
  total_videos: number;
  total_views: number;
  total_subscribers: number;
  shorts_count: number;
  longform_count: number;
  shorts_ratio: number;
  avg_engagement: number;
}

export interface TimeseriesPoint {
  date: string;
  views: number;
  engaged_views: number | null;
  watch_time_minutes: number;
  subscribers_gained: number;
  subscribers_lost: number;
}

export interface DataStatus {
  last_refresh: string | null;
  video_count: number;
  database_path: string;
}

export const api = {
  getChannels: () => fetchJson<ChannelConfig[]>("/channels"),
  getVideos: (channelId?: string) =>
    fetchJson<VideoSummary[]>(
      channelId ? `/videos?channel_id=${channelId}` : "/videos"
    ),
  getVideo: (id: string) => fetchJson<VideoSummary>(`/videos/${id}`),
  getOverview: () => fetchJson<OverviewKPIs>("/analytics/overview"),
  getTimeseries: (days = 90) =>
    fetchJson<TimeseriesPoint[]>(`/analytics/timeseries?days=${days}`),
  getShows: () => fetchJson<ShowSummary[]>("/analytics/shows"),
  getShorts: () => fetchJson<ShortsComparison>("/analytics/shorts"),
  getArchival: (months = 12) =>
    fetchJson<VideoSummary[]>(`/analytics/archival?months=${months}`),
  getSubscribers: () => fetchJson<Record<string, unknown>[]>("/analytics/subscribers"),
  getDataStatus: () => fetchJson<DataStatus>("/data/status"),
  triggerRefresh: () =>
    fetch(`${BASE}/data/refresh`, { method: "POST" }).then((r) => r.json()),
};
```

**Step 2: Create `web/src/hooks/useAnalytics.ts`**

```typescript
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export const useOverview = () =>
  useQuery({ queryKey: ["overview"], queryFn: api.getOverview });

export const useTimeseries = (days = 90) =>
  useQuery({
    queryKey: ["timeseries", days],
    queryFn: () => api.getTimeseries(days),
  });

export const useShows = () =>
  useQuery({ queryKey: ["shows"], queryFn: api.getShows });

export const useShorts = () =>
  useQuery({ queryKey: ["shorts"], queryFn: api.getShorts });

export const useArchival = (months = 12) =>
  useQuery({
    queryKey: ["archival", months],
    queryFn: () => api.getArchival(months),
  });

export const useSubscribers = () =>
  useQuery({ queryKey: ["subscribers"], queryFn: api.getSubscribers });

export const useVideos = (channelId?: string) =>
  useQuery({
    queryKey: ["videos", channelId],
    queryFn: () => api.getVideos(channelId),
  });

export const useDataStatus = () =>
  useQuery({ queryKey: ["dataStatus"], queryFn: api.getDataStatus });
```

**Step 3: Create `web/src/hooks/useSSE.ts`**

```typescript
import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";

export function useSSE() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const source = new EventSource("/api/v1/events");

    source.addEventListener("data-refreshed", () => {
      queryClient.invalidateQueries();
    });

    source.onerror = () => {
      source.close();
      // Reconnect after 5 seconds
      setTimeout(() => {
        // Re-mount will re-establish connection
      }, 5000);
    };

    return () => source.close();
  }, [queryClient]);
}
```

**Step 4: Create `web/src/components/KpiCard.tsx`**

```tsx
interface KpiCardProps {
  label: string;
  value: string | number;
  detail?: string;
}

export default function KpiCard({ label, value, detail }: KpiCardProps) {
  return (
    <div className="rounded-lg bg-gray-800 p-4">
      <p className="text-sm text-gray-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-white">{value}</p>
      {detail && <p className="mt-1 text-xs text-gray-500">{detail}</p>}
    </div>
  );
}
```

**Step 5: Create `web/src/components/KpiRow.tsx`**

```tsx
import type { ReactNode } from "react";

export default function KpiRow({ children }: { children: ReactNode }) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">{children}</div>
  );
}
```

**Step 6: Create `web/src/components/DataTable.tsx`**

```tsx
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table";
import { useState } from "react";

interface DataTableProps<T> {
  data: T[];
  columns: ColumnDef<T, unknown>[];
}

export default function DataTable<T>({ data, columns }: DataTableProps<T>) {
  const [sorting, setSorting] = useState<SortingState>([]);

  const table = useReactTable({
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-700">
      <table className="min-w-full divide-y divide-gray-700">
        <thead className="bg-gray-800">
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id}>
              {hg.headers.map((header) => (
                <th
                  key={header.id}
                  onClick={header.column.getToggleSortingHandler()}
                  className="cursor-pointer px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-400"
                >
                  {flexRender(
                    header.column.columnDef.header,
                    header.getContext()
                  )}
                  {{ asc: " ↑", desc: " ↓" }[
                    header.column.getIsSorted() as string
                  ] ?? ""}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody className="divide-y divide-gray-700 bg-gray-900">
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id} className="hover:bg-gray-800">
              {row.getVisibleCells().map((cell) => (
                <td
                  key={cell.id}
                  className="whitespace-nowrap px-4 py-3 text-sm text-gray-300"
                >
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

**Step 7: Create `web/src/components/Layout.tsx`**

```tsx
import { NavLink, Outlet } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "Overview" },
  { to: "/shows", label: "Shows" },
  { to: "/shorts", label: "Shorts" },
  { to: "/archival", label: "Archival" },
  { to: "/subscribers", label: "Subscribers" },
];

export default function Layout() {
  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* Sidebar */}
      <nav className="flex w-56 flex-col border-r border-gray-800 bg-gray-900 p-4">
        <h1 className="mb-6 text-lg font-bold text-white">PBS Wisconsin</h1>
        <ul className="space-y-1">
          {NAV_ITEMS.map(({ to, label }) => (
            <li key={to}>
              <NavLink
                to={to}
                className={({ isActive }) =>
                  `block rounded-md px-3 py-2 text-sm ${
                    isActive
                      ? "bg-gray-800 text-white font-medium"
                      : "text-gray-400 hover:bg-gray-800 hover:text-white"
                  }`
                }
              >
                {label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto p-6">
        <Outlet />
      </main>
    </div>
  );
}
```

**Step 8: Replace `web/src/App.tsx`**

```tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Layout from "./components/Layout";
import Overview from "./pages/Overview";
import Shows from "./pages/Shows";
import Shorts from "./pages/Shorts";
import Archival from "./pages/Archival";
import Subscribers from "./pages/Subscribers";
import { useSSE } from "./hooks/useSSE";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 5 * 60 * 1000 } },
});

function AppInner() {
  useSSE();
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Overview />} />
          <Route path="shows" element={<Shows />} />
          <Route path="shorts" element={<Shorts />} />
          <Route path="archival" element={<Archival />} />
          <Route path="subscribers" element={<Subscribers />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppInner />
    </QueryClientProvider>
  );
}
```

**Step 9: Update `web/src/main.tsx`**

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./theme/echarts"; // Register theme on startup
import "./index.css";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

**Step 10: Create placeholder pages**

Create `web/src/pages/Overview.tsx`:
```tsx
export default function Overview() {
  return <h2 className="text-xl font-bold">Overview</h2>;
}
```

Create `web/src/pages/Shows.tsx`:
```tsx
export default function Shows() {
  return <h2 className="text-xl font-bold">Shows</h2>;
}
```

Create `web/src/pages/Shorts.tsx`:
```tsx
export default function Shorts() {
  return <h2 className="text-xl font-bold">Shorts</h2>;
}
```

Create `web/src/pages/Archival.tsx`:
```tsx
export default function Archival() {
  return <h2 className="text-xl font-bold">Archival</h2>;
}
```

Create `web/src/pages/Subscribers.tsx`:
```tsx
export default function Subscribers() {
  return <h2 className="text-xl font-bold">Subscribers</h2>;
}
```

**Step 11: Verify it builds**

Run: `cd web && npm run build`
Expected: Build succeeds

**Step 12: Commit**

```bash
git add web/
git commit -m "feat(web): add layout, routing, API client, hooks, and shared components"
```

---

## Batch 4: React Pages (Tasks 10-14)

### Task 10: Overview Page

**Files:**
- Modify: `web/src/pages/Overview.tsx`

**Step 1: Implement the Overview page**

Replace `web/src/pages/Overview.tsx`:

```tsx
import KpiCard from "../components/KpiCard";
import KpiRow from "../components/KpiRow";
import BaseChart from "../components/BaseChart";
import { useOverview, useTimeseries } from "../hooks/useAnalytics";

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
}

export default function Overview() {
  const { data: kpis, isLoading: kpisLoading } = useOverview();
  const { data: timeseries, isLoading: tsLoading } = useTimeseries(90);

  if (kpisLoading) return <p className="text-gray-400">Loading...</p>;

  const chartOption = {
    tooltip: { trigger: "axis" as const },
    xAxis: {
      type: "category" as const,
      data: (timeseries ?? []).map((p) => p.date?.slice(0, 10) ?? ""),
    },
    yAxis: { type: "value" as const },
    series: [
      {
        name: "Views",
        type: "line",
        data: (timeseries ?? []).map((p) => p.views),
        smooth: true,
      },
      {
        name: "Subscribers Gained",
        type: "line",
        data: (timeseries ?? []).map((p) => p.subscribers_gained),
        smooth: true,
      },
    ],
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Overview</h2>

      <KpiRow>
        <KpiCard label="Total Videos" value={formatNumber(kpis?.total_videos ?? 0)} />
        <KpiCard label="Total Views" value={formatNumber(kpis?.total_views ?? 0)} />
        <KpiCard
          label="Shorts"
          value={formatNumber(kpis?.shorts_count ?? 0)}
          detail={`${(kpis?.shorts_ratio ?? 0).toFixed(1)}% of catalog`}
        />
        <KpiCard
          label="Avg Engagement"
          value={`${(kpis?.avg_engagement ?? 0).toFixed(2)}%`}
        />
      </KpiRow>

      <div className="rounded-lg bg-gray-900 p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">
          Daily Views & Subscribers (90 days)
        </h3>
        {tsLoading ? (
          <p className="text-gray-500">Loading chart...</p>
        ) : (
          <BaseChart option={chartOption} height="350px" />
        )}
      </div>
    </div>
  );
}
```

**Step 2: Verify it builds**

Run: `cd web && npm run build`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add web/src/pages/Overview.tsx
git commit -m "feat(web): implement Overview page with KPIs and time series chart"
```

---

### Task 11: Shows Page

**Files:**
- Modify: `web/src/pages/Shows.tsx`

**Step 1: Implement the Shows page**

Replace `web/src/pages/Shows.tsx`:

```tsx
import { createColumnHelper } from "@tanstack/react-table";
import BaseChart from "../components/BaseChart";
import DataTable from "../components/DataTable";
import { useShows } from "../hooks/useAnalytics";
import type { ShowSummary } from "../api/client";

const col = createColumnHelper<ShowSummary>();

const columns = [
  col.accessor("show_name", { header: "Show" }),
  col.accessor("video_count", { header: "Videos" }),
  col.accessor("total_views", {
    header: "Views",
    cell: (info) => info.getValue().toLocaleString(),
  }),
  col.accessor("total_likes", {
    header: "Likes",
    cell: (info) => info.getValue().toLocaleString(),
  }),
  col.accessor("avg_engagement", {
    header: "Avg Engagement %",
    cell: (info) => info.getValue().toFixed(2),
  }),
  col.accessor("shorts_count", { header: "Shorts" }),
];

export default function Shows() {
  const { data: shows, isLoading } = useShows();

  if (isLoading) return <p className="text-gray-400">Loading...</p>;
  if (!shows?.length)
    return <p className="text-gray-400">No show data available.</p>;

  const sorted = [...shows].sort((a, b) => b.total_views - a.total_views);

  const barOption = {
    tooltip: { trigger: "axis" as const },
    grid: { left: "20%", right: "5%" },
    xAxis: { type: "value" as const, name: "Total Views" },
    yAxis: {
      type: "category" as const,
      data: sorted.map((s) => s.show_name ?? "Unknown"),
      inverse: true,
    },
    series: [
      {
        type: "bar",
        data: sorted.map((s) => s.total_views),
      },
    ],
  };

  const treemapOption = {
    tooltip: { formatter: "{b}: {c} videos" },
    series: [
      {
        type: "treemap",
        data: sorted.map((s) => ({
          name: s.show_name ?? "Unknown",
          value: s.video_count,
        })),
      },
    ],
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Show Breakdown</h2>

      <div className="rounded-lg bg-gray-900 p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">
          Views by Show
        </h3>
        <BaseChart
          option={barOption}
          height={`${Math.max(400, sorted.length * 30)}px`}
        />
      </div>

      <div className="rounded-lg bg-gray-900 p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">
          Catalog Size by Show
        </h3>
        <BaseChart option={treemapOption} height="450px" />
      </div>

      <div>
        <h3 className="mb-2 text-sm font-medium text-gray-400">
          All Show Metrics
        </h3>
        <DataTable data={sorted} columns={columns} />
      </div>
    </div>
  );
}
```

**Step 2: Verify it builds**

Run: `cd web && npm run build`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add web/src/pages/Shows.tsx
git commit -m "feat(web): implement Shows page with bar chart, treemap, and table"
```

---

### Task 12: Shorts Page

**Files:**
- Modify: `web/src/pages/Shorts.tsx`

**Step 1: Implement the Shorts page**

Replace `web/src/pages/Shorts.tsx`:

```tsx
import KpiCard from "../components/KpiCard";
import KpiRow from "../components/KpiRow";
import BaseChart from "../components/BaseChart";
import { useShorts } from "../hooks/useAnalytics";

export default function Shorts() {
  const { data, isLoading } = useShorts();

  if (isLoading) return <p className="text-gray-400">Loading...</p>;
  if (!data) return <p className="text-gray-400">No data available.</p>;

  const { shorts, longform } = data;

  if (shorts.count === 0)
    return (
      <p className="text-gray-400">
        No Shorts detected. Videos 3 minutes or shorter are classified as
        Shorts.
      </p>
    );

  const barOption = {
    tooltip: { trigger: "axis" as const },
    legend: { data: ["Avg Views", "Avg Engagement (%)"] },
    xAxis: { type: "category" as const, data: ["Shorts", "Longform"] },
    yAxis: [
      { type: "value" as const, name: "Avg Views", position: "left" as const },
      {
        type: "value" as const,
        name: "Avg Engagement (%)",
        position: "right" as const,
      },
    ],
    series: [
      {
        name: "Avg Views",
        type: "bar",
        yAxisIndex: 0,
        data: [shorts.avg_views ?? 0, longform.avg_views ?? 0],
      },
      {
        name: "Avg Engagement (%)",
        type: "bar",
        yAxisIndex: 1,
        data: [shorts.avg_engagement ?? 0, longform.avg_engagement ?? 0],
      },
    ],
  };

  const pieOption = {
    tooltip: { trigger: "item" as const },
    series: [
      {
        type: "pie",
        radius: ["40%", "70%"],
        data: [
          { name: "Shorts", value: shorts.count ?? 0 },
          { name: "Longform", value: longform.count ?? 0 },
        ],
        label: { formatter: "{b}: {c} ({d}%)" },
      },
    ],
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Shorts vs Longform Analysis</h2>

      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-400">Shorts</h3>
          <KpiRow>
            <KpiCard label="Count" value={(shorts.count ?? 0).toLocaleString()} />
            <KpiCard
              label="Total Views"
              value={(shorts.total_views ?? 0).toLocaleString()}
            />
          </KpiRow>
          <KpiRow>
            <KpiCard
              label="Avg Views"
              value={Math.round(shorts.avg_views ?? 0).toLocaleString()}
            />
            <KpiCard
              label="Avg Engagement"
              value={`${(shorts.avg_engagement ?? 0).toFixed(2)}%`}
            />
          </KpiRow>
        </div>
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-400">Longform</h3>
          <KpiRow>
            <KpiCard label="Count" value={(longform.count ?? 0).toLocaleString()} />
            <KpiCard
              label="Total Views"
              value={(longform.total_views ?? 0).toLocaleString()}
            />
          </KpiRow>
          <KpiRow>
            <KpiCard
              label="Avg Views"
              value={Math.round(longform.avg_views ?? 0).toLocaleString()}
            />
            <KpiCard
              label="Avg Engagement"
              value={`${(longform.avg_engagement ?? 0).toFixed(2)}%`}
            />
          </KpiRow>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="rounded-lg bg-gray-900 p-4">
          <h3 className="mb-2 text-sm font-medium text-gray-400">
            Avg Views & Engagement
          </h3>
          <BaseChart option={barOption} height="350px" />
        </div>
        <div className="rounded-lg bg-gray-900 p-4">
          <h3 className="mb-2 text-sm font-medium text-gray-400">
            Content Mix
          </h3>
          <BaseChart option={pieOption} height="350px" />
        </div>
      </div>
    </div>
  );
}
```

**Step 2: Verify it builds**

Run: `cd web && npm run build`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add web/src/pages/Shorts.tsx
git commit -m "feat(web): implement Shorts page with comparison metrics and charts"
```

---

### Task 13: Archival Page

**Files:**
- Modify: `web/src/pages/Archival.tsx`

**Step 1: Implement the Archival page**

Replace `web/src/pages/Archival.tsx`:

```tsx
import { useState } from "react";
import { createColumnHelper } from "@tanstack/react-table";
import KpiCard from "../components/KpiCard";
import KpiRow from "../components/KpiRow";
import BaseChart from "../components/BaseChart";
import DataTable from "../components/DataTable";
import { useArchival } from "../hooks/useAnalytics";
import type { VideoSummary } from "../api/client";

const col = createColumnHelper<VideoSummary>();

const columns = [
  col.accessor("title", { header: "Title" }),
  col.accessor("show_name", { header: "Show" }),
  col.accessor("views", {
    header: "Views",
    cell: (info) => info.getValue().toLocaleString(),
  }),
  col.accessor("views_per_day", {
    header: "Views/Day",
    cell: (info) => info.getValue().toFixed(1),
  }),
  col.accessor("engagement_rate", {
    header: "Engagement %",
    cell: (info) => info.getValue().toFixed(2),
  }),
  col.accessor("days_since_publication", {
    header: "Age (months)",
    cell: (info) => Math.round(info.getValue() / 30),
  }),
];

export default function Archival() {
  const [months, setMonths] = useState(12);
  const { data: videos, isLoading } = useArchival(months);

  if (isLoading) return <p className="text-gray-400">Loading...</p>;
  if (!videos?.length)
    return (
      <p className="text-gray-400">
        No archival videos found older than {months} months.
      </p>
    );

  const sorted = [...videos].sort(
    (a, b) => b.views_per_day - a.views_per_day
  );
  const top10 = sorted.slice(0, 10);

  const totalViews = videos.reduce((s, v) => s + v.views, 0);
  const avgVpd =
    videos.reduce((s, v) => s + v.views_per_day, 0) / videos.length;

  const scatterOption = {
    tooltip: {
      formatter: (p: { data: number[]; name: string }) =>
        `${p.name}<br/>Age: ${p.data[0]} months<br/>Views/Day: ${p.data[1].toFixed(1)}`,
    },
    xAxis: { type: "value" as const, name: "Age (months)" },
    yAxis: { type: "value" as const, name: "Views per Day" },
    series: [
      {
        type: "scatter",
        data: videos.map((v) => ({
          value: [Math.round(v.days_since_publication / 30), v.views_per_day],
          name: v.title,
        })),
        symbolSize: 8,
      },
    ],
  };

  const barOption = {
    tooltip: { trigger: "axis" as const },
    grid: { left: "30%", right: "5%" },
    xAxis: { type: "value" as const, name: "Views per Day" },
    yAxis: {
      type: "category" as const,
      data: top10.map((v) => v.title.slice(0, 40)),
      inverse: true,
    },
    series: [
      {
        type: "bar",
        data: top10.map((v) => v.views_per_day),
      },
    ],
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Archival Performance</h2>
        <label className="text-sm text-gray-400">
          Threshold:{" "}
          <input
            type="range"
            min={6}
            max={36}
            value={months}
            onChange={(e) => setMonths(Number(e.target.value))}
            className="ml-2 w-32"
          />
          <span className="ml-2 text-white">{months} months</span>
        </label>
      </div>

      <KpiRow>
        <KpiCard label="Archival Videos" value={videos.length.toLocaleString()} />
        <KpiCard label="Total Views" value={totalViews.toLocaleString()} />
        <KpiCard label="Avg Views/Day" value={avgVpd.toFixed(1)} />
      </KpiRow>

      <div className="rounded-lg bg-gray-900 p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">
          Age vs Daily Velocity
        </h3>
        <BaseChart option={scatterOption} height="400px" />
      </div>

      <div className="rounded-lg bg-gray-900 p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">
          Top 10 by Daily Velocity
        </h3>
        <BaseChart option={barOption} height="400px" />
      </div>

      <div>
        <h3 className="mb-2 text-sm font-medium text-gray-400">
          Top 20 Archival Videos
        </h3>
        <DataTable data={sorted.slice(0, 20)} columns={columns} />
      </div>
    </div>
  );
}
```

**Step 2: Verify it builds**

Run: `cd web && npm run build`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add web/src/pages/Archival.tsx
git commit -m "feat(web): implement Archival page with scatter, bar chart, and table"
```

---

### Task 14: Subscribers Page

**Files:**
- Modify: `web/src/pages/Subscribers.tsx`

**Step 1: Implement the Subscribers page**

Replace `web/src/pages/Subscribers.tsx`:

```tsx
import KpiCard from "../components/KpiCard";
import KpiRow from "../components/KpiRow";
import BaseChart from "../components/BaseChart";
import { useSubscribers } from "../hooks/useAnalytics";

export default function Subscribers() {
  const { data: sources, isLoading } = useSubscribers();

  if (isLoading) return <p className="text-gray-400">Loading...</p>;
  if (!sources?.length)
    return (
      <p className="text-gray-400">
        Subscriber attribution data is not available. Requires YouTube Analytics
        API access.
      </p>
    );

  // Calculate totals from subscriber source data
  const totalGained = sources.reduce(
    (s, v) => s + ((v as Record<string, number>).subscribers_gained ?? 0),
    0
  );
  const totalLost = sources.reduce(
    (s, v) => s + ((v as Record<string, number>).subscribers_lost ?? 0),
    0
  );
  const netTotal = totalGained - totalLost;

  const top10 = sources.slice(0, 10) as Array<{
    video_id: string;
    subscribers_gained: number;
    subscribers_lost: number;
    net_subscribers: number;
  }>;

  const barOption = {
    tooltip: { trigger: "axis" as const },
    grid: { left: "5%", right: "5%" },
    xAxis: {
      type: "category" as const,
      data: top10.map((_, i) => `Video ${i + 1}`),
      axisLabel: { rotate: 45 },
    },
    yAxis: { type: "value" as const, name: "Net Subscribers" },
    series: [
      {
        type: "bar",
        data: top10.map((v) => v.net_subscribers),
      },
    ],
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Subscriber Attribution</h2>

      <KpiRow>
        <KpiCard label="Total Gained" value={totalGained.toLocaleString()} />
        <KpiCard label="Total Lost" value={totalLost.toLocaleString()} />
        <KpiCard label="Net Subscribers" value={netTotal.toLocaleString()} />
      </KpiRow>

      <div className="rounded-lg bg-gray-900 p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">
          Top 10 Videos by Subscriber Gain
        </h3>
        <BaseChart option={barOption} height="400px" />
      </div>

      <p className="text-xs text-gray-500">
        Subscriber attribution is based on a 90-day rolling window from the
        YouTube Analytics API.
      </p>
    </div>
  );
}
```

**Step 2: Verify it builds**

Run: `cd web && npm run build`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add web/src/pages/Subscribers.tsx
git commit -m "feat(web): implement Subscribers page with attribution chart"
```

---

## Batch 5: Docker Setup (Task 15)

### Task 15: Docker Compose, Dockerfiles, nginx

**Files:**
- Create: `Dockerfile.api`
- Create: `Dockerfile.web`
- Create: `nginx.conf`
- Create: `docker-compose.yml`

**Step 1: Create `Dockerfile.api`**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY api/ api/

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 2: Create `nginx.conf`**

```nginx
server {
    listen 80;

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Step 3: Create `Dockerfile.web`**

```dockerfile
FROM node:20-alpine AS build

WORKDIR /app
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

**Step 4: Create `docker-compose.yml`**

```yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./credentials:/app/credentials:ro
      - ./config:/app/config:ro
    environment:
      - DATABASE_PATH=/app/data/youtube_analytics.db

  web:
    build:
      context: .
      dockerfile: Dockerfile.web
    ports:
      - "3000:80"
    depends_on:
      - api
```

**Step 5: Verify Docker Compose config**

Run: `docker compose config`
Expected: Valid YAML output, no errors

**Step 6: Commit**

```bash
git add Dockerfile.api Dockerfile.web nginx.conf docker-compose.yml
git commit -m "feat: add Docker Compose setup with API and web containers"
```

---

## Final Verification

After all batches are complete:

1. **Run all Python tests**: `venv/bin/python -m pytest tests/ -v`
2. **Run React build**: `cd web && npm run build`
3. **Start both servers manually**:
   - Terminal 1: `venv/bin/python -m uvicorn api.main:app --port 8000`
   - Terminal 2: `cd web && npm run dev`
   - Open http://localhost:3000 — verify all 5 pages render
4. **Docker Compose** (optional): `docker compose up --build`

When all verifications pass, use **superpowers:finishing-a-development-branch** to complete the work.
