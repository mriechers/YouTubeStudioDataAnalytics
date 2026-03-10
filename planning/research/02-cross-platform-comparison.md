# Cross-Platform Comparison Visualizations — Research Report

## Summary

Publishing shortform video to YouTube Shorts, Instagram Reels, TikTok, and Facebook Reels creates a fundamental measurement problem: each platform counts "views" using different thresholds and methodologies, making raw number comparison misleading or outright invalid. The industry has converged on two practical strategies — engagement-rate normalization (converting all platforms to interactions-per-view as a percentage) and indexed scoring (expressing each platform's performance relative to that platform's own historical baseline for the same account). Commercial tools like Dash Hudson, Tubular Labs, and Sprout Social use a combination of platform-coded visual encoding (color or icon per platform), small-multiple layouts with platform-native metric labels, and optional "normalized score" overlays to let analysts compare apples to apples without erasing platform-specific context. Content-level cross-platform tracking remains partially manual for small publishers (5–20 Shorts/month), but can be reliably implemented via publish-date + title-similarity matching stored in a lightweight linkage table, making it compatible with the SQLAlchemy/SQLite stack already in this codebase. The most effective visualization primitives for this problem are indexed bar charts with platform annotations, radar/spider charts for multi-metric profiles of a single piece of content across platforms, and scatter plots that encode platform as color with engagement rate on one axis and reach on the other.

---

## Key Findings

1. **"Views" are not comparable across platforms.** YouTube counts any playback initiation as a view. TikTok counts a view when the video begins playing (functionally identical to YouTube). Instagram counts "plays" (same threshold) but surfaces "Accounts Reached" (unique accounts) as its primary distribution metric. Facebook's standard is "3-second video views" — a video must play for at least 3 continuous seconds to register. This means the same video posted to all four platforms will show materially different view counts even if identical numbers of people saw it. Any cross-platform dashboard that sums or averages raw views is arithmetically invalid.

2. **Engagement rate is the most defensible cross-platform metric.** Engagement rate — defined as (likes + comments + shares) / views × 100 — has a consistent conceptual meaning across all four platforms even though the denominator varies by platform methodology. Industry benchmarks from Rival IQ (2024 Social Media Industry Benchmark Report) show median engagement rates differ significantly by platform: Instagram Reels ~0.47%, TikTok ~2.63%, Facebook ~0.07%, YouTube Shorts ~3.5%. Publishing the raw rate per platform alongside the platform-specific median lets PBS Wisconsin answer "is this good for THIS platform" rather than making invalid cross-platform comparisons of raw rates.

3. **Indexed scoring is the standard normalization strategy in commercial tools.** Tools like Tubular Labs and Dash Hudson compute a "performance index": (content metric / account average for that platform) × 100. A score of 100 = average for your own account on that platform; 150 = 50% above your average. This makes cross-platform comparison meaningful because it answers "how did this piece of content perform relative to your norms on each platform" rather than "which platform had more views." The formula is scale-invariant and works even with small samples (n >= 5 per platform).

4. **Small-multiple layout with platform-coded color is the dominant dashboard pattern.** Virtually all cross-platform tools (Sprout Social, Hootsuite Insights, Later, Metricool) use a grid of platform-specific panels with shared time axes rather than a single merged chart. Each cell displays platform-native metrics with platform-native labels ("Plays" for Instagram, "Views" for TikTok and YouTube, "3-sec views" for Facebook). A summary row or aggregated "across all platforms" panel appears at the top using indexed or normalized values only.

5. **Content-level linking (same video, multiple platforms) is mostly manual at small scale.** At 5–20 Shorts/month, a content ID linkage table (`cross_platform_posts` with `canonical_content_id`, platform, platform_video_id) with a 48-hour publish window and fuzzy title matching is sufficient. Tools like Dash Hudson and Sprout Social offer this as a paid feature called "cross-channel content tagging" or "content sets." For PBS Wisconsin's volume, a simple SQLite join table and a manual title-linking workflow accomplishes the same goal without vendor lock-in.

6. **Watch time / completion rate is more platform-neutral than views.** YouTube's average view duration and TikTok's average watch time per video are computed on the same basis (total watch time / number of plays). Instagram and Facebook also provide average play time. Completion rate (average watch time / video duration × 100) is arguably the most platform-neutral performance signal for shortform content, provided video duration is controlled. For variable-length content, use absolute average watch time (seconds) rather than completion percentage to avoid confounding length effects.

7. **Radar/spider charts work well for multi-platform content profiles but degrade with more than 6 axes.** For a single piece of content, a radar chart with axes for Reach, Engagement Rate, Completion Rate, Share Rate, and Click-Through (where available) across platforms gives an immediate visual summary of how the content performed on each platform relative to that platform's baseline. The limitation: radar charts require all axes to be on normalized scales (0–100 or percentile rank). Raw values on mixed-scale axes produce misleading polygon shapes dominated by whichever metric has the largest absolute value.

