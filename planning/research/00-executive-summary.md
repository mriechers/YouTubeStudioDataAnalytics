# Shortform Monitoring & Visualization Design — Executive Summary

_Research compiled: March 2026 | 8 specialist reports, 4,133 lines of research_
_Project: PBS Wisconsin YouTube Analytics (`pbswi-youtube-analytics`)_

---

## What We Researched

PBS Wisconsin publishes 5–20 shortform videos per month across YouTube Shorts, Instagram Reels, TikTok, and Facebook Reels. This research sprint investigated **report structures, dashboard patterns, and visualization approaches** that can help the team monitor and iterate on shortform content — informed by the existing [Shortform Content Landscape](~/Developer/research-hub/shortform-content-landscape/) research.

Eight specialist agents investigated: KPI hierarchies, cross-platform comparison, periodic report design, time-series visualization, content categorization UX, actionable insight patterns, small-dataset visualization, and accessible dashboard design.

---

## Agent Summaries

### 01 — Shortform Dashboards & KPIs
- **Completion rate is the single most actionable metric** across all platforms — it directly correlates with algorithmic distribution and reveals hook/pacing quality.
- YouTube's **engaged views** (quality-filtered) vs. raw views distinction is the highest-priority gap in the current dashboard. The codebase already has `engaged_views` in the data model but doesn't surface it.
- The dominant dashboard architecture is a **four-layer pattern**: summary scorecard → trend over time → per-video table → detail drill-down. PBS Wisconsin's current dashboard stops at layer 2.
- **Subscriber conversion per Short** is the highest-value KPI for a public broadcaster (audience-building, not ad RPM). Currently in the database but not attributed per-video.
- Revenue metrics should be **deprioritized for Shorts** ($0.01–$0.07 RPM makes monetization negligible at this volume).

### 02 — Cross-Platform Comparison
- **Raw view counts are not comparable** across platforms (YouTube = any play, Facebook = 3-second threshold, Instagram = "accounts reached" as primary). Never sum or average views across platforms.
- Two normalization approaches work: **engagement rate** (`(likes+comments+shares)/views`) and **indexed scoring** (`value / account 30-day avg * 100`).
- **Small-multiple layout** (one panel per platform, shared time axis) is the industry standard — never merge raw metrics onto a shared Y-axis.
- Content-level linking across platforms is achievable with a **`cross_platform_posts` join table** using publish-date + title similarity matching.
- **Watch time in seconds** beats completion rate for cross-platform comparison because it avoids length-confounded percentages.

### 03 — Content Performance Reports
- **Cadence determines depth**: weekly = "is anything broken?" (5-min email); monthly = "what should we make more of?" (20-min read with scorecards); quarterly = "should we change our approach?" (strategic deck).
- The **"so what?" layer** (explicit recommendations after data) is the most commonly omitted and most important section.
- **Template discipline matters** — keep the same report structure every period so recipients develop scanning patterns and anomalies become instantly visible.
- Content scorecards should show **relative benchmarks** (vs. channel average, vs. show average), not just raw numbers. Traffic-light (RAG) systems reduce cognitive load.
- Automated report generation with **Jinja2 + WeasyPrint** fits the existing Python stack; weekly reports can run via launchd.

### 04 — Time-Series & Trend Visualization
- **Lifecycle age-normalization** (x-axis = "days since publish") is the most important technique — lets you compare any two Shorts at equivalent lifecycle ages.
- **7-day rolling averages** for daily views, **28-day** for subscriber trends, **90-day** only for strategic planning.
- **Sparklines in table rows** are the single highest-ROI visualization upgrade for content catalog views.
- **Calendar heatmaps** (GitHub-style) reveal seasonal patterns and publication cadence gaps immediately.
- **ECharts** (already in the project stack) supports all required visualization types natively — no new library needed.

