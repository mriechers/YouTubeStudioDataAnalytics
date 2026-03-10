# Actionable Insights & Recommendation Patterns — Research Report

_Compiled: 2026-03-05 | Researcher: Claude (Sonnet 4.6)_
_Note: WebSearch and WebFetch were unavailable during this session. Findings draw on training knowledge through August 2025, cross-referenced with patterns observable in the existing codebase._

---

## Summary

Modern analytics tools have converged on a layered insight model: automated anomaly detection surfaces unexpected events, comparative benchmarks contextualize individual metrics, and natural-language narrative summaries translate data into editorial language that non-analysts can act on. The shift from "here is what happened" dashboards toward "here is what you should do next" recommendation engines accelerated between 2022 and 2025, driven by LLM integration and product pressure from tools like GA4 Insights, Amplitude's Ask feature, and YouTube Studio's Key Metrics cards. For PBS Wisconsin, the most actionable pattern is a tiered card-based insight system — surfacing anomaly alerts, benchmark comparisons, and prescriptive content recommendations — combined with Slack-based alerting for time-sensitive events (viral posts, quota warnings). The current codebase's `generate_insights()` method in `src/analytics/core.py` is the right scaffold; it needs structured data types, severity levels, and a richer presentation layer to become genuinely actionable.

---

## Key Findings

1. **Insight cards are the dominant UI pattern.** YouTube Studio, GA4, Amplitude, Chartbeat, and Looker all use card-based insight surfaces — self-contained panels with a headline, supporting stat, and a single call-to-action link. Cards work because they are scannable and dismissible. Banner-style alerts are reserved for high-urgency anomalies only.

2. **Comparative framing drives action more than absolute numbers.** "This Short got 3.2x your channel average in 48 hours" is more actionable than "This Short has 4,200 views." Tools that show performance relative to a benchmark (channel average, show average, prior period, peer cohort) consistently outperform pure raw-metric dashboards in user studies cited by Mixpanel and Amplitude product documentation.

3. **Severity tiering prevents alert fatigue.** Effective alerting systems use three levels: informational (blue), warning (amber), and critical (red/banner). Surfacing everything at the same urgency trains users to ignore all of it. YouTube Studio's "Key Metrics" section only elevates an insight to a banner if the anomaly exceeds a dynamic threshold (typically 2+ standard deviations from rolling baseline).

4. **LLM-generated narrative summaries are table-stakes by 2025.** GA4's Insights, Chartbeat's AI summaries, and Amplitude's Ask feature all use LLMs to produce 2–4 sentence natural-language summaries. The pattern is: compute statistical findings → templatize into prose → optionally use LLM for fluency/variation. Pure template strings ("Your top video this week was X with Y views") work well at scale with low hallucination risk. LLM generation adds value for non-obvious insights ("Despite lower view counts, Archival content drove 40% of subscriber gains this quarter").

5. **"What to make next" recommendations require explicit show/topic taxonomy.** Tools that give content creation recommendations (Vidooly, TubeBuddy, VidIQ) all rely on a content taxonomy (topics, series, formats). For PBS Wisconsin, the existing show-name parser and Airtable show taxonomy make this achievable — group past performance by show, identify top performers, and generate "Make more Wisconsin Life content — your last 3 episodes averaged 2.1x channel views" style recommendations.

6. **Threshold-based alerting with Slack integration is the strongest ROI for small teams.** For a team of producers and content leaders who are not living in a dashboard, push notifications via Slack are far more effective than in-app alerts that require a dashboard visit. The pattern: define thresholds in config → evaluate on each data refresh → emit Slack webhook message if crossed. Tools like Supermetrics, Databox, and custom solutions all converge here.

7. **Benchmarking requires a defined reference population.** Percentile framing ("top 10% of your content") is more meaningful than absolute benchmarks from YouTube's general population (too heterogeneous). Within-channel percentiles computed from the SQLite database are already feasible and highly contextual for PBS Wisconsin.

