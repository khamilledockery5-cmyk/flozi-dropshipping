# Trade AI

An AI-powered trading assistant — scaffolded as a [Next.js](https://nextjs.org)
web app (App Router, TypeScript, Tailwind CSS).

> ⚠️ This is a starter scaffold. The market data and "AI sentiment" scores are
> mock/sample values. It is **not** financial advice. Wire in real market-data
> feeds and your own models before using it for anything real.

## Features

- **Landing page** (`/`) — product intro and call to action.
- **Dashboard** (`/dashboard`) — tracked symbols, summary stats, and an
  AI-sentiment signals table.
- **API route** (`/api/signals`) — returns sample signals as JSON; the single
  place to swap in a real data source.

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
  page.tsx            Landing page
  dashboard/page.tsx  Dashboard
  api/signals/route.ts  Sample signals API (replace with real data)
components/
  SignalsTable.tsx    Signals table + sentiment bars
```

## Next steps

- Replace the mock data in `app/api/signals/route.ts` with a real market-data
  provider.
- Plug in an LLM (e.g. the Claude API) to generate the sentiment scores and
  recommendations from news/filings.
- Add auth and persistence for user watchlists and positions.
