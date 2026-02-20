import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";

export function useSSE() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const source = new EventSource("/api/v1/events");

    source.addEventListener("data-refreshed", () => {
      queryClient.invalidateQueries();
    });

    source.onerror = () => {
      source.close();
    };

    return () => source.close();
  }, [queryClient]);
}