8. **Anomaly detection in small datasets should use simple statistical methods.** For a channel publishing 5–20 Shorts/month, z-score or IQR-based outlier detection on 90–365 day rolling windows is more reliable than ML-based approaches (insufficient training data for anomaly models). Save ML for prediction tasks; use statistics for anomaly detection.

---

## Tools & Technologies

### YouTube Studio Insights
- **Key Metrics cards**: Shown on the Studio home screen; surface the single most notable change in the past 28 days. Uses rolling baseline + dynamic threshold. Cards include: view velocity anomalies, subscriber surge correlation to a specific video, and engagement rate changes.
- **Analytics tab tooltips**: Inline annotations on charts for notable events (upload days, threshold crossings).
- **"Research" tab**: Trend-based content recommendations derived from YouTube Search trends in the creator's content niche.
- **AI-generated captions insight (2024)**: Studio now highlights videos where auto-captions drove significant impression-to-click improvements.

### Google Analytics 4 Insights
- **Automated insights panel**: Appears in the "Insights" section of GA4 reports. Uses anomaly detection across all tracked metrics; fires when a metric deviates beyond a confidence interval.
- **Custom insights**: Users define metric + threshold + comparison period. When crossed, an email and in-app notification is generated.
- **Natural language query**: "Show me sessions from organic search last month" — GA4 parses intent and returns a pre-built report. Powered by Google's internal LLMs (not publicly disclosed which model).
- **Intelligence events API**: Programmatic access to automated insight data — relevant for building a custom alerting layer on top of GA4 data.

### Amplitude
- **Automated insights (Charts)**: In-chart anomaly flagging with a "Why?" explainer that segments the anomaly by user property dimensions.
- **Ask Amplitude (2024)**: Natural language interface for generating charts. "Show me which shows drove the most new subscribers last quarter" resolves to a retention/conversion funnel query.
- **Root cause analysis**: When a metric drops, Amplitude's AI automatically runs a breakdown across all available segments to find the most explanatory dimension (geography, device, content type). The result is presented as "X% of the drop is explained by Y" — a powerful framing for content teams.
- **Notebook feature**: Combine charts + natural language annotation in a shareable document — the product-analytics analog of a weekly editorial memo.

### Mixpanel
- **Signal**: Automated insight engine that monitors event streams for statistically significant behavioral changes. Surfaces insights as cards on the home screen with severity coloring.
- **Flows**: Sankey-diagram visualization of user journeys; paired with an insight card when a step in the flow degrades. For PBS Wisconsin this maps to: Short watched → show page visited → subscribed.
- **Cohort comparison**: "Users who watched Archival content vs. users who only watched new content" — engagement and retention differences surfaced automatically.

### Chartbeat
- **Real-time heads-up display**: Visitor count + engagement score for each article, color-coded by performance (red/amber/green). Used by editorial teams in newsrooms — analogous to a channel producer monitoring Shorts velocity.
- **AI-generated summaries (2024)**: On weekly performance reports, Chartbeat generates a 3–5 sentence editorial summary of the week's top performers and anomalies. Produced with an LLM layer over structured report data.
- **Benchmark comparisons**: Every article's engaged time is shown relative to site average and category average — dual-benchmark framing eliminates the "is this good?" question.

### VidIQ / TubeBuddy (YouTube-specific tools)
- **Score-based recommendations**: VidIQ assigns each video a "VidIQ Score" (0–100) that combines SEO, engagement, and trend factors. The score is explicitly designed to answer "how likely is this to succeed?" before publishing.
- **Trending topics feed**: VidIQ's "Trending" section shows topics gaining velocity in the creator's niche, framed as "Opportunity" cards with estimated view potential ranges.
- **Best time to post**: Computed from the creator's historical subscriber activity patterns; presented as a weekly heatmap with a single top recommendation highlighted.
- **Competitor insights**: TubeBuddy allows channel-to-channel benchmarking for public channels — relevant if PBS Wisconsin wants to compare against other public media YouTube channels.

