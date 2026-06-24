import { NextResponse } from "next/server";
import { runCycle } from "@/lib/engine";

export const dynamic = "force-dynamic";

// Trigger a single automation cycle on demand. Wire this to an external
// scheduler (cron, GitHub Actions, a queue) for production-grade scheduling.
export async function POST() {
  try {
    const result = await runCycle();
    return NextResponse.json({ ok: true, result });
  } catch (err) {
    return NextResponse.json(
      { ok: false, error: err instanceof Error ? err.message : String(err) },
      { status: 500 },
    );
  }
}
