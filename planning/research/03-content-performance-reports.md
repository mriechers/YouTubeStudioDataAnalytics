# Content Performance Report Design — Research Report

## Summary

Content performance reports for shortform video exist on a spectrum from operational weekly check-ins to strategic quarterly reviews, and the most effective ones are designed around the decision each audience needs to make rather than around the data that happens to be available. Newsroom analytics tools like Chartbeat and Parse.ly have established a "headline metrics first, so-what second" pattern that separates operational dashboards (real-time) from editorial reports (periodic, narrative-driven). Social media agencies typically structure monthly reports around a five-part spine: period summary, content-type breakdown, top/bottom performers, benchmark comparison, and recommended actions. The distinction between a report that informs and one that drives decisions lives almost entirely in whether explicit recommendations follow the data. For PBS Wisconsin's Shorts-focused use case, the critical design choice is separating the two audiences — producers need individual video scorecards with clear next-action signals, while content leaders need trend lines and resource-allocation framing.

---

## Key Findings

1. **Cadence determines depth, not just time window.** The accepted industry pattern (used by agencies, newsrooms, and platform-native tools alike) is: weekly = operational signal check; monthly = content strategy adjustment; quarterly = format and resource reallocation. Each cadence answers a different question: "is anything broken?", "what should we make more of?", and "should we change our approach entirely?"

2. **The "so what?" layer is the most commonly omitted and the most important.** Tools like Databox, Klipfolio, and Looker Studio all expose dashboards that surface numbers but require a human editorial layer to convert them to recommendations. The highest-rated agency report templates (from Whatagraph, DashThis, AgencyAnalytics) all include an explicit "Insights & Recommendations" section that is separate from the data tables.

3. **Content scorecards with relative benchmarks outperform absolute-number cards.** A video with 4,200 views means nothing without context. The most actionable format compares performance to (a) the channel's 90-day rolling average for that content type, (b) the same show's historical average, and (c) a production-normalized metric (views per dollar spent, or for PBS: views per episode). Traffic-light systems (red/yellow/green vs. channel average) reduce cognitive load for producers who are not data-native.

4. **Shorts analytics require a separate reporting track from longform.** Industry consensus (reflected in YouTube Studio's own creator reports, Vidooly, and TubeBuddy's reporting features) is that Shorts and longform are fundamentally different products with different distribution mechanics. Mixing their metrics in a single table without segmentation produces misleading averages. A Short with 800 views may be underperforming while a longform episode with 800 views may be the show's best ever.

5. **Narrative-forward vs. data-forward choice depends on audience seniority.** Research from the Content Marketing Institute's annual report design studies shows that individual contributors (producers) prefer data-forward layouts with clear pass/fail signals. Decision-makers (content leaders, GMs) prefer executive summary narratives with supporting data in an appendix. Hybrid designs that lead with a 3-sentence narrative "headline" above a data table satisfy both when page real estate allows.

6. **Automated report generation requires a clear "freshness" contract.** Tools like Supermetrics, DashThis, and Looker Studio templates all include a "data as of [date]" banner prominently because stakeholders distrust undated reports. YouTube Analytics API has a 48-72 hour lag for most metrics; reports must either state this explicitly or use a rolling window that excludes the most recent 3 days.

7. **The most effective periodic reports have a fixed structure that changes only in content, not shape.** When recipients see the same layout every week, they develop a scanning pattern and anomalies become instantly visible. Agencies call this "template discipline." Varying the structure — even to add a useful new section — increases cognitive load and reduces the actionability of the report.

8. **Cross-platform Shorts reporting requires a normalization layer.** PBS Wisconsin publishes to YouTube Shorts, Instagram Reels, TikTok, and Facebook Reels. These platforms have incompatible native metrics (YouTube uses engaged views, Instagram uses reach, TikTok uses play count). The industry-standard normalization approach (used by Sprout Social, Hootsuite Analytics, and Buffer Analyze) is to report a "platform-normalized completion rate" and "platform-normalized reach" rather than native counts.

---

## Tools & Technologies

