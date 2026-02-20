import KpiCard from "../components/KpiCard";
import KpiRow from "../components/KpiRow";
import BaseChart from "../components/BaseChart";
import { useOverview, useTimeseries } from "../hooks/useAnalytics";

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
}

export default function Overview() {
  const { data: kpis, isLoading: kpisLoading } = useOverview();
  const { data: timeseries, isLoading: tsLoading } = useTimeseries(90);

  if (kpisLoading) return <p className="text-gray-400">Loading...</p>;

  const chartOption = {
    tooltip: { trigger: "axis" as const },
    xAxis: {
      type: "category" as const,
      data: (timeseries ?? []).map((p) => p.date?.slice(0, 10) ?? ""),
    },
    yAxis: { type: "value" as const },
    series: [
      {
        name: "Views",
        type: "line" as const,
        data: (timeseries ?? []).map((p) => p.views),
        smooth: true,
      },
      {
        name: "Subscribers Gained",
        type: "line" as const,
        data: (timeseries ?? []).map((p) => p.subscribers_gained),
        smooth: true,
      },
    ],
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Overview</h2>
      <KpiRow>
        <KpiCard label="Total Videos" value={formatNumber(kpis?.total_videos ?? 0)} />
        <KpiCard label="Total Views" value={formatNumber(kpis?.total_views ?? 0)} />
        <KpiCard
          label="Shorts"
          value={formatNumber(kpis?.shorts_count ?? 0)}
          detail={`${(kpis?.shorts_ratio ?? 0).toFixed(1)}% of catalog`}
        />
        <KpiCard
          label="Avg Engagement"
          value={`${(kpis?.avg_engagement ?? 0).toFixed(2)}%`}
        />
      </KpiRow>
      <div className="rounded-lg bg-gray-900 p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">
          Daily Views & Subscribers (90 days)
        </h3>
        {tsLoading ? (
          <p className="text-gray-500">Loading chart...</p>
        ) : (
          <BaseChart option={chartOption} height="350px" />
        )}
      </div>
    </div>
  );
}