8. **Platform-specific context labels are critical for avoiding misleading comparisons.** The single biggest anti-pattern in cross-platform dashboards is presenting raw metrics from different platforms in the same chart without labeling the counting methodology. A tooltip or annotation explaining "YouTube counts any playback; Facebook counts 3+ seconds" directly on the visualization is standard practice in tools targeting sophisticated users (Brandwatch, Tubular Labs). Note: the `VideoTable` model in this codebase already has a `view_count_methodology` column — this field should be extended to the cross-platform data model and surfaced in tooltips.

9. **TikTok API access is a structural risk for smaller publishers.** TikTok's Research API requires academic/institutional approval. The Display API (for creators) provides limited analytics. The Business Content API has significant approval friction for organizations under 100K followers. As of 2024–2025, potential US regulatory disruptions added further uncertainty. Any cross-platform implementation should treat TikTok data as an optional, gracefully-degrading component rather than a required data source.

10. **Tubular Labs' V30 metric is the best-established cross-platform normalization concept.** V30 (views in first 30 days of publication) corrects for the fact that older content accumulates views at different rates on different platforms. The concept is directly adaptable: adding a `views_first_30d` column to the cross-platform data model creates a time-normalized comparison metric that eliminates recency bias without requiring z-score computation.

---

## Tools & Technologies

### Commercial Cross-Platform Analytics Tools

- **Dash Hudson** (dashhudson.com): Covers Instagram, TikTok, YouTube, Pinterest, Facebook. Uses "Effectiveness Score" as a normalized index combining engagement rate, reach, and save rate against the account's historical baseline. Provides "Visual Insights" — side-by-side content performance with platform color-coding. Layout: platform-specific tabs at top with an "All Channels" aggregate view. Strong for visual content publishers. Pricing targets mid-to-enterprise brands.

- **Tubular Labs** (tubularlabs.com): Video-first cross-platform tool covering YouTube, Facebook, Instagram, TikTok, Twitter/X. Signature metric is "V30" — views in first 30 days, which normalizes for recency bias. Unique capability: tracks content across platforms using video fingerprinting (perceptual hash matching), enabling automatic cross-platform content linking without manual tagging. Primarily for enterprise video publishers and agencies.

- **Sprout Social** (sproutsocial.com): Broad social media management + analytics. Cross-channel reporting uses "post impressions" as a unified metric (noting platform differences in footnotes). Dashboard layout: platform tabs with a cross-channel summary tab. Cross-channel summary uses indexed values rather than raw. Strong on scheduling + analytics combination. The most widely deployed pattern for general social media teams.

- **Brandwatch** (brandwatch.com): Primarily social listening + analytics. Cross-platform analytics show engagement metrics in a unified timeline with platform as a filter. Good for trend detection and audience sentiment; less strong on content-level performance tracking. Acquired Falcon.io in 2021, adding publishing and reporting capabilities.

- **Hootsuite** (hootsuite.com): Analytics module offers side-by-side platform comparison with metric selector. "Best time to post" analysis is cross-platform. Weaker on video-specific metrics (completion rate, watch time) than Dash Hudson or Tubular. The go-to reference for the standard "social media report" format that most practitioners expect.

- **Metricool** (metricool.com): Mid-market, strong on YouTube Shorts + Instagram Reels cross-comparison. Shows completion rate alongside views. "Network Comparison" view displays platform rows with equivalent metrics side-by-side. Explicitly labels methodology differences (Instagram "Plays" vs. YouTube "Views") in tooltips. More affordable than Dash Hudson; popular with independent creators and small teams. Publishes quarterly benchmark data from their user base segmented by follower count.

- **Later** (later.com): Visual-first scheduling + analytics. Cross-platform comparison focuses on reach and engagement rate. Separates Stories analytics from Reels/feed posts. Good for visual content teams managing multiple platforms from one interface.

- **Rival IQ** (rivaliq.com): Best-in-class for benchmarking and competitive analysis. Annual Social Media Industry Benchmark Reports by vertical are the most widely cited free source for platform engagement rate baselines. Computes engagement rate per platform and contextualizes against industry medians. Radar chart outputs appear in their benchmark reports.

### Visualization Libraries

- **Plotly / Plotly Express** (Python): Already used in this codebase (`src/analytics/visualizations.py`). Supports radar charts (`go.Scatterpolar`), small multiples via `make_subplots(shared_xaxes=True)`, parallel coordinates (`go.Parcoords`), and faceted scatter plots. Platform-coded color encoding is straightforward with `color_discrete_map`. No new dependency required for Streamlit implementation.

- **Recharts** (React/TypeScript): Used in the existing web frontend (`web/src/`). `ComposedChart` supports bar + line overlays on the same axes. `RadarChart` component supports the spider-chart pattern. `ResponsiveContainer` enables small-multiple grid layouts. See implementation pattern in Section 4b below.

- **Apache ECharts** (JavaScript/TypeScript): Excellent radar chart and parallel coordinates support. Used by several analytics SaaS products. More expressive than Recharts for multi-dimensional data but adds a dependency. Not currently in the project stack.

