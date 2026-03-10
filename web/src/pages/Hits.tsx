import { useState, useMemo } from "react";
import type { ColumnDef } from "@tanstack/react-table";
import KpiCard from "../components/KpiCard";
import KpiRow from "../components/KpiRow";
import BaseChart from "../components/BaseChart";
import DataTable from "../components/DataTable";
import { useHits } from "../hooks/useAnalytics";
import type { VideoWithContext } from "../api/client";

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
}

function truncate(s: string, max: number): string {
  return s.length > max ? s.slice(0, max) + "…" : s;
}

const PERIOD_OPTIONS = [
  { label: "30 days", value: 30 },
  { label: "90 days", value: 90 },
  { label: "180 days", value: 180 },
  { label: "365 days", value: 365 },
];

type FormatFilter = "All" | "Shorts" | "Long";

const columns: ColumnDef<VideoWithContext, unknown>[] = [
  {
    id: "title",
    accessorKey: "title",
    header: "Title",
    cell: (info) => truncate(info.getValue() as string, 50),
  },
  {
    id: "show_name",
    accessorKey: "show_name",
    header: "Show",
    cell: (info) => (info.getValue() as string | undefined) ?? "—",
  },
  {
    id: "views",
    accessorKey: "views",
    header: "Views",
    cell: (info) => formatNumber(info.getValue() as number),
  },
  {
    id: "vs_show_multiplier",
    accessorKey: "vs_show_multiplier",
    header: "vs Show",
    cell: (info) => {
      const val = info.getValue() as number;
      const color =
        val > 1.5
          ? "text-green-400"
          : val < 0.7
          ? "text-red-400"
          : "text-gray-300";
      return <span className={color}>{val.toFixed(1)}x</span>;
    },
  },
  {
    id: "engagement_rate",
    accessorKey: "engagement_rate",
    header: "Eng%",
    cell: (info) => {
      const val = info.getValue() as number | undefined;
      return val != null ? `${val.toFixed(2)}%` : "—";
    },
  },
  {
    id: "subscribers_gained",
    accessorKey: "subscribers_gained",
    header: "Subs",
    cell: (info) => {
      const val = info.getValue() as number | undefined;
      return val != null ? formatNumber(val) : "0";
    },
  },
];

