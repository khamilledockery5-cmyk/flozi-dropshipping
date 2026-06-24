import type { Signal } from "@/app/api/signals/route";

function recColor(rec: Signal["recommendation"]) {
  if (rec === "Buy") return "text-up";
  if (rec === "Sell") return "text-down";
  return "text-slate-300";
}

function SentimentBar({ value }: { value: number }) {
  const pct = Math.round(((value + 1) / 2) * 100);
  const color = value >= 0.2 ? "bg-up" : value <= -0.2 ? "bg-down" : "bg-slate-400";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-24 overflow-hidden rounded-full bg-white/10">
        <div className={`h-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="w-10 text-right text-xs text-slate-400">
        {value.toFixed(2)}
      </span>
    </div>
  );
}

export default function SignalsTable({ signals }: { signals: Signal[] }) {
  return (
    <div className="overflow-hidden rounded-xl border border-white/10 bg-panel">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-white/10 text-xs uppercase tracking-wide text-slate-400">
          <tr>
            <th className="px-4 py-3">Symbol</th>
            <th className="px-4 py-3">Price</th>
            <th className="px-4 py-3">24h</th>
            <th className="px-4 py-3">AI sentiment</th>
            <th className="px-4 py-3">Signal</th>
          </tr>
        </thead>
        <tbody>
          {signals.map((s) => (
            <tr key={s.symbol} className="border-b border-white/5 last:border-0">
              <td className="px-4 py-3">
                <div className="font-medium">{s.symbol}</div>
                <div className="text-xs text-slate-500">{s.name}</div>
              </td>
              <td className="px-4 py-3 tabular-nums">${s.price.toFixed(2)}</td>
              <td
                className={`px-4 py-3 tabular-nums ${
                  s.changePct >= 0 ? "text-up" : "text-down"
                }`}
              >
                {s.changePct >= 0 ? "+" : ""}
                {s.changePct.toFixed(2)}%
              </td>
              <td className="px-4 py-3">
                <SentimentBar value={s.sentiment} />
              </td>
              <td className={`px-4 py-3 font-medium ${recColor(s.recommendation)}`}>
                {s.recommendation}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