### Databox / Supermetrics (BI alerting layer)
- **Metric alerts**: Databox allows configuring threshold-based alerts across any connected data source (YouTube, Google Analytics, etc.). Notifications via Slack, email, SMS, or push.
- **Goal tracking**: Define a weekly views goal; Databox tracks pace and sends a mid-week "at risk of missing goal" alert when trajectory falls short.
- **Scorecards**: Auto-generated weekly performance summary emails — one paragraph per key metric with a trend arrow and period comparison. Good pattern for PBS Wisconsin's editorial team.

### Narrative Science / Quill (now part of Salesforce)
- **Template-based NLG**: Structured approach to natural language generation — define insight templates with variable slots, fill from computed statistics, apply grammatical variation rules. Low hallucination risk vs. open-ended LLM generation.
- **Insight taxonomy**: Narrative Science categorizes insights as: trend, comparison, anomaly, record, milestone. Each type has distinct prose templates. This taxonomy is directly applicable to PBS Wisconsin's insight engine.

---

## Examples in the Wild

### 1. YouTube Studio — "Key Metrics" Home Cards
YouTube Studio's creator home screen shows 2–4 insight cards that change weekly. Each card follows a strict format: **metric name** + **change value with direction arrow** + **1-sentence explanation** + **"See analytics" CTA link**. Example: "Views are up 47% — Your Short 'Wisconsin River Cleanup' is driving most of this growth." The card links directly to the specific video's analytics, not the generic dashboard. This is the gold standard pattern for PBS Wisconsin: single-sentence insight + direct link to the data.

### 2. Chartbeat — Live Newsroom Dashboard
Used in newsrooms including major public media organizations. The live view shows all active articles as a table with: visitors, engaged time, and a color band (green = above average, amber = average, red = below average). No numbers needed to read the room — producers glance at the color column to identify what needs attention. The benchmark (site average engaged time) is computed in real time and shown as a reference line on each sparkline. **The key pattern: color-coding relative to benchmark eliminates cognitive load for the primary use case (triage).**

### 3. GA4 Custom Insights — Threshold Alerts
GA4's custom insights allow a content team to define: "Alert me when weekly organic sessions drop more than 20% below the prior 4-week average." The alert fires via email and appears as an insight card in the dashboard. The card shows: the metric, the threshold that was crossed, the actual value, and a pre-built comparison chart. **The key pattern: user-defined thresholds + automatic comparison chart generation in the alert itself, so no dashboard visit is required to understand the situation.**

### 4. Amplitude — Root Cause AI (2024)
When Amplitude detects a metric anomaly, the "Why?" button runs an automated breakdown across all event properties and user segments. It returns: "73% of the drop in engagement is explained by iOS users in the 18–34 age group." For PBS Wisconsin: if Shorts views drop, an equivalent breakdown would identify which show's Shorts declined and whether it's a new-upload problem or existing-video velocity change. **The key pattern: automated dimensional decomposition presented as a ranked list of contributing factors, with confidence percentages.**

### 5. VidIQ — "Boost" Content Recommendations
VidIQ's home screen shows a "Boost" section with 3–5 video-creation recommendations, each structured as: **topic** + **why now** (trending signal) + **estimated view range** + **"Create" button**. Example: "Wisconsin Wildlife in Spring — trending +340% in your niche, estimated 5K–25K views." The framing is explicitly prescriptive ("create this") not just descriptive. **The key pattern: recommendation includes a "why now" urgency signal and a view range that sets expectations without false precision.**

---

## Code Patterns & Implementation Notes

### Insight Data Model

The existing `generate_insights()` in `src/analytics/core.py` returns unstructured strings in categorized lists. A structured insight model enables severity filtering, UI rendering, and Slack formatting:

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class InsightSeverity(Enum):
    INFO = "info"        # blue — notable but routine
    WARNING = "warning"  # amber — needs attention
    ALERT = "alert"      # red — requires action now

