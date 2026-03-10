interface EmptyStateProps {
  message: string;
  suggestion?: string;
}

export default function EmptyState({ message, suggestion }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <p className="text-gray-400">{message}</p>
      {suggestion && <p className="mt-1 text-sm text-gray-500">{suggestion}</p>}
    </div>
  );
}
