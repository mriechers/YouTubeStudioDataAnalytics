import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import { useChannel } from "./useChannel";

export const useOverview = () => {
  const { channelId } = useChannel();
  return useQuery({
    queryKey: ["overview", channelId],
    queryFn: () => api.getOverview(channelId),
  });
};

export const useTimeseries = (days = 90) => {
  const { channelId } = useChannel();
  return useQuery({
    queryKey: ["timeseries", days, channelId],
    queryFn: () => api.getTimeseries(days, channelId),
  });
};

export const useShows = () => {
  const { channelId } = useChannel();
  return useQuery({
    queryKey: ["shows", channelId],
    queryFn: () => api.getShows(channelId),
  });
};

export const useShorts = (days = 90) => {
  const { channelId } = useChannel();
  return useQuery({
    queryKey: ["shorts", days, channelId],
    queryFn: () => api.getShorts(days, channelId),
  });
};

export const useVideoDailyStats = (videoId: string, days = 30) =>
  useQuery({
    queryKey: ["videoDailyStats", videoId, days],
    queryFn: () => api.getVideoDailyStats(videoId, days),
    enabled: Boolean(videoId),
  });

export const useArchival = (months = 12) => {
  const { channelId } = useChannel();
  return useQuery({
    queryKey: ["archival", months, channelId],
    queryFn: () => api.getArchival(months, channelId),
  });
};

export const useSubscribers = () =>
  useQuery({ queryKey: ["subscribers"], queryFn: api.getSubscribers });

export const useVideos = (channelId?: string) =>
  useQuery({
    queryKey: ["videos", channelId],
    queryFn: () => api.getVideos(channelId),
  });

export const useDataStatus = () =>
  useQuery({ queryKey: ["dataStatus"], queryFn: api.getDataStatus });

export const useMatrix = () => {
  const { channelId } = useChannel();
  return useQuery({
    queryKey: ["matrix", channelId],
    queryFn: () => api.getMatrix(channelId),
  });
};

export const useLoyalty = (days = 30) =>
  useQuery({
    queryKey: ["loyalty", days],
    queryFn: () => api.getLoyalty(days),
  });
