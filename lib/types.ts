// Shared domain types for the Trade AI automation system.

export type Recommendation = "Buy" | "Hold" | "Sell";

export interface Signal {
  symbol: string;
  name: string;
  price: number;
  changePct: number;
  /** AI-derived sentiment score from -1 (bearish) to 1 (bullish). */
  sentiment: number;
  recommendation: Recommendation;
  /** One-line explanation for the sentiment/recommendation, when available. */
  rationale?: string;
}

export type Side = "buy" | "sell";

/** A field of a Signal that a rule can test. */
export type Metric = "sentiment" | "changePct" | "price";

export type Comparator = "gt" | "lt" | "gte" | "lte";

export interface Rule {
  id: string;
  /** Human-readable label. */
  name: string;
  enabled: boolean;
  /** Limit the rule to one symbol, or leave undefined to apply to all. */
  symbol?: string;
  metric: Metric;
  comparator: Comparator;
  threshold: number;
  /** What to do when the condition is met. */
  action: Side;
  /** Notional amount (USD) to trade when the rule fires. */
  amountUsd: number;
}

export interface Alert {
  id: string;
  ruleId: string;
  ruleName: string;
  symbol: string;
  message: string;
  createdAt: string;
}

export interface Order {
  id: string;
  symbol: string;
  side: Side;
  amountUsd: number;
  price: number;
  quantity: number;
  status: "filled" | "rejected";
  broker: string;
  createdAt: string;
  note?: string;
}

export interface ActivityEntry {
  id: string;
  at: string;
  kind: "cycle" | "alert" | "order" | "error";
  message: string;
}