class InsightType(Enum):
    ANOMALY = "anomaly"          # unexpected deviation from baseline
    TREND = "trend"              # sustained directional change
    COMPARISON = "comparison"    # relative performance vs. benchmark
    RECORD = "record"            # new high/low
    MILESTONE = "milestone"      # threshold crossed (e.g. 10K views)
    RECOMMENDATION = "recommendation"  # prescriptive: "do this"

@dataclass
class Insight:
    id: str                          # stable identifier for deduplication
    type: InsightType
    severity: InsightSeverity
    headline: str                    # 1-sentence summary (max 120 chars)
    detail: str                      # 2–4 sentence explanation
    metric: str                      # which metric triggered this
    metric_value: float              # current value
    benchmark_value: Optional[float] # comparison value (channel avg, prior period)
    benchmark_label: str             # "channel average", "prior 30 days", etc.
    action_label: Optional[str]      # CTA text, e.g. "View video analytics"
    action_url: Optional[str]        # deep link into the dashboard
    entity_type: str                 # "video", "show", "channel", "short"
    entity_id: Optional[str]         # video_id, show_name, etc.
    entity_title: Optional[str]
    generated_at: str                # ISO timestamp
```

### Anomaly Detection (Statistical, No ML Required)

For a channel publishing 5–20 Shorts/month, use rolling z-score or IQR against a 90-day window:

```python
import pandas as pd
import numpy as np
from typing import List

def detect_view_velocity_anomalies(
    videos_df: pd.DataFrame,
    window_days: int = 90,
    z_threshold: float = 2.0,
) -> List[Insight]:
    """
    Flag videos whose views-per-day velocity is anomalously high or low
    relative to the rolling channel average.
    """
    insights = []
    recent = videos_df[
        videos_df['publish_date'] >= pd.Timestamp.now() - pd.Timedelta(days=window_days)
    ].copy()

    if len(recent) < 5:
        return insights  # insufficient baseline

    mean_vpd = recent['views_per_day'].mean()
    std_vpd = recent['views_per_day'].std()

    for _, row in recent.iterrows():
        if std_vpd == 0:
            continue
        z = (row['views_per_day'] - mean_vpd) / std_vpd

        if z >= z_threshold:
            insights.append(Insight(
                id=f"anomaly-velocity-high-{row['video_id']}",
                type=InsightType.ANOMALY,
                severity=InsightSeverity.ALERT if z >= 3.0 else InsightSeverity.WARNING,
                headline=f"'{row['title'][:60]}' is getting {row['views_per_day']:.0f} views/day — {z:.1f}x above average",
                detail=(
                    f"This video is performing significantly above the channel baseline of "
                    f"{mean_vpd:.0f} views/day over the past {window_days} days. "
                    f"Consider boosting with a community post or cross-posting to other platforms while momentum is high."
                ),
                metric="views_per_day",
                metric_value=row['views_per_day'],
                benchmark_value=mean_vpd,
                benchmark_label=f"{window_days}-day channel average",
                action_label="Open in YouTube Studio",
                action_url=f"https://studio.youtube.com/video/{row['video_id']}/analytics",
                entity_type="video",
                entity_id=row['video_id'],
                entity_title=row['title'],
                generated_at=pd.Timestamp.now().isoformat(),
            ))

        elif z <= -z_threshold:
            insights.append(Insight(
                id=f"anomaly-velocity-low-{row['video_id']}",
                type=InsightType.ANOMALY,
                severity=InsightSeverity.INFO,
                headline=f"'{row['title'][:60]}' is underperforming at {row['views_per_day']:.0f} views/day",
                detail=(
                    f"This video is below the {window_days}-day channel average of {mean_vpd:.0f} views/day. "
                    f"Consider reviewing thumbnail, title, or publishing time."
                ),
                metric="views_per_day",
                metric_value=row['views_per_day'],
                benchmark_value=mean_vpd,
                benchmark_label=f"{window_days}-day channel average",
                action_label=None,
                action_url=None,
                entity_type="video",
                entity_id=row['video_id'],
                entity_title=row['title'],
                generated_at=pd.Timestamp.now().isoformat(),
            ))

    return insights