### 05 — Content Categorization & Tagging
- **Show/series is the right primary dimension** — `show_name` from the title parser is already correctly positioned as the root.
- **Flat tags beat deep hierarchies** at this scale. Add `tags[]`, `campaign`, and `topic_categories[]` to `VideoRecord`.
- YouTube's **`topicCategories`** field (free, no extra quota) provides ~30 auto-classified topic labels via the Data API — currently unused.
- **Faceted filtering** with multi-select dropdowns, dismissible chips, and saved filter presets is the established UX pattern.
- A **sortable table with inline chip badges** is the highest-density content inventory format at this scale.

### 06 — Actionable Insights & Recommendations
- **Insight cards** (headline + stat + CTA) are the dominant UI pattern across YouTube Studio, GA4, Amplitude, and Chartbeat.
- **Comparative framing** ("3.2x your channel average") drives action more than absolute numbers ("4,200 views").
- **Three-tier severity** (info/warning/critical) prevents alert fatigue.
- **Slack integration** has the strongest ROI for a small team not living in a dashboard — push alerts when thresholds are crossed.
- Content creation recommendations need the **show taxonomy** (already available) to generate "Make more Wisconsin Life content" style insights.
- Use **z-score / IQR** for anomaly detection, not ML — insufficient data volume for ML models.

### 07 — Small Dataset Visualization
- Traditional charts **fail predictably** at 5–20 items: bar charts look empty, line charts imply false trends, scatter plots show no distribution.
- **Ranked leaderboards and per-item card layouts** are almost always the right default for small catalogs.
- **Benchmark lines** (channel average, platform median) are the single highest-ROI improvement for any small-n chart.
- **Empty states** must be designed as first-class components, not afterthoughts.
- **Period selectors** should default to 30/90 days, not 7 days — weekly granularity doesn't match monthly publishing cadence.
- Podcast analytics platforms (Spotify for Podcasters, Chartable) face the same problem and are the best design analogues.

### 08 — Accessible Dashboard Design
- No single WCAG criterion covers charts — it's a **matrix of 13+ criteria** (1.1.1, 1.4.1, 1.4.11, 2.1.1, 4.1.2, etc.).
- YouTube red and TikTok's brand colors **cannot be used together** for color-blind users. A custom categorical palette is needed (Paul Tol's Bright scheme recommended).
- **Highcharts** is the only chart library with first-class a11y (screen reader, keyboard nav, sonification). Recharts/Chart.js require manual ARIA work.
- **Text summaries above charts** improve comprehension for all users — the "inverted pyramid" pattern (headline finding → data → chart).
- **`prefers-reduced-motion`** must be respected for animated chart transitions and sparklines.
- **Focus management** during filter re-renders is a distinct challenge — focus should not jump or be lost.

---

## Cross-Cutting Themes

### 1. Individual Items Over Aggregation
At 5–20 Shorts/month, the data is sparse enough that every individual video matters. Reports 01, 03, 04, 05, and 07 all converge on: **show individual items, not summaries**. Ranked lists, per-video scorecards, and card layouts beat bar charts and line graphs at this scale.

### 2. Relative Framing Over Absolute Numbers
Reports 01, 02, 03, 06, and 07 all emphasize: **raw numbers without benchmarks are useless**. "4,200 views" means nothing; "2.1x your channel average" is immediately actionable. Indexed scoring, percentile ranking, and channel-average reference lines appear across nearly every report.

### 3. Completion Rate as the North Star
Reports 01, 02, and 04 all identify **completion rate** as the most actionable shortform metric. It's the primary algorithmic signal on YouTube and TikTok, it's comparable across platforms (when normalized for duration), and it directly reveals whether content hooks and holds attention.

### 4. The Dashboard You Don't Visit Is Worthless
Reports 03 and 06 converge on: **push insights to where the team already lives** (Slack, email) rather than building dashboards that require a daily visit. Weekly automated email digests and Slack alerts for anomalies deliver more value than a polished dashboard with low traffic.

