import Link from "next/link";
import LiveSignals from "@/components/LiveSignals";
import AutomationPanel from "@/components/AutomationPanel";

export default function Dashboard() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-12">
      <div className="mb-8">
        <Link href="/" className="text-sm text-slate-400 hover:text-slate-200">
          ← Trade AI
        </Link>
        <h1 className="mt-1 text-3xl font-bold">Dashboard</h1>
      </div>

      <section className="mb-12">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-400">
          Signals
        </h2>
        <LiveSignals />
      </section>

      <section>
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-400">
          Automation
        </h2>
        <AutomationPanel />
      </section>

      <p className="mt-8 text-xs text-slate-500">
        Sample data and simulated (paper) trading for scaffolding only. Not
        financial advice. Live trading is disabled unless explicitly enabled and
        implemented — see the README.
      </p>
    </main>
  );
}
