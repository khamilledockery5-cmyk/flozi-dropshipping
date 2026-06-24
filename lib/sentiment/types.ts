import type { Quote } from "../marketdata/types";
import type { Recommendation } from "../types";

export interface SentimentResult {
  symbol: string;
  /** -1 (very bearish) to 1 (very bullish). */
  sentiment: number;
  recommendation: Recommendation;
  rationale?: string;
}

export interface SentimentProvider {
  readonly name: string;
  /** Whether scores come from an LLM (vs a deterministic heuristic). */
  readonly ai: boolean;
  score(quotes: Quote[]): Promise<SentimentResult[]>;
}

export function recommend(sentiment: number): Recommendation {
  if (sentiment >= 0.4) return "Buy";
  if (sentiment <= -0.3) return "Sell";
  return "Hold";
}

export function clamp(n: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, n));
}
