"use client";

import { useCallback, useEffect, useState } from "react";
import type { ActivityEntry, Alert, Order } from "@/lib/types";

interface AutomationStatus {
  lastRunAt: string | null;
  autoEnabled: boolean;
  live: boolean;
  broker: string;
  counts: { rules: number; enabledRules: number; alerts: number; orders: number };
  activity: ActivityEntry[];
  alerts: Alert[];
  orders: Order[];
}

const kindColor: Record<ActivityEntry["kind"], string> = {
  cycle: "text-slate-400",
  alert: "text-accent",
  order: "text-up",
  error: "text-down",
};

export default function AutomationPanel() {
  const [status, setStatus] = useState<AutomationStatus | null>(null);
  const [running, setRunning] = useState(false);
  const [auto, setAuto] = useState(false);

  const refresh = useCallback(async () => {
    const res = await fetch("/api/automation", { cache: "no-store" });
    if (res.ok) setStatus(await res.json());
  }, []);

  const runOnce = useCallback(async () => {
    setRunning(true);
    try {
      await fetch("/api/automation/run", { method: "POST" });
      await refresh();
    } finally {
      setRunning(false);
    }
  }, [refresh]);

  // Poll status every 5s for live alerts/activity.
  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 5000);
    return () => clearInterval(t);
  }, [refresh]);

  // Client-side auto-run loop (in addition to the optional server scheduler).
  useEffect(() => {
    if (!auto) return;
    const t = setInterval(runOnce, 10000);
    return () => clearInterval(t);
  }, [auto, runOnce]);

  if (!status) {
    return (
      <div className="rounded-xl border border-white/10 bg-panel p-5 text-sm text-slate-400">
        Loading automation status…
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3 rounded-xl border border-white/10 bg-panel p-5">
        <div className="mr-auto">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Automation</span>
            <span
              className={`rounded-full px-2 py-0.5 text-xs ${
                status.live
                  ? "bg-down/20 text-down"
                  : "bg-up/20 text-up"
              }`}
            >
              {status.live ? "LIVE" : "PAPER"} · {status.broker}
            </span>
          </div>
          <div className="mt-1 text-xs text-slate-500">
            {status.counts.enabledRules}/{status.counts.rules} rules active ·{" "}
            {status.counts.orders} orders ·{" "}
            {status.lastRunAt
              ? `last run ${new Date(status.lastRunAt).toLocaleTimeString()}`
              : "never run"}
          </div>
        </div>

        <button
          onClick={runOnce}
          disabled={running}
          className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-600 disabled:opacity-50"
        >
          {running ? "Running…" : "Run cycle"}
        </button>

        <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-300">
          <input
            type="checkbox"
            checked={auto}
            onChange={(e) => setAuto(e.target.checked)}
            className="h-4 w-4 accent-blue-500"
          />
          Auto-run (10s)
        </label>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel title={`Alerts (${status.alerts.length})`}>
          {status.alerts.length === 0 ? (
            <Empty>No alerts yet. Run a cycle to evaluate rules.</Empty>
          ) : (
            status.alerts.map((a) => (
              <Row key={a.id} time={a.createdAt}>
                <span className="text-accent">{a.ruleName}</span> — {a.message}
              </Row>
            ))
          )}
        </Panel>

        <Panel title={`Orders (${status.orders.length})`}>
          {status.orders.length === 0 ? (
            <Empty>No orders yet.</Empty>
          ) : (
            status.orders.map((o) => (
              <Row key={o.id} time={o.createdAt}>
                <span className={o.status === "filled" ? "text-up" : "text-down"}>
                  {o.status.toUpperCase()}
                </span>{" "}
                {o.side} {o.symbol} ${o.amountUsd} @ ${o.price.toFixed(2)}{" "}
                <span className="text-slate-500">({o.broker})</span>
              </Row>
            ))
          )}
        </Panel>
      </div>

      <Panel title="Activity">
        {status.activity.length === 0 ? (
          <Empty>No activity yet.</Empty>
        ) : (
          status.activity.map((e) => (
            <Row key={e.id} time={e.at}>
              <span className={kindColor[e.kind]}>[{e.kind}]</span> {e.message}
            </Row>
          ))
        )}
      </Panel>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-white/10 bg-panel">
      <div className="border-b border-white/10 px-4 py-2 text-xs uppercase tracking-wide text-slate-400">
        {title}
      </div>
      <div className="max-h-64 divide-y divide-white/5 overflow-auto">{children}</div>
    </div>
  );
}

function Row({ time, children }: { time: string; children: React.ReactNode }) {
  return (
    <div className="flex gap-3 px-4 py-2 text-sm">
      <span className="shrink-0 text-xs text-slate-600">
        {new Date(time).toLocaleTimeString()}
      </span>
      <span className="text-slate-200">{children}</span>
    </div>
  );
}

function Empty({ children }: { children: React.ReactNode }) {
  return <div className="px-4 py-6 text-center text-sm text-slate-500">{children}</div>;
}
