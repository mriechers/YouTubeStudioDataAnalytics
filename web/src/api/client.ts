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
};
