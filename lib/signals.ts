import { getMarketDataProvider } from "./marketdata";
import type { WatchlistItem } from "./marketdata";
import { getSentimentProvider } from "./sentiment";
import type { SentimentResult } from "./sentiment";
import { recommend } from "./sentiment/types";
import type { Signal } from "./types";

// The instruments the app tracks. The base values are used as fallbacks when no
// live market-data source is configured (or a fetch fails).
const WATCHLIST: WatchlistItem[] = [
  { symbol: "AAPL", name: "Apple", basePrice: 214.32, baseChangePct: 1.24 },
  { symbol: "TSLA", name: "Tesla", basePrice: 178.91, baseChangePct: -2.13 },
  { symbol: "NVDA", name: "Nvidia", basePrice: 126.45, baseChangePct: 3.41 },
  { symbol: "MSFT", name: "Microsoft", basePrice: 447.12, baseChangePct: 0.42 },
  { symbol: "AMZN", name: "Amazon", basePrice: 189.05, baseChangePct: -0.87 },
  { symbol: "META", name: "Meta", basePrice: 502.3, baseChangePct: 2.05 },
];

function ttlMs(): number {
  return Math.max(5, Number(process.env.SIGNALS_TTL_SEC ?? 30)) * 1000;
}

// Cache the combined snapshot to limit market-data and (paid) LLM calls — the
// dashboard polls every few seconds but the underlying data refreshes slower.
const g = globalThis as unknown as { __tradeAiSignals?: { at: number; signals: Signal[] } };

/**
 * Returns the current signal snapshot: live quotes scored for sentiment by the
 * configured providers (mock + heuristic by default; Finnhub + Claude when keys
 * are set). Cached for SIGNALS_TTL_SEC seconds.
 */
export async function getSignals(): Promise<Signal[]> {
  const cached = g.__tradeAiSignals;
  if (cached && Date.now() - cached.at < ttlMs()) return cached.signals;

  const quotes = await getMarketDataProvider().getQuotes(WATCHLIST);

  let scores: SentimentResult[];
  try {
    scores = await getSentimentProvider().score(quotes);
  } catch {
    scores = [];
  }
  const bySymbol = new Map(scores.map((s) => [s.symbol, s]));

  const signals: Signal[] = quotes.map((q) => {
    const s = bySymbol.get(q.symbol);
    const sentiment = s ? s.sentiment : q.changePct / 5;
    return {
      symbol: q.symbol,
      name: q.name,
      price: q.price,
      changePct: q.changePct,
      sentiment: round2(sentiment),
      recommendation: s?.recommendation ?? recommend(sentiment),
      rationale: s?.rationale,
    };
  });

  g.__tradeAiSignals = { at: Date.now(), signals };
  return signals;
}

/** Names of the active data/sentiment providers, for display. */
export function getSources() {
  const market = getMarketDataProvider();
  const sentiment = getSentimentProvider();
  return {
    market: market.name,
    marketLive: market.live,
    sentiment: sentiment.name,
    sentimentAi: sentiment.ai,
  };
}

function round2(n: number): number {
  return Math.round(n * 100) / 100;
}
