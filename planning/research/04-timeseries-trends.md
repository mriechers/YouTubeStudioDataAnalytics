# Time-Series & Trend Visualization Patterns — Research Report

## Summary

Short-form video content has a fundamentally different performance lifecycle than longform: spikes are sharper, decay is faster, and algorithmic resurfacing creates irregular secondary peaks that can arrive weeks or months after publication. Effective dashboards for this content type require more than simple line charts — they need lifecycle-normalized views, compact sparkline grids for catalog scanning, smoothed trend layers that preserve spike visibility, and cohort analysis that accounts for each video's age. The visualization patterns best suited to PBS Wisconsin's Shorts analytics are well-established in media analytics tooling, content marketing platforms, and financial time-series dashboards, and they map well onto the ECharts library already in the project's stack.

---

## Key Findings

1. **Lifecycle age-normalization is the most important technique for Shorts analytics.** Comparing raw view counts across videos published on different dates is misleading. The industry standard (used by YouTube Studio, Vidooly, and TubeBuddy) is to normalize the x-axis to "days since publish," allowing direct comparison of content at equivalent lifecycle ages. A 7-day-old Short that has 10,000 views is directly comparable to last month's Short at day 7 — raw date charts cannot reveal this.

2. **7-day rolling averages are the standard for daily video metrics; 28-day for subscriber trends.** YouTube Analytics itself uses 7-day rolling averages for channel-level daily views. The consensus in analytics tooling (Chartbeat, Social Blade, Later) is: use 7-day for volatile daily engagement metrics, 28-day for subscriber and audience retention trends, and 90-day only for strategic planning views. Rolling averages should be overlaid on top of raw daily bars, not replace them — viewers need both the noise and the signal.

3. **Sparklines in table rows are the single highest-ROI visualization upgrade for catalog views.** When a table lists 20+ Shorts, adding a 28-day sparkline in a column next to each video title gives editors an at-a-glance sense of trajectory (growing, flat, decaying, spiking) without requiring a click-through to a detail view. This is the pattern used by Metricool, Hootsuite Analytics, and Supermetrics dashboards.

4. **Cohort analysis for content should use "publish week" as the cohort key, not calendar week.** Tools like ContentStudio and Sprout Social segment content by the week it was published, then compare all videos in that cohort at equivalent lifecycle ages. For PBS Wisconsin publishing 5-20 Shorts per month, a monthly cohort cadence (January Shorts vs. February Shorts at days 1, 7, 14, 30) is more meaningful than weekly.

5. **Statistical anomaly detection with simple z-score thresholds (±2 standard deviations) is sufficient for small-catalog analytics.** Complex ML-based anomaly detection (Facebook Prophet, AWS Lookout) is over-engineered for a catalog of 5-20 Shorts/month. A 28-day rolling mean and standard deviation allows flagging videos that are performing unusually well or poorly with a simple color-coded indicator, which is the approach used by Chartbeat and ContentSquare for editorial dashboards.

6. **Calendar heatmaps are the clearest way to visualize seasonal and publication cadence patterns.** GitHub-style calendar heatmaps (each square = one day, color intensity = views) reveal both seasonal demand (Wisconsin events, seasons) and publishing cadence gaps immediately. This pattern appears in YouTube Studio's own date-range selectors and in tools like Social Blade.

7. **ECharts (already in the project stack) supports all required visualization types natively**, including sparklines via `type: 'line'` with `symbol: 'none'` and minimal styling, calendar heatmaps via `type: 'heatmap'` with a `calendar` coordinate system, and lifecycle curves via normalized scatter/line charts. No additional charting library is needed.

---

## Tools & Technologies

### Already in the Stack

**Apache ECharts 6 / echarts-for-react 3** (project dependency)
- Supports: line, bar, scatter, heatmap, candlestick, custom series
- Calendar heatmap: native `calendar` coordinate system
- Sparklines: line series with `symbol: 'none'`, no axes, `silent: true`
- Lifecycle curves: scatter/line with custom x-axis (days since publish)
- Rolling averages: computed server-side in Python/pandas, rendered as a second line series
- Anomaly markers: `markPoint` and `markArea` for highlighting outliers
- Reference: https://echarts.apache.org/en/option.html

