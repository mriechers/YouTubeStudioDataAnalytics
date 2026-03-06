# Insight-Driven Dashboard Redesign

## Context

The current dashboard organizes data by type (Overview, Shows, Shorts, Archival, Subscribers). This produces pages that display metrics without answering editorial questions. The redesign reorganizes around three decision-making lenses plus a general-purpose lookup tool.

## Architecture: 4-Tab Layout

Replaces the current 5-tab structure entirely. Reusable components (BaseChart, KpiCard, EmptyState, PeriodSelector, ChartSummary, SparklineCell, chartHelpers) carry forward.

### Tab 1: Channel Health

Morning check-in view. Answers: "Are we growing or plateauing?"

**KPI cards (4):** Subscriber count, daily views (avg), watch time (total hours), avg view duration. Each shows period-over-period trend (current vs prior period of same length).

**Growth Trends chart:** Dual-axis line. Left: daily views. Right: cumulative subscriber count. 30-day moving average overlay.

**Content Velocity section:**
- New uploads count in period
- Avg views at 7 days and at 30 days for videos published in period
- Catalog vs new content view split (% of total views from videos older than the period vs newer)

**Publishing Cadence:** Bar or heatmap showing uploads per week across the period.

**Watch Time Breakdown:** Stacked area chart — Shorts vs Longform watch time contribution over time.

**Data dependency:** Requires `channel_snapshots` and `daily_stats` tables populated via backfill.

### Tab 2: Hits & Insights

Answers: "What's working and what can we learn from it?"

**Hit definition:** A video performing >2 standard deviations above its show's average views/day. Hits are contextual — measured relative to show peers, not raw numbers.

**KPI cards (4):** Hits found (count of >2σ videos), avg hit multiplier, top subscriber driver (video title), best show hit rate (show name + percentage).

**Top Performers table:** Ranked by show-relative z-score. Columns: Title, Show, Views, vs Show (multiplier), Eng%, Subscribers gained. Filterable by show and format (Shorts/Longform). Expandable detail row shows traffic source breakdown when daily_stats data is available.

**Hit Patterns section (2 charts):**
- Show Hit Rates: horizontal bar showing % of each show's videos that qualify as hits
- Engagement vs Views scatter: every video as a dot, hits highlighted. Spots engagement outliers the algorithm may not have pushed.

**Subscriber Drivers:** Horizontal bar of top 10 videos by net subscribers gained in period.

**Data dependency:** Z-scores and hit rates work immediately from lifetime stats. Traffic source detail and subscriber drivers need daily_stats.

### Tab 3: Opportunities

Answers: "What should we change or act on?"

**Summary banner:** Aggregated opportunity counts (N inconsistent shows, N catalog risers, N format gaps). Each clickable to scroll to its section.

**Inconsistent Shows table:** Shows ranked by coefficient of variation (σ/μ of views/day). High variance = some episodes pop, most don't. Columns: Show, Videos, Avg V/Day, Hit Rate, Coefficient of Variation. Editorial signal: topic/title/thumbnail selection matters more than show brand for these shows.

**Catalog Risers table:** Videos older than 6 months where last-30d views/day exceeds prior-30d views/day by >25%. Columns: Title, Show, Age, Recent V/Day, Prior V/Day, Δ%. Editorial action: create fresh content on trending topics, or promote in playlists.

**Format Gaps (2 columns):**
- Shows with no Shorts: longform shows with zero Shorts — highlights clip potential
- Underperforming formats: shows with declining views/day trend and below-channel-average engagement — candidates for format pivots

**Data dependency:** Inconsistent shows and format gaps work immediately. Catalog risers need daily_stats.

### Tab 4: Recent Content

General-purpose lookup tool. Answers: "How is the stuff we just published doing?"

**Search + filters:** Free-text title search (client-side). Show dropdown. Format toggle (All/Shorts/Longform). PeriodSelector with 7/14/30/90 day presets, default 30.

**Summary KPIs (4):** Count published, total views, avg views/day, avg engagement. Update dynamically as filters change.

**Sortable table:** All columns sortable. Title (full, wrapping), Show, Type (Short/Long badge), Views, V/Day, Eng%, vs Show (views/day ÷ show average, colored green >1.5x / red <0.7x).

No charts. Fast, filterable, sortable table. The "vs Show" column contextualizes every video.

**Data dependency:** Works entirely from existing videos table. No backfill needed.

## Prerequisite: Data Backfill

New script `scripts/backfill_analytics.py`:

1. Channel-level daily metrics (18 months) → `channel_snapshots` table
   - Single API call per date range chunk
   - Metrics: views, watch time, subscribers gained/lost, avg view duration
2. Per-video daily metrics → `daily_stats` table
   - Batched by date range to stay within 200 queries/day Analytics API limit
   - Metrics: views, engaged views, watch time, subscribers gained
   - Full backfill of 4,600 videos will take multiple days at quota limits
3. `--daily` mode for ongoing collection (yesterday's data)
   - Cron-able, idempotent (upserts)

## What Gets Removed

- `web/src/pages/Overview.tsx`
- `web/src/pages/Shows.tsx`
- `web/src/pages/Shorts.tsx`
- `web/src/pages/Archival.tsx`
- `web/src/pages/Subscribers.tsx`
- Associated sidebar nav items
- Backend endpoints that only served the old pages (can be cleaned up or left as API surface)

## Data Available Today (no backfill)

| Feature | Data source | Available now? |
|---------|------------|---------------|
| Recent content table | videos table, publish date filter | Yes |
| Hit z-scores & show hit rates | videos table, show averages | Yes |
| Inconsistent shows (CoV) | videos table | Yes |
| Format gaps | videos table, is_short flag | Yes |
| Catalog risers | daily_stats (period comparison) | After backfill |
| Health trend charts | channel_snapshots | After backfill |
| Content velocity (7d/30d views) | daily_stats | After backfill |
| Traffic source breakdowns | Analytics API per-video | After backfill |
| Subscriber drivers | Analytics API subscriber sources | After backfill |

## Future Iteration (out of scope)

- Recent Content tab will evolve based on usage — tracked as open issue
- Slack notifications for new hits or catalog risers
- Content categorization beyond title parsing (manual tags in Airtable)
- Cross-platform data (social, web analytics)
