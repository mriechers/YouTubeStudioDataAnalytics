import KpiCard from "../components/KpiCard";
import KpiRow from "../components/KpiRow";
import BaseChart from "../components/BaseChart";
import EmptyState from "../components/EmptyState";
import ChartSummary from "../components/ChartSummary";
import { useSubscribers } from "../hooks/useAnalytics";

export default function Subscribers() {
  const { data: sources, isLoading } = useSubscribers();

  if (isLoading) return <EmptyState message="Loading subscriber data..." />;
  if (!sources?.length)
    return (
      <EmptyState
        message="Subscriber attribution data is not available."
        suggestion="Requires YouTube Analytics API access with the yt-analytics.readonly scope."
      />
    );

  const totalGained = sources.reduce(
    (s, v) => s + ((v as Record<string, number>).subscribers_gained ?? 0),
    0
  );
  const totalLost = sources.reduce(
    (s, v) => s + ((v as Record<string, number>).subscribers_lost ?? 0),
    0
  );
  const netTotal = totalGained - totalLost;

  const top10 = sources.slice(0, 10) as Array<{
    video_id: string;
    subscribers_gained: number;
    subscribers_lost: number;
    net_subscribers: number;
  }>;

  const barOption = {
    tooltip: { trigger: "axis" as const },
    grid: { left: "5%", right: "5%" },
    xAxis: {
      type: "category" as const,
      data: top10.map((_, i) => `Video ${i + 1}`),
      axisLabel: { rotate: 45 },
    },
    yAxis: { type: "value" as const, name: "Net Subscribers" },
    series: [
      {
        type: "bar" as const,
        data: top10.map((v) => v.net_subscribers),
      },
    ],
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Subscriber Attribution</h2>
      <KpiRow>
        <KpiCard label="Total Gained" value={totalGained.toLocaleString()} />
        <KpiCard label="Total Lost" value={totalLost.toLocaleString()} />
        <KpiCard label="Net Subscribers" value={netTotal.toLocaleString()} />
      </KpiRow>
      <div className="rounded-lg bg-gray-900 p-4">
        <h3 className="mb-2 text-sm font-medium text-gray-400">
          Top 10 Videos by Subscriber Gain
        </h3>
        <ChartSummary>
          Net subscriber change attributed to each of the top 10 videos over a 90-day rolling window.
        </ChartSummary>
        <BaseChart
          option={barOption}
          height="400px"
          ariaLabel="Bar chart showing net subscriber change attributed to the top 10 videos over a 90-day window"
        />
      </div>
      <p className="text-xs text-gray-500">
        Subscriber attribution is based on a 90-day rolling window from the YouTube Analytics API.
      </p>
    </div>
  );
}
