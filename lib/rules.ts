import type { Comparator, Metric, Rule, Signal } from "./types";

// Default starter strategy. These are illustrative only — edit via the API or
// the dashboard's rules endpoint to build your own strategy.
export const DEFAULT_RULES: Rule[] = [
  {
    id: "buy-strong-bullish",
    name: "Buy strongly bullish",
    enabled: true,
    metric: "sentiment",
    comparator: "gte",
    threshold: 0.7,
    action: "buy",
    amountUsd: 500,
  },
  {
    id: "sell-bearish",
    name: "Sell on bearish turn",
    enabled: true,
    metric: "sentiment",
    comparator: "lte",
    threshold: -0.3,
    action: "sell",
    amountUsd: 500,
  },
  {
    id: "buy-dip",
    name: "Buy the dip (>3% down)",
    enabled: false,
    metric: "changePct",
    comparator: "lte",
    threshold: -3,
    action: "buy",
    amountUsd: 250,
  },
];

const COMPARATORS: Record<Comparator, (a: number, b: number) => boolean> = {
  gt: (a, b) => a > b,
  lt: (a, b) => a < b,
  gte: (a, b) => a >= b,
  lte: (a, b) => a <= b,
};

const SYMBOLS: Record<Comparator, string> = {
  gt: ">",
  lt: "<",
  gte: "≥",
  lte: "≤",
};

function metricValue(signal: Signal, metric: Metric): number {
  return signal[metric];
}

export interface RuleMatch {
  rule: Rule;
  signal: Signal;
}

/** Returns every (rule, signal) pair where an enabled rule's condition holds. */
export function evaluateRules(rules: Rule[], signals: Signal[]): RuleMatch[] {
  const matches: RuleMatch[] = [];
  for (const rule of rules) {
    if (!rule.enabled) continue;
    for (const signal of signals) {
      if (rule.symbol && rule.symbol !== signal.symbol) continue;
      const value = metricValue(signal, rule.metric);
      if (COMPARATORS[rule.comparator](value, rule.threshold)) {
        matches.push({ rule, signal });
      }
    }
  }
  return matches;
}

export function describeRule(rule: Rule): string {
  const scope = rule.symbol ?? "any symbol";
  return `${scope} ${rule.metric} ${SYMBOLS[rule.comparator]} ${rule.threshold} → ${rule.action.toUpperCase()} $${rule.amountUsd}`;
}

export function matchMessage(match: RuleMatch): string {
  const { rule, signal } = match;
  const value = metricValue(signal, rule.metric);
  return `${signal.symbol}: ${rule.metric} ${value} ${SYMBOLS[rule.comparator]} ${rule.threshold} → ${rule.action.toUpperCase()} $${rule.amountUsd}`;
}