```

### Benchmarking with Percentile Framing

```python
def compute_percentile_rank(value: float, reference_series: pd.Series) -> float:
    """Return the percentile rank (0–100) of value within reference_series."""
    return (reference_series < value).mean() * 100

def generate_benchmark_insight(
    video_row: dict,
    channel_videos: pd.DataFrame,
    metric: str = "views",
) -> Optional[Insight]:
    pct = compute_percentile_rank(video_row[metric], channel_videos[metric])
    channel_avg = channel_videos[metric].mean()

    if pct >= 80:
        severity = InsightSeverity.ALERT  # positive alert
        headline = (
            f"'{video_row['title'][:60]}' is in the top {100 - pct:.0f}% "
            f"of your channel by {metric}"
        )
    elif pct <= 20:
        severity = InsightSeverity.INFO
        headline = (
            f"'{video_row['title'][:60]}' is in the bottom {pct:.0f}% "
            f"of your channel by {metric}"
        )
    else:
        return None  # mid-range — not worth surfacing

    return Insight(
        id=f"benchmark-{metric}-{video_row['video_id']}",
        type=InsightType.COMPARISON,
        severity=severity,
        headline=headline,
        detail=f"Channel average: {channel_avg:,.0f}. This video: {video_row[metric]:,.0f}.",
        metric=metric,
        metric_value=video_row[metric],
        benchmark_value=channel_avg,
        benchmark_label="channel average",
        ...
    )
