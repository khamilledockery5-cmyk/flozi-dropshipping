import { NextResponse } from "next/server";

export interface Signal {
  symbol: string;
  name: string;
  price: number;
  changePct: number;
  /** AI-derived sentiment score from -1 (bearish) to 1 (bullish). */
  sentiment: number;
  recommendation: "Buy" | "Hold" | "Sell";
}

// Deterministic mock data. Swap this route for a real market-data + model
// integration when you're ready to go live.
const SIGNALS: Signal[] = [
  { symbol: "AAPL", name: "Apple", price: 214.32, changePct: 1.24, sentiment: 0.62, recommendation: "Buy" },
  { symbol: "TSLA", name: "Tesla", price: 178.91, changePct: -2.13, sentiment: -0.18, recommendation: "Hold" },
  { symbol: "NVDA", name: "Nvidia", price: 126.45, changePct: 3.41, sentiment: 0.81, recommendation: "Buy" },
  { symbol: "MSFT", name: "Microsoft", price: 447.12, changePct: 0.42, sentiment: 0.35, recommendation: "Hold" },
  { symbol: "AMZN", name: "Amazon", price: 189.05, changePct: -0.87, sentiment: 0.11, recommendation: "Hold" },
  { symbol: "META", name: "Meta", price: 502.30, changePct: 2.05, sentiment: 0.54, recommendation: "Buy" },
];

export function GET() {
  return NextResponse.json({ signals: SIGNALS, asOf: new Date().toISOString() });
}
