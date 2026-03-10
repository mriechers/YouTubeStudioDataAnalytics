import { useState } from "react";
import { createColumnHelper } from "@tanstack/react-table";
import KpiCard from "../components/KpiCard";
import KpiRow from "../components/KpiRow";
import BaseChart from "../components/BaseChart";
import DataTable from "../components/DataTable";
import EmptyState from "../components/EmptyState";
import ChartSummary from "../components/ChartSummary";
import { useArchival } from "../hooks/useAnalytics";
import type { VideoSummary } from "../api/client";

const col = createColumnHelper<VideoSummary>();

const columns = [
  col.accessor("title", { header: "Title" }),
  col.accessor("show_name", { header: "Show" }),
  col.accessor("views", {
    header: "Views",
    cell: (info: any) => info.getValue().toLocaleString(),
  }),
  col.accessor("views_per_day", {
    header: "Views/Day",
    cell: (info: any) => info.getValue().toFixed(1),
  }),
  col.accessor("engagement_rate", {
    header: "Engagement %",
    cell: (info: any) => info.getValue().toFixed(2),
  }),
  col.accessor("days_since_publication", {
    header: "Age (months)",
    cell: (info: any) => Math.round(info.getValue() / 30),
  }),
] as const;

export default function Archival() {
  const [months, setMonths] = useState(12);
  const { data: videos, isLoading } = useArchival(months);

  if (isLoading) return <EmptyState message="Loading archival data..." />;
  if (!videos?.length)
    return (
      <EmptyState
        message={`No archival videos found older than ${months} months.`}
        suggestion="Try reducing the age threshold using the slider above."
      />
    );

  const sorted = [...videos].sort((a, b) => b.views_per_day - a.views_per_day);
  const top10 = sorted.slice(0, 10);

  const totalViews = videos.reduce((s, v) => s + v.views, 0);
  const avgVpd = videos.reduce((s, v) => s + v.views_per_day, 0) / videos.length;

  const scatterOption = {
    tooltip: { trigger: "item" as const },
    xAxis: { type: "value" as const, name: "Age (months)" },
    yAxis: { type: "value" as const, name: "Views per Day" },
    series: [
      {
        type: "scatter" as const,
        data: videos.map((v) => ({
          value: [Math.round(v.days_since_publication / 30), v.views_per_day],
          name: v.title,
        })),
        symbolSize: 8,
      },
    ],
  };

  const barOption = {
    tooltip: { trigger: "axis" as const },
    grid: { left: "30%", right: "5%" },
    xAxis: { type: "value" as const, name: "Views per Day" },
    yAxis: {
      type: "category" as const,
      data: top10.map((v) => v.title.slice(0, 40)),
      inverse: true,
    },
    series: [
      {
        type: "bar" as const,
        data: top10.map((v) => v.views_per_day),
      },
    ],
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Archival Performance</h2>
        <label className="text-sm text-gray-400">
          Threshold:{" "}
          <input
            type="range"
            min={6}
            max={36}
            value={months}
            onChange={(e) => setMonths(Number(e.target.value))}
            className="ml-2 w-32"
          />
          <span className="ml-2 text-white">{months} months</span>
        </label>
      </div>
      <KpiRow>
        <KpiCard label="Archival Videos" value={videos.length.toLocaleString()} />
        <KpiCard label="Total Views" value={totalViews.toLocaleString()} />
        <KpiCard label="Avg Views/Day" value={avgVpd.toFixed(1)} />
      </KpiRow>
      <div className="rounded-lg bg-gray-900 p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">Age vs Daily Velocity</h3>
        <ChartSummary>
          Each dot is a video older than {months} months. Higher on the Y axis means more daily views — these are your evergreen performers.
        </ChartSummary>
        <BaseChart
          option={scatterOption}
          height="400px"
          ariaLabel="Scatter chart showing archival video age in months versus daily view velocity, identifying evergreen content"
        />
      </div>
      <div className="rounded-lg bg-gray-900 p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">Top 10 by Daily Velocity</h3>
        <ChartSummary>
          The 10 archival videos currently earning the most daily views — strong candidates for promotion or updates.
        </ChartSummary>
        <BaseChart
          option={barOption}
          height="400px"
          ariaLabel="Horizontal bar chart showing the top 10 archival videos ranked by daily view velocity"
        />
      </div>
      <div>
        <h3 className="mb-2 text-sm font-medium text-gray-400">Top 20 Archival Videos</h3>
        <DataTable data={sorted.slice(0, 20)} columns={columns as any} />
      </div>
    </div>
  );
}
