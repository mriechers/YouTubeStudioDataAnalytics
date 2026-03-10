# Content Categorization & Tagging UX — Research Report

## Summary

Media organizations managing multi-show, multi-platform content need a categorization system that balances automated signal extraction with lightweight manual curation. The most effective approaches layer structured taxonomy (show/series as the primary anchor) over flexible flat tags (topic, format, campaign), with automation handling the deterministic cases (title parsing, duration detection) and a minimal human-in-the-loop for ambiguous or cross-cutting categories. For a small-volume operation like PBS Wisconsin (5–20 pieces/month), a title-pattern-first pipeline with a YAML override layer and SQLite-stored manual tags is both sufficient and maintainable without requiring NLP infrastructure. Faceted filtering with multi-select dropdowns and saved presets is the established UX pattern for analytics catalog views, and a sortable table with inline chip badges is the highest-density format for a content inventory at this scale.

---

## Key Findings

1. **Show/series is the right primary dimension.** CMS platforms (Arc XP, Brightcove, WordPress VIP) universally treat the publication/series as the root node of their content taxonomy. For PBS Wisconsin, `show_name` extracted from the pipe-delimited title pattern is already the correct anchor. Every other dimension (content type, topic, campaign) should be a secondary attribute layered on top of show.

2. **Flat tags beat deep hierarchies at small scale.** Systems like Brightcove's Video Cloud use a two-level structure (folder + tags), not a deep tree. WordPress uses categories (1–2 levels) plus tags (flat). Deep hierarchies (Show > Season > Episode > Clip) create maintenance overhead that outweighs their query value when the catalog is under a few thousand items. For PBS Wisconsin, a flat `tags[]` array on each video alongside `show_name`, `content_type`, and optional `campaign` string covers all practical filter combinations.

3. **Automation should handle deterministic signals; humans handle semantics.** Title parsing (already implemented), duration-based Shorts detection (already implemented), and YouTube's `topicCategories` from the Data API (free, no quota cost beyond the video list call) provide reliable automated signals. Topic/theme labels like "Nature" or "History" require either NLP or manual assignment — at 5–20 videos/month, a one-time manual tagging pass during or after upload is cheaper than building an NLP classifier.

4. **YouTube's `topicCategories` field is underused.** The YouTube Data API v3 `videos.list` endpoint returns `topicDetails.topicCategories[]` — an array of Wikipedia topic URLs (e.g., `https://en.wikipedia.org/wiki/Nature`) — at no additional quota cost when included in the `part=topicDetails` request. These map to a stable set of ~30 Freebase-derived categories. PBS Wisconsin videos about nature or science will likely already carry these signals from YouTube's own classifier.

5. **Faceted filtering is the dominant analytics UX pattern.** Tableau, Looker, Grafana, and purpose-built media analytics tools like Tubular Labs and Social Blade all use the same core pattern: a filter sidebar or filter bar with per-dimension multi-select controls, active filters displayed as dismissible chips/pills, and a live-updating results table or chart grid. This pattern should be the target for the PBS Wisconsin catalog view.

6. **Saved filter presets are disproportionately valuable for recurring workflows.** Analytics tools (Looker, Tableau) show that power users spend most of their time applying the same 3–5 filter combinations repeatedly (e.g., "Here & Now Shorts this quarter"). Storing named filter presets in localStorage or user preferences eliminates this friction and is a low-effort, high-value feature.

7. **The content inventory table is the workhorse view.** Card grid layouts favor thumbnails and are suited to discovery; sortable table views favor comparison across metrics and are suited to analytics. At PBS Wisconsin's scale, a sortable table with thumbnail + title in the first column, inline badge chips for content type and show, and sortable numeric columns for views/engagement is the right default. An optional card grid can be added as a toggle for show-level views.

8. **Campaign/series tracking requires a dedicated grouping field, not just tags.** Social media tools (Sprout Social, Later, Hootsuite) expose a concept of "campaigns" — a named grouping with a date range that can span multiple posts across platforms. This is distinct from the `show_name` dimension. A `campaign` string field on the video record enables queries like "all content published for the Summer in Wisconsin push" across shows.

