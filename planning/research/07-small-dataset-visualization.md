# Data Visualization for Small Datasets — Research Report

## Summary

PBS Wisconsin's shortform video output of 5–20 videos per month creates a visualization problem that most dashboard toolkits are not designed for: charts built for hundreds or thousands of data points become sparse, misleading, or simply ugly at small-n. The core principle from data visualization theory is that **the chart type must match the data density** — when n is small enough that you can read individual values without aggregation, you should show individual items explicitly rather than summarizing them. Ranked lists, stat cards, and per-item card layouts outperform traditional bar and line charts at this scale. The goal shifts from "reveal pattern in noise" to "make individual items legible and comparable," which requires a fundamentally different design philosophy than most analytics dashboards assume.

---

## Key Findings

1. **Traditional charts fail small datasets in predictable ways.** Bar charts with 5–15 bars look empty and invite misleading comparisons (the relative heights feel significant even when absolute differences are small). Line charts with fewer than 10–12 time points should almost never be used because they imply continuity and trend where none exists. Scatter plots below ~30 points give no sense of distribution. The visual grammar of these chart types was designed to compress large datasets — when the dataset is small, the compression adds no value and the visual encoding misleads.

2. **Show individual items, not summaries.** Edward Tufte's "data-ink ratio" principle cuts both ways: at small-n, individual data points ARE the story, so hiding them in aggregation wastes the most information-dense representation available. Cole Nussbaumer Knaflic (*Storytelling with Data*, 2015) explicitly recommends showing individual data points as dots overlaid on summary ranges when n is small. Stephen Few (*Show Me the Numbers*, 2012) warns that bar charts aggregate visual attention away from outliers — the exact outliers that matter most in small content libraries.

3. **Ranked lists and leaderboards are the most natural small-n view.** When you have 10–20 items and one or two key metrics, a ranked list with inline metric values is almost always the right answer. It's scannable, doesn't require decoding visual encoding, and scales gracefully from 5 to 50 items without redesign. This is why every major podcast platform (Spotify for Podcasters, Apple Podcasts Connect, Podtrac) defaults to episode ranking tables for low-volume shows.

4. **Card layouts (one card per item) work extremely well for 5–20 items.** When the item count fits on a single screen, per-item cards with a thumbnail, title, and 3–4 key metrics give users immediate access to full item detail without clicking through. YouTube Studio itself uses this pattern for the channel's video list. The design cost is vertical space; the benefit is zero cognitive overhead in decoding charts.

5. **Dot plots and strip plots are the best chart alternatives for small-n distributions.** When you genuinely need to show distribution (e.g., "how does this month's video performance distribute?"), a dot plot or strip plot showing individual data points is far more honest than a box plot or histogram. Dot plots were popularized by William Cleveland (*The Elements of Graphing Data*, 1985) and consistently outperform bar charts in perception studies at small n. Each point remains individually meaningful and can be labeled.

6. **Aggregation should be explicit and justified, not automatic.** Monthly totals and rolling averages are appropriate when the question is trend-level ("are we growing?"), but obscure individual-item insight ("which video overperformed?"). The recommended pattern is to offer both views explicitly — a period-level trend view and an item-level detail view — and default to whichever matches the primary user question.

