"use client";

import { useEffect, useState } from "react";
import SignalsTable from "@/components/SignalsTable";
import type { Signal } from "@/lib/types";

export default function LiveSignals() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [asOf, setAsOf] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const load = async () => {
      const res = await fetch("/api/signals", { cache: "no-store" });
      if (!res.ok || !active) return;
      const data = await res.json();
      setSignals(data.signals);
      setAsOf(data.asOf);
    };
    load();
    const t = setInterval(load, 5000); // auto-refresh every 5s
    return () => {
      active = false;
      clearInterval(t);
    };
  }, []);

  const bullish = signals.filter((s) => s.sentiment >= 0.2).length;
  const avg = signals.length
    ? signals.reduce((sum, s) => sum + s.sentiment, 0) / signals.length
    : 0;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Stat label="Tracked symbols" value={String(signals.length)} />
        <Stat label="Bullish signals" value={String(bullish)} />
        <Stat label="Avg sentiment" value={avg.toFixed(2)} />
      </div>
      {signals.length > 0 ? (
        <SignalsTable signals={signals} />
      ) : (
        <div className="rounded-xl border border-white/10 bg-panel p-6 text-center text-sm text-slate-500">
          Loading signals…
        </div>
      )}
      {asOf && (
        <p className="text-xs text-slate-500">
          Auto-refreshing every 5s · as of {new Date(asOf).toLocaleTimeString()}
        </p>
      )}
    </div>
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