**Pandas** (project dependency, Python analytics layer)
- `DataFrame.rolling(window=7).mean()` — 7-day rolling average
- `DataFrame.rolling(window=28).mean()` — 28-day rolling average
- `DataFrame.resample('W').sum()` — weekly aggregation for cohort views
- `(x - x.mean()) / x.std()` — z-score normalization for anomaly detection

### Alternative/Complementary Libraries (Not Currently in Stack)

**Observable Plot** (MIT, JavaScript)
- Best for: lifecycle curves, cohort grids, small-multiple sparklines
- `Plot.lineY()` with a `facet` option generates a grid of per-video trend lines automatically
- Works well alongside ECharts — can be used for specific analytical views
- Reference: https://observablehq.com/plot/

**Recharts** (MIT, React-native)
- Better TypeScript ergonomics than ECharts for simple line/area charts
- `<Sparkline>` component is purpose-built for compact trend indicators
- Lower bundle size than ECharts for single chart types
- Note: Would require adding a dependency; ECharts already covers this use case

**Plotly.js / Plotly Python** (MIT)
- Best for: interactive lifecycle curves with hover-over video metadata
- Python `plotly.express.line()` integrates naturally with the existing Streamlit dashboard
- `facet_col='cohort'` generates cohort comparison grids automatically
- Reference: https://plotly.com/python/line-charts/

**Python: Prophet (Meta, MIT)**
- Overkill for 5-20 Shorts/month, but appropriate if the catalog grows significantly
- Automatically detects seasonality (weekly, yearly) and holiday effects
- Reference: https://facebook.github.io/prophet/

**Python: statsmodels**
- `seasonal_decompose()` separates trend, seasonality, and residual components
- Appropriate for understanding annual Wisconsin seasonal cycles in performance data
- Reference: https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.seasonal_decompose.html

### Specialized Analytics Platforms (Reference Only)

- **Chartbeat**: "Attention minutes" — tracks engaged time, not just pageviews. Key insight: their decay curve visualizations normalize to "hours since publish" for articles, which is the equivalent of "days since publish" for YouTube content.
- **YouTube Studio**: Uses 28-day rolling comparisons for channel-level metrics and "first 24 hours" / "first 7 days" benchmarking for individual video performance.
- **TubeBuddy**: Shows per-video lifecycle curves with a "similar videos" overlay — the gold standard for Shorts comparison.
- **Vidooly / Tubular Labs**: Enterprise-grade content cohort tools. Their cohort methodology (normalize to publish date, compare at equivalent ages) is the industry reference implementation.

---

## Examples in the Wild

### 1. YouTube Studio — "Reach" Tab, Individual Video View
YouTube Studio's per-video analytics panel shows a lifecycle curve with "days since publish" on the x-axis alongside a reference band showing the channel's average performance at equivalent ages. The most important visual element is the shaded band (min/max range of comparable videos), not the average line. This framing — your video vs. the range of what's normal — is the most actionable display for editorial decisions.
- URL: https://studio.youtube.com (requires login)

### 2. GitHub Contribution Calendar
The canonical calendar heatmap implementation. Each cell is a day; color intensity represents activity volume. Applied to YouTube: each cell = a day, color = daily views or daily Shorts published. Reveals publishing cadence gaps and seasonal demand spikes at a glance. GitHub's implementation details are documented in their open-source Primer design system.
- Reference: https://primer.style/components/

### 3. Chartbeat Real-Time Dashboard
Chartbeat's editorial dashboard uses small sparklines in a table — each article row shows a 60-minute rolling view count as a sparkline. The key design decision: sparklines in the table are 80px wide and 30px tall with no labels. They serve as directional indicators only (up, flat, down, spike), not as precise data displays. This is the correct use of sparklines.
- Reference: https://chartbeat.com/publishing/real-time/

### 4. Social Blade — Channel Statistics
Social Blade's channel history view overlays daily subscriber count (bar) with a 30-day trend line (smooth line). The dual-layer approach (raw bars + smoothed trend) is a well-tested pattern for content analytics: bars show actual events, the trend line provides context.
- Reference: https://socialblade.com

### 5. Observable Plot — "Faceted Sparklines" Notebook
Observable's documentation includes examples of faceted small-multiple line charts that serve as per-entity sparklines in a grid layout. Each facet is a video; the y-axis is normalized 0-100% of peak views; the x-axis is days since publish. This is the most technically elegant implementation of lifecycle-normalized cohort comparison.
- Reference: https://observablehq.com/@observablehq/plot-facets

