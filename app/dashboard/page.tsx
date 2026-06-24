import Link from "next/link";
import SignalsTable from "@/components/SignalsTable";
import type { Signal } from "@/app/api/signals/route";

async function getSignals(): Promise<{ signals: Signal[]; asOf: string }> {
  // Read directly from the route's data source. In a real app you might fetch
  // from an external service or query a database here instead.
  const { GET } = await import("@/app/api/signals/route");
  const res = GET();
  return res.json();
}

export default async function Dashboard() {
  const { signals, asOf } = await getSignals();

  const bullish = signals.filter((s) => s.sentiment >= 0.2).length;
  const avgSentiment =
    signals.reduce((sum, s) => sum + s.sentiment, 0) / signals.length;

  return (
    <main className="mx-auto max-w-5xl px-6 py-12">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <Link href="/" className="text-sm text-slate-400 hover:text-slate-200">
            ← Trade AI
          </Link>
          <h1 className="mt-1 text-3xl font-bold">Dashboard</h1>
        </div>
        <span className="text-xs text-slate-500">
          As of {new Date(asOf).toLocaleString()}
        </span>
      </div>

      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Stat label="Tracked symbols" value={String(signals.length)} />
        <Stat label="Bullish signals" value={String(bullish)} />
        <Stat label="Avg sentiment" value={avgSentiment.toFixed(2)} />
      </div>

      <SignalsTable signals={signals} />

      <p className="mt-6 text-xs text-slate-500">
        Data shown is mock/sample data for scaffolding purposes only and is not
        financial advice.
      </p>
    </main>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-panel p-5">
      <div className="text-sm text-slate-400">{label}</div>
      <div className="mt-1 text-2xl font-semibold tabular-nums">{value}</div>
    </div>
  );
}
