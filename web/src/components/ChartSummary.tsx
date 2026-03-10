import type { ReactNode } from "react";

interface ChartSummaryProps {
  children: ReactNode;
}

export default function ChartSummary({ children }: ChartSummaryProps) {
  return (
    <p className="mb-2 text-sm text-gray-400" role="status">
      {children}
    </p>
  );
}
