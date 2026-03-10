# Backlog

Session scratchpad for tracking work items. Items here should be promoted to GitHub Issues when ready for formal tracking.

---

## High Priority

### Dashboard Integration
- [ ] Wire YouTubeAPIDataLoader into Streamlit dashboard
- [ ] Replace CSV loading paths with API data loader calls
- [ ] Update dashboard UI to show API connection status
- [ ] Add OAuth token refresh handling in dashboard

### PBS-Specific Dashboard Panels
- [ ] **Shorts → Longform Conversion Panel**: Track which Shorts drive views to longform content
- [ ] **Archival Content Performance Panel**: Surface older videos gaining new traction
- [ ] **Subscriber Source Attribution Panel**: Identify which videos/shows drive subscriptions
- [ ] **Show Breakdown Panel**: Per-show analytics with comparison views

---

## Medium Priority

### Automation & Data Management
- [ ] Automated daily data refresh (launchd job on macOS)
  - Schedule: 6 AM daily
  - Tasks: Fetch new video stats, update database, generate reports
  - Error handling: Email notifications on API quota exceeded
- [ ] Historical backfill script
  - Fetch all available historical data from YouTube Analytics API
  - Respect API rate limits (200 queries/day)
  - Store in SQLite for local querying

### Testing & Quality
- [ ] Add pytest test suite for `src/youtube_api/` module
- [ ] Integration tests for API authentication flow
- [ ] Mock YouTube API responses for CI/CD
- [ ] Validate PBS title pattern parser against real video titles

---

## Low Priority / Future Enhancements

### Multi-Channel Support
- [ ] Multi-channel comparison view (if PBS Wisconsin adds more channels)
- [ ] Channel switcher in dashboard UI
- [ ] Aggregate cross-channel metrics

### Advanced Analytics
- [ ] Predictive analytics: ML model for video performance prediction
- [ ] Trend detection: Identify emerging content patterns
- [ ] Competitive benchmarking: Compare against similar public media channels

### Developer Experience
- [ ] Add project-specific agents (YouTube Analytics Expert, PBS Content Strategist)
- [ ] Create knowledge/ directory with YouTube API best practices
- [ ] Document PBS Wisconsin video taxonomy in knowledge base

---

## Completed (Archive as items finish)

- [x] YouTube API integration module (`src/youtube_api/`)
- [x] OAuth2 authentication flow
- [x] SQLite database persistence
- [x] PBS-specific title pattern parser
- [x] Shorts detection logic
- [x] Repository modernization (CLAUDE.md, planning/, git hooks, manifest registration)

---

## Notes

**API Rate Limits to Monitor**:
- YouTube Data API v3: 10,000 quota units/day
- YouTube Analytics API: 200 queries/day/user
- Strategy: Cache aggressively in SQLite, only fetch new data

**PBS Wisconsin Show Taxonomy** (for title parser):
- Standard format: `"Video Title | SHOW NAME"`
- Exception: `"Wisconsin Life | Video Title"` (show name comes first)
- Other exceptions to document: TBD from Airtable analysis
