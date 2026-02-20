import * as echarts from "echarts/core";

const OKABE_ITO = [
  "#E69F00",
  "#56B4E9",
  "#009E73",
  "#F0E442",
  "#0072B2",
  "#D55E00",
  "#CC79A7",
  "#999999",
];

export const THEME_NAME = "pbs-dark";

echarts.registerTheme(THEME_NAME, {
  color: OKABE_ITO,
  backgroundColor: "transparent",
  textStyle: { color: "#e5e7eb" },
  title: { textStyle: { color: "#f9fafb" } },
  legend: { textStyle: { color: "#d1d5db" } },
  categoryAxis: {
    axisLine: { lineStyle: { color: "#4b5563" } },
    axisLabel: { color: "#9ca3af" },
    splitLine: { lineStyle: { color: "#374151" } },
  },
  valueAxis: {
    axisLine: { lineStyle: { color: "#4b5563" } },
    axisLabel: { color: "#9ca3af" },
    splitLine: { lineStyle: { color: "#374151" } },
  },
  tooltip: {
    backgroundColor: "#1f2937",
    borderColor: "#374151",
    textStyle: { color: "#f9fafb" },
  },
});
