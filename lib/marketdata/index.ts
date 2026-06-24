import { MarketDataProvider } from "./types";
import { MockMarketData } from "./mock";
import { FinnhubMarketData } from "./finnhub";

export type { MarketDataProvider, Quote, WatchlistItem } from "./types";

/**
 * Selects the market-data provider from the environment. Defaults to simulated
 * data; uses live Finnhub data when FINNHUB_API_KEY is set.
 */
export function getMarketDataProvider(): MarketDataProvider {
  const key = process.env.FINNHUB_API_KEY;
  if (key) return new FinnhubMarketData(key);
  return new MockMarketData();
}
