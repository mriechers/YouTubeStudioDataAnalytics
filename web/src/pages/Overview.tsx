import KpiCard from "../components/KpiCard";
import KpiRow from "../components/KpiRow";
import BaseChart from "../components/BaseChart";
import EmptyState from "../components/EmptyState";
import ChartSummary from "../components/ChartSummary";
import MatrixChart from "../components/MatrixChart";
import { useOverview, useTimeseries, useMatrix } from "../hooks/useAnalytics";

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
}

export default function Overview() {
  const { data: kpis, isLoading: kpisLoading } = useOverview();
  const { data: timeseries, isLoading: tsLoading } = useTimeseries(90);
  const { data: matrixVideos, isLoading: matrixLoading } = useMatrix();

  if (kpisLoading) return <EmptyState message="Loading overview..." />;

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

      <div className="grid grid-cols-1 gap-6">
        <div className="rounded-lg bg-gray-900 p-4 shadow-sm border border-gray-100">
          <h3 className="mb-2 text-sm font-medium text-gray-400 uppercase tracking-wider">
            Channel Growth Momentum
          </h3>
          {tsLoading ? (
            <EmptyState message="Loading chart..." />
          ) : (
            <>
              <ChartSummary>
                Daily views and subscriber gains (90 days).
              </ChartSummary>
              <BaseChart
                option={chartOption}
                height="350px"
                ariaLabel="Line chart showing daily views and subscriber gains"
              />
            </>
          )}
        </div>
      </div>

      <div>
        <h3 className="mb-4 text-sm font-medium text-gray-500 uppercase tracking-wider">
          Performance Optimization (CTR vs. Retention)
        </h3>
        {matrixLoading ? (
          <EmptyState message="Loading matrix..." />
        ) : (
          <MatrixChart videos={matrixVideos ?? []} />
        )}
      </div>
    </div>
  );
}
