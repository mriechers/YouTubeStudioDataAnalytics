import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import { useChannel } from "../hooks/useChannel";

export default function ChannelSelector() {
  const { channelId, setChannelId } = useChannel();
  const { data: channels } = useQuery({
    queryKey: ["channels"],
    queryFn: api.getChannels,
  });

  if (!channels || channels.length <= 1) return null;

  return (
    <select
      value={channelId ?? ""}
      onChange={(e) => setChannelId(e.target.value || undefined)}
      className="w-full rounded-md border border-gray-700 bg-gray-800 px-3 py-1.5 text-sm text-gray-200 focus:border-blue-500 focus:outline-none"
    >
      <option value="">All Channels</option>
      {channels.map((ch) => (
        <option key={ch.id} value={ch.id}>
          {ch.name}
        </option>
      ))}
    </select>
  );
}
