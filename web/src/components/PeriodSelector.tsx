interface PeriodSelectorProps {
  value: number;
  onChange: (days: number) => void;
  options?: number[];
}

const DEFAULT_OPTIONS = [30, 90, 180, 365];

export default function PeriodSelector({
  value,
  onChange,
  options = DEFAULT_OPTIONS,
}: PeriodSelectorProps) {
  return (
    <div className="flex gap-1">
      {options.map((days) => (
        <button
          key={days}
          onClick={() => onChange(days)}
          className={`rounded px-3 py-1 text-sm font-medium transition-colors ${
            value === days
              ? "bg-gray-700 text-white"
              : "bg-gray-800 text-gray-400 hover:text-gray-300"
          }`}
        >
          {days}d
        </button>
      ))}
    </div>
  );
}
