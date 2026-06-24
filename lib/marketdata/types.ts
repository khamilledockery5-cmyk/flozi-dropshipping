// A symbol the app tracks, plus fallback values used when no live data source
// is configured (or a fetch fails).
export interface WatchlistItem {
  symbol: string;
  name: string;
  basePrice: number;
  baseChangePct: number;
}

export interface Quote {
  symbol: string;
  name: string;
  price: number;
  changePct: number;
}

export interface MarketDataProvider {
  readonly name: string;
  /** Whether this provider returns real (vs simulated) market data. */
  readonly live: boolean;
  getQuotes(watchlist: WatchlistItem[]): Promise<Quote[]>;
}

export function round2(n: number): number {
  return Math.round(n * 100) / 100;
}
