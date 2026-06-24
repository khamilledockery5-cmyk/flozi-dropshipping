import { NextResponse } from "next/server";
import { describeRule } from "@/lib/rules";
import { setRules, store } from "@/lib/store";
import type { Rule } from "@/lib/types";

export const dynamic = "force-dynamic";

export function GET() {
  const rules = store().rules;
  return NextResponse.json({
    rules: rules.map((r) => ({ ...r, description: describeRule(r) })),
  });
}

// Replace the full rule set. Body: { rules: Rule[] }.
export async function PUT(req: Request) {
  let body: { rules?: unknown };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body." }, { status: 400 });
  }

  if (!Array.isArray(body.rules)) {
    return NextResponse.json({ error: "Expected { rules: Rule[] }." }, { status: 400 });
  }

  const valid: Rule[] = [];
  for (const r of body.rules as Rule[]) {
    if (
      typeof r?.id !== "string" ||
      typeof r?.name !== "string" ||
      typeof r?.threshold !== "number" ||
      typeof r?.amountUsd !== "number" ||
      !["sentiment", "changePct", "price"].includes(r?.metric) ||
      !["gt", "lt", "gte", "lte"].includes(r?.comparator) ||
      !["buy", "sell"].includes(r?.action)
    ) {
      return NextResponse.json({ error: `Invalid rule: ${JSON.stringify(r)}` }, { status: 400 });
    }
    valid.push({
      id: r.id,
      name: r.name,
      enabled: Boolean(r.enabled),
      symbol: r.symbol || undefined,
      metric: r.metric,
      comparator: r.comparator,
      threshold: r.threshold,
      action: r.action,
      amountUsd: r.amountUsd,
    });
  }

  setRules(valid);
  return NextResponse.json({ ok: true, count: valid.length });
}
