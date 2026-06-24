import { NextResponse } from "next/server";
import { getSignals } from "@/lib/signals";

export const dynamic = "force-dynamic";

export function GET() {
  return NextResponse.json({ signals: getSignals(), asOf: new Date().toISOString() });
}
