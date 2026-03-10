import { useState, useMemo } from "react";
import { type ColumnDef } from "@tanstack/react-table";
import KpiCard from "../components/KpiCard";
import KpiRow from "../components/KpiRow";
import DataTable from "../components/DataTable";
import { useRecent } from "../hooks/useAnalytics";
import { type VideoWithContext } from "../api/client";

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
}

const columns: ColumnDef<VideoWithContext>[] = [
  {
    accessorKey: "title",
    header: "Title",
    cell: (info) => (
      <span className="whitespace-normal">{info.getValue() as string}</span>
    ),
  },
  {
    accessorKey: "show_name",
    header: "Show",
    cell: (info) => (info.getValue() as string | undefined) ?? "—",
  },
  {
    accessorKey: "is_short",
    header: "Type",
    cell: (info) => {
      const isShort = info.getValue() as boolean | undefined;
      return (
        <span
          className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${
            isShort ? "bg-blue-900 text-blue-300" : "bg-gray-700 text-gray-300"
          }`}
        >
          {isShort ? "Short" : "Long"}
        </span>
      );
    },
  },
  {
    accessorKey: "views",
    header: "Views",
    cell: (info) => formatNumber(info.getValue() as number),
  },
  {
    accessorKey: "views_per_day",
    header: "V/Day",
    cell: (info) => {
      const val = info.getValue() as number | undefined;
      return val != null ? val.toFixed(1) : "—";
    },
  },
  {
    accessorKey: "engagement_rate",
    header: "Eng%",
    cell: (info) => {
      const val = info.getValue() as number | undefined;
      return val != null ? val.toFixed(2) : "—";
    },
  },
  {
    accessorKey: "vs_show_multiplier",
    header: "vs Show",
    cell: (info) => {
      const val = info.getValue() as number;
      const colorClass =
        val > 1.5 ? "text-green-400" : val < 0.7 ? "text-red-400" : "text-gray-300";
      return <span className={colorClass}>{val.toFixed(1)}x</span>;
    },
  },
];

export default function Recent() {
  const [days, setDays] = useState(30);
  const [search, setSearch] = useState("");
  const [showFilter, setShowFilter] = useState("");
  const [formatFilter, setFormatFilter] = useState("all");

  const { data, isLoading } = useRecent(days);

  const showOptions = useMemo(() => {
    const names = (data?.videos ?? [])
      .map((v) => v.show_name)
      .filter((n): n is string => !!n);
    return Array.from(new Set(names)).sort();
  }, [data?.videos]);

  const filtered = useMemo(() => {
    let result = data?.videos ?? [];
    if (search) {
      const q = search.toLowerCase();
      result = result.filter((v) => v.title.toLowerCase().includes(q));
    }
    if (showFilter) {
      result = result.filter((v) => v.show_name === showFilter);
    }
    if (formatFilter === "shorts") {
      result = result.filter((v) => v.is_short);
    } else if (formatFilter === "longform") {
      result = result.filter((v) => !v.is_short);
    }
    return result;
  }, [data?.videos, search, showFilter, formatFilter]);

  const summaryCount = filtered.length;
  const summaryTotalViews = filtered.reduce((acc, v) => acc + v.views, 0);
  const summaryAvgVpd =
    filtered.length > 0
      ? filtered.reduce((acc, v) => acc + (v.views_per_day ?? 0), 0) / filtered.length
      : 0;
  const summaryAvgEng =
    filtered.length > 0
      ? filtered.reduce((acc, v) => acc + (v.engagement_rate ?? 0), 0) / filtered.length
      : 0;

  if (isLoading) return <p className="text-gray-400">Loading...</p>;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-4 items-center">
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="bg-gray-800 text-gray-100 rounded px-3 py-1 text-sm border border-gray-700"
        >
          <option value={7}>7 days</option>
          <option value={14}>14 days</option>
          <option value={30}>30 days</option>
          <option value={90}>90 days</option>
        </select>

        <input
          type="text"
          placeholder="Search titles..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-gray-800 text-gray-100 rounded px-3 py-1 text-sm border border-gray-700 w-64"
        />

        <select
          value={showFilter}
          onChange={(e) => setShowFilter(e.target.value)}
          className="bg-gray-800 text-gray-100 rounded px-3 py-1 text-sm border border-gray-700"
        >
          <option value="">All Shows</option>
          {showOptions.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>

        <select
          value={formatFilter}
          onChange={(e) => setFormatFilter(e.target.value)}
          className="bg-gray-800 text-gray-100 rounded px-3 py-1 text-sm border border-gray-700"
        >
          <option value="all">All Formats</option>
          <option value="shorts">Shorts</option>
          <option value="longform">Longform</option>
        </select>
      </div>

      <KpiRow>
        <KpiCard label="Published" value={String(summaryCount)} />
        <KpiCard label="Total Views" value={formatNumber(summaryTotalViews)} />
        <KpiCard label="Avg Views/Day" value={summaryAvgVpd.toFixed(1)} />
        <KpiCard label="Avg Engagement" value={`${summaryAvgEng.toFixed(2)}%`} />
      </KpiRow>

      <DataTable data={filtered} columns={columns} />
    </div>
  );
}
