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
- **Pluggable data & sentiment** — market data and sentiment are provider
  interfaces. Defaults are a simulated price feed and a price-action heuristic;
  set keys to switch to **real Finnhub market data** and **Claude-generated
  sentiment** (see below).

## Data & sentiment sources

Signals are produced by two swappable providers, selected from the environment:

| Layer       | Default (no key)        | With key                                      |
| ----------- | ----------------------- | --------------------------------------------- |
| Market data | Simulated mock prices   | **Finnhub** live quotes (`FINNHUB_API_KEY`)   |
| Sentiment   | Price-action heuristic  | **Claude API** (`ANTHROPIC_API_KEY`)          |

- `lib/marketdata/` — `MockMarketData` (default) and `FinnhubMarketData`, behind
  `getMarketDataProvider()`. Live fetches fall back per-symbol on failure.
- `lib/sentiment/` — `HeuristicSentiment` (default) and `ClaudeSentiment`
  (`claude-opus-4-8`, structured outputs), behind `getSentimentProvider()`.
- `lib/signals.ts` combines them and caches the snapshot for `SIGNALS_TTL_SEC`
  seconds (default 30) to limit market-data and paid LLM calls.

The active sources are shown under the signals table and returned by
`/api/signals`. See `.env.example` for all keys.

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
  signals.ts                  Combines market data + sentiment (cached)
  marketdata/                 Market-data providers (mock + Finnhub)
  sentiment/                  Sentiment providers (heuristic + Claude)
  rules.ts                    Strategy/rules engine
  engine.ts                   One automation cycle
  scheduler.ts                In-process interval scheduler
  store.ts                    In-memory state (swap for a DB)
  brokers/                    Broker adapters (paper + live stub)
instrumentation.ts            Starts the scheduler on boot (opt-in)
```

## Next steps

- Set `FINNHUB_API_KEY` and `ANTHROPIC_API_KEY` to enable real market data and
  Claude-generated sentiment (or implement another provider in `lib/marketdata/`
  / `lib/sentiment/`).
- Feed the sentiment model richer context (news, filings) beyond price action.
- Swap the in-memory `lib/store.ts` for a database to persist rules and history.
- Implement `lib/brokers/live.ts` for your broker before enabling live trading.
- Add auth and per-user watchlists, positions, and risk limits.
