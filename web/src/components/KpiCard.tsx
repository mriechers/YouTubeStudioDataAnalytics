interface TrendIndicator {
  direction: "up" | "down" | "flat";
  label: string;
}

interface KpiCardProps {
  label: string;
  value: string | number;
  detail?: string;
  trend?: TrendIndicator;
}

const TREND_STYLES: Record<TrendIndicator["direction"], { color: string; symbol: string }> = {
  up: { color: "text-green-400", symbol: "▲" },
  down: { color: "text-red-400", symbol: "▼" },
  flat: { color: "text-gray-400", symbol: "—" },
};

export default function KpiCard({ label, value, detail, trend }: KpiCardProps) {
  return (
    <div className="rounded-lg bg-gray-800 p-4">
      <p className="text-sm text-gray-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-white">{value}</p>
      {trend && (
        <p className={`mt-1 text-xs ${TREND_STYLES[trend.direction].color}`}>
          {TREND_STYLES[trend.direction].symbol} {trend.label}
        </p>
      )}
      {detail && <p className="mt-1 text-xs text-gray-500">{detail}</p>}
    </div>
  );
}