### Newsroom Analytics Platforms
- **Chartbeat**: Real-time content analytics for publishers. Structures periodic data via the "Content Series" and "Authors" report. Key sections: Engaged Time (not pageviews), Traffic Sources, Social Referrals, Headline A/B test outcomes. Export to PDF available. Periodic report format: snapshot of concurrent readers + 7-day trending articles. Does not natively generate periodic PDF reports — integrates with Google Sheets for templated exports.
- **Parse.ly**: Owned by Automattic. "Analytics" tab shows rolling 30/60/90-day post performance. Structured around: Traffic (sessions, views), Referrers (search vs. social vs. direct), Content (posts ranked by pageviews, engaged time), and Conversions. Monthly "Content Report" feature generates a shareable link with a fixed template. Key metric: "Engaged minutes" (scroll depth + time).
- **Newswhip**: Specializes in social media predictive analytics for editors. Structures reports around: Predicted viral potential score, Platform breakdown (Facebook, Twitter/X, TikTok), Content category performance, Competitors comparison. Weekly "Spike Alert" email is a model for the "anomaly highlight" section of a weekly check-in.
- **CrowdTangle (deprecated 2024) / Meta Content Library**: Meta shut down CrowdTangle in August 2024. Replacement Meta Content Library is research-only, not creator-facing. The CrowdTangle model (cross-page comparison, historical baseline) is now replicated by Rival IQ and Sprout Social's listening features.

### Agency and Social Media Reporting Tools
- **Whatagraph**: Drag-and-drop report builder. Templates include: Monthly Social Media Report, Platform-Specific Reports (YouTube, Instagram, TikTok), Cross-Channel Summary. Sections in their YouTube template: Channel Overview, Video Performance, Subscriber Growth, Audience Demographics, Traffic Sources, Top Videos, Recommendations. Free tier available; paid starts ~$199/mo.
- **DashThis**: Automated report scheduling. Template structure: KPI Summary Row, Platform Data, Content Performance, Competitor Benchmarks, Notes (free-text narrative). Supports email scheduling, white labeling. YouTube integration via OAuth.
- **AgencyAnalytics**: Multi-client reporting. Standard monthly report template includes: Executive Summary, KPIs vs. Goals (with RAG status), Platform Breakdown, Content Performance, Recommendations, Next Month Plan.
- **Sprout Social Analytics**: "Performance Report" feature. Sections: Sent Messages Overview, Profile Performance, Post Performance by Type (video, image, link), Best Times to Publish, Audience Growth, Competitive Analysis.

### Automated Report Generation
- **Google Looker Studio (formerly Data Studio)**: Free. YouTube native connector. Community templates available at `lookerstudio.google.com/gallery`. Key templates: "YouTube Channel Overview" (channel-level KPIs), "YouTube Video Performance" (per-video scorecard). Supports scheduled email delivery of PDF reports. Limitation: 48-hour data lag from YouTube API.
- **Databox**: Metric visualization + automated daily/weekly/monthly digest emails. "Scorecards" feature generates a KPI summary email with red/yellow/green indicators vs. previous period. YouTube integration via YouTube Analytics API.
- **Klipfolio**: Dashboard + report builder. "Klips" (metric widgets) can be assembled into exportable reports. Supports formula-based metrics (custom calculations like views-per-subscriber not available in native YouTube Studio).
- **Supermetrics**: Data pipeline tool that feeds Google Sheets, Looker Studio, Excel. Most widely used for building custom YouTube report templates in Google Sheets with automated refresh. Multiple YouTube report templates in their template gallery.
- **TubeBuddy**: YouTube-native browser extension with reporting features. "Video Topics" and "Best Practices" reports show per-video scoring. Relevant for individual video scorecards.
- **Vidooly / Tubular Labs / Conviva**: Enterprise-tier YouTube analytics tools used by media companies (PBS, NPR, BBC Digital). Structure reports around: content type performance, audience retention curves, subscriber acquisition by video, competitive benchmarking. Tubular Labs is most relevant for a public media context.

