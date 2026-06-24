import { NextResponse } from "next/server";
import { isLiveEnabled } from "@/lib/brokers";
import { store } from "@/lib/store";

export const dynamic = "force-dynamic";

export function GET() {
  const s = store();
  return NextResponse.json({
    lastRunAt: s.lastRunAt,
    autoEnabled: s.autoEnabled,
    live: isLiveEnabled(),
    broker: isLiveEnabled() ? "live" : "paper",
    counts: {
      rules: s.rules.length,
      enabledRules: s.rules.filter((r) => r.enabled).length,
      alerts: s.alerts.length,
      orders: s.orders.length,
    },
    activity: s.activity.slice(0, 25),
    alerts: s.alerts.slice(0, 25),
    orders: s.orders.slice(0, 25),
  });
}
