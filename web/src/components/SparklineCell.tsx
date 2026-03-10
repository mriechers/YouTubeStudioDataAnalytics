import ReactECharts from "echarts-for-react";
import { THEME_NAME } from "../theme/echarts";

interface SparklineCellProps {
  data: number[];
  width?: string;
  height?: string;
}

export default function SparklineCell({
  data,
  width = "120px",
  height = "32px",
}: SparklineCellProps) {
  if (!data || data.length === 0) {
    return <span className="text-gray-600">—</span>;
  }

  const option = {
    animation: false,
    grid: { top: 2, right: 2, bottom: 2, left: 2 },
    xAxis: { type: "category" as const, show: false },
    yAxis: { type: "value" as const, show: false },
    series: [
      {
        type: "line" as const,
        data,
        showSymbol: false,
        smooth: true,
      },
    ],
  };

  return (
    <ReactECharts
      option={option}
      theme={THEME_NAME}
      style={{ width, height }}
      opts={{ renderer: "svg" }}
    />
  );
}
