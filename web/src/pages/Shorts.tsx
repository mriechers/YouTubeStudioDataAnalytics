import KpiCard from "../components/KpiCard";
import KpiRow from "../components/KpiRow";
import BaseChart from "../components/BaseChart";
import { useShorts } from "../hooks/useAnalytics";

export default function Shorts() {
  const { data, isLoading } = useShorts();

  if (isLoading) return <p className="text-gray-400">Loading...</p>;
  if (!data) return <p className="text-gray-400">No data available.</p>;

  const { shorts, longform } = data;

  if (shorts.count === 0)
    return (
      <p className="text-gray-400">
        No Shorts detected. Videos 3 minutes or shorter are classified as Shorts.
      </p>
    );

  const barOption = {
    tooltip: { trigger: "axis" as const },
    legend: { data: ["Avg Views", "Avg Engagement (%)"] },
    xAxis: { type: "category" as const, data: ["Shorts", "Longform"] },
    yAxis: [
      { type: "value" as const, name: "Avg Views", position: "left" as const },
      { type: "value" as const, name: "Avg Engagement (%)", position: "right" as const },
    ],
    series: [
      {
        name: "Avg Views",
        type: "bar" as const,
        yAxisIndex: 0,
        data: [shorts.avg_views ?? 0, longform.avg_views ?? 0],
      },
      {
        name: "Avg Engagement (%)",
        type: "bar" as const,
        yAxisIndex: 1,
        data: [shorts.avg_engagement ?? 0, longform.avg_engagement ?? 0],
      },
    ],
  };

  const pieOption = {
    tooltip: { trigger: "item" as const },
    series: [
      {
        type: "pie" as const,
        radius: ["40%", "70%"],
        data: [
          { name: "Shorts", value: shorts.count ?? 0 },
          { name: "Longform", value: longform.count ?? 0 },
        ],
      },
    ],
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Shorts vs Longform Analysis</h2>
      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-400">Shorts</h3>
          <KpiRow>
            <KpiCard label="Count" value={(shorts.count ?? 0).toLocaleString()} />
            <KpiCard label="Total Views" value={(shorts.total_views ?? 0).toLocaleString()} />
          </KpiRow>
          <KpiRow>
            <KpiCard label="Avg Views" value={Math.round(shorts.avg_views ?? 0).toLocaleString()} />
            <KpiCard label="Avg Engagement" value={`${(shorts.avg_engagement ?? 0).toFixed(2)}%`} />
          </KpiRow>
        </div>
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-400">Longform</h3>
          <KpiRow>
            <KpiCard label="Count" value={(longform.count ?? 0).toLocaleString()} />
            <KpiCard label="Total Views" value={(longform.total_views ?? 0).toLocaleString()} />
          </KpiRow>
          <KpiRow>
            <KpiCard label="Avg Views" value={Math.round(longform.avg_views ?? 0).toLocaleString()} />
            <KpiCard label="Avg Engagement" value={`${(longform.avg_engagement ?? 0).toFixed(2)}%`} />
          </KpiRow>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-6">
        <div className="rounded-lg bg-gray-900 p-4">
          <h3 className="mb-2 text-sm font-medium text-gray-400">Avg Views & Engagement</h3>
          <BaseChart option={barOption} height="350px" />
        </div>
        <div className="rounded-lg bg-gray-900 p-4">
          <h3 className="mb-2 text-sm font-medium text-gray-400">Content Mix</h3>
          <BaseChart option={pieOption} height="350px" />
        </div>
      </div>
    </div>
  );
}
