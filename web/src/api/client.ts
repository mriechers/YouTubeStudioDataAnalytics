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
  avg_view_pct?: number;
  ctr?: number;
  viewed_vs_swiped_pct?: number;
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

export interface ShortsDetailVideo {
  video_id: string;
  title: string;
  published_at?: string;
  show_name?: string;
  views: number;
  likes: number;
  comments: number;
  engagement_rate?: number;
  avg_view_pct?: number;
  ctr?: number;
  viewed_vs_swiped_pct?: number;
  views_per_day?: number;
  days_since_publication?: number;
  sparkline?: number[];
}

export interface ShortsOverviewKPIs {
  count: number;
  total_views: number;
  total_engaged_views?: number;
  avg_views: number;
  avg_engagement: number;
  avg_views_per_day: number;
  viewed_vs_swiped_pct?: number;
  channel_avg_views: number;
}

export interface ShortsFullResponse {
  kpis: ShortsOverviewKPIs;
  comparison: ShortsComparison;
  videos: ShortsDetailVideo[];
  timeseries: TimeseriesPoint[];
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
  avg_view_pct?: number;
  ctr?: number;
  viewed_vs_swiped_pct?: number;
  subscribers_gained: number;
  subscribers_lost: number;
}

export interface AudienceLoyaltyPoint {
  date: string;
  new_views: number;
  returning_views: number;
}

export interface AudienceLoyaltyResponse {
  timeseries: AudienceLoyaltyPoint[];
  summary: {
    total_new: number;
    total_returning: number;
    loyalty_ratio: number;
  };
}

export interface DataStatus {
  last_refresh: string | null;
  video_count: number;
  database_path: string;
}

function channelParam(channelId?: string): string {
  return channelId ? `channel_id=${channelId}` : "";
}

function qs(...params: string[]): string {
  const filtered = params.filter(Boolean);
  return filtered.length ? `?${filtered.join("&")}` : "";
}

export const api = {
  getChannels: () => fetchJson<ChannelConfig[]>("/channels"),
  getVideos: (channelId?: string) =>
    fetchJson<VideoSummary[]>(`/videos${qs(channelParam(channelId))}`),
  getVideo: (id: string) => fetchJson<VideoSummary>(`/videos/${id}`),
  getOverview: (channelId?: string) =>
    fetchJson<OverviewKPIs>(`/analytics/overview${qs(channelParam(channelId))}`),
  getTimeseries: (days = 90, channelId?: string) =>
    fetchJson<TimeseriesPoint[]>(
      `/analytics/timeseries${qs(`days=${days}`, channelParam(channelId))}`
    ),
  getShows: (channelId?: string) =>
    fetchJson<ShowSummary[]>(`/analytics/shows${qs(channelParam(channelId))}`),
  getShorts: (days = 90, channelId?: string) =>
    fetchJson<ShortsFullResponse>(
      `/analytics/shorts${qs(`days=${days}`, channelParam(channelId))}`
    ),
  getMatrix: (channelId?: string) =>
    fetchJson<VideoSummary[]>(`/analytics/matrix${qs(channelParam(channelId))}`),
  getLoyalty: (days = 30) =>
    fetchJson<AudienceLoyaltyResponse>(`/analytics/loyalty${qs(`days=${days}`)}`),
  getVideoDailyStats: (videoId: string, days = 30) =>
    fetchJson<TimeseriesPoint[]>(
      `/analytics/videos/${videoId}/daily${qs(`days=${days}`)}`
    ),
  getArchival: (months = 12, channelId?: string) =>
    fetchJson<VideoSummary[]>(
      `/analytics/archival${qs(`months=${months}`, channelParam(channelId))}`
    ),
  getSubscribers: () => fetchJson<Record<string, unknown>[]>("/analytics/subscribers"),
  getDataStatus: () => fetchJson<DataStatus>("/data/status"),
  triggerRefresh: () =>
    fetch(`${BASE}/data/refresh`, { method: "POST" }).then((r) => r.json()),
};