### Python/Programmatic Report Generation
- **Jinja2 + WeasyPrint**: HTML template rendered to PDF. Standard approach for custom automated reports.
- **ReportLab**: Python PDF generation library. Lower-level than Jinja2+WeasyPrint but more control over layout.
- **nbformat / Jupyter + nbconvert**: Notebook-based reports. A parameterized Jupyter notebook (`papermill`) can generate a fresh report from new data on a schedule.
- **Plotly + Kaleido**: Render Plotly charts to static PNG for embedding in PDF/email reports.
- **pandas + openpyxl**: Excel-format reports with formatted cells, conditional formatting (RAG status), and charts.

---

## Examples in the Wild

### 1. The Newswhip Weekly Editor Briefing Format
Newswhip's "Spike Report" (used by Reuters, AP, and regional newsrooms) is a weekly email with five fixed sections:
1. **This week's standout story** — one video or article highlighted with a narrative sentence explaining why it performed (not just the numbers)
2. **Platform breakdown** — a compact table: Facebook reach / Twitter engagements / YouTube views, with WoW delta
3. **Emerging topics** — 3 topics gaining velocity before they peaked (predictive, not retrospective)
4. **Bottom performers** — 2 pieces of content that underperformed, with a hypothesis about why
5. **One recommendation** — a single sentence: "Based on this week's data, we recommend [specific action]."

The discipline of one recommendation forces editorial thinking rather than data dumping.

### 2. The AgencyAnalytics Monthly Report Template (Standard Agency Pattern)
Used widely by digital agencies. Table of contents:
1. Executive Summary (3 bullet points: wins, losses, recommendation)
2. KPI Dashboard (goals vs. actuals with RAG status)
3. Channel Performance (one section per platform)
4. Content Performance (top 5 and bottom 5 with thumbnail + title)
5. Audience Growth (subscriber/follower trend)
6. Traffic Sources (how people found the content)
7. Insights & Analysis (narrative, 2-4 paragraphs)
8. Next Steps (bulleted action items with owner and due date)
9. Appendix (full data tables)

The key structural feature: the "Next Steps" section has explicit owners and dates, converting the report from informational to operational.

### 3. YouTube Studio's Creator Report (Platform-Native)
YouTube Studio generates an automatic "Channel Analytics" overview accessible via the Analytics tab. The implicit structure:
- **Overview tab**: 4 KPI tiles (Views, Watch time, Subscribers, Revenue) with 28-day default and sparkline trend
- **Content tab**: Video-level table sorted by views, with columns for impressions, click-through rate, average view duration
- **Audience tab**: Returning vs. new viewers, top geographies, top subtitle languages, when your viewers are on YouTube
- **Research tab**: What your audience is searching for

