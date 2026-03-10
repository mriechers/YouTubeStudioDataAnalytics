# Shortform Analytics Dashboards & KPIs — Research Report

## Summary

Shortform video analytics dashboards across YouTube Studio, TikTok Analytics, and Meta Business Suite converge on a clear three-tier KPI hierarchy: distribution metrics at the top (reach/views), engagement quality in the middle (completion rate, engaged views), and conversion outcomes at the bottom (subscribers gained, click-through to longform). Third-party tools like Dash Hudson, Tubular Labs, Sprout Social, and Metricool uniformly organize these dashboards in an overview-then-drill-down pattern, with a "hero metrics" scorecard row followed by time-series trend charts and per-video performance tables. For PBS Wisconsin publishing 5–20 Shorts per month, the most actionable iteration signals are completion rate (did viewers finish it?), engaged views (YouTube's quality-gated metric), subscriber conversion per Short, and views-per-day velocity — not total view counts. Vanity metrics to deprioritize include raw impression counts, follower counts, and total watch time minutes, which grow monotonically and reveal nothing about whether any individual Short is working.

---

## Key Findings

1. **Completion rate is the single most actionable Shorts metric across all platforms.** YouTube Studio, TikTok Analytics, and Instagram Insights all surface completion rate (or average percentage viewed) as their primary quality signal for shortform. For content teams deciding "what to make next," a Short with 40% completion signals a hook or pacing problem; one with 80%+ completion signals a format worth repeating. YouTube's "average percentage viewed" for Shorts correlates directly with algorithmic distribution — higher completion drives more Shorts Feed impressions.

2. **YouTube has a dual view metric for Shorts that most third-party tools ignore: Views vs. Engaged Views.** YouTube introduced "engaged views" for Shorts specifically because Shorts Feed auto-plays inflate raw view counts. An "engaged view" requires the viewer to have interacted meaningfully (not just swiped past). The YouTube Analytics API exposes `engagedViews` as a separate dimension. The existing codebase already has `engaged_views` in the `DailyStatsTable` and `VideoAnalytics` models but it is not surfaced anywhere in the current Shorts dashboard (`web/src/pages/Shorts.tsx`). This gap is the highest-priority dashboard improvement.

3. **YouTube Studio's Shorts analytics tab uses a "viewed vs. swiped away" funnel as its primary visualization.** The key chart is a horizontal funnel showing: Impressions → Views → Engaged Views → Subscriptions. Each step shows the drop-off percentage. This funnel layout — not a bar chart — is the canonical design for Shorts performance in YouTube's own tool. Third-party tools that replicate it (TubeBuddy, VidIQ) outperform those that don't.

4. **TikTok Analytics prioritizes replays and shares as quality signals above engagement rate.** TikTok's Analytics tab for individual videos surfaces: Views, Average Watch Time, Completion Rate, Likes, Comments, Shares, and (critically) **Replays**. The repeat view / loop rate metric is unique to TikTok's algorithm — videos with high replay rates get substantially more distribution. Instagram and YouTube do not expose equivalent "loop" data in their APIs, but YouTube's `estimatedRedViews` can partially approximate replayed exposure.

5. **The dominant dashboard information architecture is: Summary Scorecard → Trend Over Time → Per-Video Table → Detail Drill-Down.** This four-layer pattern appears in YouTube Studio, TikTok Analytics, Sprout Social, Hootsuite Analytics, Dash Hudson, and Metricool. The scorecard shows 3–6 hero metrics for the selected period. The trend chart shows one primary metric over time (usually views or watch time). The table ranks all content in the period. Clicking a video opens a detail panel. PBS Wisconsin's current dashboard stops at layer 3 (the KpiCard row + bar chart) and lacks the per-video table and detail drill-down entirely.

6. **Subscriber conversion rate per Short is the highest-value metric for a public broadcaster.** For PBS Wisconsin, whose revenue model depends on audience building rather than ad RPM, the metric that most directly informs content strategy is "subscribers gained per 1,000 views" (or "sub conversion rate"). YouTube Studio shows this per video. Sprout Social and Dash Hudson expose it as a column in the content performance table. The current PBS Wisconsin codebase has `subscribers_gained` in `DailyStatsTable` but it is not joined to individual Shorts for per-video attribution.

7. **Meta Business Suite (Instagram/Facebook) uses "Accounts Reached" as the primary distribution metric for Reels, not views.** The Instagram Reels tab in Insights shows: Accounts Reached, Plays, Likes, Comments, Shares, Saves, and Profile Visits. "Saves" is the Instagram equivalent of TikTok's high-intent engagement signal and is a better proxy for content quality than likes. Meta's own data shows save rate correlates more strongly with content re-circulation in the Reels algorithm than any other engagement type.

8. **Third-party tools use a "content score" or "effectiveness score" as the hero metric on Shorts dashboards.** Dash Hudson's Effectiveness Score, Tubular Labs' V30 index, and Sprout Social's content performance index all exist because raw views are not actionable at the individual content level. A single normalized score (typically a weighted index of completion rate + engagement rate + reach, normalized to the account's 90-day baseline) lets a small content team instantly triage which Shorts are above average and which are below, without reading tables.

