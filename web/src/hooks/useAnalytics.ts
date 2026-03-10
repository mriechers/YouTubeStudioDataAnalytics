import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export const useOverview = () =>
  useQuery({ queryKey: ["overview"], queryFn: api.getOverview });

export const useTimeseries = (days = 90) =>
  useQuery({
    queryKey: ["timeseries", days],
    queryFn: () => api.getTimeseries(days),
  });

export const useShows = () =>
  useQuery({ queryKey: ["shows"], queryFn: api.getShows });

export const useShorts = () =>
  useQuery({ queryKey: ["shorts"], queryFn: api.getShorts });

export const useArchival = (months = 12) =>
  useQuery({
    queryKey: ["archival", months],
    queryFn: () => api.getArchival(months),
  });

export const useSubscribers = () =>
  useQuery({ queryKey: ["subscribers"], queryFn: api.getSubscribers });

export const useVideos = (channelId?: string) =>
  useQuery({
    queryKey: ["videos", channelId],
    queryFn: () => api.getVideos(channelId),
  });

export const useDataStatus = () =>
  useQuery({ queryKey: ["dataStatus"], queryFn: api.getDataStatus });