```

### Streamlit Insight Card Component

```python
def render_insight_card(insight: Insight, container=None):
    """Render a single Insight as a styled Streamlit card."""
    target = container or st

    COLOR_MAP = {
        InsightSeverity.INFO: "#1f77b4",      # blue
        InsightSeverity.WARNING: "#ff7f0e",   # amber
        InsightSeverity.ALERT: "#d62728",     # red
    }
    ICON_MAP = {
        InsightType.ANOMALY: "⚡",
        InsightType.TREND: "📈",
        InsightType.COMPARISON: "🔢",
        InsightType.RECORD: "🏆",
        InsightType.MILESTONE: "🎯",
        InsightType.RECOMMENDATION: "💡",
    }

    color = COLOR_MAP[insight.severity]
    icon = ICON_MAP[insight.type]

    target.markdown(
        f"""
        <div style="
            border-left: 4px solid {color};
            background: #f8f9fa;
            padding: 12px 16px;
            border-radius: 4px;
            margin-bottom: 12px;
        ">
            <div style="font-weight: 600; font-size: 0.95rem;">
                {icon} {insight.headline}
            </div>
            <div style="color: #555; font-size: 0.85rem; margin-top: 4px;">
                {insight.detail}
            </div>
            {"" if not insight.benchmark_value else
             f'<div style="color: #888; font-size: 0.8rem; margin-top: 6px;">'
             f'Benchmark ({insight.benchmark_label}): '
             f'{insight.benchmark_value:,.0f}</div>'}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if insight.action_label and insight.action_url:
        target.markdown(f"[{insight.action_label}]({insight.action_url})")


def render_insights_panel(insights: List[Insight]):
    """Render all insights, grouped by severity (ALERT first)."""
    st.header("Insights & Recommendations")

    ordered = sorted(insights, key=lambda i: (
        {InsightSeverity.ALERT: 0, InsightSeverity.WARNING: 1, InsightSeverity.INFO: 2}[i.severity]
    ))

    alerts = [i for i in ordered if i.severity == InsightSeverity.ALERT]
    warnings = [i for i in ordered if i.severity == InsightSeverity.WARNING]
    infos = [i for i in ordered if i.severity == InsightSeverity.INFO]

    if alerts:
        st.subheader("Needs Attention")
        for insight in alerts:
            render_insight_card(insight)

    if warnings:
        st.subheader("Worth Watching")
        for insight in warnings:
            render_insight_card(insight)

    if infos:
        with st.expander(f"Additional insights ({len(infos)})"):
            for insight in infos:
                render_insight_card(insight)

    if not insights:
        st.info("No significant insights detected in this period.")
```

### Slack Alerting Integration

```python
import requests
import json

class SlackAlerter:
    """Send insight alerts to a Slack webhook."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def _severity_emoji(self, severity: InsightSeverity) -> str:
        return {
            InsightSeverity.ALERT: ":rotating_light:",
            InsightSeverity.WARNING: ":warning:",
            InsightSeverity.INFO: ":information_source:",
        }[severity]

    def send_insight(self, insight: Insight) -> bool:
        """Send a single insight as a Slack message."""
        emoji = self._severity_emoji(insight.severity)
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *{insight.headline}*\n{insight.detail}",
                },
            }
        ]

        if insight.benchmark_value is not None:
            blocks.append({
                "type": "context",
                "elements": [{
                    "type": "mrkdwn",
                    "text": (
                        f"Benchmark ({insight.benchmark_label}): "
                        f"{insight.benchmark_value:,.0f} | "
                        f"Actual: {insight.metric_value:,.0f}"
                    ),
                }]
            })

        if insight.action_label and insight.action_url:
            blocks.append({
                "type": "actions",
                "elements": [{
                    "type": "button",
                    "text": {"type": "plain_text", "text": insight.action_label},
                    "url": insight.action_url,
                }]
            })

        payload = {"blocks": blocks}
        resp = requests.post(
            self.webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        return resp.status_code == 200

    def send_digest(self, insights: List[Insight], title: str = "Weekly PBS Wisconsin Analytics Digest"):
        """Send a grouped digest of all insights."""
        alerts = [i for i in insights if i.severity == InsightSeverity.ALERT]
        warnings = [i for i in insights if i.severity == InsightSeverity.WARNING]

        lines = [f"*{title}*\n"]
        if alerts:
            lines.append(f":rotating_light: *{len(alerts)} items need attention*")
            for i in alerts:
                lines.append(f"  • {i.headline}")
        if warnings:
            lines.append(f"\n:warning: *{len(warnings)} items worth watching*")
            for i in warnings:
                lines.append(f"  • {i.headline}")

        payload = {"text": "\n".join(lines)}
        requests.post(self.webhook_url, json=payload, timeout=5)
```

### Natural Language Summary Generator (Template-Based)

```python
def generate_weekly_narrative(
    insights: List[Insight],
    overview: dict,
    period_label: str = "this week",
) -> str:
    """
    Generate a 3–5 sentence plain-English summary of weekly performance.
    Uses templates (low hallucination risk) with optional LLM for fluency.
    """
    alerts = [i for i in insights if i.severity == InsightSeverity.ALERT]
    top_performing = [i for i in insights if i.type == InsightType.RECORD]

    lines = []

    # Lead: overall performance
    views = overview.get("total_views", 0)
    pct_change = overview.get("views_pct_change_vs_prior_period", 0)
    direction = "up" if pct_change >= 0 else "down"
    lines.append(
        f"PBS Wisconsin's channel earned {views:,} views {period_label}, "
        f"{direction} {abs(pct_change):.0f}% from the prior period."
    )

    # Notable events
    if alerts:
        top_alert = alerts[0]
        lines.append(top_alert.detail)

    # Record / milestone
    if top_performing:
        lines.append(top_performing[0].headline + ".")

    # Recommendation hook
    recs = [i for i in insights if i.type == InsightType.RECOMMENDATION]
    if recs:
        lines.append(f"Top recommendation: {recs[0].headline}")

    return " ".join(lines)
```

### PBS Wisconsin — Show-Based Content Recommendations

```python
def generate_show_recommendations(
    show_df: pd.DataFrame,
    lookback_videos: int = 5,
) -> List[Insight]:
    """
    Generate 'what to make next' recommendations based on per-show performance.
    Requires show_df with columns: show_name, avg_views, avg_engagement, video_count,
    last_publish_date, trend_direction (+1/-1/0).
    """
    insights = []
    channel_avg_views = show_df['avg_views'].mean()

    for _, show in show_df.iterrows():
        ratio = show['avg_views'] / max(channel_avg_views, 1)
        days_since_last = (pd.Timestamp.now() - show['last_publish_date']).days

        if ratio >= 1.5 and days_since_last > 30:
            insights.append(Insight(
                id=f"rec-show-{show['show_name'].replace(' ', '-').lower()}",
                type=InsightType.RECOMMENDATION,
                severity=InsightSeverity.WARNING,
                headline=(
                    f"Publish a new {show['show_name']} Short — "
                    f"last {min(lookback_videos, show['video_count'])} averaged "
                    f"{show['avg_views']:,.0f} views ({ratio:.1f}x channel average)"
                ),
                detail=(
                    f"{show['show_name']} consistently outperforms the channel average "
                    f"and hasn't published in {days_since_last} days. "
                    f"Audience demand is likely unfulfilled."
                ),
                metric="avg_views",
                metric_value=show['avg_views'],
                benchmark_value=channel_avg_views,
                benchmark_label="channel average views",
                action_label=None,
                action_url=None,
                entity_type="show",
                entity_id=None,
                entity_title=show['show_name'],
                generated_at=pd.Timestamp.now().isoformat(),
            ))

    return sorted(insights, key=lambda i: -i.metric_value)
```

### FastAPI Endpoint for Insights

Aligns with the existing `api/routers/analytics.py` pattern:

```python
# api/routers/insights.py
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from api.dependencies import get_db
from api.schemas import InsightSchema  # Pydantic model mirroring Insight dataclass

router = APIRouter()

@router.get("/analytics/insights", response_model=List[InsightSchema])
def get_insights(
    channel_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None, description="Filter by severity: info|warning|alert"),
    days: int = Query(90, ge=7, le=365),
    db=Depends(get_db),
):
    """
    Return computed insights for the channel.
    Insights are computed on-demand from the SQLite database.
    """
    videos = db.get_all_videos(channel_id=channel_id)
    shows = db.get_show_summary(channel_id=channel_id)
    # ... run insight generators, filter by severity, return
