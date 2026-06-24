import { NextResponse } from "next/server";
import { getSignals, getSources } from "@/lib/signals";

export const dynamic = "force-dynamic";

export async function GET() {
  const signals = await getSignals();
  return NextResponse.json({
    signals,
    sources: getSources(),
    asOf: new Date().toISOString(),
  });
}
