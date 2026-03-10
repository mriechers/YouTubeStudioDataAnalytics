import { createColumnHelper } from "@tanstack/react-table";
import BaseChart from "../components/BaseChart";
import DataTable from "../components/DataTable";
import EmptyState from "../components/EmptyState";
import ChartSummary from "../components/ChartSummary";
import { useShows } from "../hooks/useAnalytics";
import type { ShowSummary } from "../api/client";

const col = createColumnHelper<ShowSummary>();

const columns = [
  col.accessor("show_name", { header: "Show" }),
  col.accessor("video_count", { header: "Videos" }),
  col.accessor("total_views", {
    header: "Views",
    cell: (info: any) => info.getValue().toLocaleString(),
  }),
  col.accessor("total_likes", {
    header: "Likes",
    cell: (info: any) => info.getValue().toLocaleString(),
  }),
  col.accessor("avg_engagement", {
    header: "Avg Engagement %",
    cell: (info: any) => info.getValue().toFixed(2),
  }),
  col.accessor("shorts_count", { header: "Shorts" }),
] as const;

export default function Shows() {
  const { data: shows, isLoading } = useShows();

  if (isLoading) return <EmptyState message="Loading show data..." />;
  if (!shows?.length)
    return (
      <EmptyState
        message="No show data available."
        suggestion="Show names are parsed from video titles using the pipe separator pattern."
      />
    );

  const sorted = [...shows].sort((a, b) => b.total_views - a.total_views);

  const barOption = {
    tooltip: { trigger: "axis" as const },
    grid: { left: "20%", right: "5%" },
    xAxis: { type: "value" as const, name: "Total Views" },
    yAxis: {
      type: "category" as const,
      data: sorted.map((s) => s.show_name ?? "Unknown"),
      inverse: true,
    },
    series: [
      {
        type: "bar" as const,
        data: sorted.map((s) => s.total_views),
      },
    ],
  };

  const treemapOption = {
    tooltip: { trigger: "item" as const },
    series: [
      {
        type: "treemap" as const,
        data: sorted.map((s) => ({
          name: s.show_name ?? "Unknown",
          value: s.video_count,
        })),
      },
    ],
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Show Breakdown</h2>
      <div className="rounded-lg bg-gray-900 p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">Views by Show</h3>
        <ChartSummary>
          Total cumulative views per show, sorted highest to lowest. Longer bars indicate higher overall reach.
        </ChartSummary>
        <BaseChart
          option={barOption}
          height={`${Math.max(400, sorted.length * 30)}px`}
          ariaLabel="Horizontal bar chart showing total views by show, sorted from highest to lowest"
        />
      </div>
      <div className="rounded-lg bg-gray-900 p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">Catalog Size by Show</h3>
        <ChartSummary>
          Treemap showing relative catalog size (video count) per show. Larger tiles indicate more published videos.
        </ChartSummary>
        <BaseChart
          option={treemapOption}
          height="450px"
          ariaLabel="Treemap chart showing catalog size by show, where tile area represents video count"
        />
      </div>
      <div>
        <h3 className="mb-2 text-sm font-medium text-gray-400">All Show Metrics</h3>
        <DataTable data={sorted} columns={columns as any} />
      </div>
    </div>
  );
}