---

## Code Patterns & Implementation Notes

### 1. Lifecycle Curve — ECharts (Days Since Publish)

```typescript
// Server returns: { video_id, title, day_offset, views }[]
// day_offset = (metric_date - publish_date).days

const lifecycleOption = {
  tooltip: {
    trigger: 'axis',
    formatter: (params) => params.map(p =>
      `Day ${p.axisValue}: ${p.seriesName} — ${p.value.toLocaleString()} views`
    ).join('<br/>')
  },
  xAxis: {
    type: 'value',
    name: 'Days Since Publish',
    min: 0,
    max: 90,
  },
  yAxis: { type: 'value', name: 'Daily Views' },
  series: videoCohort.map(video => ({
    name: video.title,
    type: 'line',
    smooth: true,
    symbol: 'none',
    data: video.daily_data.map(d => [d.day_offset, d.views]),
    lineStyle: { width: 1.5, opacity: 0.7 },
  })),
};
```

### 2. Rolling Average Overlay — ECharts

```typescript
// Two series on same yAxis: raw daily bars + rolling average line
const rollingAverageOption = {
  tooltip: { trigger: 'axis' },
  legend: { data: ['Daily Views', '7-Day Avg'] },
  xAxis: { type: 'category', data: dates },
  yAxis: { type: 'value' },
  series: [
    {
      name: 'Daily Views',
      type: 'bar',
      data: rawViews,
      itemStyle: { color: '#3b82f6', opacity: 0.5 },
    },
    {
      name: '7-Day Avg',
      type: 'line',
      data: rolling7dayAvg,  // computed server-side with pandas
      smooth: true,
      symbol: 'none',
      lineStyle: { color: '#f59e0b', width: 2.5 },
    },
  ],
};
```

### 3. Sparklines in Table Rows — ECharts (Minimal Config)

```typescript
// Rendered inside a table cell; each instance is a tiny chart
function SparklineCell({ data }: { data: number[] }) {
  const option = {
    animation: false,
    grid: { top: 0, bottom: 0, left: 0, right: 0 },
    xAxis: { type: 'category', show: false, data: data.map((_, i) => i) },
    yAxis: { type: 'value', show: false },
    series: [{
      type: 'line',
      data,
      symbol: 'none',
      smooth: true,
      lineStyle: { color: data[data.length-1] > data[0] ? '#22c55e' : '#ef4444', width: 1.5 },
      areaStyle: { opacity: 0.1 },
      silent: true,
    }],
  };
  return <ReactECharts option={option} style={{ width: 80, height: 32 }} />;
}
```

### 4. Calendar Heatmap — ECharts

```typescript
// Visualize daily view counts across a year (seasonal pattern detection)
const calendarOption = {
  tooltip: { formatter: p => `${p.data[0]}: ${p.data[1].toLocaleString()} views` },
  visualMap: {
    min: 0,
    max: maxDailyViews,
    inRange: { color: ['#1e293b', '#3b82f6', '#06b6d4'] },
    show: false,
  },
  calendar: {
    range: '2024',
    cellSize: ['auto', 16],
    dayLabel: { firstDay: 1 },
  },
  series: [{
    type: 'heatmap',
    coordinateSystem: 'calendar',
    data: dailyViewData, // [['2024-01-01', 12453], ['2024-01-02', 8921], ...]
  }],
};
```

### 5. Anomaly Detection — Python (Server Side)

```python
import pandas as pd

def flag_anomalies(df: pd.DataFrame, metric: str = 'views', window: int = 28) -> pd.DataFrame:
    """Flag videos performing ±2 standard deviations from rolling mean."""
    rolling_mean = df[metric].rolling(window, min_periods=7).mean()
    rolling_std = df[metric].rolling(window, min_periods=7).std()

    df['z_score'] = (df[metric] - rolling_mean) / rolling_std.replace(0, float('nan'))
    df['anomaly_type'] = pd.cut(
        df['z_score'],
        bins=[-float('inf'), -2, -1, 1, 2, float('inf')],
        labels=['severe_under', 'under', 'normal', 'over', 'viral']
    )
    return df
```

