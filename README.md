# Trade AI

An AI-powered trading assistant — scaffolded as a [Next.js](https://nextjs.org)
web app (App Router, TypeScript, Tailwind CSS).

> ⚠️ This is a starter scaffold. The market data and "AI sentiment" scores are
> mock/sample values. It is **not** financial advice. Wire in real market-data
> feeds and your own models before using it for anything real.

## Features

- **Landing page** (`/`) — product intro and call to action.
- **Dashboard** (`/dashboard`) — auto-refreshing signals table, summary stats,
  and an automation panel (alerts, orders, activity log).
- **Strategy / rules engine** — user-defined conditions on sentiment, price, or
  24h change that emit alerts and trigger orders.
- **Scheduled automation** — a background engine that pulls signals, evaluates
  rules, and acts on an interval.
- **Alerts & auto-refresh** — the dashboard polls every 5s; matched rules raise
  alerts in real time.
- **Live trade execution** — a pluggable broker adapter. Ships with a safe
  **paper (simulated) broker by default**; a live adapter is env-gated and
  unimplemented until you wire in your own broker.

## Automation

The automation system lives under `lib/` and is exposed via API routes:

| Route                     | Method | Purpose                                       |
| ------------------------- | ------ | --------------------------------------------- |
| `/api/signals`            | GET    | Current signal snapshot                       |
| `/api/rules`              | GET/PUT| Read or replace the strategy rule set         |
| `/api/automation`         | GET    | Status, counts, recent alerts/orders/activity |
| `/api/automation/run`     | POST   | Run a single automation cycle on demand       |

**One cycle** = pull signals → evaluate enabled rules → raise an alert per match
→ place an order through the configured broker → append to the activity log.

### Scheduling

- **In-process:** set `AUTOMATION_ENABLED=true` (and optionally
  `AUTOMATION_INTERVAL_SEC`). `instrumentation.ts` starts the scheduler on boot.
- **External (recommended for production):** leave the in-process scheduler off
  and `POST /api/automation/run` from cron, a GitHub Action, or a queue.

### ⚠️ Live trading

Live trading is **off by default**. The default `PaperBroker` simulates fills
and never touches real money. To go live you must, deliberately:

1. Set `TRADE_AI_LIVE=true` and provide `BROKER_API_KEY` / `BROKER_API_SECRET`.
2. Implement `placeOrder` in `lib/brokers/live.ts` against your broker/exchange.

Until step 2 is done, live orders are **rejected** by design, so enabling live
mode without finishing the integration cannot move money. See `.env.example`.

## Getting started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Scripts

| Command             | Description                          |
| ------------------- | ------------------------------------ |
| `npm run dev`       | Start the dev server                 |
| `npm run build`     | Production build                     |
| `npm run start`     | Run the production build             |
| `npm run lint`      | Lint with ESLint                     |
| `npm run typecheck` | Type-check with `tsc --noEmit`       |

## Project structure

```
app/
  page.tsx                    Landing page
  dashboard/page.tsx          Dashboard (signals + automation)
  api/signals/route.ts        Signals API
  api/rules/route.ts          Strategy rules (GET/PUT)
  api/automation/route.ts     Automation status
  api/automation/run/route.ts Run one cycle (POST)
components/
  SignalsTable.tsx            Signals table + sentiment bars
  LiveSignals.tsx             Auto-refreshing signals view
  AutomationPanel.tsx         Alerts / orders / activity + controls
lib/
  types.ts                    Shared domain types
  signals.ts                  Signal source (replace with real data)
  rules.ts                    Strategy/rules engine
  engine.ts                   One automation cycle
  scheduler.ts                In-process interval scheduler
  store.ts                    In-memory state (swap for a DB)
  brokers/                    Broker adapters (paper + live stub)
instrumentation.ts            Starts the scheduler on boot (opt-in)
```

## Next steps

- Replace the sample data in `lib/signals.ts` with a real market-data provider.
- Plug in an LLM (e.g. the Claude API) to generate the sentiment scores and
  recommendations from news/filings.
- Swap the in-memory `lib/store.ts` for a database to persist rules and history.
- Implement `lib/brokers/live.ts` for your broker before enabling live trading.
- Add auth and per-user watchlists, positions, and risk limits.
