import Anthropic from "@anthropic-ai/sdk";
import type { Quote } from "../marketdata/types";
import { SentimentProvider, SentimentResult, clamp, recommend } from "./types";

// JSON schema the model's output is constrained to (structured outputs).
const SCHEMA = {
  type: "object",
  additionalProperties: false,
  properties: {
    signals: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        properties: {
          symbol: { type: "string" },
          sentiment: { type: "number" },
          recommendation: { type: "string", enum: ["Buy", "Hold", "Sell"] },
          rationale: { type: "string" },
        },
        required: ["symbol", "sentiment", "recommendation", "rationale"],
      },
    },
  },
  required: ["signals"],
} as const;

const SYSTEM = `You are a trading sentiment analyst for an educational demo (not financial advice).
For each instrument, estimate a market sentiment score from -1 (very bearish) to 1 (very bullish) based on the
price action provided, and give a Buy/Hold/Sell recommendation plus a one-sentence rationale.`;

/**
 * LLM-backed sentiment using the Claude API. Requires ANTHROPIC_API_KEY.
 * Scores the whole watchlist in a single request and returns structured output.
 */
export class ClaudeSentiment implements SentimentProvider {
  readonly name = "claude";
  readonly ai = true;
  private readonly client: Anthropic;

  constructor(apiKey: string) {
    this.client = new Anthropic({ apiKey });
  }

  async score(quotes: Quote[]): Promise<SentimentResult[]> {
    const list = quotes
      .map((q) => `${q.symbol} (${q.name}): $${q.price}, 24h change ${q.changePct}%`)
      .join("\n");

    const response = await this.client.messages.create({
      model: "claude-opus-4-8",
      max_tokens: 1024,
      output_config: { format: { type: "json_schema", schema: SCHEMA } },
      system: SYSTEM,
      messages: [{ role: "user", content: `Score these instruments:\n${list}` }],
    });

    const block = response.content.find((b) => b.type === "text");
    if (!block || block.type !== "text") return [];

    const parsed = JSON.parse(block.text) as { signals: SentimentResult[] };
    return parsed.signals.map((s) => ({
      symbol: s.symbol,
      sentiment: clamp(s.sentiment, -1, 1),
      recommendation: s.recommendation ?? recommend(s.sentiment),
      rationale: s.rationale,
    }));
  }
}