```typescript
// ECharts markPoint for anomaly visualization
const anomalyMarkPoints = {
  markPoint: {
    data: anomalies.map(a => ({
      coord: [a.date, a.views],
      symbol: a.type === 'viral' ? 'arrow' : 'pin',
      symbolSize: 20,
      itemStyle: { color: a.type === 'viral' ? '#22c55e' : '#ef4444' },
      label: { formatter: a.type === 'viral' ? '⚡' : '⚠' },
    })),
  },
};
```

### 6. Cohort Comparison — Python Data Shape

```python
def build_cohort_data(
    daily_video_metrics: pd.DataFrame,
    cohort_period: str = 'M'  # 'W' for weekly, 'M' for monthly
) -> pd.DataFrame:
    """
    Returns per-video daily metrics normalized to days-since-publish.
    Each row: video_id, cohort_label, day_offset, views, cumulative_views
    """
    df = daily_video_metrics.copy()
    df['publish_date'] = pd.to_datetime(df['publish_date'])
    df['metric_date'] = pd.to_datetime(df['metric_date'])
    df['day_offset'] = (df['metric_date'] - df['publish_date']).dt.days
    df['cohort_label'] = df['publish_date'].dt.to_period(cohort_period).astype(str)

    # Cumulative views per video over its lifecycle
    df = df.sort_values(['video_id', 'day_offset'])
    df['cumulative_views'] = df.groupby('video_id')['views'].cumsum()

    return df[['video_id', 'title', 'cohort_label', 'day_offset', 'views', 'cumulative_views']]
```

### 7. Rolling Average Window Selection Guidelines

| Metric | Recommended Window | Rationale |
|---|---|---|
| Daily channel views | 7-day | Removes weekly publishing cadence noise |
| Daily Shorts views | 7-day | Captures weekly algorithm patterns |
| Subscriber net change | 28-day | Removes viral event distortion |
| Engagement rate | 28-day | Reduces outlier video influence |
| Watch time | 7-day | Correlated with views, same window |
| Revenue / CPM | 28-day | Monthly advertising cycle alignment |

### 8. FastAPI Endpoint for Lifecycle Data

```python
# New endpoint needed: /analytics/lifecycle
from datetime import date, timedelta

@router.get("/analytics/lifecycle")
def get_lifecycle_data(
    days_window: int = Query(90, ge=7, le=180),
    content_type: str = Query("shorts", regex="^(shorts|longform|all)$"),
    channel_id: Optional[str] = Query(None),
    db=Depends(get_db),
):
    """
    Returns per-video daily metrics normalized to days-since-publish.
    Used for lifecycle curves and cohort comparison charts.
    """
    videos = db.get_all_videos(channel_id=channel_id, content_type=content_type)
    result = []
    for video in videos:
        history = db.get_video_daily_history(video['id'], days=days_window)
        publish_date = date.fromisoformat(video['published_at'][:10])
        for point in history:
            metric_date = date.fromisoformat(point['date'])
            day_offset = (metric_date - publish_date).days
            if 0 <= day_offset <= days_window:
                result.append({
                    'video_id': video['id'],
                    'title': video['title'],
                    'day_offset': day_offset,
                    'views': point['views'],
                    'cohort': publish_date.strftime('%Y-%m'),  # monthly cohort
                })
    return result
```

---

## Gotchas & Anti-Patterns

### 1. Never Use Raw Calendar Dates on Lifecycle Charts
Plotting views on a calendar x-axis for multiple videos mixes lifecycle age with calendar time. A video published Jan 1 and a video published Jan 15 both appear in January, but the Jan 1 video's day-30 performance is the Jan 15 video's day-15 performance. Always normalize to "days since publish" before comparing videos.

### 2. Do Not Smooth Away Spikes When the Spike Is the Story
Rolling averages are valuable for trend detection but should never be the only series shown. A Shorts video that goes viral on day 3 will have its spike suppressed in a 7-day rolling average. Always render raw daily bars under or alongside the smoothed trend line.

### 3. Avoid ECharts `smooth: true` on Lifecycle Data With Gaps
ECharts' spline interpolation through gaps in a dataset can produce curves that suggest views on days where no data exists. Use `connectNulls: false` explicitly. If the YouTube Analytics API returns a gap (weekends can have reporting delays), render the gap honestly rather than interpolating across it.

### 4. Sparklines Are Not for Precision — Do Not Add Tooltips to Them
The purpose of a sparkline is directional (up/flat/down). Adding hover tooltips, axis labels, or precise values to sparklines defeats the purpose and creates visual noise. If a user needs the actual numbers, they should click through to a detail view.

