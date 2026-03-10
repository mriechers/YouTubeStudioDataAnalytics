const BASE = "/api/v1";

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json();
}

export interface ChannelConfig {
  id: string;
  name: string;
  type: string;
}

export interface VideoSummary {
  video_id: string;
  title: string;
  published_at: string | null;
  show_name: string | null;
  duration_minutes: number | null;
  is_short: boolean;
  content_type: string;
  views: number;
  likes: number;
  comments: number;
  engagement_rate: number;
  views_per_day: number;
  days_since_publication: number;
}

export interface ShowSummary {
  show_name: string | null;
  video_count: number;
  total_views: number;
  total_likes: number;
  avg_engagement: number;
  shorts_count: number;
}

export interface ShortsComparison {
  shorts: Record<string, number>;
  longform: Record<string, number>;
}

export interface OverviewKPIs {
  total_videos: number;
  total_views: number;
  total_subscribers: number;
  shorts_count: number;
  longform_count: number;
  shorts_ratio: number;
  avg_engagement: number;
}

export interface TimeseriesPoint {
  date: string;
  views: number;
  engaged_views: number | null;
  watch_time_minutes: number;
  subscribers_gained: number;
  subscribers_lost: number;
}

export interface DataStatus {
  last_refresh: string | null;
  video_count: number;
  database_path: string;
}

// --- Insight Dashboard Types ---

export interface HealthKPIs {
  subscriber_count: number;
  avg_daily_views: number;
  total_watch_time_hours: number;
  avg_view_duration_seconds: number;
  views_trend_pct?: number;
  watch_time_trend_pct?: number;
  subscribers_trend_pct?: number;
}

export interface ContentVelocity {
  new_uploads: number;
  avg_views_at_7d?: number;
  avg_views_at_30d?: number;
  catalog_view_pct: number;
  new_content_view_pct: number;
}

export interface HealthData {
  kpis: HealthKPIs;
  timeseries: TimeseriesPoint[];
  velocity: ContentVelocity;
  publishing_cadence: Array<{ week: string; count: number }>;
  watch_time_by_format: Array<Record<string, unknown>>;
}

export interface VideoWithContext {
  video_id: string;
  title: string;
  published_at?: string;
  show_name?: string;
  is_short?: boolean;
  views: number;
  likes: number;
  comments: number;
  engagement_rate?: number;
  views_per_day?: number;
  days_since_publication?: number;
  z_score: number;
  vs_show_multiplier: number;
  show_avg_vpd: number;
  subscribers_gained?: number;
}

export interface ShowHitRate {
  show_name: string;
  video_count: number;
  hit_count: number;
  hit_rate: number;
}

export interface HitsData {
  hit_count: number;
  avg_hit_multiplier: number;
  top_sub_driver?: string;
  best_show_hit_rate?: string;
  top_performers: VideoWithContext[];
  show_hit_rates: ShowHitRate[];
  subscriber_drivers: Array<Record<string, unknown>>;
}

export interface ShowVariance {
  show_name: string;
  video_count: number;
  avg_views_per_day: number;
  coeff_of_variation: number;
  hit_count: number;
  hit_rate: number;
}

export interface FormatGapShow {
  show_name: string;
  video_count: number;
  total_views?: number;
  avg_engagement?: number;
  avg_views_per_day?: number;
  channel_avg_views_per_day?: number;
  ratio?: number;
}

export interface OpportunitiesData {
  inconsistent_shows: ShowVariance[];
  catalog_risers: Array<Record<string, unknown>>;
  no_shorts: FormatGapShow[];
  underperforming: FormatGapShow[];
}

export interface RecentData {
  videos: VideoWithContext[];
  summary: {
    count: number;
    total_views: number;
    avg_views_per_day: number;
    avg_engagement: number;
  };
}

export const api = {
  getChannels: () => fetchJson<ChannelConfig[]>("/channels"),
  getVideos: (channelId?: string) =>
    fetchJson<VideoSummary[]>(
      channelId ? `/videos?channel_id=${channelId}` : "/videos"
    ),
  getVideo: (id: string) => fetchJson<VideoSummary>(`/videos/${id}`),
  getOverview: () => fetchJson<OverviewKPIs>("/analytics/overview"),
  getTimeseries: (days = 90) =>
    fetchJson<TimeseriesPoint[]>(`/analytics/timeseries?days=${days}`),
  getShows: () => fetchJson<ShowSummary[]>("/analytics/shows"),
  getShorts: () => fetchJson<ShortsComparison>("/analytics/shorts"),
  getArchival: (months = 12) =>
    fetchJson<VideoSummary[]>(`/analytics/archival?months=${months}`),
  getSubscribers: () => fetchJson<Record<string, unknown>[]>("/analytics/subscribers"),
  getDataStatus: () => fetchJson<DataStatus>("/data/status"),
  triggerRefresh: () =>
    fetch(`${BASE}/data/refresh`, { method: "POST" }).then((r) => r.json()),
  getHealth: (days = 90) =>
    fetchJson<HealthData>(`/analytics/health?days=${days}`),
  getHits: (days = 90) =>
    fetchJson<HitsData>(`/analytics/hits?days=${days}`),
  getOpportunities: () =>
    fetchJson<OpportunitiesData>("/analytics/opportunities"),
  getRecent: (days = 30) =>
    fetchJson<RecentData>(`/analytics/recent?days=${days}`),
};