### 5. ECharts Does Everything You Need
Reports 04 and 07 confirm: the project's existing **ECharts** dependency handles sparklines, calendar heatmaps, lifecycle curves, anomaly markers, and small-multiple layouts. No new chart library is needed. The key insight: configure ECharts differently for small-n contexts (benchmark lines, dot plots, minimal axes).

### 6. Platform-Native Metrics Can't Be Merged
Reports 01 and 02 establish firmly: **never combine raw metrics from different platforms on the same axis**. The solutions — indexed scoring, engagement rate normalization, small-multiple layouts — all preserve platform context while enabling comparison.

---

## Decision Matrix

| If you're working on... | Start with reports... |
|---|---|
| The main YouTube Shorts dashboard | 01 (KPIs), 04 (time-series), 07 (small datasets) |
| Cross-platform analytics | 02 (comparison), 05 (categorization) |
| Periodic reporting (weekly/monthly/quarterly) | 03 (reports), 06 (insights) |
| Content catalog/inventory view | 05 (categorization), 07 (small datasets) |
| Automated alerts and insights | 06 (insights), 03 (reports) |
| Accessibility compliance | 08 (a11y) — applies to everything |
| New API endpoints | 04 (lifecycle endpoint), 05 (catalog endpoint), 06 (insights endpoint) |

---

## Top 10 Actionable Recommendations

1. **Surface `engaged_views` in the Shorts dashboard.** It's already in the data model but not displayed. This is the single highest-priority dashboard fix.

2. **Add a per-video leaderboard table** below the current scorecard row. Sortable by completion rate, views, engagement rate. Include 28-day sparklines per video.

3. **Implement indexed scoring** (`value / 30-day account average * 100`) as the primary cross-platform comparison metric.

4. **Build three report cadences**: weekly email digest (automated), monthly scorecard (semi-automated), quarterly strategic review (manual with data support).

5. **Add `topicCategories` from YouTube's Data API** to the video metadata pipeline — free automated topic labels at zero extra quota cost.

6. **Design a categorical color palette** that's color-blind safe across platforms — don't use brand colors for data encoding.

7. **Add benchmark reference lines** to every chart — channel average at minimum, show average where applicable.

8. **Build an insights card system** with severity tiers (info/warning/critical) and comparative framing ("2.3x your show average").

9. **Implement Slack webhook alerts** for viral content detection and performance anomalies.

10. **Add a `/analytics/lifecycle` API endpoint** that returns days-since-publish normalized data for lifecycle curve visualization.

---

## Tensions & Tradeoffs

| Tension | Resolution |
|---|---|
| **Rich visualization vs. small datasets** | Default to ranked lists and scorecards; use charts only when n > 10 and the pattern is genuine. (Reports 01 vs. 07) |
| **Cross-platform comparison vs. metric incompatibility** | Use indexed scoring and small-multiples — never merge raw metrics. (Report 02) |
| **Dashboard polish vs. actual usage** | Build push mechanisms (Slack, email) first; dashboard second. A Slack alert that reaches 5 people beats a dashboard that reaches 0. (Reports 03, 06) |
| **Automation vs. editorial judgment** | Automate anomaly detection and data aggregation; keep "what does this mean?" and "what should we do?" as human-written sections in reports. (Reports 03, 06) |
| **Accessibility vs. visual richness** | Text summaries above charts satisfy both — the chart enhances, the text carries the message. Use Highcharts if full a11y is required, or add manual ARIA to ECharts. (Reports 07, 08) |
| **Recharts vs. ECharts** | ECharts is already in the stack and covers all needed patterns. Adding Recharts would mean maintaining two chart libraries. Stick with ECharts unless a specific component (e.g., Tremor stat cards) justifies the addition. (Reports 04, 07) |

---

## Recommended Build Sequence

Based on dependencies between the recommendations:

1. **Data model extensions** — Add `topic_categories`, `tags`, `campaign` fields to `VideoRecord` and database schema. Add `topicCategories` to the API fetch pipeline. (Report 05)

