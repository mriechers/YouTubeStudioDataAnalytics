import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Layout from "./components/Layout";
import Overview from "./pages/Overview";
import Shows from "./pages/Shows";
import Shorts from "./pages/Shorts";
import Archival from "./pages/Archival";
import Subscribers from "./pages/Subscribers";
import { useSSE } from "./hooks/useSSE";
import { ChannelContext } from "./hooks/useChannel";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 5 * 60 * 1000 } },
});

function AppInner() {
  useSSE();
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Overview />} />
          <Route path="shows" element={<Shows />} />
          <Route path="shorts" element={<Shorts />} />
          <Route path="archival" element={<Archival />} />
          <Route path="subscribers" element={<Subscribers />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default function App() {
  const [channelId, setChannelId] = useState<string | undefined>(undefined);

  return (
    <QueryClientProvider client={queryClient}>
      <ChannelContext.Provider value={{ channelId, setChannelId }}>
        <AppInner />
      </ChannelContext.Provider>
    </QueryClientProvider>
  );
}
