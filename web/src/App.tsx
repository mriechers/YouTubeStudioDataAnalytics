import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Layout from "./components/Layout";
import Health from "./pages/Health";
import Hits from "./pages/Hits";
import Opportunities from "./pages/Opportunities";
import Recent from "./pages/Recent";
import { useSSE } from "./hooks/useSSE";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 5 * 60 * 1000 } },
});

function AppInner() {
  useSSE();
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Health />} />
          <Route path="hits" element={<Hits />} />
          <Route path="opportunities" element={<Opportunities />} />
          <Route path="recent" element={<Recent />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppInner />
    </QueryClientProvider>
  );
}
