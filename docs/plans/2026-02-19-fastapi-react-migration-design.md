# FastAPI + React Migration Design

**Date:** 2026-02-19
**Status:** Approved
**Scope:** Phase A4-A7 of the PBS Wisconsin YouTube Analytics roadmap

## Context

PBS Wisconsin's YouTube analytics tool currently runs as a Streamlit dashboard backed by a Python module (`src/youtube_api/`) that wraps the YouTube Data API v3, YouTube Analytics API, and a local SQLite database. The tool has 4 custom PBS panels (archival performance, shorts analysis, subscriber attribution, show breakdown) plus an overview dashboard.

This design migrates to a FastAPI + React stack to support better UX/design, future feature needs (Shorts funnels, collaboration tracking, content calendars), and alignment with the Cardigan v4 architecture. The existing Streamlit app remains operational throughout migration.

## Approach: Full Parallel Stack

Build FastAPI + React alongside the existing Streamlit app. Both stacks share the same SQLite database and `src/youtube_api/` Python module. Streamlit is retired only after React reaches full feature parity.

### Why this approach

- Zero downtime: Streamlit stays usable during development
- Visual validation: React panels can be compared against Streamlit panels
- Clean boundary: new code lives in `api/` and `web/`, existing `src/` is untouched
- Shared data: both stacks read/write the same SQLite database

## Directory Structure

```
pbswi-youtube-analytics/
├── api/                          # NEW: FastAPI backend
│   ├── __init__.py
│   ├── main.py                   # App factory, CORS, lifespan
│   ├── config.py                 # Settings (db path, credentials, channels)
│   ├── dependencies.py           # Shared deps (db session, api client)
│   ├── routers/
│   │   ├── auth.py               # GET /auth/status, POST /auth/refresh
│   │   ├── channels.py           # GET /channels, GET /channels/{id}/stats
│   │   ├── videos.py             # GET /videos, GET /videos/{id}
│   │   ├── analytics.py          # overview, timeseries, shows, shorts, archival, subscribers
│   │   └── data.py               # POST /data/refresh, GET /data/status, GET /events (SSE)
│   └── schemas.py                # Pydantic response models
├── web/                          # NEW: React frontend
│   ├── package.json
│   ├── vite.config.ts            # Proxy /api -> localhost:8000
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx               # React Router + TanStack QueryProvider
│   │   ├── api/
│   │   │   └── client.ts         # Typed fetch wrapper per endpoint
│   │   ├── hooks/
│   │   │   ├── useAnalytics.ts   # TanStack Query hooks per endpoint
│   │   │   └── useSSE.ts         # SSE listener -> query invalidation
│   │   ├── components/
│   │   │   ├── Layout.tsx        # Sidebar nav + main content area
│   │   │   ├── KpiCard.tsx       # Metric + delta + sparkline
│   │   │   ├── KpiRow.tsx        # 3-4 cards in responsive grid
│   │   │   ├── BaseChart.tsx     # ECharts wrapper (dark theme, Okabe-Ito palette)
│   │   │   └── DataTable.tsx     # TanStack Table (sortable, filterable)
│   │   ├── pages/
│   │   │   ├── Overview.tsx      # KPI row + time series
│   │   │   ├── Shows.tsx         # Bar chart + treemap + table
│   │   │   ├── Shorts.tsx        # Side-by-side comparison + donut
│   │   │   ├── Archival.tsx      # Scatter + bar + table
│   │   │   └── Subscribers.tsx   # Donut + metrics
│   │   └── theme/
│   │       └── echarts.ts        # Okabe-Ito palette + dark theme
├── src/                          # EXISTING: untouched
├── docker-compose.yml            # NEW
├── Dockerfile.api                # NEW
└── Dockerfile.web                # NEW
```

## Backend Architecture

### Design principle

The FastAPI layer is thin. Route handlers call existing `src/youtube_api/` classes and return their results as JSON. No business logic lives in `api/`.

### Dependency injection

FastAPI's `Depends()` provides shared instances:

- `AnalyticsDatabase`: single instance per app lifespan, injected into route handlers
- `YouTubeAPIClient`: lazy-initialized, injected when API calls are needed
- `channels.yaml` config: loaded once at startup

### Example router

```python
# api/routers/analytics.py
@router.get("/analytics/shows")
def get_show_breakdown(db: AnalyticsDatabase = Depends(get_db)):
    return db.get_show_summary()
```

## API Endpoints

All routes prefixed with `/api/v1/`.

### Core data

| Method | Route | Source | Returns |
|---|---|---|---|
| GET | `/auth/status` | Token file check | `{authenticated, expires_at}` |
| POST | `/auth/refresh` | `auth.py` refresh | `{success}` |
| GET | `/channels` | `channels.yaml` | Channel list |
| GET | `/channels/{id}/stats` | `client.get_channel_info()` | Subscriber count, video count, views |
| GET | `/videos` | `db.get_all_videos()` | Paginated, filterable by channel/show/content_type |
| GET | `/videos/{id}` | DB query by PK | Single video detail |