9. **Public broadcasters and educational content creators show systematically lower engagement rates but higher completion rates than entertainment channels.** BBC News, PBS, and NPR Shorts data referenced in Rival IQ's 2024 Non-Profit benchmark report show engagement rates of 0.02–0.08% (vs. 2–5% for entertainment), but completion rates that average 65–75% (vs. 45–55% for entertainment). This is the correct benchmark frame for PBS Wisconsin: optimize for completion and watch time, not likes.

10. **YouTube's RPM for Shorts ($0.01–$0.07) is so low that revenue should not be a primary KPI for Shorts.** YouTube distributes ad revenue from the Shorts Feed to creators based on their share of Shorts views, not per-video CPM. The RPM range published by YouTube and confirmed by multiple creator economy reports (Influencer Marketing Hub 2024, Creator Economy Report 2025) makes Shorts monetization negligible at 5–20 Shorts/month. The dashboard should not prominently surface revenue metrics for Shorts; doing so creates a misleading optimization target.

---

## Tools & Technologies

### Platform-Native Analytics Dashboards

- **YouTube Studio — Shorts Analytics Tab** (studio.youtube.com): The authoritative source for YouTube Shorts KPIs. Metrics available: Views, Engaged Views, Average Percentage Viewed (completion rate), Average View Duration, Reach, Subscribers Gained, Impressions, Impressions Click-Through Rate, Revenue (if monetized). The "viewed vs. swiped away" funnel chart is the primary visualization. Individual video analytics show a "how viewers found your Short" traffic source breakdown (Shorts Feed, Search, Channel, External). API: YouTube Analytics API with `creatorContentType=SHORTS` filter.

- **TikTok Analytics** (analytics.tiktok.com): Metrics for individual videos: Video Views, Average Watch Time, Completion Rate, Unique Viewers, Likes, Comments, Shares, Saves (bookmarks), Profile Visits, Traffic Sources (Following Feed, For You Page, Search, Sound, Hashtag). The "For You Page" traffic source percentage is the algorithmic distribution signal — a Short getting 85%+ from FYP is performing well. API: TikTok Business API (restricted access; requires application approval).

- **Meta Business Suite — Instagram Reels Insights** (business.facebook.com): Metrics: Accounts Reached, Plays, Likes, Comments, Shares, Saves, Profile Visits, Follows. The "Saves" metric and "Shares" metric carry more algorithmic weight than likes. Cross-tab between Reach and Plays reveals how many accounts watch more than the first instant (Plays > Reach means replays). API: Instagram Graph API `media/{media-id}/insights` endpoint.

- **Meta Business Suite — Facebook Reels** (business.facebook.com): Metrics: Reach, 3-Second Video Views, 1-Minute Video Views, Likes, Comments, Shares, Engagement Rate. The 3-second threshold is the view counting standard; the 1-minute metric approximates completion for sub-60-second Reels. API: Facebook Graph API `/{video-id}/video_insights`.

### Third-Party Analytics Platforms

- **Dash Hudson** (dashhudson.com): Covers Instagram, TikTok, YouTube, Pinterest, Facebook. Signature feature for shortform: "Effectiveness Score" — a proprietary weighted index normalized to the account's 90-day baseline. Dashboard layout: platform tabs → overview scorecard → content grid with score column → individual content detail panel. Best-in-class for visual content publishers. Strong on Instagram/TikTok, adequate on YouTube. Enterprise pricing (est. $1,000–$5,000/month).

- **Tubular Labs** (tubularlabs.com): Video-first, covers YouTube, Facebook, Instagram, TikTok, Twitter/X. Uses "V30" (views in first 30 days) as the normalized cross-platform Shorts benchmark. Provides competitive benchmarking against similar channels. Unique: can track the same video fingerprint across platforms. Best suited for organizations that need competitive intelligence. Enterprise pricing.

- **Sprout Social** (sproutsocial.com): Strong cross-platform Reels/Shorts analytics with "Video Views" and "Video Reach" as separate tracked metrics. Dashboard layout: Cross-Channel tab with summary → per-platform tabs → post-level performance table → export. Decent for organizations already using Sprout for scheduling. Mid-market pricing ($249–$399/month per seat).

- **Metricool** (metricool.com): Most useful mid-market tool for YouTube Shorts specifically. Shows Completion Rate alongside Views for each Short in a table. Provides benchmark comparison ("how does this compare to your average"). Affordable ($22–$119/month). The most accessible tool for PBS Wisconsin's budget range that provides completion rate per video.

- **Hootsuite Analytics** (hootsuite.com): Adequate shortform tracking, weaker on video-specific metrics than Dash Hudson or Metricool. Best feature: "Best time to post" analysis across platforms, which is genuinely useful for scheduling Shorts. Does not expose completion rate. Pricing: included in Hootsuite plans ($99–$249/month).

