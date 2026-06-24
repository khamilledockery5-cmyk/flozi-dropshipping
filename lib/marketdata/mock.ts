import { MarketDataProvider, Quote, WatchlistItem, round2 } from "./types";

// Simulated market data. Layers a small time-based walk on top of each item's
// base values so the dashboard shows gentle movement without any external API.
export class MockMarketData implements MarketDataProvider {
  readonly name = "mock";
  readonly live = false;

  async getQuotes(watchlist: WatchlistItem[]): Promise<Quote[]> {
    return watchlist.map((w, i) => {
      const changePct = w.baseChangePct + jitter(i + 7, 0.4);
      const price = w.basePrice * (1 + (changePct - w.baseChangePct) / 100);
      return {
        symbol: w.symbol,
        name: w.name,
        price: round2(price),
        changePct: round2(changePct),
      };
    });
  }
}

function jitter(seed: number, scale: number): number {
  const t = Math.sin(seed * 12.9898 + Date.now() / 60000) * 43758.5453;
  return (t - Math.floor(t) - 0.5) * 2 * scale;
}
