import { useState } from "react";
import type { ColumnDef } from "@tanstack/react-table";
import type { EChartsOption } from "echarts";
import KpiCard from "../components/KpiCard";
import KpiRow from "../components/KpiRow";
import BaseChart from "../components/BaseChart";
import DataTable from "../components/DataTable";
import SparklineCell from "../components/SparklineCell";
import PeriodSelector from "../components/PeriodSelector";
import EmptyState from "../components/EmptyState";
import ChartSummary from "../components/ChartSummary";
import { useShorts } from "../hooks/useAnalytics";
import { rollingAverage, addBenchmarkLine } from "../utils/chartHelpers";
import type { ShortsDetailVideo } from "../api/client";

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
}

function truncate(s: string, max: number): string {
  return s.length > max ? s.slice(0, max) + "…" : s;
}

const VIDEO_COLUMNS: ColumnDef<ShortsDetailVideo, unknown>[] = [
  {
    id: "title",
    header: "Title",
    accessorFn: (row) => row.title,
    cell: (info) => truncate(info.getValue() as string, 50),
  },
  {
    id: "show_name",
    header: "Show",
    accessorFn: (row) => row.show_name ?? "—",
  },
  {
    id: "views",
    header: "Views",
    accessorFn: (row) => row.views,
    cell: (info) => formatNumber(info.getValue() as number),
  },
  {
    id: "viewed_vs_swiped_pct",
    header: "Viewed vs. Swiped",
    accessorFn: (row) => row.viewed_vs_swiped_pct ?? 0,
    cell: (info) => `${((info.getValue() as number) ?? 0).toFixed(1)}%`,
  },
  {
    id: "avg_view_pct",
    header: "Retention (APV)",
    accessorFn: (row) => row.avg_view_pct ?? 0,
    cell: (info) => `${((info.getValue() as number) ?? 0).toFixed(1)}%`,
  },
  {
    id: "engagement_rate",
    header: "Engagement %",
    accessorFn: (row) => row.engagement_rate ?? 0,
    cell: (info) => `${((info.getValue() as number) ?? 0).toFixed(2)}%`,
  },
  {
    id: "views_per_day",
    header: "Views/Day",
    accessorFn: (row) => row.views_per_day ?? 0,
    cell: (info) => (info.getValue() as number).toFixed(1),
  },
  {
    id: "days_since_publication",
    header: "Age (days)",
    accessorFn: (row) => row.days_since_publication ?? 0,
  },
  {
    id: "sparkline",
    header: "28d Trend",
    enableSorting: false,
    accessorFn: (row) => row.sparkline,
    cell: (info) => (
      <SparklineCell data={(info.getValue() as number[] | undefined) ?? []} />
    ),
  },
];

