import Link from "next/link";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col items-center justify-center px-6 text-center">
      <span className="mb-4 rounded-full border border-white/10 bg-panel px-4 py-1 text-sm text-slate-300">
        AI-powered market insights
      </span>
      <h1 className="bg-gradient-to-br from-white to-slate-400 bg-clip-text text-5xl font-bold tracking-tight text-transparent sm:text-6xl">
        Trade AI
      </h1>
      <p className="mt-6 max-w-2xl text-lg text-slate-400">
        Surface signals, score sentiment, and track positions in one place.
        A starting point for building an AI trading assistant — wire in your own
        data sources and models as you grow.
      </p>
      <div className="mt-10 flex gap-4">
        <Link
          href="/dashboard"
          className="rounded-lg bg-accent px-6 py-3 font-medium text-white transition hover:bg-blue-600"
        >
          Open dashboard
        </Link>
        <a
          href="https://nextjs.org/docs"
          className="rounded-lg border border-white/10 px-6 py-3 font-medium text-slate-200 transition hover:bg-panel"
        >
          Docs
        </a>
      </div>
    </main>
  );
}