- **D3.js**: Gold standard for custom cross-platform visualizations, especially parallel coordinates and connected dot plots. Steep learning curve; overkill for internal dashboards.

- **Vega-Lite**: Declarative grammar well-suited for small-multiple faceted charts. Good for rapid prototyping. Not currently in the project stack.

### Normalization Approaches

- **Z-score normalization**: `(value - mean) / std_dev` across platform samples. Produces dimensionless scores comparable across platforms. Problem: sensitive to outliers; requires a meaningful sample (n > 20 per platform for stable estimates).

- **Percentile rank**: `scipy.stats.percentileofscore(platform_values, this_value)`. Converts raw metric to 0–100 percentile within platform history. Robust and interpretable. Works reasonably with n >= 5 per platform for directional ranking, though precision improves significantly at n >= 20.

- **Min-max normalization**: `(value - min) / (max - min)`. Produces 0–1 scale. Problem: a single extreme outlier compresses all other values toward 0. Not recommended for small catalogs (5–20 posts/month).

- **Indexed scoring (account baseline)**: `(value / account_30d_average_for_platform) × 100`. Most interpretable for practitioners; directly used by Dash Hudson and Tubular Labs. Scale-invariant, works even with small samples (n >= 3 for a usable baseline), and the formula is easy to explain to non-technical stakeholders ("this post did 1.5x your average on Instagram").

- **V30 windowed comparison**: `views_in_first_30d` per platform, compared across platforms. Eliminates recency confound without normalization math. Requires tracking a `published_at` timestamp per platform post and computing the 30-day window per-post.

---

## Examples in the Wild

### 1. Tubular Labs — V30 Cross-Platform Benchmark

Tubular Labs' signature metric is "V30" — views in the first 30 days of publication. By capping the window, V30 corrects for the fact that older content accumulates views over time at different rates on different platforms (YouTube content tends to have longer tails than TikTok content). Their dashboard shows V30 as horizontal bars for the same creator across YouTube, Facebook, and Instagram, with platform icons color-coded (red for YouTube, blue for Facebook, purple for Instagram). A "creator rank" column shows percentile within a peer set of similar publishers. This is the most technically principled example of cross-platform normalization in video analytics. See: tubularlabs.com and coverage in Digiday's creator economy reporting (2023–2024).

### 2. Dash Hudson — Effectiveness Score + Small Multiples

Dash Hudson's post-analytics views show individual pieces of content in a grid, with platform as a filter or color dimension. Their "Effectiveness Score" is a proprietary weighted index combining engagement rate, reach, and save rate, normalized to the account's historical baseline on each platform. The layout uses platform-specific tabs at the top with an "All Channels" aggregate view available. Individual post cards show platform icon, raw views (with methodology footnote), and Effectiveness Score side-by-side. This is the textbook example of showing both native metrics and a normalized score simultaneously — letting analysts see both the raw signal ("2,300 plays on Instagram") and the contextualized signal ("1.4x your average on Instagram").

### 3. Sprout Social — Cross-Channel Report Tab

Sprout Social's "Cross-Channel" report shows a time-series line chart with one line per platform (color-coded), a metric selector for impressions/engagement/follower growth, and a period-over-period comparison table below. The platform lines use different line styles (solid/dashed) in addition to color for colorblindness accessibility. The comparison table footnotes each platform's metric definition. This is the most widely-deployed pattern for social media managers because it maps to how platform managers already think about their data. See: sproutsocial.com/features/reports/.

### 4. Metricool — YouTube Shorts vs. Reels Comparison

Metricool's "Network Comparison" view for shortform content shows YouTube Shorts and Instagram Reels side by side with: Views, Reach, Likes, Comments, Shares, and Average Watch Time (seconds). The key design decision: they display Average Watch Time in absolute seconds rather than completion percentage, which sidesteps the video-length confound. Their tooltip explicitly notes "Instagram 'Plays' vs. YouTube 'Views'" methodology differences inline. Published product screenshots available on their blog with benchmark data from their creator user base. See: metricool.com/blog/youtube-shorts-vs-instagram-reels/.

### 5. Rival IQ — Industry Benchmark Radar Charts

Rival IQ's annual benchmark reports use radar/spider charts to show a brand's engagement rate profile across platforms vs. industry median. Six axes (one per platform/content type): Instagram Feed, Instagram Reels, Facebook, Twitter/X, TikTok, YouTube. Each axis is scaled to a fixed range (e.g., 0–5% engagement rate). Brand score and industry median appear as two overlapping filled polygons in contrasting colors. This makes it immediately visible where a brand over- or under-performs relative to peers on each platform. The 2024 Social Media Industry Benchmark Report is freely downloadable without account registration and is the most-cited source for platform engagement rate benchmarks. See: rivaliq.com/resources/social-media-industry-benchmark-report/.

---

## Code Patterns & Implementation Notes

### 1. Platform Data Model

For PBS Wisconsin's use case, a lightweight extension to the existing `VideoRecord` model is sufficient. This model mirrors the `view_count_methodology` field already present in `VideoTable` in `src/youtube_api/database.py`:

```python
# Extension to src/youtube_api/models.py
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Platform(str, Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"

class CrossPlatformPost(BaseModel):
    """Links a canonical piece of content across platforms."""
    canonical_content_id: str       # e.g., "shorts-2024-wisconsin-life-ep12"
    platform: Platform
    platform_video_id: str          # native ID on that platform
    published_at: datetime
    title: str
    duration_seconds: int
    # Raw platform-native metrics (labeled with methodology)
    raw_views: int = 0              # YouTube: any play; TikTok: any play;
                                    # Instagram: plays; Facebook: 3-sec views
    reach: Optional[int] = None     # unique accounts (Instagram/Facebook only)
    likes: int = 0
    comments: int = 0
    shares: int = 0
    avg_watch_time_seconds: float = 0.0
    view_methodology: str = ""      # e.g., "3-second threshold (Facebook)"
    views_first_30d: Optional[int] = None   # V30 metric for time-normalized comparison

    @property
    def completion_rate(self) -> Optional[float]:
        """Completion rate as 0-100 percentage. Requires avg_watch_time_seconds."""
        if self.duration_seconds == 0:
            return None
        return (self.avg_watch_time_seconds / self.duration_seconds) * 100

    @property
    def engagement_rate(self) -> float:
        """(likes + comments + shares) / raw_views * 100."""
        if self.raw_views == 0:
            return 0.0
        return ((self.likes + self.comments + self.shares) / self.raw_views) * 100
```

### 2. Normalization Functions

```python
import numpy as np
import pandas as pd
from scipy import stats

def compute_indexed_score(
    value: float,
    platform_history: list[float],
    window_days: int = 90
) -> float:
    """
    Indexed score: performance relative to account's own baseline.
    100 = average; 150 = 50% above average.
    This is the Dash Hudson / Tubular Labs approach.
    Works with n >= 3 for a directional baseline.
    """
    if not platform_history or np.mean(platform_history) == 0:
        return 100.0
    return (value / np.mean(platform_history)) * 100


def compute_percentile_rank(
    value: float,
    platform_history: list[float]
) -> float:
    """
    Percentile rank within platform history.
    Returns 0-100. Directionally useful at n >= 5; reliable at n >= 20.
    """
    return float(stats.percentileofscore(platform_history, value, kind='rank'))


def normalize_engagement_for_comparison(
    posts_df: pd.DataFrame,
    platform_col: str = "platform",
    engagement_col: str = "engagement_rate"
) -> pd.DataFrame:
    """
    Z-score normalize engagement rate within each platform group.
    Allows comparing relative performance across platforms on the same axis.
    Requires n >= 5 posts per platform for meaningful results.
    Adds a 'sample_size_warning' column when n < 10.
    """
    df = posts_df.copy()
    df["engagement_zscore"] = df.groupby(platform_col)[engagement_col].transform(
        lambda x: stats.zscore(x, ddof=1) if len(x) > 1 else pd.Series([0.0] * len(x), index=x.index)
    )
    # Flag small samples for UI warning
    platform_counts = df.groupby(platform_col)[engagement_col].transform("count")
    df["sample_size_warning"] = platform_counts < 10
    return df


def compute_cross_platform_score(
    post: dict,
    platform_baselines: dict[str, dict[str, float]]
) -> dict[str, float]:
    """
    Compute indexed scores for a post across all available metrics.

    platform_baselines = {
        "youtube": {"engagement_rate": 2.1, "completion_rate": 45.0, ...},
        "instagram": {"engagement_rate": 0.8, "completion_rate": 38.0, ...},
    }
    Returns: {"engagement_index": 142.0, "completion_index": 98.0}
    """
    platform = post["platform"]
    baseline = platform_baselines.get(platform, {})
    scores = {}
    for metric, baseline_val in baseline.items():
        post_val = post.get(metric, 0.0)
        if baseline_val > 0:
            scores[f"{metric}_index"] = (post_val / baseline_val) * 100
    return scores
```

### 3. SQLite Linkage Table for Content Tracking

This extends the existing SQLAlchemy setup in `src/youtube_api/database.py`. Add alongside `VideoTable` and `DailyStatsTable`:

```python
# Add to src/youtube_api/database.py as a new SQLAlchemy model

class CrossPlatformPostTable(Base):
    """Cross-platform content linkage. One row per (canonical_content_id, platform) pair."""
    __tablename__ = 'cross_platform_posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    canonical_content_id = Column(String, nullable=False)   # manually assigned or auto-matched
    platform = Column(String, nullable=False)               # 'youtube', 'instagram', 'tiktok', 'facebook'
    platform_video_id = Column(String, nullable=False)
    title = Column(String)
    published_at = Column(DateTime)
    duration_seconds = Column(Integer)
    raw_views = Column(Integer, default=0)
    reach = Column(Integer)                                 # NULL if platform doesn't provide
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    avg_watch_time_seconds = Column(Float, default=0.0)
    engagement_rate = Column(Float, default=0.0)
    completion_rate = Column(Float)                         # NULL if watch time not available
    views_first_30d = Column(Integer)                       # V30: views in first 30 days
    view_methodology = Column(String)                       # human-readable counting note
    fetched_at = Column(DateTime, default=func.now())

    __table_args__ = (
        # Prevent duplicate (platform, platform_video_id) pairs
        Index('idx_xplatform_canonical', 'canonical_content_id'),
        Index('idx_xplatform_published', 'published_at'),
        Index('idx_xplatform_platform', 'platform'),
    )
```