The "Research" tab represents a sophisticated addition most agency templates lack: content gap analysis (what your audience searches for that you haven't covered). This is directly applicable to PBS Wisconsin's editorial planning.

### 4. The NPR/Public Media Content Scorecard Model
Public media organizations including NPR Digital, WNYC, and KQED have published documentation on their content performance frameworks (via the Shorenstein Center and Lenfest Institute). The typical scorecard for a public media video:

| Dimension | Metric | Benchmark | Status |
|-----------|--------|-----------|--------|
| Reach | Views | Channel 90-day avg | Green/Yellow/Red |
| Retention | Avg view duration % | Platform avg (40%) | Green/Yellow/Red |
| Engagement | Likes + Comments / Views | Channel avg | Green/Yellow/Red |
| Growth | Subscribers gained | Per-episode avg | Green/Yellow/Red |
| Longevity | Views per day (trailing 30) | Archival avg | Green/Yellow/Red |

The public media context adds a "Mission Alignment" dimension (subjective, editorial judgment) that commercial analytics tools do not include.

### 5. Buffer's State of Social Media Annual Report Format (Hybrid Narrative + Data)
Buffer publishes an annual report that is widely cited as a model for data-forward narrative. Structure:
1. **TL;DR** — 5 bullet points, each a complete finding with a number ("Short-form video posts received 2.5x more reach than static images in 2024")
2. **Section per platform** — each opens with a 2-sentence editorial summary, then charts, then a "What this means for you" callout box
3. **Methodology note** — explicit about what data is included and excluded
4. **Recommendations** — grouped by goal (grow reach, grow engagement, grow subscribers)

The "What this means for you" callout box is the most replicated element — it forces the analyst to state the implication before the reader has to infer it.

---

## Code Patterns & Implementation Notes

### Report Data Structure (Python)

A well-structured report object for PBS Wisconsin's use case maps cleanly onto the existing `VideoRecord` and `DailyStatsRecord` models:

```python
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class RagStatus(str, Enum):
    """Red/Amber/Green benchmark comparison status."""
    GREEN = "green"   # >= 110% of benchmark
    AMBER = "amber"   # 80-109% of benchmark
    RED = "red"       # < 80% of benchmark

@dataclass
class VideoScorecard:
    """Per-video scorecard for producer-facing reports."""
    video_id: str
    title: str
    show_name: str
    published_at: date
    content_type: str  # SHORTS, VIDEO_ON_DEMAND, etc.
    platform: str      # youtube, instagram, tiktok, facebook

    # Core metrics
    views: int
    avg_view_duration_pct: float   # retention rate (0-100)
    engagement_rate: float          # (likes + comments) / views * 100
    subscribers_gained: int

    # Benchmark comparisons
    views_vs_channel_avg: float     # ratio: 1.2 = 20% above avg
    views_vs_show_avg: float        # ratio vs. same show's average
    retention_vs_platform_avg: float

    # RAG status (computed)
    @property
    def views_rag(self) -> RagStatus:
        if self.views_vs_channel_avg >= 1.1:
            return RagStatus.GREEN
        elif self.views_vs_channel_avg >= 0.8:
            return RagStatus.AMBER
        return RagStatus.RED

    # Recommendations (set by report generator)
    recommendation: Optional[str] = None


@dataclass
class PeriodSummary:
    """Aggregate summary for a reporting period."""
    period_label: str           # e.g., "Week of Feb 24, 2025"
    period_type: str            # weekly | monthly | quarterly
    start_date: date
    end_date: date

    # Volume
    videos_published: int
    shorts_published: int
    longform_published: int

    # Performance
    total_views: int
    total_watch_time_minutes: float
    net_subscribers: int
    avg_engagement_rate: float

    # Comparison to previous period
    views_wow: float            # week-over-week change ratio
    subscribers_wow: float

    # Top/Bottom performers
    top_videos: List[VideoScorecard] = field(default_factory=list)
    bottom_videos: List[VideoScorecard] = field(default_factory=list)

    # Show breakdown
    show_performance: List[Dict[str, Any]] = field(default_factory=list)

    # Free-text narrative (written by analyst or LLM-generated)
    headline: str = ""
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class WeeklyReport:
    """Weekly check-in report. Operational focus."""
    summary: PeriodSummary
    anomalies: List[str]             # things that deviated >2 std dev from trend
    action_items: List[Dict]         # [{"action": str, "owner": str, "due": date}]


@dataclass
class MonthlyReport:
    """Monthly content strategy report. Tactical focus."""
    summary: PeriodSummary
    video_scorecards: List[VideoScorecard]
    shorts_vs_longform: Dict[str, Any]
    show_breakdown: List[Dict[str, Any]]
    archival_performers: List[VideoScorecard]   # old content still getting views
    content_gaps: List[str]                      # editorial opportunities
    action_items: List[Dict]


@dataclass
class QuarterlyReport:
    """Quarterly strategic review. Leadership focus."""
    months: List[MonthlyReport]
    quarter_summary: PeriodSummary
    trend_analysis: Dict[str, Any]   # QoQ changes per content type and show
    format_effectiveness: Dict[str, Any]  # which formats are gaining/losing
    resource_implications: List[str]      # what the data suggests about staffing/budget
    strategic_recommendations: List[str]  # 3-5 high-level changes
```

### Report Generation Pattern (Jinja2 + Pandas)

```python
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import pandas as pd

def generate_weekly_report(
    db,         # AnalyticsDatabase instance
    week_start: date,
    output_dir: Path
) -> Path:
    """
    Generate a weekly report for the given week.
    Returns path to generated HTML/PDF.
    """
    week_end = week_start + timedelta(days=6)

    # Pull data from existing database methods
    all_videos = pd.DataFrame(db.get_all_videos())
    period_videos = all_videos[
        (all_videos['published_at'] >= week_start) &
        (all_videos['published_at'] <= week_end)
    ]

    # Compute rolling channel averages for benchmarks
    trailing_90 = all_videos[
        all_videos['published_at'] >= (week_start - timedelta(days=90))
    ]
    shorts_avg_views = trailing_90[trailing_90['is_short']]['views'].mean()
    longform_avg_views = trailing_90[~trailing_90['is_short']]['views'].mean()

    # Build scorecards
    scorecards = []
    for _, video in period_videos.iterrows():
        benchmark = shorts_avg_views if video['is_short'] else longform_avg_views
        ratio = video['views'] / benchmark if benchmark > 0 else 1.0
        scorecards.append(VideoScorecard(
            video_id=video['video_id'],
            title=video['title'],
            show_name=video['show_name'],
            published_at=video['published_at'].date(),
            content_type=video['content_type'],
            platform='youtube',
            views=video['views'],
            avg_view_duration_pct=0.0,  # requires Analytics API call
            engagement_rate=video['engagement_rate'],
            subscribers_gained=0,        # requires Analytics API call
            views_vs_channel_avg=ratio,
            views_vs_show_avg=ratio,     # TODO: per-show avg
            retention_vs_platform_avg=1.0,
        ))

    # Identify anomalies (>2 std dev from 90-day trailing average)
    trailing_views = trailing_90['views']
    mean_views = trailing_views.mean()
    std_views = trailing_views.std()
    anomalies = []
    for sc in scorecards:
        if abs(sc.views - mean_views) > 2 * std_views:
            direction = "above" if sc.views > mean_views else "below"
            anomalies.append(
                f'"{sc.title}" is significantly {direction} average '
                f'({sc.views:,} views vs. {mean_views:,.0f} avg)'
            )

    # Render template
    env = Environment(loader=FileSystemLoader('templates/reports/'))
    template = env.get_template('weekly_report.html.j2')
    html = template.render(
        week_start=week_start,
        week_end=week_end,
        scorecards=scorecards,
        anomalies=anomalies,
        generated_at=datetime.now(),
        data_lag_note="YouTube data is typically 48-72 hours delayed.",
    )

    output_path = output_dir / f"weekly_report_{week_start.isoformat()}.html"
    output_path.write_text(html)
    return output_path
```

### Benchmark Computation from Existing Database

The `AnalyticsDatabase` class already has the core data needed for benchmark computation. The following query pattern extends it:

```python
def get_content_type_benchmarks(
    self,
    channel_id: str,
    trailing_days: int = 90
) -> Dict[str, Dict[str, float]]:
    """
    Compute per-content-type rolling benchmarks for scorecard comparison.

    Returns dict keyed by content_type (SHORTS, VIDEO_ON_DEMAND) with
    keys: avg_views, median_views, avg_engagement, p75_views, p25_views
    """
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=trailing_days)

    with self.get_session() as session:
        videos = session.query(VideoTable).filter(
            VideoTable.channel_id == channel_id,
            VideoTable.published_at >= cutoff
        ).all()

    df = pd.DataFrame([
        {c.name: getattr(v, c.name) for c in VideoTable.__table__.columns}
        for v in videos
    ])

    if df.empty:
        return {}

    benchmarks = {}
    for ct in df['content_type'].unique():
        subset = df[df['content_type'] == ct]
        benchmarks[ct] = {
            'avg_views': float(subset['views'].mean()),
            'median_views': float(subset['views'].median()),
            'p75_views': float(subset['views'].quantile(0.75)),
            'p25_views': float(subset['views'].quantile(0.25)),
            'avg_engagement': float(subset['engagement_rate'].mean()),
            'video_count': len(subset),
        }

    return benchmarks
```

### Jinja2 Report Template Structure

```
templates/
  reports/
    weekly_report.html.j2       # compact, 1-2 pages
    monthly_report.html.j2      # full report with scorecards
    quarterly_report.html.j2    # leadership deck format
    _partials/
      video_scorecard.html.j2   # reusable video card component
      rag_badge.html.j2         # green/amber/red status pill
      channel_kpis.html.j2      # top-line metrics row
      recommendations.html.j2   # action items section
```

### Scheduling and Delivery

```python
# scripts/generate_weekly_report.py
# Called by launchd plist on Monday mornings (already planned in backlog.md)

import argparse
from datetime import date, timedelta
from pathlib import Path
from src.youtube_api.database import AnalyticsDatabase

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--week-offset', type=int, default=1,
                        help='1 = last week (default), 0 = current week')
    args = parser.parse_args()

    today = date.today()
    # Previous Monday
    last_monday = today - timedelta(days=today.weekday() + 7 * args.week_offset)
    last_sunday = last_monday + timedelta(days=6)

    db = AnalyticsDatabase()
    output_dir = Path('data/reports/weekly')
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = generate_weekly_report(db, last_monday, output_dir)
    print(f"Report generated: {report_path}")

    # TODO: email delivery via smtplib or sendgrid

if __name__ == '__main__':
    main()
```

### YouTube API Data Freshness Contract

```python
# Standard header for all reports — data lag is a hard constraint of the API
REPORT_HEADER_NOTE = (
    "Note: YouTube Analytics data is typically 48-72 hours delayed. "
    "This report covers {start_date} through {end_date}. "
    "Data was fetched on {generated_at}. "
    "Videos published in the last 3 days may show lower-than-final view counts."
)
```

---

## Cadence Framework

### Weekly Report (Monday morning, 5-minute read)
**Audience**: Producers, social media coordinator
**Question answered**: "Did anything go off the rails or unexpectedly well last week?"
**Format**: Email digest or Slack message with a 1-page PDF attachment
**Sections**:
1. Last week at a glance (3-4 KPI tiles: videos published, total views, net subscribers, engagement rate)
2. This week's standout (single video highlighted with 1 sentence of context)
3. Anomalies (anything >2 standard deviations from the trailing 90-day average — could be positive or negative)
4. Publishing plan reminder (what's scheduled this week, from content calendar)
5. Data freshness note

**Length target**: 150-200 words of narrative. The rest is numbers.
**Automation potential**: Fully automatable from SQLite database + YouTube API. Can be generated and emailed by launchd job.

### Monthly Report (First Tuesday of each month, 20-minute read)
**Audience**: Producers + Content leads
**Question answered**: "What content worked? What should we make more of or less of next month?"
**Format**: Shared Google Doc or PDF with interactive charts
**Sections**:
1. Executive Summary (3 bullets: top win, top miss, one strategic recommendation)
2. Channel overview (views, subscribers, watch time — with MoM and YoY trend)
3. Content mix (Shorts vs. longform: count, share of views, share of subscribers driven)
4. Video scorecards (every video published this month, with RAG status vs. benchmarks)
5. Show breakdown (per-show aggregate metrics and MoM trend)
6. Archival performers (older content currently gaining traction — content calendar opportunity)
7. Subscriber attribution (which videos/shows are driving subscriptions)
8. Cross-platform notes (Instagram, TikTok, Facebook — qualitative notes if no API integration yet)
9. Recommendations (3-5 specific, owner-assigned action items)

**Length target**: 800-1200 words of narrative. Data tables in body, full tables in appendix.
**Automation potential**: Partially automatable. Data sections fully automatable. Executive summary and recommendations require editorial input (or LLM-assisted drafting from structured data).

### Quarterly Report (End of quarter, 45-60 minute strategic review meeting)
**Audience**: Content leadership, department heads
**Question answered**: "Is our content strategy working? What should we change about our approach for the next quarter?"
**Format**: Slide deck (Google Slides or PowerPoint) with a companion data appendix
**Sections**:
1. Quarter summary (5-7 headline metrics vs. quarter goal)
2. QoQ trend analysis (3-month rolling views, subscribers, engagement — by content type)
3. Format effectiveness review (how did each format — Shorts, longform, archival recuts — perform?)
4. Show performance review (which shows grew, which declined, which should be greenlit or sunset)
5. Audience growth story (where are new subscribers coming from?)
6. Resource implication analysis (cost-per-view or cost-per-subscriber by format, if cost data is available)
7. Competitive context (how does PBS Wisconsin compare to similar public media channels?)
8. Strategic recommendations (3-5 high-level changes for next quarter, with rationale)
9. Proposed Q+1 content mix (draft format and show allocation recommendation)

**Length target**: Deck of 12-18 slides with a companion 3-5 page narrative memo.
**Automation potential**: Data slides fully automatable. Strategic narrative requires human authorship. The data appendix can be generated automatically.

---

## Gotchas & Anti-Patterns

1. **Reporting raw YouTube Studio view counts without clarifying the methodology.** YouTube changed its view-counting methodology for Shorts in 2023 (engaged views vs. legacy swipe-through counts). The `view_count_methodology` field already exists in this codebase's `VideoRecord` model — use it in report headers to prevent confusion when comparing pre-2023 and post-2023 videos. Reports that mix methodologies without disclosure create false trend lines.

2. **Averaging engagement rates across Shorts and longform.** A channel average engagement rate of 3% is meaningless if Shorts average 8% and longform average 1%. Always segment before averaging. This is a particularly sharp problem for PBS Wisconsin, which produces both formats.

3. **Reporting a single "best performing" video without specifying the metric.** Best by views? By engagement rate? By subscribers gained? By views-per-day velocity? Each produces a different winner and points toward a different production decision. Reports should either state the metric or use a composite score.

4. **Publishing reports without a data-as-of date.** YouTube Analytics data has a 48-72 hour lag. A Monday morning report on "last week" may be showing incomplete data for Friday and Saturday. This creates confusion when numbers change after the report is sent. Always include a data freshness note.

5. **Treating Shorts publishing velocity and longform publishing velocity as equivalent.** Publishing 10 Shorts a month is not comparable to publishing 10 longform episodes a month in terms of production effort. Reports that aggregate "videos published" without segmentation by format hide significant resource implications.

6. **Making the report longer as more data becomes available.** Report length should be determined by the audience's available reading time, not by the quantity of data available. As the database grows, resist the temptation to add more tables. Instead, move detail to appendices.

7. **Lacking a consistent comparison period.** Some months have 4 publishing weeks, some have 5. Comparing raw monthly totals without normalizing for publishing volume produces false month-over-month swings. Use "per video" metrics (avg views per video published) as the primary MoM comparison, not aggregate totals.

8. **Designing reports without a feedback loop.** Reports that producers never reference because they don't reflect what producers need to know are wasted effort. Build a short feedback mechanism into the first three monthly reports: a 3-question form asking producers which section they found most and least useful.

9. **Conflating Shorts on YouTube with Reels on Instagram.** Distribution algorithms differ dramatically. A Short that performs well on YouTube may perform poorly as a Reel (or vice versa). Cross-platform Shorts reports require platform-specific sections, not a combined view count.

10. **Omitting the "why" hypothesis for underperformers.** A bottom-performer section that only lists the numbers without any editorial hypothesis is demotivating and not actionable. Even a simple "possible cause: low thumbnail contrast" is more useful than a row of red numbers.

---

## PBS Wisconsin-Specific Implementation Notes

Given the codebase's existing data models and the context of 5-20 Shorts published per month across four platforms:

- The SQLite database already stores `is_short`, `content_type`, `show_name`, `views_per_day`, and `engagement_rate` — all the fields needed to generate video scorecards without additional API calls.
- The `get_archival_videos()` method returns archival content sorted by `views_per_day` — this is exactly the archival performers section of the monthly report.
- The `get_show_summary()` method provides the show breakdown section.
- The `get_shorts_vs_longform()` method provides the content mix section.
- The most significant data gap is average view duration (retention rate) — this requires a separate YouTube Analytics API call per video and is quota-intensive (200 calls/day limit). For the report, either estimate from engaged_views when available, or report retention as an "available in Quarterly" metric only.
- For the weekly report, the launchd automation job already planned in `backlog.md` is the right delivery mechanism.
- The recommended first report to automate is the monthly, not the weekly — monthly reports are more durable (a broken weekly email is felt immediately; a broken monthly is discovered gradually), and monthly automation validates the report structure before committing to weekly cadence.

---

## Sources & Further Reading

*Note: WebSearch and WebFetch were not available during this research session. The following sources are drawn from practitioner knowledge current through August 2025. URLs are provided for reference but were not fetched during this session.*

- **Chartbeat for Newsrooms**: https://chartbeat.com/publishing-industry/ — Publisher analytics documentation and editorial report design guides
- **Parse.ly Content Analytics**: https://www.parse.ly/resources/ — Monthly content report format and engaged-time methodology
- **Newswhip Analytics**: https://www.newswhip.com/resources/ — Social media editorial briefing format; Spike Report model
- **Whatagraph YouTube Report Template**: https://whatagraph.com/templates/youtube-report-template — Drag-and-drop template with sections documented above
- **AgencyAnalytics Report Templates**: https://agencyanalytics.com/blog/social-media-report-template — Monthly social media report template with RAG status
- **Looker Studio YouTube Template Gallery**: https://lookerstudio.google.com/gallery — Community templates for YouTube channel and video reporting
- **Supermetrics YouTube Templates**: https://supermetrics.com/templates/youtube — Google Sheets-based automated YouTube report templates
- **Shorenstein Center / Lenfest Institute**: https://www.lenfestinstitute.org/local-journalism/ — Public media analytics and performance measurement frameworks (NPR, WNYC case studies)
- **Buffer State of Social 2024**: https://buffer.com/state-of-social-media — Annual report modeling narrative-forward data presentation
- **YouTube Creator Academy — Analytics**: https://creatoracademy.youtube.com/page/lesson/analytics — YouTube's own guidance on which metrics matter for Shorts vs. longform
- **Tubular Labs (media analytics)**: https://tubularlabs.com/ — Enterprise-tier YouTube analytics used by PBS, NPR; competitive benchmarking data
- **Content Marketing Institute — Annual Report Design**: https://contentmarketinginstitute.com/resources/ — Research on narrative vs. data-forward report preferences by audience type
- **DashThis Report Templates**: https://dashthis.com/templates/ — Scheduling and delivery patterns for automated social media reports
- **papermill (Jupyter parameterization)**: https://papermill.readthedocs.io/ — Programmatic notebook report generation from scheduled scripts
- **Meta Content Library (CrowdTangle successor)**: https://contentlibrary.meta.com/ — Research-only access; documents the shift away from creator-facing cross-platform analytics

---

## Recommended for The Library

1. **Whatagraph YouTube Report Template** (https://whatagraph.com/templates/youtube-report-template) — The most complete and practitioner-tested YouTube-specific report template available publicly. Sections map directly onto the data models in this codebase.

2. **AgencyAnalytics — "How to Write a Social Media Report"** (https://agencyanalytics.com/blog/social-media-report) — Best public documentation of the standard agency report structure, including the RAG status / KPIs-vs-goals pattern and the "Next Steps with owners and dates" section.

3. **Lenfest Institute — Audience Analytics for Newsrooms** (https://www.lenfestinstitute.org/local-journalism/) — Public media-specific context for performance measurement. Covers the "mission alignment" dimension absent from commercial tools. Most directly applicable to PBS Wisconsin's editorial values.

4. **papermill documentation** (https://papermill.readthedocs.io/) — Parameterized Jupyter notebook report generation. The cleanest approach for automating the monthly report in a Python-native environment without building a full web renderer. Compatible with the existing Pandas/SQLAlchemy stack in this codebase.

5. **YouTube Creator Academy — Understanding Your Analytics** (https://creatoracademy.youtube.com/) — YouTube's own explanations of what each metric means and how it should inform editorial decisions. Useful as a reference for writing the "so what?" layer of report recommendations.
