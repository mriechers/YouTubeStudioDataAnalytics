import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "echarts";
import { THEME_NAME } from "../theme/echarts";

interface BaseChartProps {
  option: EChartsOption;
  height?: string;
  className?: string;
}

export default function BaseChart({
  option,
  height = "400px",
  className = "",
}: BaseChartProps) {
  return (
    <ReactECharts
      option={option}
      theme={THEME_NAME}
      style={{ height, width: "100%" }}
      className={className}
      opts={{ renderer: "canvas" }}
    />
  );
}
