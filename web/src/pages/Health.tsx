import { useState } from "react";
import KpiCard from "../components/KpiCard";
import KpiRow from "../components/KpiRow";
import BaseChart from "../components/BaseChart";
import { useHealth } from "../hooks/useAnalytics";

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
}

function trendLabel(pct?: number): string | undefined {
  if (pct == null) return undefined;
  const arrow = pct >= 0 ? "↑" : "↓";
  return `${arrow} ${Math.abs(pct).toFixed(1)}% vs prior period`;
}

export default function Health() {
  const [days, setDays] = useState(90);
  const { data, isLoading } = useHealth(days);

  if (isLoading) return <p className="text-gray-400">Loading...</p>;

  const { kpis, timeseries, velocity, publishing_cadence } = data ?? {};

  const hasTimeseries = timeseries && timeseries.length > 0;

  const growthChartOption = {
    tooltip: { trigger: "axis" as const },
    xAxis: {
      type: "category" as const,
      data: (timeseries ?? []).map((p) => p.date?.slice(0, 10) ?? ""),
    },
    yAxis: [
      { type: "value" as const, name: "Views" },
      { type: "value" as const, name: "Subs Gained" },
    ],
    series: [
      {
        name: "Views",
        type: "line" as const,
        yAxisIndex: 0,
        data: (timeseries ?? []).map((p) => p.views),
        smooth: true,
      },
      {
        name: "Subscribers Gained",
        type: "line" as const,
        yAxisIndex: 1,
        data: (timeseries ?? []).map((p) => p.subscribers_gained),
        smooth: true,
      },
    ],
  };

  const cadenceChartOption = {
    tooltip: { trigger: "axis" as const },
    xAxis: {
      type: "category" as const,
      data: (publishing_cadence ?? []).map((p) => p.week),
    },
    yAxis: { type: "value" as const, name: "Uploads" },
    series: [
      {
        name: "Uploads",
        type: "bar" as const,
        data: (publishing_cadence ?? []).map((p) => p.count),
      },
    ],
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold">Channel Health</h2>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="bg-gray-800 text-gray-100 rounded px-2 py-1 text-sm border border-gray-700"
        >
          <option value={30}>30 days</option>
          <option value={90}>90 days</option>
          <option value={180}>180 days</option>
          <option value={365}>365 days</option>
        </select>
      </div>

      <KpiRow>
        <KpiCard
          label="Subscribers"
          value={formatNumber(kpis?.subscriber_count ?? 0)}
          detail={trendLabel(kpis?.subscribers_trend_pct)}
        />
        <KpiCard
          label="Avg Daily Views"
          value={formatNumber(kpis?.avg_daily_views ?? 0)}
          detail={trendLabel(kpis?.views_trend_pct)}
        />
        <KpiCard
          label="Watch Time"
          value={`${(kpis?.total_watch_time_hours ?? 0).toLocaleString()} hrs`}
          detail={trendLabel(kpis?.watch_time_trend_pct)}
        />
        <KpiCard
          label="Avg View Duration"
          value={`${kpis?.avg_view_duration_seconds ?? 0}s`}
          detail={kpis?.avg_view_duration_seconds === 0 ? "Backfill needed" : undefined}
        />
      </KpiRow>

      <div className="rounded-lg bg-gray-900 p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">Growth Trends</h3>
        {!hasTimeseries ? (
          <p className="text-sm text-gray-500">
            Channel history will appear after running the backfill script.
          </p>
        ) : (
          <BaseChart option={growthChartOption} height="350px" />
        )}
      </div>

      <div className="rounded-lg bg-gray-900 p-4">
        <h3 className="mb-3 text-sm font-medium text-gray-400">Content Velocity</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-800 rounded-lg p-3">
            <p className="text-xs text-gray-400">New Uploads</p>
            <p className="mt-1 text-xl font-semibold text-white">
              {velocity?.new_uploads ?? 0}
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg p-3">
            <p className="text-xs text-gray-400">Catalog Views</p>
            <p className="mt-1 text-xl font-semibold text-white">
              {velocity?.catalog_view_pct ?? 0}%
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg p-3">
            <p className="text-xs text-gray-400">New Content Views</p>
            <p className="mt-1 text-xl font-semibold text-white">
              {velocity?.new_content_view_pct ?? 0}%
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg p-3">
            <p className="text-xs text-gray-400">Avg Views at 7d</p>
            <p className="mt-1 text-xl font-semibold text-white">
              {velocity?.avg_views_at_7d != null
                ? formatNumber(velocity.avg_views_at_7d)
                : "—"}
            </p>
          </div>
        </div>
      </div>

      <div className="rounded-lg bg-gray-900 p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">Publishing Cadence</h3>
        {!publishing_cadence || publishing_cadence.length === 0 ? (
          <p className="text-sm text-gray-500">
            Channel history will appear after running the backfill script.
          </p>
        ) : (
          <BaseChart option={cadenceChartOption} height="250px" />
        )}
      </div>
    </div>
  );
}
