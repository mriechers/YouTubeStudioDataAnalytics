import { createContext, useContext } from "react";

interface ChannelContextValue {
  channelId: string | undefined;
  setChannelId: (id: string | undefined) => void;
}

export const ChannelContext = createContext<ChannelContextValue>({
  channelId: undefined,
  setChannelId: () => {},
});

export const useChannel = () => useContext(ChannelContext);
