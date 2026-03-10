import type { EChartsOption } from "echarts";

export function addBenchmarkLine(
  option: EChartsOption,
  value: number,
  label: string
): EChartsOption {
  const series = Array.isArray(option.series) ? option.series : [];
  const updatedSeries = series.map((s, i) => {
    if (i === 0) {
      return {
        ...s,
        markLine: {
          silent: true,
          symbol: "none",
          data: [{ yAxis: value, name: label }],
          lineStyle: {
            type: "dashed" as const,
            color: "#6b7280",
          },
          label: {
            formatter: `{b}: {c}`,
            color: "#6b7280",
          },
        },
      };
    }
    return s;
  });

  return { ...option, series: updatedSeries };
}

export function rollingAverage(data: number[], window: number): number[] {
  if (window <= 0 || data.length === 0) return data;

  return data.map((_, i) => {
    const start = Math.max(0, i - window + 1);
    const slice = data.slice(start, i + 1);
    return slice.reduce((sum, v) => sum + v, 0) / slice.length;
  });
}