Raw SQL equivalent for reference or manual migration:

```sql
CREATE TABLE IF NOT EXISTS cross_platform_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_content_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    platform_video_id TEXT NOT NULL,
    title TEXT,
    published_at DATETIME,
    duration_seconds INTEGER,
    raw_views INTEGER DEFAULT 0,
    reach INTEGER,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    avg_watch_time_seconds REAL DEFAULT 0.0,
    engagement_rate REAL DEFAULT 0.0,
    completion_rate REAL,
    views_first_30d INTEGER,
    view_methodology TEXT,
    fetched_at DATETIME,
    UNIQUE (platform, platform_video_id)
);

CREATE INDEX IF NOT EXISTS idx_cross_platform_canonical
    ON cross_platform_posts(canonical_content_id);
CREATE INDEX IF NOT EXISTS idx_cross_platform_published
    ON cross_platform_posts(published_at);
```

### 4a. Small-Multiple Chart Pattern (Plotly — Streamlit)

Recommended implementation for Streamlit: one subplot per platform, shared time axis, platform-native metric labels.

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

PLATFORM_COLORS = {
    "youtube": "#FF0000",
    "instagram": "#E1306C",
    "tiktok": "#69C9D0",    # TikTok teal (use black for dark mode)
    "facebook": "#1877F2",
}

PLATFORM_VIEW_LABELS = {
    "youtube": "Views (any play)",
    "instagram": "Plays",
    "tiktok": "Views (any play)",
    "facebook": "Views (3-sec threshold)",
}

