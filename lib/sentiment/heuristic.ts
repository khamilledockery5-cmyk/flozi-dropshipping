import type { Quote } from "../marketdata/types";
import { SentimentProvider, SentimentResult, clamp, recommend } from "./types";

/**
 * Deterministic fallback. Derives sentiment from recent price action when no
 * LLM is configured: a +5% move maps to roughly +1.0 sentiment.
 */
export class HeuristicSentiment implements SentimentProvider {
  readonly name = "heuristic";
  readonly ai = false;

  async score(quotes: Quote[]): Promise<SentimentResult[]> {
    return quotes.map((q) => {
      const sentiment = Math.round(clamp(q.changePct / 5, -1, 1) * 100) / 100;
      return {
        symbol: q.symbol,
        sentiment,
        recommendation: recommend(sentiment),
        rationale: `Derived from 24h change of ${q.changePct}%.`,
      };
    });
  }
}
