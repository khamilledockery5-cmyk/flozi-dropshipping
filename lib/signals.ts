import type { Signal } from "./types";

// Deterministic base data. A small pseudo-random walk is layered on top at read
// time so the dashboard's auto-refresh shows live movement. Swap this module for
// a real market-data + model integration when you're ready to go live.
const BASE: Signal[] = [
  { symbol: "AAPL", name: "Apple", price: 214.32, changePct: 1.24, sentiment: 0.62, recommendation: "Buy" },
  { symbol: "TSLA", name: "Tesla", price: 178.91, changePct: -2.13, sentiment: -0.18, recommendation: "Hold" },
  { symbol: "NVDA", name: "Nvidia", price: 126.45, changePct: 3.41, sentiment: 0.81, recommendation: "Buy" },
  { symbol: "MSFT", name: "Microsoft", price: 447.12, changePct: 0.42, sentiment: 0.35, recommendation: "Hold" },
  { symbol: "AMZN", name: "Amazon", price: 189.05, changePct: -0.87, sentiment: 0.11, recommendation: "Hold" },
  { symbol: "META", name: "Meta", price: 502.30, changePct: 2.05, sentiment: 0.54, recommendation: "Buy" },
];

function recommend(sentiment: number): Signal["recommendation"] {
  if (sentiment >= 0.4) return "Buy";
  if (sentiment <= -0.3) return "Sell";
  return "Hold";
}

function jitter(seed: number, scale: number): number {
  // Cheap deterministic-ish noise based on the current minute so repeated calls
  // within a refresh window stay stable but evolve over time.
  const t = Math.sin(seed * 12.9898 + Date.now() / 60000) * 43758.5453;
  return (t - Math.floor(t) - 0.5) * 2 * scale;
}

/** Returns the current signal snapshot. */
export function getSignals(): Signal[] {
  return BASE.map((s, i) => {
    const sentiment = clamp(s.sentiment + jitter(i + 1, 0.08), -1, 1);
    const changePct = s.changePct + jitter(i + 7, 0.4);
    const price = round2(s.price * (1 + changePct / 100 - s.changePct / 100));
    return {
      ...s,
      price,
      changePct: round2(changePct),
      sentiment: round2(sentiment),
      recommendation: recommend(sentiment),
    };
  });
}

function clamp(n: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, n));
}

function round2(n: number): number {
  return Math.round(n * 100) / 100;
}