### Analytics

| Method | Route | Source | Returns |
|---|---|---|---|
| GET | `/analytics/overview` | Aggregated from DB | KPI summary (views, subs, watch time, Shorts ratio) |
| GET | `/analytics/timeseries` | `db.get_channel_history()` | Daily metrics for line charts |
| GET | `/analytics/shows` | `db.get_show_summary()` | Show breakdown |
| GET | `/analytics/shorts` | `db.get_shorts_vs_longform()` | Shorts vs longform comparison |
| GET | `/analytics/archival` | `db.get_archival_videos()` | Archival content (`?months=12`) |
| GET | `/analytics/subscribers` | `client.get_subscriber_sources()` | Subscriber attribution by video |

### Data management

| Method | Route | Source | Returns |
|---|---|---|---|
| POST | `/data/refresh` | `data_loader.load_all_data()` | Triggers full API sync to SQLite |
| GET | `/data/status` | DB metadata | Last refresh time, video count |
| GET | `/events` | SSE stream | `data-refreshed` events |

## Frontend Architecture

### Page-to-panel mapping

Each React page replaces one Streamlit panel, using the same underlying data:

| React Page | Streamlit Panel | Key Charts |
|---|---|---|
| `Overview.tsx` | Main dashboard tab | KPI cards, time series line chart |
| `Shows.tsx` | `render_show_breakdown_panel` | Horizontal bar, treemap, data table |
| `Shorts.tsx` | `render_shorts_analysis_panel` | Grouped bar (dual axis), donut, per-show table |
| `Archival.tsx` | `render_archival_performance_panel` | Scatter (age vs velocity), horizontal bar, top-20 table |
| `Subscribers.tsx` | `render_subscriber_attribution_panel` | Donut chart, KPI metrics row |

### Data flow

```
User navigates to page
  -> TanStack Query fires GET /api/v1/analytics/*
  -> FastAPI handler calls db.get_*() or client.get_*()
  -> JSON response cached by TanStack Query (stale-while-revalidate)
  -> ECharts renders chart from cached data

SSE /events stream:
  POST /data/refresh completes
  -> SSE pushes "data-refreshed" event
  -> useSSE hook invalidates all TanStack Query caches
  -> Charts re-render with fresh data
```

### Charting

- **Primary**: Apache ECharts via `echarts-for-react` (~150 kB gzipped with tree-shaking)
- **Color palette**: Okabe-Ito (8 colorblind-safe colors)
- **Dark theme**: Registered globally via `echarts.registerTheme()`
- **BaseChart wrapper**: Handles theme, responsive resize, and `getDataURL()` for PNG export

### Key dependencies

```
echarts + echarts-for-react    # Charts
@tanstack/react-query          # Data fetching + cache
@tanstack/react-table          # Sortable, filterable tables
react-router-dom               # Page routing
tailwindcss                    # Styling
```

## Docker Setup

```yaml
services:
  api:
    build:
      dockerfile: Dockerfile.api
    ports: ["8000:8000"]
    volumes:
      - ./data:/app/data
      - ./credentials:/app/credentials:ro
      - ./config:/app/config:ro
    environment:
      - DATABASE_PATH=/app/data/youtube_analytics.db

  web:
    build:
      dockerfile: Dockerfile.web
    ports: ["3000:80"]
    depends_on: [api]
```

- **Dev mode**: Vite dev server on :3000 with proxy to api:8000
- **Prod mode**: nginx serving static files + proxying `/api` to api:8000
- **Volumes**: SQLite database in `./data/`, OAuth credentials read-only from `./credentials/`

## OAuth Strategy

This is a single-user internal tool. OAuth setup remains a CLI step:

1. Run `python -m src.youtube_api.auth` (opens browser for Google consent)
2. Token saved to `credentials/token.json`
3. FastAPI reads the persisted token at startup
4. `GET /auth/status` checks token validity
5. `POST /auth/refresh` uses the stored refresh_token

No web-based OAuth consent flow needed.

## Migration Complete When

1. All 5 React pages render with visual parity to Streamlit panels
2. Data refresh works end-to-end: API trigger -> SQLite -> FastAPI -> React
3. Docker Compose starts cleanly with `docker-compose up`
4. All existing tests pass plus new API endpoint tests

At that point, Streamlit retirement is a separate PR (remove `src/dashboards/`, update `main.py`).

## Estimated Scope

- ~8 files in `api/` (main, config, deps, schemas, 4 routers)
- ~15 files in `web/src/` (5 pages, 5 components, 2 hooks, api client, theme, app, main)
- 2 Dockerfiles + 1 docker-compose.yml + nginx.conf
- ~30 new files total
