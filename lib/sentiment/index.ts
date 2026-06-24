import { SentimentProvider } from "./types";
import { HeuristicSentiment } from "./heuristic";
import { ClaudeSentiment } from "./claude";

export type { SentimentProvider, SentimentResult } from "./types";

/**
 * Selects the sentiment provider from the environment. Defaults to a
 * deterministic heuristic; uses the Claude API when ANTHROPIC_API_KEY is set.
 */
export function getSentimentProvider(): SentimentProvider {
  const key = process.env.ANTHROPIC_API_KEY;
  if (key) return new ClaudeSentiment(key);
  return new HeuristicSentiment();
}