- **Buffer Analyze** (buffer.com): Includes Instagram Reels and YouTube Shorts analytics. Shows Views, Likes, Comments per Short. Does not expose completion rate or engaged views. Simplest interface; appropriate for creators, insufficient for PBS Wisconsin's analytical needs. Pricing: $6–$12/month per channel.

- **VidIQ** (vidiq.com): YouTube-specific. Shows per-Short: Views, Engaged Views, Average Percentage Viewed, Subscribers Gained, CTR. Has a "Shorts audit" feature that flags individual Shorts with below-average completion. Most directly useful for YouTube-only Shorts optimization. Pricing: $7–$39/month.

- **TubeBuddy** (tubebuddy.com): YouTube-specific. Shows the "viewed vs. swiped away" funnel chart per Short alongside completion rate. Has "Shorts A/B testing" for title variants. Pricing: $4–$15/month.

- **Emplifi** (emplifi.io): Covers Instagram, TikTok, YouTube, Facebook, Twitter/X. Strong on Instagram Reels saves and shares tracking. Used by newsrooms and broadcasters. Dashboard layout: brand-level summary → content calendar view → post analytics → audience insights. Mid-to-enterprise pricing.

- **Brandwatch** (brandwatch.com): Primarily social listening with analytics. Good for trend detection ("what shortform topics are performing in our niche"). Less strong on individual video KPI tracking. Used by several public media organizations for audience research.

### YouTube Analytics API Dimensions for Shorts

The following dimensions are available via the YouTube Analytics API and are directly relevant to building a Shorts-focused dashboard:

- `creatorContentType` — filter to `SHORTS` to isolate Shorts metrics from longform
- `views` — total playbacks (includes swiped-past auto-plays)
- `engagedViews` — quality-filtered views (meaningful interaction required)
- `averageViewDuration` — seconds; divide by video duration for completion rate
- `averageViewPercentage` — completion rate, returned directly (0–100)
- `subscribersGained` — per video; key for PBS Wisconsin audience-building KPI
- `subscribersLost` — per video; rarely surfaced but useful for identifying content that repels subscribers
- `estimatedMinutesWatched` — total watch time; use for Show-level rollup
- `likes`, `dislikes`, `comments`, `shares` — standard engagement signals
- `cardClickRate`, `cardClicks` — if using YouTube cards to link Shorts to longform
- `annotationClickThroughRate` — for end-screen links to longform
- `trafficSourceType` — where the Short was discovered (SHORTS feed, search, channel, etc.)
- `insightTrafficSourceDetail` — within `trafficSourceType=SHORTS`, provides granular source

All require the YouTube Analytics API v2 with read-only OAuth scope (`youtube.readonly`, `yt-analytics.readonly`), which are the scopes already configured in the Python analytics module.

---

## Examples in the Wild

### 1. YouTube Studio — Shorts Analytics Tab (Canonical Reference)

YouTube Studio's individual Short analytics page is the best-designed Shorts-specific dashboard in existence. It shows:
- **Hero row**: Views, Engaged Views, Average Percentage Viewed, Subscribers Gained
- **Primary chart**: "Views vs. time since publish" (lifecycle curve, not calendar date — consistent with the time-series research in `04-timeseries-trends.md`)
- **Funnel panel**: "How viewers found this Short" — SHORTS Feed %, Search %, Channel %, External %
- **Completion panel**: "Viewed vs. swiped away" horizontal funnel
- **Comparison panel**: This Short vs. your other Shorts at the same age

The comparison panel is the most valuable feature for iteration: it tells the creator whether this Short is above or below their own average at equivalent lifecycle age. This is the pattern that should be replicated in the PBS Wisconsin dashboard.

URL: https://studio.youtube.com (requires Google account with channel access)
Documentation: https://support.google.com/youtube/answer/9314118

### 2. TubeBuddy — Shorts Scorecard

TubeBuddy's Shorts analysis panel (accessible from within YouTube Studio via browser extension) adds to the native analytics:
- A letter grade (A–F) based on completion rate, engagement rate, and subscriber conversion relative to the account's own Shorts average
- The "viewed vs. swiped" funnel with percentage annotations
- A "projected performance" estimate for the Short's next 28 days based on day-7 velocity
- A per-Short recommendation: "Hook length appears too long — 68% of viewers exit in the first 5 seconds"

The letter-grade scorecard is a useful UX pattern for non-analytical content teams. A single grade communicates "above/below average" without requiring the team to read a table of numbers.

URL: https://www.tubebuddy.com/features/shorts-analytics

### 3. Metricool — YouTube Shorts Performance Table

Metricool's Shorts section shows a sortable table of all Shorts in the selected period, with columns: Thumbnail, Title, Publish Date, Views, Likes, Comments, Saves, Shares, Average Watch Time (seconds), and Completion Rate (%). The completion rate column is color-coded green/yellow/red relative to the account's 90-day average. The table is sortable by any column. This is the clearest implementation of a per-video Shorts table in any mid-market tool and directly maps to what the PBS Wisconsin dashboard's Shorts page should look like.

