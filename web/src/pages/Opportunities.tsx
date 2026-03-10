import { createColumnHelper } from "@tanstack/react-table";
import DataTable from "../components/DataTable";
import KpiCard from "../components/KpiCard";
import KpiRow from "../components/KpiRow";
import { useOpportunities } from "../hooks/useAnalytics";
import type { FormatGapShow, ShowVariance } from "../api/client";

const showVarianceCol = createColumnHelper<ShowVariance>();
const noShortsCol = createColumnHelper<FormatGapShow>();
const underperformingCol = createColumnHelper<FormatGapShow>();

const inconsistentColumns = [
  showVarianceCol.accessor("show_name", { header: "Show" }),
  showVarianceCol.accessor("video_count", { header: "Videos" }),
  showVarianceCol.accessor("avg_views_per_day", {
    header: "Avg V/Day",
    cell: (info: any) => info.getValue().toFixed(1),
  }),
  showVarianceCol.accessor("hit_rate", {
    header: "Hit Rate",
    cell: (info: any) => `${info.getValue()}%`,
  }),
  showVarianceCol.accessor("coeff_of_variation", {
    header: "CoV",
    cell: (info: any) => {
      const val: number = info.getValue();
      const color =
        val > 2.0 ? "text-red-400" : val > 1.5 ? "text-amber-400" : "";
      return <span className={color}>{val.toFixed(2)}</span>;
    },
  }),
] as const;

const noShortsColumns = [
  noShortsCol.accessor("show_name", { header: "Show" }),
  noShortsCol.accessor("video_count", { header: "Videos" }),
  noShortsCol.accessor("total_views", {
    header: "Total Views",
    cell: (info: any) => info.getValue()?.toLocaleString() ?? "—",
  }),
  noShortsCol.accessor("avg_engagement", {
    header: "Avg Engagement",
    cell: (info: any) => info.getValue()?.toFixed(2) ?? "—",
  }),
] as const;

const underperformingColumns = [
  underperformingCol.accessor("show_name", { header: "Show" }),
  underperformingCol.accessor("video_count", { header: "Videos" }),
  underperformingCol.accessor("avg_views_per_day", {
    header: "Avg V/Day",
    cell: (info: any) => info.getValue()?.toFixed(1) ?? "—",
  }),
  underperformingCol.accessor("channel_avg_views_per_day", {
    header: "Channel Avg",
    cell: (info: any) => info.getValue()?.toFixed(1) ?? "—",
  }),
  underperformingCol.accessor("ratio", {
    header: "Ratio",
    cell: (info: any) => {
      const val: number = info.getValue();
      const color = val < 0.5 ? "text-red-400" : "";
      return <span className={color}>{val?.toFixed(2) ?? "—"}</span>;
    },
  }),
] as const;

export default function Opportunities() {
  const { data, isLoading } = useOpportunities();

  if (isLoading) return <p className="text-gray-400">Loading...</p>;
  if (!data) return <p className="text-gray-400">No data available.</p>;

  const { inconsistent_shows, catalog_risers, no_shorts, underperforming } =
    data;

  return (
    <div className="space-y-8">
      <h2 className="text-xl font-bold">Opportunities</h2>

      <KpiRow>
        <KpiCard label="Inconsistent Shows" value={inconsistent_shows.length} />
        <KpiCard label="Catalog Risers" value={catalog_risers.length} />
        <KpiCard
          label="Format Gaps"
          value={no_shorts.length + underperforming.length}
        />
      </KpiRow>

      <section>
        <h3 className="text-lg font-semibold mb-1">Inconsistent Shows</h3>
        <p className="text-gray-500 text-sm mb-3">
          Shows ranked by performance variance. High variance means
          topic/title selection matters more than show brand.
        </p>
        {inconsistent_shows.length > 0 ? (
          <DataTable data={inconsistent_shows} columns={inconsistentColumns as any} />
        ) : (
          <p className="text-gray-500 text-sm italic">No inconsistent shows found.</p>
        )}
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-1">Catalog Risers</h3>
        {catalog_risers.length > 0 ? (
          <DataTable data={catalog_risers} columns={[]} />
        ) : (
          <p className="text-gray-500 text-sm italic">
            Catalog risers will appear after running the daily stats backfill
            script.
          </p>
        )}
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-3">Format Gaps</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-2">
              Shows Without Shorts
            </h4>
            {no_shorts.length > 0 ? (
              <DataTable data={no_shorts} columns={noShortsColumns as any} />
            ) : (
              <p className="text-gray-500 text-sm italic">
                All shows have at least one Short.
              </p>
            )}
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-2">
              Underperforming Shows
            </h4>
            {underperforming.length > 0 ? (
              <DataTable
                data={underperforming}
                columns={underperformingColumns as any}
              />
            ) : (
              <p className="text-gray-500 text-sm italic">
                No underperforming shows found.
              </p>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