def create_cross_platform_small_multiples(
    posts_df: pd.DataFrame,
    metric: str = "raw_views",
    date_col: str = "published_at"
) -> go.Figure:
    """
    Small-multiple bar chart: one subplot per platform, shared time axis.
    Each subplot uses the platform-native metric label.
    """
    platforms = posts_df["platform"].unique()
    n = len(platforms)

    fig = make_subplots(
        rows=n, cols=1,
        shared_xaxes=True,
        subplot_titles=[
            f"{p.title()} — {PLATFORM_VIEW_LABELS.get(p, metric)}"
            for p in platforms
        ],
        vertical_spacing=0.08,
    )

    for i, platform in enumerate(platforms, start=1):
        df_p = posts_df[posts_df["platform"] == platform].sort_values(date_col)
        fig.add_trace(
            go.Bar(
                x=df_p[date_col],
                y=df_p[metric],
                name=platform.title(),
                marker_color=PLATFORM_COLORS.get(platform, "#888888"),
                hovertemplate=(
                    f"<b>{platform.title()}</b><br>"
                    f"Date: %{{x}}<br>"
                    f"{PLATFORM_VIEW_LABELS.get(platform, metric)}: %{{y:,}}<extra></extra>"
                ),
            ),
            row=i, col=1,
        )

    fig.update_layout(
        title="Cross-Platform Performance — Raw Reach by Platform",
        showlegend=False,
        height=220 * n,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
```

### 4b. Small-Multiple Chart Pattern (Recharts — React/TypeScript Web Frontend)

The existing web frontend (`web/src/`) uses Recharts. This pattern renders one `BarChart` per platform in a responsive grid, matching the Plotly small-multiples layout:

```tsx
// web/src/components/CrossPlatformSmallMultiples.tsx
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from "recharts";

const PLATFORM_COLORS: Record<string, string> = {
  youtube: "#FF0000",
  instagram: "#E1306C",
  tiktok: "#69C9D0",
  facebook: "#1877F2",
};

const PLATFORM_VIEW_LABELS: Record<string, string> = {
  youtube: "Views (any play)",
  instagram: "Plays",
  tiktok: "Views (any play)",
  facebook: "Views (3-sec threshold)",
};

interface PlatformPost {
  published_at: string;
  raw_views: number;
  platform: string;
  canonical_content_id?: string;
}

interface Props {
  data: PlatformPost[];
}

export function CrossPlatformSmallMultiples({ data }: Props) {
  const platforms = [...new Set(data.map((d) => d.platform))];

  return (
    <div className="grid gap-6">
      {platforms.map((platform) => {
        const platformData = data
          .filter((d) => d.platform === platform)
          .sort((a, b) => a.published_at.localeCompare(b.published_at));

        return (
          <div key={platform}>
            <h3 className="text-sm font-medium text-muted-foreground mb-2">
              {platform.charAt(0).toUpperCase() + platform.slice(1)}
              {" — "}
              <span className="italic">
                {PLATFORM_VIEW_LABELS[platform] ?? "Views"}
              </span>
            </h3>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={platformData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis
                  dataKey="published_at"
                  tick={{ fontSize: 11 }}
                  tickFormatter={(v) => v.slice(0, 10)}
                />
                <YAxis tick={{ fontSize: 11 }} width={60} />
                <Tooltip
                  formatter={(value: number) => [
                    value.toLocaleString(),
                    PLATFORM_VIEW_LABELS[platform] ?? "Views",
                  ]}
                  labelFormatter={(label) => `Published: ${label.slice(0, 10)}`}
                />
                <Bar
                  dataKey="raw_views"
                  fill={PLATFORM_COLORS[platform] ?? "#888"}
                  radius={[3, 3, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        );
      })}
    </div>
  );
}
```

### 5. Radar Chart for Single-Content Multi-Platform Profile (Plotly)

```python
def create_content_radar_chart(
    canonical_content_id: str,
    posts_df: pd.DataFrame,
    platform_baselines: dict[str, dict]
) -> go.Figure:
    """
    Radar chart showing a single piece of content's performance
    across platforms on normalized (indexed) axes.
    Axes: Engagement Rate Index, Completion Rate Index, Share Rate Index.
    All axes are scaled to account baseline = 100.
    """
    content = posts_df[posts_df["canonical_content_id"] == canonical_content_id]
    axes = ["engagement_rate", "completion_rate", "shares"]
    axis_labels = ["Engagement Rate", "Completion Rate", "Share Rate"]

    fig = go.Figure()

    for _, row in content.iterrows():
        platform = row["platform"]
        baseline = platform_baselines.get(platform, {})
        # Compute indexed scores (100 = platform average)
        r_vals = []
        for ax in axes:
            val = row.get(ax, 0.0) or 0.0
            base = baseline.get(ax, 1.0) or 1.0
            r_vals.append(min((val / base) * 100, 300))  # cap at 300 to prevent chart collapse

        # Close the polygon
        r_vals_closed = r_vals + [r_vals[0]]
        theta_closed = axis_labels + [axis_labels[0]]

        fig.add_trace(go.Scatterpolar(
            r=r_vals_closed,
            theta=theta_closed,
            fill="toself",
            name=platform.title(),
            line_color=PLATFORM_COLORS.get(platform, "#888888"),
            opacity=0.6,
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 200],
                ticktext=["0", "50", "Avg (100)", "150", "200"],
                tickvals=[0, 50, 100, 150, 200],
            )
        ),
        title=(
            f"Content Performance Profile — Indexed to Platform Average<br>"
            f"<sup>{canonical_content_id}</sup>"
        ),
        showlegend=True,
    )
    return fig
```

### 6. Engagement Rate Benchmark Table

Industry benchmarks from Rival IQ (2024) for shortform content. These values should be stored as constants in the codebase and updated when Rival IQ publishes their annual report (typically Q1 each year):

```python
# Rival IQ 2024 Social Media Industry Benchmark medians (all industries)
# Source: rivaliq.com/resources/social-media-industry-benchmark-report/
PLATFORM_BENCHMARKS_2024 = {
    "youtube_shorts": {
        "engagement_rate": 0.035,    # 3.5% median for YouTube Shorts
        "source": "Rival IQ 2024",
        "methodology": "Interactions / Views"
    },
    "instagram_reels": {
        "engagement_rate": 0.0047,   # 0.47% median for Instagram Reels
        "source": "Rival IQ 2024",
        "methodology": "Interactions / Follower count"
    },
    "tiktok": {
        "engagement_rate": 0.0263,   # 2.63% median for TikTok
        "source": "Rival IQ 2024",
        "methodology": "Interactions / Views"
    },
    "facebook_reels": {
        "engagement_rate": 0.0007,   # 0.07% median for Facebook
        "source": "Rival IQ 2024",
        "methodology": "Interactions / Reach"
    },
}

def add_benchmark_context(posts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 'vs_industry_benchmark' column: ratio of post engagement rate
    to platform industry median. 1.0 = at benchmark; 2.0 = 2x above benchmark.
    """
    df = posts_df.copy()

    def get_benchmark(row):
        key = (
            f"{row['platform']}_reels"
            if row["platform"] in ("instagram", "facebook")
            else row["platform"]
        )
        b = PLATFORM_BENCHMARKS_2024.get(key, {}).get("engagement_rate")
        if b and row.get("engagement_rate", 0) > 0:
            return row["engagement_rate"] / b
        return None

    df["vs_industry_benchmark"] = df.apply(get_benchmark, axis=1)
    return df
```

### 7. YouTube Analytics API Fields for Cross-Platform Alignment

The YouTube Analytics API (`yt-analytics.readonly` scope, already authorized in `src/youtube_api/auth.py`) returns these fields directly relevant to cross-platform comparison. Use these when fetching YouTube-side data for the `CrossPlatformPost` model:

```python
# Relevant YouTube Analytics API dimensions/metrics for cross-platform comparison
YOUTUBE_CROSSPLATFORM_METRICS = [
    "views",                    # raw_views equivalent
    "estimatedMinutesWatched",  # convert to avg_watch_time_seconds: (total / views) * 60
    "averageViewDuration",      # avg_watch_time_seconds directly (in seconds)
    "averageViewPercentage",    # completion_rate directly (as 0-100 percentage)
    "likes",
    "comments",
    "shares",
    "subscribersGained",
    # Note: 'engagedViews' is available for Shorts specifically
    # (used for monetization threshold, distinct from raw views)
]

# YouTube Shorts specifically: use 'engagedViews' as a secondary metric
# that is NOT comparable to raw views but IS relevant to monetization
# See: VideoAnalytics.engaged_views already in the database schema
```

---

## Gotchas & Anti-Patterns

1. **Summing raw views across platforms.** Never add YouTube views + TikTok views + Instagram plays + Facebook 3-sec views to get "total views." This number is arithmetically invalid and misleads stakeholders. If an aggregated reach number is required, use reach (unique accounts) where available, with a clear note that reach is also not additive across platforms (the same person may follow on multiple platforms).

2. **Using the same Y-axis scale for all platforms.** PBS Wisconsin's YouTube channel likely has an order of magnitude more views than their TikTok or Instagram accounts. A shared Y-axis will compress the smaller platforms to near-zero bars, making them appear irrelevant. Use per-platform Y-axes in small multiples, or normalize to indexed scores before any shared-axis chart.

3. **Engagement rate without clarifying the denominator.** "Engagement rate" can mean (likes + comments) / views, (likes + comments + shares) / views, (likes + comments + shares) / reach, or interactions / impressions. Each platform's native analytics dashboard uses a different formula. Define one formula for the cross-platform model and apply it consistently — regardless of what each platform's own "engagement rate" field reports.

4. **Radar charts with un-normalized axes.** If `engagement_rate` (0–5%) and `raw_views` (0–50,000) appear on the same radar chart, the polygon is visually dominated by the raw_views axis. All radar chart axes must be on the same scale (percentile rank or indexed score) before rendering.

5. **Treating completion rate as directly comparable across content lengths.** A 15-second Short with 80% completion (12 seconds watched) is very different from a 60-second Short with 80% completion (48 seconds watched). When comparing across platforms where video length varies, prefer absolute average watch time (seconds) rather than completion percentage.

6. **Ignoring publish-time differences in same-content comparison.** If the same Short is published to YouTube on Monday and TikTok on Thursday, a "first 30 days" view window is misaligned by 4 days. Any cross-platform comparison of the same content must anchor to each platform's own `published_at` timestamp and use equivalent relative windows (e.g., "views in first 7 days from publish date on each platform").

7. **Conflating "reach" and "views."** Instagram surfaces "Accounts Reached" prominently, which is a unique-user metric. YouTube and TikTok show views, which count repeat plays. These cannot be displayed in the same column without a methodology footnote. The `view_methodology` field in the `CrossPlatformPost` model exists to capture and surface this distinction.

8. **Over-engineering for 5–20 pieces of content per month.** At PBS Wisconsin's volume, a scatter plot with platform as color and a data table with platform-native labels will communicate more than a complex radar or parallel-coordinates visualization. Start with the simplest chart that answers "which posts performed above our average on each platform." Complexity should scale with data volume.

9. **Assuming TikTok API access is reliable.** TikTok's Research API requires institutional approval. The Business Content API has significant access friction for smaller publishers. As of 2024–2025, potential US regulatory disruptions introduced additional uncertainty. Design the cross-platform system so TikTok data is optional: the `platform` field should be treated as a nullable dimension, and any platform-specific view should render without errors when TikTok rows are absent.

10. **Normalizing with too small a sample.** Z-score normalization and percentile ranking require a meaningful distribution. With fewer than 10 posts on a platform, percentile ranks are unstable. For PBS Wisconsin's volume (5–20 Shorts/month), use at minimum 3 months of history before activating normalized comparison views. Display a visible "sample size: n=X" indicator when n < 10 per platform so users understand the confidence level of any normalized score.

11. **Displaying engagement rates from different denominator conventions side-by-side without annotation.** Instagram's native engagement rate uses follower count as the denominator; YouTube's uses views. If you compute engagement rate consistently across platforms (always interactions/views), this diverges from each platform's own reported engagement rate. Document your formula explicitly in the UI and consider surfacing both "your formula" and "platform-reported" values for the YouTube YouTube Studio comparison.

12. **Ignoring the `engagedViews` vs. `views` distinction for YouTube Shorts.** YouTube reports both raw `views` and `engagedViews` (views meeting the monetization threshold, approximately 10+ seconds watched or full video completion for very short Shorts). The `VideoTable` model already has `engaged_views` — ensure this distinction is not lost when building the cross-platform summary. `engagedViews` is a better proxy for "real" reach on YouTube Shorts than raw views.

---

## Sources & Further Reading

- **Rival IQ 2024 Social Media Industry Benchmark Report** — https://www.rivaliq.com/resources/social-media-industry-benchmark-report/ — The most widely cited free source for platform-specific engagement rate benchmarks by industry vertical. Freely downloadable without account registration. Updated annually in Q1; check for the 2025 edition at the same URL.

- **Tubular Labs Blog** — https://tubularlabs.com/blog/ — Explains the V30 methodology and cross-platform video fingerprinting approach. Best available public description of enterprise-grade time-windowed normalization and content-level cross-platform tracking.

- **Dash Hudson Blog — Cross-Channel Analytics** — https://dashhudson.com/blog/ — Product-focused but contains genuine methodology explanation for their Effectiveness Score and how they handle platform-native metric differences. Good primary source for the "indexed to account baseline" approach used by mid-market tools.

- **Metricool Blog — YouTube Shorts vs Instagram Reels** — https://metricool.com/youtube-shorts-vs-instagram-reels/ — Practical cross-platform comparison with real user-base data. Best example of how a mid-market tool presents cross-platform comparison with methodology transparency. Metricool publishes updated versions of this post annually with fresh benchmark data.

- **Sprout Social Insights — Cross-Channel Analytics** — https://sproutsocial.com/insights/cross-channel-analytics/ — Overview of how cross-channel reporting is structured in their tool. Reference for the dominant dashboard layout pattern used in the mid-market.

- **Hootsuite — How to Create a Social Media Report** — https://blog.hootsuite.com/social-media-report/ — Documents the standard cross-platform metrics table format expected by social media managers. Good reference for what non-technical PBS Wisconsin staff would expect to see.

- **Plotly Radar Chart documentation (Python)** — https://plotly.com/python/radar-chart/ — Implementation reference for `go.Scatterpolar`. Includes normalization examples and the polygon-closing pattern required for closed radar shapes.

- **Plotly Subplots documentation (Python)** — https://plotly.com/python/subplots/ — Implementation reference for `make_subplots` with `shared_xaxes=True`. The recommended pattern for small-multiple Streamlit layouts.

- **Facebook Business Help — Video Metrics** — https://www.facebook.com/business/help/metrics — Official documentation for the 3-second view threshold and other Facebook video metric definitions. Authoritative source for footnote/annotation copy in the dashboard.

- **YouTube Help — YouTube Shorts and Engaged Views** — https://support.google.com/youtube/answer/12470237 — Official documentation distinguishing "views" from "engaged views" for Shorts monetization. Directly relevant to the `VideoAnalytics.engaged_views` field already in the database schema.

- **Instagram Business Help — Reels Insights** — https://help.instagram.com/1265642380755493 — Official definitions for Plays vs. Reach vs. Impressions for Reels. Required reading before designing the Instagram data ingestion module.

- **TikTok for Developers — Research API** — https://developers.tiktok.com/products/research-api/ — Documents the institutional approval process for TikTok Research API access. Important for understanding why TikTok data should be treated as optional in the system architecture.

- **Recharts Documentation — RadarChart** — https://recharts.org/en-US/api/RadarChart — Component reference for implementing radar charts in the existing React/TypeScript web frontend.

- **Recharts Documentation — ComposedChart** — https://recharts.org/en-US/api/ComposedChart — Reference for the bar + line overlay pattern useful for showing raw values alongside normalized trend lines in the same chart.

---

## Recommended for The Library

These five resources have the highest signal-to-noise ratio for ongoing use when building or extending the cross-platform analytics feature:

1. **Rival IQ 2024 Social Media Industry Benchmark Report** (https://www.rivaliq.com/resources/social-media-industry-benchmark-report/) — Provides the quantitative baselines (engagement rate by platform by industry) needed to populate `PLATFORM_BENCHMARKS_2024` and the benchmark context column. Updated annually; the 2025 edition should be checked in Q1 2026.

2. **Tubular Labs documentation on V30 methodology** (https://tubularlabs.com/blog/) — The best public explanation of time-windowed cross-platform normalization. The V30 concept is directly adaptable for a `views_first_30d` tracking column in the PBS Wisconsin `cross_platform_posts` table.

3. **Plotly radar chart + subplots Python documentation** (https://plotly.com/python/radar-chart/ and https://plotly.com/python/subplots/) — Both are directly applicable to the Streamlit implementation patterns in this report. No new dependency required since Plotly is already used in the codebase.

4. **Facebook official video metric definitions** (https://www.facebook.com/business/help/metrics) — The 3-second view threshold is the most confusing methodology difference for non-technical stakeholders. Having the official source in The Library makes it easy to pull accurate annotation copy into dashboard tooltips.

5. **Metricool shortform benchmark posts** (https://metricool.com/blog/) — Metricool publishes quarterly benchmark data on Shorts vs. Reels performance from their creator user base, segmented by follower count. More granular than Rival IQ for shortform-specific benchmarks and more directly applicable to PBS Wisconsin's content type and audience scale.