export default function Shorts() {
  const [days, setDays] = useState(90);
  const { data, isLoading } = useShorts(days);

  if (isLoading) return <EmptyState message="Loading Shorts data..." />;

  if (!data || data.kpis.count === 0) {
    return (
      <EmptyState
        message="No Shorts data available"
        suggestion="Upload videos shorter than 60 seconds to see Shorts analytics"
      />
    );
  }

  const { kpis, comparison, videos, timeseries } = data;
  const { shorts, longform } = comparison;

  // --- Layer 1: KPI helpers ---
  const avgMultiplier =
    kpis.channel_avg_views > 0 ? kpis.avg_views / kpis.channel_avg_views : 1;

  // --- Layer 2: Trend chart ---
  const dates = timeseries.map((p) => p.date?.slice(0, 10) ?? "");
  const viewsData = timeseries.map((p) => p.views);
  const engagedData = timeseries.map((p) => p.engaged_views ?? 0);
  const rollingAvgData = rollingAverage(viewsData, 7);
  const periodAvg =
    viewsData.length > 0
      ? Math.round(viewsData.reduce((a, b) => a + b, 0) / viewsData.length)
      : 0;

  const baseTrendOption: EChartsOption = {
    tooltip: { trigger: "axis" },
    legend: {
      data: ["Views", "Engaged Views", "7-day Avg"],
      textStyle: { color: "#9ca3af" },
    },
    xAxis: { type: "category", data: dates },
    yAxis: { type: "value" },
    series: [
      {
        name: "Views",
        type: "line",
        data: viewsData,
        smooth: true,
        lineStyle: { type: "solid" },
        showSymbol: false,
      },
      {
        name: "Engaged Views",
        type: "line",
        data: engagedData,
        smooth: true,
        lineStyle: { type: "dashed" },
        showSymbol: false,
      },
      {
        name: "7-day Avg",
        type: "line",
        data: rollingAvgData,
        smooth: true,
        lineStyle: { type: "dotted" },
        showSymbol: false,
      },
    ],
  };

  const trendOption = addBenchmarkLine(baseTrendOption, periodAvg, "Period Avg");

  const avgViewsPerDay =
    timeseries.length > 0 ? Math.round(periodAvg) : 0;

  // --- Layer 3: Comparison charts ---
  const barOption: EChartsOption = {
    tooltip: { trigger: "axis" },
    legend: {
      data: ["Avg Views", "Avg Engagement (%)"],
      textStyle: { color: "#9ca3af" },
    },
    xAxis: { type: "category", data: ["Shorts", "Longform"] },
    yAxis: [
      { type: "value", name: "Avg Views", position: "left" },
      { type: "value", name: "Avg Engagement (%)", position: "right" },
    ],
    series: [
      {
        name: "Avg Views",
        type: "bar",
        yAxisIndex: 0,
        data: [shorts.avg_views ?? 0, longform.avg_views ?? 0],
      },
      {
        name: "Avg Engagement (%)",
        type: "bar",
        yAxisIndex: 1,
        data: [shorts.avg_engagement ?? 0, longform.avg_engagement ?? 0],
      },
    ],
  };

  const pieOption: EChartsOption = {
    tooltip: { trigger: "item" },
    series: [
      {
        type: "pie",
        radius: ["40%", "70%"],
        data: [
          { name: "Shorts", value: shorts.count ?? 0 },
          { name: "Longform", value: longform.count ?? 0 },
        ],
      },
    ],
  };

  // --- Layer 4: Table (pre-sorted views desc for default order) ---
  const sortedVideos = [...videos].sort((a, b) => b.views - a.views);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Shorts Analytics</h2>
        <PeriodSelector value={days} onChange={setDays} />
      </div>

      {/* Layer 1 — KPI Scorecard */}
      <KpiRow>
        <KpiCard label="Shorts Count" value={kpis.count.toLocaleString()} />
        <KpiCard
          label="Viewed vs. Swiped"
          value={`${(kpis.viewed_vs_swiped_pct ?? 0).toFixed(1)}%`}
          detail="Target: >70%"
        />
        <KpiCard label="Total Views" value={formatNumber(kpis.total_views)} />
        <KpiCard
          label="Avg Views"
          value={formatNumber(Math.round(kpis.avg_views))}
          trend={{
            direction:
              avgMultiplier > 1 ? "up" : avgMultiplier < 1 ? "down" : "flat",
            label: `${avgMultiplier.toFixed(1)}x avg`,
          }}
        />
        <KpiCard
          label="Avg Engagement"
          value={`${(kpis.avg_engagement ?? 0).toFixed(2)}%`}
        />
      </KpiRow>

      {/* Layer 2 — Trend Chart */}
      <div className="rounded-lg bg-gray-900 p-4">
        <ChartSummary>
          Shorts averaged {formatNumber(avgViewsPerDay)} views/day over the past{" "}
          {days} days, {avgMultiplier.toFixed(1)}x the channel average.
        </ChartSummary>
        <BaseChart
          option={trendOption}
          height="350px"
          ariaLabel={`Line chart showing Shorts daily views and engaged views over the past ${days} days`}
        />
      </div>

      {/* Layer 3 — Comparison */}
      <div className="grid grid-cols-2 gap-6">
        <div className="rounded-lg bg-gray-900 p-4">
          <h3 className="mb-2 text-sm font-medium text-gray-400">
            Avg Views & Engagement
          </h3>
          <BaseChart
            option={barOption}
            height="350px"
            ariaLabel="Bar chart comparing average views and engagement between Shorts and longform videos"
          />
        </div>
        <div className="rounded-lg bg-gray-900 p-4">
          <h3 className="mb-2 text-sm font-medium text-gray-400">
            Content Mix
          </h3>
          <BaseChart
            option={pieOption}
            height="350px"
            ariaLabel="Donut chart showing ratio of Shorts to longform videos"
          />
        </div>
      </div>

      {/* Layer 4 — Per-Video Ranked Table */}
      <div>
        <h3 className="mb-3 text-sm font-medium text-gray-400">
          Per-Video Performance
        </h3>
        <DataTable data={sortedVideos} columns={VIDEO_COLUMNS} />
      </div>
    </div>
  );
}