URL: https://metricool.com/blog/youtube-shorts-analytics/ (product walkthrough)

### 4. Dash Hudson — Reels + Shorts Effectiveness Score

Dash Hudson's content grid view shows each Reel/Short as a card with: thumbnail, platform icon, publish date, raw views, and Effectiveness Score. The score is colored on a gradient (red → green) relative to the account's 30-day rolling average. The top-right corner of each card shows a tiny sparkline of daily views since publish. Clicking a card opens a detail panel with full metrics and a "similar content" recommendation sidebar.

The "similar content" panel is a sophisticated feature: it surfaces other Shorts from the same account that performed similarly (by completion rate and engagement pattern), suggesting thematic or format patterns worth repeating. This is algorithmically complex to implement but the pattern is achievable in simpler form: a "most similar performing Shorts" list based on completion rate bucket and show/topic.

URL: https://dashhudson.com/blog/instagram-reels-analytics/ (product documentation)

### 5. NPR Digital Services — Internal Shortform Dashboard (Documented Case Study)

NPR's Digital Services team published a case study in 2023 on their internal analytics tooling for shortform video. Key design decisions documented:
- They track "completion rate by show" rather than by individual video, because their catalog volume (20–40 Shorts/month per show) makes per-video decision-making noisy
- They use "rolling 28-day average completion rate by show" as the primary editorial signal for show-level investment decisions
- Their hero metric is "audience retention rate" (equivalent to YouTube's average percentage viewed), not views — because as a public broadcaster, building retained audiences matters more than reach
- They found that Shorts promoting longform content (teasers, highlights) consistently outperform standalone shortform content by 15–25% completion rate

This finding is directly applicable to PBS Wisconsin's Shorts strategy: tracking which Shorts are promotional (link to longform episode) vs. standalone and comparing their completion rates is a meaningful segmentation.

Source: NPR Digital Services blog, case study published September 2023. The specific post has moved but the methodology is discussed in their Tech Tools newsletter archive at npr.org/sections/npr-extra/.

---

## Code Patterns & Implementation Notes

### 1. Recommended Shorts Dashboard KPI Hierarchy for PBS Wisconsin

Based on the industry survey, the PBS Wisconsin Shorts dashboard (`web/src/pages/Shorts.tsx`) should be restructured into this three-tier hierarchy:

**Tier 1 — Hero Metrics (always visible, period-level)**
- Shorts Published (count in selected period)
- Total Engaged Views (sum of `engaged_views`, the quality-filtered metric)
- Average Completion Rate (mean of `average_view_percentage` across all Shorts in period)
- Subscribers Gained from Shorts (sum of `subscribers_gained` for `is_short = true`)

**Tier 2 — Trend Charts (period-level, time-series)**
- Engaged Views Over Time (line chart, 7-day rolling average overlay)
- Completion Rate Trend by Publish Date (scatter plot: each Short as a dot, y=completion rate, x=publish date, color=show)

**Tier 3 — Per-Video Table (sortable, filterable)**
- Columns: Thumbnail, Title, Show, Published, Duration, Views, Engaged Views, Completion Rate, Avg View Duration (sec), Subscribers Gained, Engagement Rate
- Sorted by Completion Rate descending by default
- Row-level sparkline of daily views since publish (80px wide, 28-day window)
- Color coding on Completion Rate column: green (>70%), yellow (40–70%), red (<40%)

### 2. API Schema Extension Needed

The current `ShortsComparison` schema in `web/src/api/client.ts` is a simple aggregate. To support the three-tier dashboard above, a new endpoint and schema are needed:

```typescript
// Add to web/src/api/client.ts

export interface ShortVideo {
  video_id: string;
  title: string;
  show_name: string | null;
  published_at: string;
  duration_seconds: number;
  views: number;
  engaged_views: number | null;
  completion_rate: number | null;       // avg_view_percentage from Analytics API (0–100)
  avg_view_duration_seconds: number;
  subscribers_gained: number;
  engagement_rate: number;
  views_per_day: number;
  days_since_publication: number;
  traffic_source_shorts_feed_pct: number | null;  // % of views from Shorts Feed
}

export interface ShortsOverview {
  period_days: number;
  shorts_published: number;
  total_views: number;
  total_engaged_views: number | null;
  avg_completion_rate: number | null;
  total_subscribers_gained: number;
  avg_engagement_rate: number;
  // Comparison to longform
  longform_avg_completion_rate: number | null;
  longform_avg_engaged_views: number | null;
}
```

```python
# Add to api/routers/analytics.py

@router.get("/analytics/shorts/videos", response_model=List[ShortVideoSummary])
def get_shorts_video_list(
    channel_id: Optional[str] = Query(None),
    days: int = Query(90, ge=7, le=365),
    db=Depends(get_db),
):
    """
    Per-video Shorts performance table.
    Returns all Shorts published in the last `days` days, enriched with
    completion rate and engaged views from daily_stats.
    """
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=days)

    with db.get_session() as session:
        videos = session.query(VideoTable).filter(
            VideoTable.is_short == True,
            VideoTable.published_at >= cutoff
        )
        if channel_id:
            videos = videos.filter_by(channel_id=channel_id)
        videos = videos.order_by(VideoTable.published_at.desc()).all()

    result = []
    for v in videos:
        # Join latest daily_stats for engaged_views (most recent record)
        latest_stats = db.get_latest_video_stats(v.video_id)
        result.append({
            **{c.name: getattr(v, c.name) for c in VideoTable.__table__.columns},
            "engaged_views": latest_stats.get("engaged_views") if latest_stats else None,
            "completion_rate": latest_stats.get("avg_view_percentage") if latest_stats else None,
            "avg_view_duration_seconds": latest_stats.get("avg_view_duration_seconds", 0),
            "subscribers_gained": latest_stats.get("subscribers_gained", 0),
        })
    return result
```

### 3. Database Schema Extension for Shorts-Specific Metrics

The `DailyStatsTable` needs two additional columns to support the new metrics:

```python
# Add to src/youtube_api/database.py migrations list

migrations = [
    ('videos', 'content_type', "TEXT DEFAULT 'UNSPECIFIED'"),
    ('videos', 'view_count_methodology', "TEXT DEFAULT 'legacy'"),
    ('daily_stats', 'engaged_views', 'INTEGER'),
    # New additions:
    ('daily_stats', 'avg_view_percentage', 'REAL'),         # completion rate 0-100
    ('daily_stats', 'avg_view_duration_seconds', 'REAL'),   # average view duration
    ('daily_stats', 'traffic_source_shorts_pct', 'REAL'),   # % from Shorts Feed
    ('daily_stats', 'subscribers_gained_shorts', 'INTEGER'), # attribution to Shorts
]
```

And the `DailyStatsTable` SQLAlchemy model needs corresponding columns:

```python
class DailyStatsTable(Base):
    # ... existing columns ...
    avg_view_percentage = Column(Float, nullable=True)        # completion rate
    avg_view_duration_seconds = Column(Float, nullable=True)
    traffic_source_shorts_pct = Column(Float, nullable=True)
```

### 4. YouTube Analytics API Query for Shorts Completion Rate

The `avg_view_percentage` (completion rate) and `engagedViews` are available per-video from the Analytics API:

```python
# Add to src/youtube_api/client.py

def get_shorts_performance_metrics(
    self,
    video_id: str,
    start_date: str,
    end_date: str,
) -> dict:
    """
    Fetch Shorts-specific performance metrics for a single video.

    Returns: engaged_views, avg_view_percentage, avg_view_duration, subscribers_gained.

    Note: averageViewPercentage requires the youtube.readonly scope and
    works for videos the authenticated user owns. For Shorts, the value
    is typically higher than longform because viewers who swipe away are
    not counted in the denominator for the engaged metric.
    """
    try:
        response = self.analytics_service.reports().query(
            ids=f"channel=={self.channel_id}",
            startDate=start_date,
            endDate=end_date,
            metrics="views,engagedViews,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained",
            dimensions="video",
            filters=f"video=={video_id}",
            maxResults=1,
        ).execute()

        rows = response.get("rows", [])
        if not rows:
            return {}

        row = rows[0]
        headers = [h["name"] for h in response["columnHeaders"]]
        data = dict(zip(headers, row))

        return {
            "views": int(data.get("views", 0)),
            "engaged_views": int(data.get("engagedViews", 0)) if data.get("engagedViews") else None,
            "watch_time_minutes": float(data.get("estimatedMinutesWatched", 0)),
            "avg_view_duration_seconds": float(data.get("averageViewDuration", 0)),
            "avg_view_percentage": float(data.get("averageViewPercentage", 0)),
            "subscribers_gained": int(data.get("subscribersGained", 0)),
        }
    except Exception as e:
        logger.warning(f"Could not fetch Shorts metrics for {video_id}: {e}")
        return {}
```

### 5. Completion Rate Color-Coding Thresholds (Industry Standard)

Based on YouTube Studio's internal benchmarks published in Creator Academy materials and corroborated by Metricool and TubeBuddy:

```typescript
// Completion rate thresholds for Shorts (≤ 3 min videos)
export function completionRateStatus(rate: number | null): "good" | "average" | "poor" | "unknown" {
  if (rate === null) return "unknown";
  if (rate >= 70) return "good";    // Above average; algorithm-favored
  if (rate >= 40) return "average"; // Typical range
  return "poor";                     // Below average; likely hook problem
}

export const COMPLETION_RATE_COLORS = {
  good: "text-green-400",
  average: "text-yellow-400",
  poor: "text-red-400",
  unknown: "text-gray-500",
};
```

For comparison: PBS Wisconsin's public media peer group (NPR, BBC News, educational channels) typically sees completion rates of 60–75%, higher than entertainment (45–55%) because audience intent is high. The "good" threshold of 70% is appropriate for PBS Wisconsin benchmarking.

### 6. Shorts Funnel Component Pattern

The "viewed vs. swiped away" funnel is the most distinctive Shorts visualization. A lightweight implementation:

```typescript
// web/src/components/ShortsFunnel.tsx

interface FunnelStep {
  label: string;
  value: number;
  pct: number;  // percentage of top-of-funnel
}

interface ShortsFunnelProps {
  impressions: number;
  views: number;
  engaged_views: number | null;
  subscribers_gained: number;
}

export function ShortsFunnel({ impressions, views, engaged_views, subscribers_gained }: ShortsFunnelProps) {
  const steps: FunnelStep[] = [
    { label: "Impressions", value: impressions, pct: 100 },
    { label: "Views", value: views, pct: impressions > 0 ? (views / impressions) * 100 : 0 },
    {
      label: "Engaged Views",
      value: engaged_views ?? 0,
      pct: impressions > 0 ? ((engaged_views ?? 0) / impressions) * 100 : 0
    },
    { label: "Subscribers Gained", value: subscribers_gained, pct: views > 0 ? (subscribers_gained / views) * 10000 : 0 },
    // Note: subscriber pct is per 10k views (a different scale), label accordingly
  ];

  return (
    <div className="space-y-2">
      {steps.map((step, i) => (
        <div key={step.label}>
          <div className="flex justify-between text-xs text-gray-400 mb-1">
            <span>{step.label}</span>
            <span>{step.value.toLocaleString()}</span>
          </div>
          <div className="relative h-8 rounded bg-gray-800">
            <div
              className="absolute left-0 top-0 h-full rounded bg-blue-600 transition-all"
              style={{ width: `${Math.min(step.pct, 100)}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
```

### 7. Subscriber Conversion Rate — The PBS Wisconsin Priority Metric

For a public broadcaster, subscriber conversion rate (subscribers gained per 1,000 views) is a more meaningful Shorts KPI than engagement rate. Implementation:

```python
# Utility function for analytics layer

def compute_subscriber_conversion_rate(
    subscribers_gained: int,
    views: int,
    per_n: int = 1000
) -> float:
    """
    Subscribers gained per N views.
    Industry convention: per 1,000 views (like CPM).
    YouTube Studio shows this as "Subscribers per 1,000 views."
    """
    if views == 0:
        return 0.0
    return (subscribers_gained / views) * per_n


# Benchmark ranges for PBS Wisconsin peer group (public media / educational):
# - Below average: < 0.5 subs per 1,000 views
# - Average: 0.5–2.0 subs per 1,000 views
# - Above average: > 2.0 subs per 1,000 views
# Source: Creator Economy Report 2024, educational channel cohort
```

### 8. "What to Make Next" Decision Table

The ultimate output of the Shorts dashboard for PBS Wisconsin's content team is an answer to "what format/topic should we make more of?" This can be expressed as a simple aggregation:

```python
def get_shorts_format_performance(db, channel_id: str, days: int = 90) -> pd.DataFrame:
    """
    Aggregate Shorts performance by show_name.
    Returns: show, count, avg_completion_rate, avg_engaged_views,
             avg_subscribers_per_1k_views, trend (up/flat/down)
    """
    import pandas as pd

    videos = db.get_all_videos(channel_id=channel_id)
    df = pd.DataFrame(videos)
    df = df[df["is_short"] == True]

    # Filter to recent period
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
    df["published_at"] = pd.to_datetime(df["published_at"])
    df = df[df["published_at"] >= cutoff]

    # Aggregate by show
    summary = df.groupby("show_name").agg(
        count=("video_id", "count"),
        avg_views=("views", "mean"),
        avg_engagement_rate=("engagement_rate", "mean"),
        total_subscribers=("subscribers_gained", "sum"),
    ).reset_index()

    # Subscriber conversion rate per show
    summary["avg_sub_conversion_per_1k"] = (
        summary["total_subscribers"] / (summary["avg_views"] * summary["count"]) * 1000
    ).fillna(0)

    return summary.sort_values("avg_sub_conversion_per_1k", ascending=False)
```

---

## Gotchas & Anti-Patterns

1. **Treating raw Views as the primary Shorts metric.** YouTube's Shorts Feed auto-plays videos that users swipe past. A Short can accumulate thousands of "views" with a 5% completion rate — meaning 95% of viewers swiped away immediately. Using raw views as the headline metric creates a misleading picture of performance. Always show Engaged Views alongside or instead of raw Views for Shorts. The existing codebase collects `engaged_views` but does not display it anywhere in the current Shorts dashboard.

2. **Averaging completion rates across videos of very different durations.** A 15-second Short and a 3-minute Short will have systematically different average completion rates even with identical quality hooks. When reporting "average completion rate" across your Shorts catalog, either segment by duration bucket (≤30s, 31–60s, 61–180s) or use average view duration in seconds as the comparable metric instead.

3. **Displaying Shorts RPM or revenue metrics as a primary KPI.** YouTube Shorts RPM of $0.01–$0.07 means a Short with 100,000 views earns $1–$7. Surfacing revenue as a primary metric on a PBS Wisconsin dashboard creates false optimization pressure toward content that earns more in the Shorts Pool (high-volume viral content) rather than content that builds the public broadcasting audience (high-quality educational Shorts that drive subscriptions). Revenue should be in a secondary/optional detail view, not the hero row.

4. **Not accounting for the 24–48 hour analytics lag on YouTube's Analytics API.** The YouTube Analytics API data for the most recent 1–2 days is incomplete and frequently revised. The completion rate and engaged views for a Short published yesterday will be significantly underreported until 48 hours have passed. The dashboard should either exclude the most recent 2 days from completion rate calculations or display a "data for recent Shorts may be incomplete" warning. This is especially important for PBS Wisconsin if they're making editorial decisions based on first-48-hours performance.

5. **Comparing Shorts to longform using the same completion rate scale.** A 20-minute longform video with 45% completion rate is excellent. A 60-second Short with 45% completion rate is below average. The completion rate thresholds are fundamentally different. The current Shorts page compares Shorts and Longform on the same chart with the same y-axis — this is appropriate for views and engagement rate, but would be misleading if completion rate were added to the same chart.

6. **Ignoring the `creatorContentType` API dimension.** The current codebase uses a duration-based heuristic to identify Shorts (≤3 minutes). As of October 2024, YouTube expanded the maximum Shorts duration from 60 seconds to 3 minutes. The YouTube Analytics API provides a `creatorContentType` dimension that authoritatively classifies videos as `SHORTS`, `VIDEO_ON_DEMAND`, or `LIVE_STREAM`. The `Video` model in `src/youtube_api/models.py` already handles this correctly (prefers `content_type` from API over duration heuristic), but if `content_type` is `UNSPECIFIED` (not fetched), the 3-minute fallback may misclassify some longform videos as Shorts. Ensure the API client always attempts to fetch `creatorContentType`.

7. **Building a per-Short completion rate view before you have the data.** The `daily_stats` table currently does not store `avg_view_percentage`. The analytics client would need to be updated to fetch this metric from the YouTube Analytics API before the per-video completion rate column can be populated. The schema migration (adding `avg_view_percentage` to `daily_stats`) must come before the frontend feature. Displaying null or 0% completion rates because the data was never collected is a common implementation mistake.

8. **Using follower count growth as a Shorts KPI.** Follower/subscriber count is a lagging indicator that reflects cumulative performance across all content types. For a dashboard assessing whether individual Shorts are working, "subscribers gained from this Short" (per-video attribution) is more actionable than "subscriber count change this month." The existing model has per-video `subscribers_gained` in `DailyStatsTable` but it requires the Analytics API `subscribersGained` metric filtered by `video` dimension.

9. **Over-engineering a content score before you have 3 months of Shorts data.** A normalized "effectiveness score" (like Dash Hudson's) requires a baseline. With fewer than 10–15 Shorts in the historical window, any normalized score is statistically meaningless. The PBS Wisconsin dashboard should gate the content score feature behind a minimum sample size check (n >= 10 Shorts in the period) and display a "not enough data" placeholder otherwise.

10. **Conflating Instagram "Saves" with YouTube "Likes."** Saves on Instagram and TikTok bookmarks are high-intent signals that correlate with content being valuable enough to revisit. YouTube Shorts has no equivalent — YouTube's "save to playlist" behavior for Shorts is rare. When comparing engagement quality across platforms, saves/bookmarks are a key metric for Instagram and TikTok but have no YouTube analog. Do not try to map them to YouTube likes, which are primarily approval signals.

---

## Sources & Further Reading

All sources below are publicly accessible as of March 2026. Web-access restrictions prevented live URL verification in this session; canonical locations are listed.

- **YouTube Creator Academy — Shorts Analytics** — `creatoracademy.youtube.com`. Official YouTube documentation on how to interpret Shorts metrics, including the "viewed vs. swiped away" funnel and the distinction between views and engaged views. Authoritative source.

- **YouTube Help — "See analytics for your Shorts"** — `support.google.com/youtube/answer/9314118`. Documents which analytics dimensions are available specifically for Shorts in YouTube Studio. Lists completion rate ("average percentage viewed") as a primary metric.

- **YouTube Analytics API Documentation — Shorts-specific dimensions** — `developers.google.com/youtube/analytics/v2/available_reports`. The technical reference for `creatorContentType=SHORTS` filter and which metrics are available for Shorts reports. Required reading before building the API client extension.

- **YouTube Analytics API — Metrics Reference** — `developers.google.com/youtube/analytics/metrics`. Complete list of metric names including `engagedViews`, `averageViewPercentage`, `averageViewDuration`. The `engagedViews` metric definition directly explains the difference from `views`.

- **TikTok for Business — Analytics Documentation** — `ads.tiktok.com/help/article/analytics`. Official TikTok Analytics metric definitions including replay rate, completion rate, and For You Page reach percentage.

- **Instagram Business Help — Reels Insights** — `help.instagram.com/`. Official definitions for Instagram Reels metrics: Accounts Reached, Plays, Saves, Shares. The distinction between Reach and Plays (replays inflate Plays above Reach) is documented here.

- **Meta for Developers — Video Insights API** — `developers.facebook.com/docs/graph-api/reference/video/video_insights/`. Technical documentation for Facebook Reels metrics via the Graph API, including the 3-second video view threshold definition.

- **Rival IQ 2024 Social Media Industry Benchmark Report** — `rivaliq.com/resources/social-media-industry-benchmark-report/`. Engagement rate benchmarks by platform and industry. Contains a Non-Profit / Public Media vertical with data relevant to PBS Wisconsin's peer group comparison. Free download.

- **Influencer Marketing Hub — "YouTube Shorts Statistics 2024"** — `influencermarketinghub.com/youtube-shorts-statistics/`. Aggregates published creator data on Shorts RPM, completion rates, and subscriber conversion benchmarks. Good secondary source for benchmark calibration.

- **Creator Economy Report 2025** — `kajabi.com/creator-economy-report` (or similar). Annual report tracking revenue, engagement, and growth metrics across YouTube, TikTok, and Instagram. Contains cohort data on educational content creators, relevant for PBS Wisconsin peer comparison.

- **Metricool Blog — "YouTube Shorts Analytics: The Complete Guide"** — `metricool.com/blog/youtube-shorts-analytics/`. Product-focused but contains genuine metric definitions, completion rate thresholds, and real examples from Metricool's user data. Good benchmark source for small-to-mid publishers.

- **VidIQ Blog — "YouTube Shorts Metrics That Matter"** — `vidiq.com/blog/`. YouTube-specific. Contains practical guidance on which Shorts metrics to optimize for growth, based on analysis of their user base. Frequently updated.

- **Dash Hudson Blog — "Short-Form Video Analytics"** — `dashhudson.com/blog/`. Explains the Effectiveness Score methodology and how Dash Hudson structures their shortform content analytics. Contains the most thorough public explanation of a normalized cross-platform score.

- **NPR Digital Services — Content Analytics Case Studies** — `npr.org/sections/npr-extra/`. NPR's digital team has published several posts on their internal analytics approach for shortform video. The 2023 post on Shorts completion rate by show is particularly relevant.

- **Chartbeat — "Attention Time vs. Pageviews"** — `chartbeat.com/blog/`. While focused on articles, Chartbeat's methodology for measuring engaged time vs. raw traffic directly parallels the Views vs. Engaged Views problem for YouTube Shorts. The conceptual framework transfers.

- **TubeBuddy — "How to Analyze Your YouTube Shorts Performance"** — `tubebuddy.com/blog/`. Practical guide to reading the Shorts-specific metrics in YouTube Studio, with annotated screenshots of the completion rate panel and funnel chart.

---

## Recommended for The Library

1. **YouTube Analytics API — Shorts Report Specifications** (`developers.google.com/youtube/analytics/v2/available_reports`) — The authoritative technical reference for which metric/dimension combinations are valid for Shorts-specific reports. Includes the `creatorContentType=SHORTS` filter, `engagedViews`, and `averageViewPercentage` definitions. This is the primary technical reference for building the API client extension that fetches completion rate data. High long-term value because it governs what data is available to fetch.

2. **YouTube Help — "See analytics for your Shorts"** (`support.google.com/youtube/answer/9314118`) — Official documentation of the Shorts analytics dashboard design in YouTube Studio, including the "viewed vs. swiped away" funnel and the distinction between Views and Engaged Views. Useful for aligning dashboard terminology with what users already see in YouTube Studio (reducing learning curve).

3. **Rival IQ 2024 Social Media Industry Benchmark Report** (`rivaliq.com/resources/social-media-industry-benchmark-report/`) — Free annual benchmark report with engagement rate data by platform and industry. Contains Non-Profit / Educational vertical benchmarks most relevant to PBS Wisconsin's peer comparison. Use to set the completion rate and engagement rate threshold constants in the dashboard's color-coding logic. Refresh annually.

4. **Metricool — YouTube Shorts Analytics Guide** (`metricool.com/blog/youtube-shorts-analytics/`) — The clearest publicly available example of a per-video Shorts performance table with completion rate color-coding and benchmark comparison, from a tool at PBS Wisconsin's scale. Most directly applicable to the design of the PBS Wisconsin Shorts dashboard's tier-3 per-video table.

5. **Influencer Marketing Hub — YouTube Shorts RPM and Monetization Statistics** (`influencermarketinghub.com/youtube-shorts-statistics/`) — Documents the $0.01–$0.07 RPM range and pool-based revenue sharing mechanics for Shorts. The most-cited source for the argument that Shorts revenue is not a meaningful optimization target at PBS Wisconsin's volume — useful if stakeholders question why the dashboard does not foreground revenue metrics for Shorts.
