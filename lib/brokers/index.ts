import { Broker } from "./types";
import { PaperBroker } from "./paper";
import { LiveBroker } from "./live";

export type { Broker, OrderRequest } from "./types";
export { PaperBroker } from "./paper";
export { LiveBroker } from "./live";

/**
 * Selects the broker from the environment. Defaults to the safe paper broker.
 * Live trading only activates when TRADE_AI_LIVE is explicitly "true".
 */
export function getBroker(): Broker {
  const live = process.env.TRADE_AI_LIVE === "true";
  if (live) {
    return new LiveBroker(process.env.BROKER_API_KEY, process.env.BROKER_API_SECRET);
  }
  return new PaperBroker();
}

export function isLiveEnabled(): boolean {
  return process.env.TRADE_AI_LIVE === "true";
}