### 5. Cohort Comparisons Break Down With Small Cohorts
If a "monthly cohort" contains only 2 Shorts, the cohort average is meaningless. Apply a minimum cohort size gate (n ≥ 5) before rendering cohort comparison charts. Display a "not enough data" state rather than a misleading chart.

### 6. Calendar Heatmaps With Sparse Data Look Empty and Confusing
With 5-20 Shorts per month, a "published date" calendar heatmap will have very few colored cells. Instead, use a "view volume" heatmap (daily views, not publish events), which will have color in every cell regardless of publishing frequency.

### 7. Avoid Dual Y-Axis Charts Unless the Scales Are Clearly Labeled
The Overview page already uses a single y-axis for views and subscribers. This works for trend direction but the magnitudes are incomparable (subscribers gained is always much smaller than views). Either use separate chart panels or use dual y-axis with explicit labeling and clear visual separation. The current ECharts `yAxisIndex` approach in `Shorts.tsx` is correct; ensure the same discipline is applied wherever the pattern is extended.

### 8. Do Not Compute Rolling Averages on the Frontend
Rolling averages require knowing all data points in the window, not just the ones currently visible on screen. Always compute rolling averages server-side in pandas and return them as pre-computed series from the API. Computing them in JavaScript from a paginated dataset produces incorrect values at page boundaries.

---

## Sources & Further Reading

- YouTube Analytics API — Dimensions and Metrics reference: https://developers.google.com/youtube/analytics/dimensions
- YouTube Analytics API — Chart types documentation: https://developers.google.com/youtube/analytics/charts
- Apache ECharts — Calendar Heatmap example: https://echarts.apache.org/examples/en/editor.html?c=calendar-heatmap
- Apache ECharts — Custom Series (for lifecycle curves): https://echarts.apache.org/en/option.html#series-custom
- Apache ECharts — markPoint documentation: https://echarts.apache.org/en/option.html#series-line.markPoint
- Observable Plot — Facets documentation: https://observablehq.com/plot/features/facets
- Observable Plot — Line chart with rolling average: https://observablehq.com/@observablehq/plot-moving-average
- Pandas rolling window documentation: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html
- Pandas resample documentation: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html
- Edward Tufte, "The Visual Display of Quantitative Information" — Chapter 6 (Sparklines): foundational theory for small multiples and inline trend indicators
- Chartbeat editorial analytics blog (attention time / decay curves): https://chartbeat.com/blog/
- Plotly Python — Faceted line charts: https://plotly.com/python/facet-plots/
- statsmodels seasonal decomposition: https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.seasonal_decompose.html
- Facebook Prophet — Seasonality modeling: https://facebook.github.io/prophet/docs/seasonality,_holiday_effects,_and_regressors.html

---

## Recommended for The Library

1. **Apache ECharts Calendar Heatmap Documentation** (https://echarts.apache.org/examples/en/editor.html?c=calendar-heatmap) — The canonical reference for implementing GitHub-style calendar heatmaps in ECharts, directly applicable to the PBS Wisconsin seasonal pattern visualization use case.

2. **Observable Plot — Moving Average Example** (https://observablehq.com/@observablehq/plot-moving-average) — Shows how to compute and overlay rolling averages as a declarative transformation, with clear explanations of window size tradeoffs. Directly translatable to pandas rolling window patterns.

3. **YouTube Analytics API Dimensions Reference** (https://developers.google.com/youtube/analytics/dimensions) — The authoritative list of what time-series dimensions are actually available from the YouTube Analytics API, including `day`, `7DayTotals`, and `28DayTotals` built-in aggregations that avoid the need to compute rolling windows manually for channel-level metrics.

4. **Observable Plot Facets Documentation** (https://observablehq.com/plot/features/facets) — Explains the "small multiples" pattern for generating per-video lifecycle comparison grids. While the library is different from ECharts, the faceting mental model applies directly to designing the cohort comparison UI.

5. **Pandas Time-Series / Resampling Guide** (https://pandas.pydata.org/docs/user_guide/timeseries.html) — The complete reference for time-series operations in pandas — resampling, rolling windows, period arithmetic, and date offset strings. Essential reading before implementing the lifecycle normalization and cohort data-shaping logic in the FastAPI analytics backend.