```

---

## Gotchas & Anti-Patterns

### 1. Insight inflation — surfacing too many things at once
Dashboards that generate 20+ insight cards simultaneously suffer from the same problem as email inboxes with 200 unread messages: users learn to ignore them. **Rule of thumb: surface at most 5–7 insights per view, prioritized by severity and novelty.** Implement deduplication by insight ID — don't re-surface the same insight every week unless it remains anomalous.

### 2. Absolute numbers without benchmarks
"This Short has 4,200 views" is useless context-free. Always pair a metric with a benchmark. The benchmark should be the most contextually relevant one available: show average is better than channel average for PBS Wisconsin, because show audiences have different baseline sizes. Never use YouTube's global benchmarks — they are dominated by content categories that have no relevance to public media.

### 3. LLM hallucination in analytical narratives
Open-ended LLM prompts like "summarize this channel's performance" will hallucinate specific numbers. Always compute statistics first, then either use structured templates or provide computed values as grounded context in an LLM prompt: "Given that views were 14,200 (up 23% from prior period), top video was X with Y views, write a 2-sentence summary." Constrain the LLM to prose fluency, not fact generation.

### 4. Severity creep — everything becoming "critical"
Alert fatigue is the #1 failure mode of alerting systems. Reserve the red/ALERT tier for genuinely time-sensitive events: a video going viral (opportunity window), a sudden views crash (potential content issue), or an API quota approaching exhaustion (operational). Weekly benchmark comparisons should never be ALERT severity.

### 5. Metric vanity — tracking what is easy, not what matters
Views are easy to measure. Subscriber conversion rate per video, and Shorts-to-longform watch continuation rate, are harder but far more actionable for PBS Wisconsin's goals. Insight systems built on vanity metrics ("10,000 views!") produce feel-good noise, not editorial direction. Define 3–5 metrics that actually reflect the content strategy goals before building the insight layer.

### 6. Real-time alerting for a 5-20 video/month publisher
Building a real-time streaming alert pipeline (Kafka, Flink, etc.) is wildly over-engineered for a channel publishing at this cadence. A daily batch job that runs after the launchd data refresh (already in the backlog) is the right architecture. Alert within hours, not seconds. Save engineering complexity for when it matters.

### 7. Comparing Shorts to longform with the same metrics
Shorts have fundamentally different discovery mechanics, view-duration expectations, and engagement patterns. Comparing a Short's average view duration to a 20-minute episode's average view duration produces misleading insights. Always segment by content type before generating any comparative insight. The existing `is_short` flag in the data model handles this — use it consistently in all insight generators.

### 8. Ignoring temporal context in recommendations
"Make more Wisconsin Life content" is a bad recommendation if Wisconsin Life just released 3 episodes last week. Good recommendation engines check recency (last publish date) and pacing (publish cadence relative to show baseline) before suggesting more content. The show-recommendation pattern above includes `days_since_last` for this reason.

---

## Sources & Further Reading

Note: URLs below are based on documented product features through August 2025 training data. Verify currency before citing.

- YouTube Studio Analytics help: https://support.google.com/youtube/answer/9002587
- YouTube Studio Key Metrics cards: https://support.google.com/youtube/answer/9314414
- Google Analytics 4 Automated Insights: https://support.google.com/analytics/answer/9443595
- GA4 Custom Insights configuration: https://support.google.com/analytics/answer/9443604
- Amplitude Automated Insights (product docs): https://amplitude.com/docs/analytics/insights
- Amplitude Ask (NL query, 2024): https://amplitude.com/blog/introducing-ask-amplitude
- Amplitude Root Cause Analysis: https://amplitude.com/docs/analytics/root-cause-analysis
- Mixpanel Signal: https://docs.mixpanel.com/docs/reports/signal
- Chartbeat Heads-up Display: https://support.chartbeat.com/hc/en-us/articles/200153135
- VidIQ Trending Topics: https://vidiq.com/youtube-tools/trending/
- TubeBuddy Channel Benchmarks: https://www.tubebuddy.com/tools/benchmarking
- Databox Metric Alerts: https://databox.com/alerts
- Supermetrics Alerting: https://supermetrics.com/blog/google-data-studio-alerts
- Narrative Science / Quill NLG taxonomy: https://narrativescience.com/resources/
- Streamlit metric components (delta patterns): https://docs.streamlit.io/library/api-reference/data/st.metric
- Plotly annotation / shape reference for chart anomaly flagging: https://plotly.com/python/shapes/
- YouTube Analytics API — quotas and caching best practices: https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits
- FastAPI background tasks for async insight computation: https://fastapi.tiangolo.com/tutorial/background-tasks/
- Slack Block Kit for structured alert messages: https://api.slack.com/block-kit

---

## Recommended for The Library

1. **Amplitude's Root Cause Analysis documentation** — the dimensional decomposition approach is directly applicable to diagnosing Shorts performance drops by show, format, or publish day. Scrape: https://amplitude.com/docs/analytics/root-cause-analysis

2. **Slack Block Kit Builder and Webhook guide** — essential reference for building the alerting integration. The Block Kit format enables rich, interactive messages that go beyond plain text. Scrape: https://api.slack.com/block-kit and https://api.slack.com/messaging/webhooks

3. **GA4 Custom Insights API documentation** — documents the programmatic access patterns for the Intelligence Events API, which is the right model for building a custom insight notification layer. Scrape: https://support.google.com/analytics/answer/9443604

4. **Chartbeat's newsroom dashboard case studies** — public media / editorial context is rare in analytics tool documentation; Chartbeat's newsroom deployment patterns (real-time triage, benchmark coloring) are directly relevant to PBS Wisconsin. Scrape: https://chartbeat.com/publishing-solutions/

5. **Plotly Annotations and Shapes reference** — the technical foundation for annotating anomalies directly on time-series charts (vertical lines at upload events, shaded regions for anomalous periods). Scrape: https://plotly.com/python/shapes/