9. **Multi-platform tracking needs a join table, not a field.** A single video may be published on YouTube, Instagram (Reels), TikTok, and Facebook as separate items with different IDs and native metrics. The right data model is a `content_piece` parent with a `platform_posts` one-to-many relationship — not a `platform` field on the YouTube-specific video record. This is how tools like Sprout Social and ContentStudio model cross-platform analytics.

10. **Brightcove and Arc XP use explicit content types as a controlled vocabulary, not free tags.** Both CMS platforms define content type as an enum (clip, episode, short, feature, archive) at the schema level, not as a free-text field. This prevents tag proliferation and enables reliable aggregation. PBS Wisconsin's `ContentType` enum (already in `models.py`) is aligned with this pattern.

---

## Tools & Technologies

### Taxonomy & Metadata Platforms

**Arc XP (Washington Post's CMS platform)**
- Uses `taxonomy.tags` (flat, freeform), `taxonomy.sections` (hierarchical, site-specific), and `type` (controlled enum: story, gallery, video, etc.)
- Canonical taxonomy stored in a central "taxonomy service"; all content references taxonomy IDs rather than embedding strings
- Enables renaming a tag globally without touching content records
- Reference: https://docs.arcxp.com/alc/arc-products/arcio/taxonomy

**Brightcove Video Cloud**
- Videos have `tags[]` (flat string array), `folder_id` (single parent folder), and `custom_fields` (configurable key-value)
- Custom fields can be typed (enum, text, date) and are the recommended path for structured metadata like show name and content type
- `tags` are intended for unstructured search/filter, not analytics grouping — Brightcove's own documentation distinguishes these use cases
- Reference: https://apis.support.brightcove.com/cms/references/cms-api-video-fields-reference.html

**WordPress (including VIP)**
- `categories`: hierarchical, typically 2 levels (section > subsection), each post assigned to 1–3
- `tags`: flat, many-to-many, intended for keyword indexing
- Custom taxonomies: registered via `register_taxonomy()`, can be hierarchical or flat, scoped to post types
- Best practice for media: use categories for navigation/structure, custom taxonomy for editorial metadata (show, format), tags for topic/keyword
- Reference: https://developer.wordpress.org/reference/functions/register_taxonomy/

**YouTube Data API v3**
- `snippet.tags[]`: channel-assigned freeform tags (up to 500 characters total)
- `snippet.categoryId`: single YouTube content category (integer, maps to a predefined list)
- `topicDetails.topicCategories[]`: array of Wikipedia URLs (e.g., `https://en.wikipedia.org/wiki/Music`) — assigned by YouTube's classifier, not the creator
- `snippet.defaultAudioLanguage`, `snippet.defaultLanguage`: useful for PBS archival content
- Analytics API `creatorContentType` dimension: returns `SHORTS`, `VIDEO_ON_DEMAND`, `LIVE_STREAM`, `STORY`, `UNSPECIFIED` — the authoritative source for content type (already used in `models.py`)
- Reference: https://developers.google.com/youtube/v3/docs/videos#resource

### Automated Tagging Approaches

**Title Parsing (already implemented)**
- `extract_show_name()` in `src/youtube_api/show_parser.py` handles the PBS Wisconsin pipe pattern
- Canonical normalization via `config/show_mappings.yaml`
- Should be treated as the ground truth for `show_name`; NLP should not override it

**YouTube `topicCategories` (free, recommended)**
- Fetched as part of `videos.list?part=topicDetails`
- Returns stable Wikipedia category URLs, parseable to a label by stripping the URL base
- No additional quota cost when batched with existing video list calls
- Covers broad theme categories well (nature, history, culture, education, science)
- Does not cover PBS-specific topics (local news, Wisconsin history, public media)

**Duration-based Classification (already implemented)**
- `is_short` computed from `duration_minutes <= 3.0` with `content_type` override
- YouTube expanded Shorts to 3 minutes in October 2024 — already reflected in the model

**Description/Tag NLP (optional, medium complexity)**
- spaCy or a lightweight zero-shot classifier (HuggingFace `facebook/bart-large-mnli`) can classify descriptions into topic buckets
- At 5–20 videos/month, the payoff is low; manual tagging is faster and more accurate
- Worth revisiting if catalog grows to 500+ videos or if description quality is high

**YouTube Chapters / Timestamps**
- Videos with chapters in the description expose structured segment data via the YouTube API (`snippet.localized.description` parsing)
- Chapter titles are rich text signals for topic classification ("Wisconsin Wildlife", "Breaking News", etc.)
- No dedicated API field — requires parsing the `##:## Title` format from description text

### Filter & Search Libraries

**TanStack Table (already in use)**
- `getFilteredRowModel()` + `columnFilters` state enables per-column filtering
- Combine with a custom `FilterBar` component that renders multi-select controls
- Supports global filter (full-text search across all columns) via `getGlobalFilteredRowModel()`
- Reference: https://tanstack.com/table/v8/docs/guide/column-filtering

**Fuse.js**
- Lightweight fuzzy search for in-memory datasets; ideal for catalog search at <10,000 records
- No server round-trip; works entirely in the browser on the existing JSON payload
- Reference: https://www.fusejs.io/

**Downshift / Headless UI Combobox**
- Accessible multi-select combobox components for filter controls
- Downshift is composable and works with any styling system
- Headless UI (Tailwind) provides a `Combobox` component that matches the existing dark theme

---

## Examples in the Wild

### 1. Tubular Labs — Media-specific content analytics

Tubular Labs is the analytics platform of record for large media companies (Condé Nast, NBCUniversal, BBC). Its filter model is the gold standard for multi-dimensional video content analysis:

- Left sidebar with collapsible filter sections: Platform, Content Type, Creator, Topic, Time Period
- Each filter section renders a multi-select list with counts next to each value (e.g., "YouTube Shorts (142)")
- Active filters shown as dismissible chips in a "filter bar" above the results
- Results update live as filters change (no "Apply" button)
- Filter state serialized into the URL for sharing
- This is the exact pattern PBS Wisconsin should target for its catalog view

### 2. Chartable (acquired by Spotify) — Podcast taxonomy

Chartable's taxonomy model is instructive for public media:
- Shows at the top level (equivalent to PBS Wisconsin's series)
- Episodes as the primary content unit
- IAB content categories as the controlled topic vocabulary (21 top-level, 200+ sub-categories)
- "Campaigns" for tracking promotional pushes with UTM-style attribution
- Playlist/collection groupings for related episode series within a show
- The IAB podcast content taxonomy (https://iabtechlab.com/standards/podcast-taxonomy/) is a well-maintained public standard that PBS Wisconsin could adopt for topic classification

### 3. Looker (Google Cloud) — Saved filter presets / "Explores"

Looker's "Explore" interface demonstrates saved filter presets at their best:
- Users define a filter combination (dimensions + metrics + date range) and save it as a named "Explore"
- Explores can be shared, embedded, and scheduled for email delivery
- The URL encodes the full filter state so any filter view is shareable
- For PBS Wisconsin: saved presets like "Here & Now — Last Quarter" or "All Shorts — 2025" would cover 80% of recurring reporting needs

### 4. Sprout Social — Cross-platform content inventory

Sprout Social's "Publishing" view demonstrates cross-platform content tracking:
- Each post is a platform-specific item (YouTube, Instagram, TikTok) linked to a parent "Campaign"
- Campaign view shows aggregate performance across platforms with per-platform breakdowns
- Tags are applied at the campaign level and inherited by constituent posts
- The "Content Calendar" view shows all content across platforms in a unified timeline
- For PBS Wisconsin: a `campaign` field on the video record + a campaign-level rollup view in the API

### 5. Airtable Gallery/Grid toggle — Content catalog UX

Airtable's interface (directly relevant since it's already used for PBS Wisconsin show metadata) demonstrates the table/card toggle pattern:
- Grid view: dense table with all metadata columns, sortable, filterable, row height adjustable
- Gallery view: card grid with cover image, title, and 2–3 key fields
- Kanban view: columns by status/show for editorial workflow
- The PBS Wisconsin dashboard already uses DataTable (TanStack Table) for the grid view; a card grid toggle using the thumbnail URL stored in `Video.thumbnail_url` would complete this pattern

---

## Code Patterns & Implementation Notes

### Extended Data Model

The current `VideoRecord` model should be extended with three new fields to support flexible categorization:

```python
# In src/youtube_api/models.py

class VideoRecord(BaseModel):
    # ... existing fields ...

    # Manual/override tags — flat list of freeform strings
    # Examples: ["nature", "summer-series-2025", "clip"]
    tags: List[str] = Field(default_factory=list)

    # Campaign/series grouping — optional named content push
    # Examples: "Summer in Wisconsin 2025", "Black History Month"
    campaign: Optional[str] = None

    # Topic categories from YouTube's topicDetails classifier
    # Stored as extracted labels: ["Nature", "History", "Education"]
    topic_categories: List[str] = Field(default_factory=list)
```

And the corresponding SQLAlchemy table extension:

```python
# In src/youtube_api/database.py — VideoTable

# JSON-serialized list of strings
tags = Column(String, default='[]')          # stored as JSON
topic_categories = Column(String, default='[]')  # stored as JSON
campaign = Column(String, nullable=True)

# New index
Index('idx_videos_campaign', 'campaign'),
```

### Tag Extraction from YouTube API

```python
# In src/youtube_api/client.py — after fetching video list

import json

def _extract_topic_labels(topic_categories: list[str]) -> list[str]:
    """Convert YouTube topicCategories URLs to readable labels.

    Input:  ['https://en.wikipedia.org/wiki/Nature']
    Output: ['Nature']
    """
    labels = []
    for url in topic_categories:
        if '/wiki/' in url:
            label = url.split('/wiki/')[-1].replace('_', ' ')
            labels.append(label)
    return labels

# In the video mapping logic:
topic_cats = item.get('topicDetails', {}).get('topicCategories', [])
video_data['topic_categories'] = json.dumps(
    _extract_topic_labels(topic_cats)
)
```

### Faceted Filter Component (React/TypeScript)

The existing `DataTable` in `web/src/components/DataTable.tsx` uses TanStack Table but lacks filtering. The recommended pattern is a `FilterBar` component above the table:

```typescript
// web/src/components/FilterBar.tsx

interface FilterOption {
  value: string;
  label: string;
  count: number;
}

interface FilterBarProps {
  filters: {
    shows: FilterOption[];
    contentTypes: FilterOption[];
    campaigns: FilterOption[];
    topics: FilterOption[];
  };
  activeFilters: Record<string, string[]>;
  onChange: (dimension: string, values: string[]) => void;
  onClear: () => void;
}

// Each dimension renders a MultiSelect dropdown
// Active filters render as dismissible chips below the dropdowns
// "Clear all" button when any filters are active
```

Wire into TanStack Table with `columnFilters` state:

```typescript
// Extend DataTable to accept and apply column filters
const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

const table = useReactTable({
  // ...existing config...
  state: { sorting, columnFilters },
  onColumnFiltersChange: setColumnFilters,
  getFilteredRowModel: getFilteredRowModel(),
  // Custom filter function for array-valued columns (tags, topic_categories)
  filterFns: {
    includesAny: (row, columnId, filterValues: string[]) => {
      const cellValue = row.getValue(columnId) as string[];
      return filterValues.some(v => cellValue.includes(v));
    },
  },
});
```

### Filter Preset Persistence

```typescript
// web/src/hooks/useFilterPresets.ts

const STORAGE_KEY = 'pbswi_filter_presets';

interface FilterPreset {
  id: string;
  name: string;
  filters: Record<string, string[]>;
  createdAt: string;
}

export function useFilterPresets() {
  const [presets, setPresets] = useState<FilterPreset[]>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  });

  const savePreset = (name: string, filters: Record<string, string[]>) => {
    const preset: FilterPreset = {
      id: crypto.randomUUID(),
      name,
      filters,
      createdAt: new Date().toISOString(),
    };
    const updated = [...presets, preset];
    setPresets(updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  };

  const deletePreset = (id: string) => {
    const updated = presets.filter(p => p.id !== id);
    setPresets(updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  };

  return { presets, savePreset, deletePreset };
}
```

### API Query Parameters for Filtered Catalog

Extend the analytics router to support multi-value filter parameters:

```python
# api/routers/analytics.py — new catalog endpoint

@router.get("/analytics/catalog")
def get_catalog(
    channel_id: Optional[str] = Query(None),
    show: Optional[List[str]] = Query(None),        # ?show=Here+%26+Now&show=Wisconsin+Life
    content_type: Optional[List[str]] = Query(None), # ?content_type=SHORTS
    campaign: Optional[str] = Query(None),
    topic: Optional[List[str]] = Query(None),
    min_views: Optional[int] = Query(None),
    max_age_months: Optional[int] = Query(None),
    sort_by: str = Query("published_at"),
    sort_dir: str = Query("desc"),
    limit: int = Query(50, le=500),
    offset: int = Query(0),
    db=Depends(get_db),
):
    """Filterable video catalog endpoint."""
    return db.get_catalog(
        channel_id=channel_id,
        shows=show,
        content_types=content_type,
        campaign=campaign,
        topics=topic,
        min_views=min_views,
        max_age_months=max_age_months,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=limit,
        offset=offset,
    )
```

### YAML-based Manual Tag Override

For the small-scale case, a simple YAML file avoids the need for an admin UI:

```yaml
# config/video_tags.yaml
# Manual tag overrides applied during database upsert.
# Keyed by video_id.

UCyY2ABh4q3fA:
  campaign: "Summer in Wisconsin 2025"
  tags: ["nature", "original"]

UCyY2ABh4bZxR:
  campaign: "Summer in Wisconsin 2025"
  tags: ["wildlife", "shorts-clip"]
```

Load during `upsert_videos_bulk()` to merge manual tags with API-derived tags. This approach works cleanly at 5–20 videos/month and requires no database admin tooling.

### Content Inventory View Layout

```
+------------------------------------------------------------------+
| [Search...]  [Show ▼]  [Type ▼]  [Topic ▼]  [Campaign ▼]  [Saved ▼] |
| Active: Here & Now ✕   SHORTS ✕   [Clear all]                    |
+------------------------------------------------------------------+
| Thumbnail | Title + Show badge | Type | Published | Views | Eng% |
|-----------|-------------------|------|-----------|-------|------|
| [img]     | Title text        | [S]  | 2025-01  | 42.1K | 3.2% |
|           | Here & Now        |      |           |       |      |
+------------------------------------------------------------------+
  Showing 23 of 187 videos   [< Prev]  [1] [2] [3]  [Next >]
```

The badge in the Type column should use a compact chip: `[S]` for Shorts, `[LF]` for longform, `[LIVE]` for streams — color-coded to enable fast visual scanning.

---

## Gotchas & Anti-Patterns

**1. Hierarchical tag trees for small catalogs.** A Show > Season > Episode taxonomy is appropriate for Netflix's catalog of 50,000 titles, not for a 500-video public media channel. Deep hierarchies fragment small datasets into near-empty buckets and make queries verbose. Flat `show_name` + flat `tags[]` is sufficient for PBS Wisconsin.

**2. Using YouTube's freeform `snippet.tags` as the analytics taxonomy.** YouTube's video tags are SEO-optimized freeform strings entered by the uploader, not a controlled vocabulary. They will be inconsistent across videos and shows ("Wisconsin" vs "Wisconsin PBS" vs "WPT"). Treat them as a search signal, not a filter dimension.

**3. Conflating content type with format.** "Short" describes format (duration/platform feature); "clip" describes provenance (derived from a longer piece); "repurposed broadcast" describes rights/origin. These are three different dimensions, not synonyms. The PBS Wisconsin model should track them separately rather than trying to encode them in a single `content_type` enum.

**4. Requiring API round-trips for facet counts.** The count next to each filter option ("Here & Now (23)") should be computed from the in-memory dataset already fetched, not from a separate API call. Separate count queries per dimension quickly exhaust the query budget (5 dimensions × 5 filter changes = 25 queries). Use the TanStack Table filtered row model to compute counts client-side.

**5. Overbuilding the admin UI before the taxonomy is stable.** A full CRUD admin interface for managing tags and campaigns is expensive to build and will be abandoned if the taxonomy changes three times during its first month. Start with YAML config files for manual overrides; add a UI only when the manual file reaches ~20+ entries and the taxonomy has stabilized.

**6. Not serializing filter state to the URL.** Filter combinations discovered during an analytics session should be shareable. Storing filter state only in React state (not in the URL query string) means every session restarts from scratch and no filter can be linked in a Slack message or saved in Obsidian. Use a library like `nuqs` (https://nuqs.47ng.com/) or manual `URLSearchParams` to sync filter state with the URL.

**7. Applying NLP classifiers to short titles.** PBS Wisconsin titles like "Here & Now | Wisconsin Budget Debate" are too short and domain-specific for general NLP models to classify reliably. `topicCategories` from YouTube's own classifier will outperform a general-purpose zero-shot model on this data.

**8. Storing tags as a delimited string instead of JSON.** SQLite does not have a native array type, but storing tags as `"nature,history,clip"` makes queries brittle (LIKE '%nature%' will match "nature-documentary") and schema migrations painful. Store as a JSON array string (`'["nature","history","clip"]'`) and parse in the ORM layer.

---

## Sources & Further Reading

- YouTube Data API v3 — Videos resource reference: https://developers.google.com/youtube/v3/docs/videos#resource
- YouTube Analytics API — `creatorContentType` dimension: https://developers.google.com/youtube/analytics/dimensions#Video_Dimensions
- Brightcove CMS API — Video fields reference: https://apis.support.brightcove.com/cms/references/cms-api-video-fields-reference.html
- Arc XP taxonomy service documentation: https://docs.arcxp.com/alc/arc-products/arcio/taxonomy
- WordPress `register_taxonomy()` developer reference: https://developer.wordpress.org/reference/functions/register_taxonomy/
- IAB Podcast Taxonomy (v2.0) — controlled vocabulary for media content: https://iabtechlab.com/standards/podcast-taxonomy/
- TanStack Table v8 — column filtering guide: https://tanstack.com/table/v8/docs/guide/column-filtering
- TanStack Table v8 — faceted values (counts for filter options): https://tanstack.com/table/v8/docs/guide/column-faceting
- Fuse.js — fuzzy search for JavaScript: https://www.fusejs.io/
- nuqs — URL-synced state for Next.js/React: https://nuqs.47ng.com/
- Headless UI Combobox (multi-select): https://headlessui.com/v2/react/combobox
- Downshift — accessible combobox primitives: https://www.downshift-js.com/
- Sprout Social — content tagging and campaign analytics: https://sproutsocial.com/features/analytics/
- Chartable podcast taxonomy model (archived, acquired by Spotify 2022): https://chartable.com/
- "Designing Data-Intensive Applications" (Kleppmann, 2017) — Chapter 2 on data models and taxonomy schemas
- Nielsen Norman Group — Faceted Navigation UX: https://www.nngroup.com/articles/filters-vs-facets/
- Baymard Institute — E-Commerce UX of Filtering (applicable to analytics catalog views): https://baymard.com/research/filters

---

## Recommended for The Library

The following resources are most worth scraping into The Library for future reference during implementation:

1. **TanStack Table v8 Column Faceting guide** — https://tanstack.com/table/v8/docs/guide/column-faceting — Explains `getFacetedUniqueValues()` and `getFacetedMinMaxValues()` which compute the filter option counts needed for the faceted filter sidebar without additional API calls.

2. **YouTube Analytics API dimensions reference** — https://developers.google.com/youtube/analytics/dimensions — Comprehensive list of all `creatorContentType`, `insightTrafficSourceType`, and other dimensions available in the Analytics API. Critical for knowing what categorization signals are available free from the API itself.

3. **YouTube Data API v3 `topicDetails` resource** — https://developers.google.com/youtube/v3/docs/videos#topicDetails — Documents the `topicCategories` field including the full list of ~30 supported Wikipedia category URLs. Useful for building the label extraction mapping.

4. **IAB Podcast Content Taxonomy v2.0** — https://iabtechlab.com/standards/podcast-taxonomy/ — The most mature public-media-adjacent controlled vocabulary for content topics. The top-level categories (News & Politics, Society & Culture, Education, Science, Arts) map cleanly onto PBS Wisconsin's content mix and provide a ready-made topic tag vocabulary.

5. **Nielsen Norman Group — Filters vs Facets** — https://www.nngroup.com/articles/filters-vs-facets/ — Foundational UX research distinguishing filtering (reducing results) from faceting (navigating by attribute). Defines the interaction patterns that should inform the PBS Wisconsin catalog filter bar design.
