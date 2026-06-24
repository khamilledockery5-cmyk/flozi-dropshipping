import { MarketDataProvider, Quote, WatchlistItem, round2 } from "./types";

interface FinnhubQuote {
  c?: number; // current price
  dp?: number; // percent change
}

/**
 * Live market data from Finnhub (https://finnhub.io). Requires FINNHUB_API_KEY.
 * Each symbol is fetched independently; on any failure that symbol falls back to
 * its watchlist base values so the dashboard degrades gracefully.
 */
export class FinnhubMarketData implements MarketDataProvider {
  readonly name = "finnhub";
  readonly live = true;

  constructor(private readonly apiKey: string) {}

  async getQuotes(watchlist: WatchlistItem[]): Promise<Quote[]> {
    return Promise.all(watchlist.map((w) => this.getQuote(w)));
  }

  private async getQuote(w: WatchlistItem): Promise<Quote> {
    try {
      const url = `https://finnhub.io/api/v1/quote?symbol=${encodeURIComponent(w.symbol)}&token=${this.apiKey}`;
      const res = await fetch(url, { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = (await res.json()) as FinnhubQuote;
      if (!data.c) throw new Error("missing price");
      return {
        symbol: w.symbol,
        name: w.name,
        price: round2(data.c),
        changePct: round2(data.dp ?? 0),
      };
    } catch {
      return {
        symbol: w.symbol,
        name: w.name,
        price: w.basePrice,
        changePct: w.baseChangePct,
      };
    }
  }
}
