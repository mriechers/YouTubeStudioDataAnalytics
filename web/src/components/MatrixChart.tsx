import type { VideoSummary } from "../api/client";
import BaseChart from "./BaseChart";
import type { EChartsOption } from "echarts";

interface MatrixChartProps {
  videos: VideoSummary[];
}

export default function MatrixChart({ videos }: MatrixChartProps) {
  // Filter out videos with zero views or missing metrics
  const data = videos
    .filter((v) => v.views > 100 && v.ctr !== undefined && v.avg_view_pct !== undefined)
    .map((v) => [v.ctr, v.avg_view_pct, v.views, v.title, v.show_name]);

  const option: EChartsOption = {
    title: {
      text: "Content vs. Thumbnail Matrix",
      left: "center",
      textStyle: { fontWeight: "normal" },
    },
    tooltip: {
      trigger: "item",
      formatter: (params: any) => {
        const [ctr, apv, views, title, show] = params.data;
        return `
          <div style="font-weight: bold; margin-bottom: 4px;">${title}</div>
          <div style="font-size: 12px; color: #666; margin-bottom: 8px;">${show || "Uncategorized"}</div>
          <div style="display: flex; justify-content: space-between; gap: 16px;">
            <span>CTR:</span> <span>${ctr.toFixed(2)}%</span>
          </div>
          <div style="display: flex; justify-content: space-between; gap: 16px;">
            <span>Retention (APV):</span> <span>${apv.toFixed(2)}%</span>
          </div>
          <div style="display: flex; justify-content: space-between; gap: 16px;">
            <span>Views:</span> <span>${views.toLocaleString()}</span>
          </div>
        `;
      },
    },
    xAxis: {
      name: "Click-Through Rate (CTR)",
      nameLocation: "middle",
      nameGap: 30,
      axisLabel: { formatter: "{value}%" },
      splitLine: { show: false },
    },
    yAxis: {
      name: "Avg Percentage Viewed (APV)",
      nameLocation: "middle",
      nameGap: 40,
      axisLabel: { formatter: "{value}%" },
      splitLine: { show: false },
    },
    series: [
      {
        type: "scatter",
        data: data,
        symbolSize: (data: any) => {
          return Math.sqrt(data[2]) / 10 + 5; // Scale by views
        },
        itemStyle: {
          opacity: 0.6,
          color: "#005596", // PBS Blue
        },
        markLine: {
          silent: true,
          lineStyle: { type: "dashed", color: "#999" },
          data: [
            { xAxis: 4, label: { formatter: "Avg CTR" } }, // Thresholds
            { yAxis: 40, label: { formatter: "Avg APV" } },
          ],
        },
        markArea: {
          silent: true,
          data: [
            [
              { name: "Powerhouses", xAxis: 4, yAxis: 40, itemStyle: { color: "rgba(0, 255, 0, 0.05)" } },
              { xAxis: 20, yAxis: 100 },
            ],
            [
              { name: "Clickbait", xAxis: 4, yAxis: 0, itemStyle: { color: "rgba(255, 0, 0, 0.05)" } },
              { xAxis: 20, yAxis: 40 },
            ],
            [
              { name: "Hidden Gems", xAxis: 0, yAxis: 40, itemStyle: { color: "rgba(0, 0, 255, 0.05)" } },
              { xAxis: 4, yAxis: 100 },
            ],
          ],
        },
      },
    ],
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
      <BaseChart option={option} height="500px" ariaLabel="Matrix chart showing Click-Through Rate versus Average Percentage Viewed" />
      <div className="mt-4 grid grid-cols-2 gap-4 text-xs text-gray-500">
        <div>
          <span className="font-bold text-gray-700">Hidden Gems:</span> Great retention, low clicks. Focus on better titles/thumbnails.
        </div>
        <div>
          <span className="font-bold text-gray-700">Powerhouses:</span> Winning on both hooks and content. Scale these!
        </div>
        <div>
          <span className="font-bold text-gray-700">Duds:</span> Poor hooks and poor retention. Re-evaluate strategy.
        </div>
        <div>
          <span className="font-bold text-gray-700">Clickbait:</span> High clicks, low retention. Video fails to deliver on promise.
        </div>
      </div>
    </div>
  );
}