7. **Empty states require proactive design.** A dashboard showing "no data this week" feels broken if not designed deliberately. The fix is to design the empty state as a first-class view: show the time axis, label the gap explicitly, and provide context ("0 Shorts published Feb 3–9 — next publish scheduled Feb 12"). This pattern comes from product design (see Shopify Polaris design system and Stripe's dashboard patterns) and is underused in analytics.

8. **Podcast analytics dashboards are the closest analogue to PBS Wisconsin's problem.** Spotify for Podcasters, Apple Podcasts Connect, and Chartable all face the same issue: shows with 1–4 episodes per month cannot use the same visualizations as daily news podcasts. These platforms consistently use: episode leaderboards, per-episode stat cards, rolling 30/60/90-day period selectors (not weekly), and explicit annotations for publication events.

9. **Visual density at small-n should be higher, not lower.** Counter-intuitively, sparse charts with lots of white space make small datasets look more incomplete. The right move is to increase information density per item: show more metrics per bar/point/card, add benchmark lines (channel average, platform average), add sparklines for historical context per item, and use color to encode a second dimension. This is Tufte's "small multiples" principle applied to dashboards.

10. **Benchmark lines transform small-dataset charts.** Adding a channel-average line, a platform-median benchmark, or a "goal" line to any chart with few data points immediately gives every point relational meaning. A bar chart with 8 bars and no reference line is hard to interpret; the same chart with a "channel average" line lets you instantly classify each bar as above or below without needing many bars to establish a trend.

---

## Tools & Technologies

### Charting Libraries

- **Recharts (React)**: Best small-dataset support among React chart libraries. `ComposedChart` allows combining bar, dot, and line on one axis. `ScatterChart` renders individual labeled data points cleanly. Easy to add reference lines, labels, and tooltips per item. Used by many analytics startups. https://recharts.org/

- **Nivo (React)**: Built on D3, has excellent `@nivo/bump` (rank-over-time bumpchart) which works beautifully with 5–20 items. Also has `@nivo/swarmplot` (strip plot equivalent) designed specifically for small distributions. Extensive animation support helps highlight individual items. https://nivo.rocks/

- **Observable Plot**: The successor to D3 for declarative charts. Has first-class support for dot plots and strip plots. Designed for exploratory data analysis where n may be small. The `dot` mark with `sort` option produces clean ranked dot plots in 5 lines of code. https://observablehq.com/plot/

- **Tremor (React)**: Component library specifically for analytics dashboards, with stat cards, leaderboard tables, and sparklines as first-class primitives. Well-suited for the "card + metric" pattern. https://www.tremor.so/

- **shadcn/ui + Recharts**: The shadcn chart components are wrappers around Recharts that follow accessible design patterns and look polished with minimal configuration. Good choice if the project already uses shadcn. https://ui.shadcn.com/charts

- **D3.js**: Still the right choice for fully custom small-n visualizations (beeswarm plots, custom dot plots with thumbnail images). The learning curve is high but no other library matches its flexibility for non-standard chart types.

### Design System References

- **Shopify Polaris**: Excellent empty state guidelines and card-based data display patterns. https://polaris.shopify.com/components/layout-and-structure/empty-state

- **Stripe Dashboard patterns**: Stripe's own analytics dashboards handle low-volume merchant data elegantly. Their period-selector ("Last 7 days / 30 days / 90 days") and stat card patterns are widely copied.

- **IBM Carbon Design System**: Has detailed guidance on data visualization accessibility and small-dataset chart types including dot plots. https://carbondesignsystem.com/data-visualization/basic-charts/

- **Tailwind UI**: "Stats" and "Leaderboard" components in Tailwind UI's application component library map directly to small-n dashboard needs.

### Python Libraries (for Streamlit dashboards)

- **Plotly Express**: `px.strip()` produces strip plots; `px.scatter()` with labeled points works for small n. Easy to add reference lines with `add_hline()`. https://plotly.com/python/strip-charts/

- **Altair**: Declarative D3-backed library with excellent dot plot and strip plot support. `mark_point()` with `sort` encoding is idiomatic for ranked visualizations. https://altair-viz.github.io/

- **Streamlit `st.metric()`**: Built-in stat card component. Supports delta values (up/down vs. prior period). Three columns of `st.metric()` is often the right top-of-dashboard pattern for small-n contexts.

---

## Examples in the Wild

### 1. Spotify for Podcasters (now Spotify Creator Studio)
**URL**: https://podcasters.spotify.com

Spotify's podcast analytics dashboard is an almost perfect case study. For shows with 1–4 episodes per month, it uses:
- A **leaderboard table** of episodes sorted by streams, with inline sparklines showing listen-over-time per episode
- **Stat cards** at the top (total streams, unique listeners, followers gained) with period-over-period deltas
- A **rolling 30/60/90 day selector** rather than calendar weeks, because weekly view is too sparse for low-volume shows
- **Audience retention curves** (per-episode, not aggregated) as the primary per-item visualization, which works beautifully at n=1
- No bar charts on the main view — only when you drill into a single episode

This is the closest analogue to PBS Wisconsin's Shorts dashboard.

### 2. Apple Podcasts Connect
**URL**: https://podcastsconnect.apple.com

Apple's analytics take a different approach for small shows:
- Uses **bubble charts** where bubble size = listener count, x-axis = episode age, y-axis = engagement rate. Works well at 10–30 episodes because each bubble is individually identifiable and labeled.
- **Per-episode retention charts** (line charts showing % listened at each second) — the small-n problem disappears because each chart represents a single item.
- Episode list defaults to a **sortable table** with inline bar-in-cell indicators rather than standalone bar charts.

### 3. Chartable (acquired by Spotify 2022)
Chartable's "SmartLinks" analytics tracked individual episode links and displayed results in a **card-per-episode** layout with platform breakdown icons. With 1–10 data points per card, this was effectively a per-item scorecard view. The design lesson: when n is small enough to list individually, list them individually with full context rather than charting aggregated views.

### 4. Substack Dashboard (for low-subscriber newsletters)
Substack's writer dashboard handles low-volume content (1–4 posts per month) by:
- Defaulting to a **ranked list of posts by open rate**, showing absolute opens and rate side by side
- Using a **small multiples approach** for post-by-post comparison (each post gets a mini retention curve)
- Prominently displaying the **ratio** (open rate %) rather than the raw count when counts are small enough to be noisy

### 5. GitHub Insights (small repositories)
GitHub's contribution graphs and traffic pages degrade gracefully at low-volume repos:
- The **traffic sparkline** shows a dotted line (not solid) when data is sparse, explicitly signaling low-confidence trend
- The **referral sources table** works from n=1 upward because it's a ranked list, not a chart
- The "No data available" state for the punch card chart includes explanatory copy ("Not enough commits to show a pattern") rather than showing a blank chart

---

## Code Patterns & Implementation Notes

### Pattern 1: Stat Card Row (Top of Dashboard)

For 3–6 summary metrics, use a row of stat cards with period-over-period deltas. This is always appropriate regardless of n, because it's absolute values, not comparative charts.

```typescript
// React / Tremor example
import { Metric, Text, BadgeDelta } from "@tremor/react";

const StatCard = ({ label, value, delta, deltaType }) => (
  <Card>
    <Text>{label}</Text>
    <Metric>{value}</Metric>
    <BadgeDelta deltaType={deltaType}>{delta}</BadgeDelta>
  </Card>
);

// Usage for PBS Wisconsin Shorts
<div className="grid grid-cols-3 gap-4">
  <StatCard label="Shorts Published" value="12" delta="+3 vs last month" deltaType="increase" />
  <StatCard label="Total Views" value="84,200" delta="+12%" deltaType="increase" />
  <StatCard label="Avg View Rate" value="68%" delta="-2pp" deltaType="decrease" />
</div>
```

```python
# Streamlit equivalent
col1, col2, col3 = st.columns(3)
col1.metric("Shorts Published", "12", "+3 vs last month")
col2.metric("Total Views", "84,200", "+12%")
col3.metric("Avg View Rate", "68%", "-2pp")
```

### Pattern 2: Ranked List / Leaderboard Table

The workhorse view for small-n video analytics. Sort by key metric, show 3–5 metrics per row, optionally add a thumbnail.

```typescript
// Recharts inline bar-in-cell for leaderboard tables
// Each row shows a normalized bar representing % of top performer
const LeaderboardRow = ({ video, maxViews }) => {
  const pct = (video.views / maxViews) * 100;
  return (
    <tr>
      <td><img src={video.thumbnail} className="w-16 h-9 object-cover" /></td>
      <td className="max-w-xs truncate">{video.title}</td>
      <td>{video.views.toLocaleString()}</td>
      <td>
        <div className="w-24 bg-gray-100 rounded">
          <div className="bg-blue-500 h-2 rounded" style={{ width: `${pct}%` }} />
        </div>
      </td>
      <td>{video.viewRate}%</td>
      <td>{video.avgWatchTime}</td>
    </tr>
  );
};
```

Key design decisions for leaderboard tables:
- Default sort by views, but allow re-sort by any metric column
- Show rank number (1, 2, 3...) explicitly — this is the most legible encoding of relative position
- Add a subtle background color change for top 3 rows
- Do NOT use a bar chart — the inline bar-in-cell is more compact and equally clear

### Pattern 3: Dot Plot with Benchmark Line

Better than a bar chart for 5–20 items. Each dot is individually labeled, benchmark line provides context.

```python
# Plotly Python — dot plot with channel average line
import plotly.graph_objects as go

fig = go.Figure()

# Individual dots
fig.add_trace(go.Scatter(
    x=df['views'],
    y=df['title'],
    mode='markers+text',
    text=df['views'].apply(lambda v: f"{v:,}"),
    textposition='middle right',
    marker=dict(size=12, color=df['color']),
    name='Videos'
))

# Channel average reference line
avg_views = df['views'].mean()
fig.add_vline(
    x=avg_views,
    line_dash="dash",
    line_color="gray",
    annotation_text=f"Channel avg: {avg_views:,.0f}",
    annotation_position="top right"
)

fig.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    xaxis_title="Views",
    height=max(300, len(df) * 40)  # Scale height to item count
)
```

### Pattern 4: Per-Item Card Grid (Card-Based Layout)

For 5–20 videos, a card grid gives users full item context without chart decoding. Works best when there's a thumbnail to show.

```typescript
// One card per video — works for 5-20 items
const VideoCard = ({ video }) => (
  <div className="border rounded-lg overflow-hidden shadow-sm">
    <img src={video.thumbnail} className="w-full aspect-video object-cover" />
    <div className="p-3">
      <p className="font-medium text-sm line-clamp-2">{video.title}</p>
      <div className="mt-2 grid grid-cols-2 gap-1 text-xs text-gray-600">
        <span>{video.views.toLocaleString()} views</span>
        <span>{video.viewRate}% view rate</span>
        <span>{video.likes} likes</span>
        <span>{video.avgWatchTime} avg watch</span>
      </div>
      {video.views > channelAvgViews && (
        <span className="mt-1 inline-block bg-green-100 text-green-800 text-xs px-2 py-0.5 rounded">
          Above average
        </span>
      )}
    </div>
  </div>
);

// Grid layout: 2 columns mobile, 3-4 columns desktop
<div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
  {videos.map(v => <VideoCard key={v.id} video={v} />)}
</div>
```

### Pattern 5: Empty State Design

Empty states must feel intentional, not broken.

```typescript
const EmptyPeriodState = ({ period, nextExpectedDate }) => (
  <div className="flex flex-col items-center justify-center py-16 text-center">
    {/* Icon — not a broken chart icon, something neutral */}
    <CalendarIcon className="w-12 h-12 text-gray-300 mb-4" />
    <h3 className="text-gray-700 font-medium">No Shorts published {period}</h3>
    <p className="text-gray-500 text-sm mt-1 max-w-xs">
      PBS Wisconsin published 0 Shorts during this period.
      {nextExpectedDate && ` Next publish expected around ${nextExpectedDate}.`}
    </p>
    {/* Show recent history to prove the dashboard isn't broken */}
    <p className="text-gray-400 text-xs mt-4">
      Last Short published: <span className="text-gray-600">Feb 12 — "Ice Fishing on Green Bay" (12,400 views)</span>
    </p>
  </div>
);
```

Design rules for empty states:
1. Explain WHY the state is empty (no data vs. API error vs. filter too narrow)
2. Show the most recent non-empty data to prove the system is working
3. Never show a blank chart frame with no data — remove the chart entirely and replace with the empty state component
4. If the period selector is causing emptiness, surface a suggestion: "Try switching to 'Last 90 days' to see more data"

### Pattern 6: Period Selector Calibrated to Publishing Cadence

Standard "Last 7 days / 30 days / 90 days" selectors are wrong for PBS Wisconsin. With 5–20 videos per month, "last 7 days" will often return 0–2 items.

```typescript
// Period options tuned to publishing cadence
const PERIOD_OPTIONS = [
  { label: "Last 30 days", value: 30 },    // ~5-20 videos
  { label: "Last 90 days", value: 90 },    // ~15-60 videos
  { label: "This year", value: 365 },      // ~60-240 videos
  { label: "Last year", value: 365 },
  { label: "All time", value: null },
];
// Note: "Last 7 days" is intentionally excluded — too sparse for this cadence
```

### Pattern 7: Table with Inline Sparklines

For showing per-video trend (how did views accumulate over time?) in a compact table format.

```typescript
// Mini sparkline per row using Recharts SparklineChart
import { SparklineChart } from "@tremor/react";

const VideoTableRow = ({ video }) => (
  <tr>
    <td>{video.title}</td>
    <td>{video.totalViews.toLocaleString()}</td>
    <td className="w-24">
      <SparklineChart
        data={video.dailyViews}
        categories={["views"]}
        index="date"
        colors={["blue"]}
        className="h-8"
      />
    </td>
    <td>{video.viewRate}%</td>
  </tr>
);
```

---

## Gotchas & Anti-Patterns

### Anti-Pattern 1: Line Charts for Sparse Time Series

**Never** use a line chart to show monthly publish counts when you have fewer than 12 months of data. A line chart with 3 points implies a trend; statistically, 3 points establish nothing. Use a bar chart (each bar is a month) or, better, a table with month-over-month delta.

**Specific failure case for PBS Wisconsin**: A line chart of "Shorts published per month" over 6 months will look like it shows a trend even when the variation is pure noise. Users will make decisions based on spurious patterns.

### Anti-Pattern 2: Pie/Donut Charts for Small Category Counts

A pie chart with 3–6 categories and small total counts is almost always the wrong choice. The arc encoding is hard to compare, and with small numbers the percentages bounce dramatically week-to-week. Use a horizontal bar chart with labeled values, or better, a stat card per category.

### Anti-Pattern 3: Histograms with Too Few Bins

A histogram of video durations with 8 videos will show 1–2 items per bin regardless of bin count. This is meaningless. Replace with a dot plot where each dot is a video, labeled by title.

### Anti-Pattern 4: Aggregating Away the Individual

When n=12, computing the "average view rate" hides that one outlier video has 4x the views of the others. Always show individual items alongside aggregates for small datasets. The aggregate is context; the individual is the story.

### Anti-Pattern 5: Comparing Percentages from Small Counts

"This Short got 15% more engagement than last month's" means almost nothing if the comparison is between 10 and 12 interactions. Always show absolute values alongside percentages at small n. Optionally, suppress percentage comparisons when the base is below a minimum threshold (e.g., fewer than 100 views).

### Anti-Pattern 6: Weekly Granularity

A publishing cadence of 5–20 videos per month means some weeks have 0 videos. Weekly charts will have systematic gaps, making the dashboard look broken. Default to monthly granularity for period-level views, and show individual items (which have their own publish dates) for item-level views. Never bucket individual videos by publish-week.

### Anti-Pattern 7: Auto-Scaling Y-Axes

Chart libraries often auto-scale Y axes to fit the data range. With small datasets, this makes a 10% difference look like a 500% difference. Always include zero on the Y-axis for absolute value charts, or explicitly label the axis range so users understand the scale. Recharts: `domain={[0, 'auto']}`. Plotly: `range=[0, max_value * 1.1]`.

### Anti-Pattern 8: "No data" as a Blank Screen

Never let a dashboard render as an empty page with no explanation. This is the most common mistake in analytics dashboard design for low-volume channels. Design empty states as first-class components before any charts.

### Anti-Pattern 9: Scatter Plots Below 30 Points

Scatter plots are designed to reveal correlation in distributions. Below 30 points, the "cloud" gives no signal — individual points are artifacts. If you want to show the relationship between two metrics for 10 videos, use a labeled dot plot (each dot is a video) where the user can read the label, or a table with both columns sortable.

### Anti-Pattern 10: Defaulting to the Date Range That Makes the Chart Look Fuller

It's tempting to default to "All time" to get more data points on charts. This can mislead users by mixing old data with current performance. Be explicit about what period is shown and why that default was chosen.

---

## Aggregation Strategy: When to Aggregate vs. Show Individual Items

**Show individual items when:**
- n ≤ 50 and the primary question is "which item performed best/worst?"
- The items have meaningful identifiers (video titles, thumbnails) that users recognize
- Outliers are more interesting than the average (almost always true for content analytics)
- The user needs to take action on specific items (e.g., decide what to promote)

**Aggregate when:**
- The primary question is trend-level ("are we growing month-over-month?")
- Individual items are not actionable in the current view
- n is large enough that individual items cannot be labeled without overlap
- You're comparing across time periods, channels, or platforms (not individual videos)

**The recommended pattern for PBS Wisconsin** is a two-level dashboard:
1. **Top level**: Period aggregates (stat cards, monthly trend bars) — answers "how are we doing overall?"
2. **Item level**: Per-video list/cards — answers "which specific videos drove that result?"

Both levels should be visible simultaneously on a single dashboard, not hidden behind tabs when n is small.

---

## Sources & Further Reading

Note: WebSearch and WebFetch were unavailable in this research session. All sources below are cited from the researcher's training knowledge through August 2025 and are verifiable at the URLs provided.

### Books (Canonical References)

- **Edward Tufte — *The Visual Display of Quantitative Information* (2001, 2nd ed.)**: Chapters 3–4 on data-ink ratio and small multiples. Tufte's rule: "Maximize the data-ink ratio, within reason." For small datasets, this means showing raw data points, not summaries. https://www.edwardtufte.com/tufte/books_vdqi

- **Cole Nussbaumer Knaflic — *Storytelling with Data* (2015)**: Chapter 2 (choosing an effective visual), Chapter 3 (clutter is your enemy). Explicitly covers when bar charts fail and when table/scorecard formats outperform charts. https://www.storytellingwithdata.com/books

- **Stephen Few — *Show Me the Numbers* (2012, 2nd ed.)**: The most detailed treatment of table vs. chart selection criteria. Few's decision framework explicitly addresses when n is too small for meaningful charts. https://www.perceptualedge.com/library.php

- **William Cleveland — *The Elements of Graphing Data* (1985, revised 1994)**: The original research behind dot plots outperforming bar charts. Cleveland and McGill's seminal 1984 paper in *Journal of the American Statistical Association* ("Graphical Perception") established that position-on-scale (dot plot) is more accurately perceived than length (bar chart). https://www.amazon.com/Elements-Graphing-Data-William-Cleveland/dp/0963488414

- **Alberto Cairo — *The Functional Art* (2012) and *How Charts Lie* (2019)**: Cairo's work on chart literacy includes extensive discussion of how small-n datasets are routinely misrepresented by inappropriate chart choices. https://www.thefunctionalart.com/

### Online References

- **Stephanie Evergreen — Evergreen Data blog**: Evergreen's "chart chooser" posts specifically address when to use tables vs. charts vs. infographics. Her "Choosing a Chart Type" flowchart is widely used in data journalism. https://stephanieevergreen.com/

- **Flowing Data (Nathan Yau)**: Extensive tutorials on dot plots, strip plots, and small-n visualization for real datasets. https://flowingdata.com/

- **Observable Plot documentation — Dot mark**: Reference implementation of dot plots and strip plots with sort encoding. https://observablehq.com/plot/marks/dot

- **Recharts documentation — ComposedChart**: The ComposedChart component is the right tool for combining dot/bar/line on small datasets. https://recharts.org/en-US/api/ComposedChart

- **Shopify Polaris — Empty States**: Industry-standard guidance on designing empty states for data dashboards. https://polaris.shopify.com/patterns/empty-states

- **IBM Carbon Data Visualization guidelines**: Includes explicit guidance on chart type selection by data characteristics including sample size. https://carbondesignsystem.com/data-visualization/chart-types/

- **Nivo Bump Chart**: Specifically designed for rank-over-time visualization of 3–20 items. https://nivo.rocks/bump/

- **Podtrac Industry Ranking methodology**: Podtrac's public methodology for podcast rankings uses episode-level tables rather than charts, explicitly because episode counts vary dramatically between shows. https://podtrac.com/methodology/

---

## Recommended for The Library

The following five resources are the highest-value additions to The Library for ongoing PBS Wisconsin dashboard development:

1. **Observable Plot documentation** (https://observablehq.com/plot/) — The most modern declarative charting library with first-class small-dataset support. The dot, rule, and text marks are directly applicable to video leaderboards and ranked lists. The entire docs should be scraped.

2. **Storytelling with Data blog** (https://www.storytellingwithdata.com/blog) — Knaflic's blog has dozens of posts on choosing between table and chart formats, with worked examples. Particularly relevant: "what is a table?" (2014), "death to pie charts" (2012), "alternatives to pie charts" (2015).

3. **Tremor component documentation** (https://www.tremor.so/docs) — React component library built specifically for analytics dashboards, with stat cards, leaderboards, and sparklines as first-class primitives. The component API docs are directly applicable to the web/ dashboard codebase.

4. **Flowing Data "Visualizing Distributions" tutorial series** (https://flowingdata.com/2012/05/15/how-to-visualize-and-compare-distributions/) — Nathan Yau's tutorials on strip plots, dot plots, and ridgeline plots with Python/R code examples. The techniques are directly portable to Plotly and Altair in the existing Streamlit dashboard.

5. **Stephen Few's "Perceptual Edge" library** (https://www.perceptualedge.com/library.php) — Few's white papers include "Tapping the Power of Visual Perception" (2004) and "Practical Rules for Using Color in Charts" (2008), both of which have direct application to the small-n chart design problem. His "Dashboard Design for Real-Time Situational Awareness" (2006) white paper is particularly relevant to the PBS Wisconsin analytics use case.

---

*Report compiled: 2026-03-05. Research session note: WebSearch and WebFetch tools were unavailable; findings draw on training data through August 2025. All URLs should be verified before scraping into The Library.*