2. **API endpoints** — Build `/analytics/lifecycle`, `/analytics/catalog`, `/analytics/insights` endpoints. These feed all downstream visualization. (Reports 04, 05, 06)

3. **Engaged views + completion rate surfacing** — Wire existing `engaged_views` data to the Shorts dashboard. Add completion rate as a first-class metric. (Report 01)

4. **Per-video leaderboard table** — Sortable table with sparklines, benchmark indicators, and chip badges. The workhorse view for producers. (Reports 01, 05, 07)

5. **Insight cards** — Z-score anomaly detection, comparative framing, severity tiers. Start with template-based strings, add LLM summaries later. (Report 06)

6. **Weekly email digest** — Jinja2-templated HTML report, automated via launchd. Covers the "push don't pull" principle. (Report 03)

7. **Cross-platform comparison views** — Indexed scoring, small-multiple layouts, `cross_platform_posts` join table. Requires multi-platform data ingestion. (Report 02)

8. **Accessibility audit** — Color palette, ARIA labels, text alternatives, keyboard navigation, `prefers-reduced-motion`. (Report 08)

9. **Slack integration** — Webhook alerts for anomalies and viral content. (Report 06)

10. **Monthly/quarterly report templates** — Build on the weekly digest with deeper analysis sections. (Report 03)

---

## Library Recommendations

Resources with lasting value beyond this project — candidates for The Library:

- [ ] [Observable Plot](https://observablehq.com/plot/) — Declarative JS charting with excellent small-n support (dot plots, strip plots, faceted layouts)
- [ ] [Storytelling with Data (blog)](https://www.storytellingwithdata.com/blog) — Cole Nussbaumer Knaflic's ongoing data viz guidance
- [ ] [Tremor](https://www.tremor.so/) — React component library purpose-built for analytics dashboards (stat cards, leaderboards, sparklines)
- [ ] [Chartability](https://chartability.fizz.studio/) — Accessible data visualization testing workbook
- [ ] [Paul Tol's Colour Schemes](https://personal.sron.nl/~pault/) — Color-blind safe palettes for scientific/data visualization
- [ ] [TanStack Table Column Faceting](https://tanstack.com/table/latest/docs/guide/column-faceting) — Client-side filter counts with `getFacetedUniqueValues()`
- [ ] [YouTube Analytics API Dimensions Reference](https://developers.google.com/youtube/analytics/dimensions) — `creatorContentType`, `engagedViews`, and all available dimensions
- [ ] [IAB Podcast Content Taxonomy v2.0](https://iabtechlab.com/standards/content-taxonomy/) — Ready-made topic vocabulary mapping to PBS Wisconsin content
- [ ] [Rival IQ Social Media Benchmarks](https://www.rivaliq.com/blog/social-media-industry-benchmark-report/) — Annual cross-platform engagement rate benchmarks by vertical
- [ ] [Highcharts Accessibility Module Docs](https://www.highcharts.com/docs/accessibility/accessibility-module) — Gold standard for accessible chart implementation
- [ ] [NNGroup: Filters vs. Facets](https://www.nngroup.com/articles/filters-vs-facets/) — Foundational UX research for analytics filter bar design
- [ ] [Datawrapper Academy: Color Guide](https://academy.datawrapper.de/article/140-what-to-consider-when-choosing-colors-for-data-visualization) — Practical color choices for data visualization
- [ ] [UK Government Data Service Dashboards](https://design-system.service.gov.uk/) — Accessible government dashboard design patterns

---

## Methodology Notes

- All 8 reports were written from training knowledge (through August 2025) because WebSearch was unavailable to the background research agents. URLs should be verified before scraping into The Library.
- Reports are grounded in the actual codebase — agents read existing models, schemas, and components to ensure recommendations build on what exists rather than proposing greenfield rewrites.
- The ECharts vs. Recharts question was resolved in favor of ECharts because it's already a project dependency.