export default function Hits() {
  const [days, setDays] = useState(90);
  const [showFilter, setShowFilter] = useState("All");
  const [formatFilter, setFormatFilter] = useState<FormatFilter>("All");

  const { data, isLoading } = useHits(days);

  const showOptions = useMemo(() => {
    if (!data) return [];
    const names = Array.from(
      new Set(
        data.top_performers
          .map((v) => v.show_name)
          .filter((n): n is string => !!n)
      )
    ).sort();
    return ["All", ...names];
  }, [data]);

  const filteredPerformers = useMemo(() => {
    if (!data) return [];
    let rows = data.top_performers;
    if (showFilter !== "All") {
      rows = rows.filter((v) => v.show_name === showFilter);
    }
    if (formatFilter === "Shorts") {
      rows = rows.filter((v) => v.is_short);
    } else if (formatFilter === "Long") {
      rows = rows.filter((v) => !v.is_short);
    }
    return rows;
  }, [data, showFilter, formatFilter]);

  const hitRateChartOption = useMemo(() => {
    if (!data || data.show_hit_rates.length === 0) return null;
    const sorted = [...data.show_hit_rates].sort((a, b) => a.hit_rate - b.hit_rate);
    return {
      tooltip: { trigger: "axis" as const },
      xAxis: { type: "value" as const, axisLabel: { formatter: "{value}%" } },
      yAxis: { type: "category" as const, data: sorted.map((s) => s.show_name) },
      series: [
        {
          type: "bar" as const,
          data: sorted.map((s) => +(s.hit_rate * 100).toFixed(1)),
          itemStyle: { color: "#6366f1" },
        },
      ],
      grid: { left: "20%", right: "5%", top: "5%", bottom: "10%" },
    };
  }, [data]);

  const scatterChartOption = useMemo(() => {
    if (!data || data.top_performers.length === 0) return null;

    const hits = data.top_performers
      .filter((v) => v.z_score > 2)
      .map((v) => ({
        value: [v.views, v.engagement_rate ?? 0],
        name: v.title,
      }));

    const normals = data.top_performers
      .filter((v) => v.z_score <= 2)
      .map((v) => ({
        value: [v.views, v.engagement_rate ?? 0],
        name: v.title,
      }));

    return {
      tooltip: {
        trigger: "item" as const,
        formatter: (params: { data: { name: string; value: number[] } }) =>
          `${truncate(params.data.name, 40)}<br/>Views: ${formatNumber(params.data.value[0])}<br/>Eng: ${params.data.value[1].toFixed(2)}%`,
      },
      xAxis: {
        type: "log" as const,
        name: "Views",
        nameLocation: "middle" as const,
        nameGap: 30,
      },
      yAxis: {
        type: "value" as const,
        name: "Engagement %",
      },
      series: [
        {
          name: "Normal",
          type: "scatter" as const,
          data: normals,
          itemStyle: { color: "#4b5563", opacity: 0.6 },
          symbolSize: 6,
        },
        {
          name: "Hits",
          type: "scatter" as const,
          data: hits,
          itemStyle: { color: "#f59e0b" },
          symbolSize: 10,
        },
      ],
      legend: { data: ["Normal", "Hits"], textStyle: { color: "#9ca3af" } },
      grid: { left: "10%", right: "5%", top: "15%", bottom: "15%" },
    };
  }, [data]);

  const subDriverChartOption = useMemo(() => {
    if (!data || data.subscriber_drivers.length === 0) return null;

    const top10 = data.subscriber_drivers.slice(0, 10);
    const titles = top10.map((d) =>
      truncate(String(d.title ?? "Unknown"), 30)
    );
    const values = top10.map((d) => Number(d.subscribers_gained ?? 0));

    return {
      tooltip: { trigger: "axis" as const },
      xAxis: { type: "value" as const },
      yAxis: { type: "category" as const, data: titles },
      series: [
        {
          type: "bar" as const,
          data: values,
          itemStyle: { color: "#10b981" },
        },
      ],
      grid: { left: "35%", right: "5%", top: "5%", bottom: "10%" },
    };
  }, [data]);

  if (isLoading) return <p className="text-gray-400">Loading...</p>;

  return (
    <div className="space-y-6">
      {/* Header + Period Selector */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Hits &amp; Insights</h2>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="bg-gray-800 text-gray-100 rounded px-2 py-1 text-sm border border-gray-700"
        >
          {PERIOD_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>

      {/* KPI Row */}
      <KpiRow>
        <KpiCard label="Hits Found" value={data?.hit_count ?? 0} />
        <KpiCard
          label="Avg Hit Multiplier"
          value={`${(data?.avg_hit_multiplier ?? 0).toFixed(1)}x`}
        />
        <KpiCard
          label="Top Sub Driver"
          value={truncate(data?.top_sub_driver ?? "—", 24)}
        />
        <KpiCard
          label="Best Show Hit Rate"
          value={data?.best_show_hit_rate ?? "—"}
        />
      </KpiRow>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-400">Show</label>
          <select
            value={showFilter}
            onChange={(e) => setShowFilter(e.target.value)}
            className="bg-gray-800 text-gray-100 rounded px-2 py-1 text-sm border border-gray-700"
          >
            {showOptions.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-400">Format</label>
          <div className="flex rounded overflow-hidden border border-gray-700">
            {(["All", "Shorts", "Long"] as FormatFilter[]).map((f) => (
              <button
                key={f}
                onClick={() => setFormatFilter(f)}
                className={`px-3 py-1 text-sm ${
                  formatFilter === f
                    ? "bg-indigo-600 text-white"
                    : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Top Performers Table */}
      <div className="space-y-2">
        <h3 className="text-sm font-medium text-gray-400">Top Performers</h3>
        {filteredPerformers.length > 0 ? (
          <DataTable data={filteredPerformers} columns={columns} />
        ) : (
          <p className="text-gray-500 text-sm py-4">No results match the current filters.</p>
        )}
      </div>

      {/* Show Hit Rates Chart */}
      <div className="bg-gray-900 rounded-lg p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">
          Hit Rate by Show
        </h3>
        {hitRateChartOption ? (
          <BaseChart option={hitRateChartOption} height="320px" />
        ) : (
          <p className="text-gray-500 text-sm">No show hit rate data available.</p>
        )}
      </div>

      {/* Engagement vs Views Scatter */}
      <div className="bg-gray-900 rounded-lg p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">
          Engagement vs Views
        </h3>
        {scatterChartOption ? (
          <BaseChart option={scatterChartOption} height="360px" />
        ) : (
          <p className="text-gray-500 text-sm">No scatter data available.</p>
        )}
      </div>

      {/* Subscriber Drivers Chart */}
      <div className="bg-gray-900 rounded-lg p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">
          Top Subscriber Drivers
        </h3>
        {subDriverChartOption ? (
          <BaseChart option={subDriverChartOption} height="280px" />
        ) : (
          <p className="text-gray-500 text-sm">No subscriber driver data available.</p>
        )}
      </div>
    </div>
  );
}
