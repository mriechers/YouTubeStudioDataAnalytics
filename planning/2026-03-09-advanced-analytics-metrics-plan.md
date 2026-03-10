# Plan: Advanced Insight-Driven Metrics Implementation

**Date:** 2026-03-09  
**Status:** Proposed  
**Author:** Gemini CLI Agent

## 1. Objective
Enhance the existing FastAPI/React dashboard with high-value metrics that move beyond "vanity" counts (views/likes) toward actionable production insights. This plan focuses on retention, audience loyalty, and content-format optimization for PBS Wisconsin.

## 2. Proposed Metrics & Value Proposition

### A. Retention & "Stickiness"
*   **Metric:** Average Percentage Viewed (APV) & 30s Retention.
*   **Value:** Helps producers identify where viewers drop off. A 50%+ APV indicates high-quality content; sharp drops in the first 30s suggest weak introductions.
*   **Data Source:** `averageViewPercentage` (Analytics API).

### B. Shorts Feed Health
*   **Metric:** Viewed vs. Swiped Ratio.
*   **Value:** The "CTR" of the Shorts feed. If >70% choose to view, the "hook" is working.
*   **Data Source:** `viewedPercentage` (Analytics API).

### C. The "Thumbnail vs. Content" Matrix
*   **Metric:** Click-Through Rate (CTR) vs. Average View Duration (AVD).
*   **Value:** A 2x2 scatter plot to categorize videos:
    *   **High CTR / Low AVD:** "Clickbait" (needs better content alignment).
    *   **Low CTR / High AVD:** "Hidden Gems" (needs better titles/thumbnails).
*   **Data Source:** `impressionClickThroughRate`, `averageViewDuration`.

### D. New vs. Returning Viewers
*   **Metric:** Loyalty Ratio.
*   **Value:** Distinguishes between "viral" one-off hits and "community-building" content that brings people back to the PBS brand.

### E. Traffic Source Attribution
*   **Metric:** Search vs. Browse vs. Suggested.
*   **Value:** Identifies if a show is "Utility" (Search-driven, like educational tips) or "Discovery" (Browse-driven, like *Wisconsin Life*).

### F. Evergreen Decay Score
*   **Metric:** Velocity Retention (Views at 365 days / Views at 30 days).
*   **Value:** Identifies which archival topics remain relevant years later, informing "evergreen" production strategies.

---

## 3. Technical Implementation Plan

### Phase 1: Data Layer & API Client (The "Plumbing")
1.  **Update `src/youtube_api/client.py`**:
    *   Expand `get_video_analytics` to include: `averageViewPercentage`, `impressionClickThroughRate`, `viewedPercentage`.
    *   Add `get_audience_loyalty(start_date, end_date)` using `newAndReturningViewers` dimension.
2.  **Update `src/youtube_api/database.py`**:
    *   Add columns to `VideoTable`: `avg_view_pct`, `ctr`, `viewed_vs_swiped_pct`.
    *   Add columns to `DailyStatsTable`: `ctr`, `avg_view_pct`.
3.  **Update `api/schemas.py`**:
    *   Add these fields to `VideoSummary`, `VideoWithContext`, and `ShortsDetailVideo`.

### Phase 2: Backend Logic (The "Brain")
1.  **Update `api/routers/analytics.py`**:
    *   **New Endpoint**: `GET /analytics/matrix` returns CTR/AVD coordinates for all videos.
    *   **New Endpoint**: `GET /analytics/loyalty` returns New vs. Returning timeseries.
2.  **Enrich `get_shorts_comparison`**: Include "Viewed vs. Swiped" in the KPI block.

### Phase 3: Frontend Visualization (The "Face")
1.  **Quadrant Chart (Overview)**: Create a scatter plot in ECharts for the CTR vs. AVD matrix.
2.  **Retention Sparklines**: Add a "Stickiness" sparkline to video tables showing APV over time.
3.  **Traffic Source Pie/Bar**: Add a breakdown of where views originate (Search vs. Suggested).

---

## 4. Migration & Backfill
1.  **Schema Migration**: Run `ALTER TABLE` via `database.py`'s existing migration logic.
2.  **Backfill Script**: Update `scripts/backfill_analytics.py` to fetch these new metrics for the last 90 days. *Note: Respect the 200-query-per-day quota.*

## 5. Success Criteria
*   Producers can identify "Hidden Gem" videos (High AVD, Low CTR) for thumbnail updates.
*   The Shorts strategy can be evaluated based on "Viewed vs. Swiped" rather than just view count.
*   The Archival panel ranks content by "Evergreen Score" to guide re-promotion.
