interface KpiCardProps {
  label: string;
  value: string | number;
  detail?: string;
}

export default function KpiCard({ label, value, detail }: KpiCardProps) {
  return (
    <div className="rounded-lg bg-gray-800 p-4">
      <p className="text-sm text-gray-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-white">{value}</p>
      {detail && <p className="mt-1 text-xs text-gray-500">{detail}</p>}
    </div>
  );
}
