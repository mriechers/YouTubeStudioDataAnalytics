import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "echarts";
import { useEffect, useState } from "react";
import { THEME_NAME } from "../theme/echarts";

interface BaseChartProps {
  option: EChartsOption;
  height?: string;
  className?: string;
  ariaLabel?: string;
}

export default function BaseChart({
  option,
  height = "400px",
  className = "",
  ariaLabel,
}: BaseChartProps) {
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReducedMotion(mq.matches);
    const handler = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  const resolvedOption = reducedMotion
    ? { ...option, animation: false }
    : option;

  const chart = (
    <ReactECharts
      option={resolvedOption}
      theme={THEME_NAME}
      style={{ height, width: "100%" }}
      className={className}
      opts={{ renderer: "canvas" }}
    />
  );

  if (ariaLabel) {
    return (
      <div role="img" aria-label={ariaLabel}>
        {chart}
      </div>
    );
  }

  return chart;
}
