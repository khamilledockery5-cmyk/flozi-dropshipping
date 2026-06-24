import { getBroker, isLiveEnabled } from "./brokers";
import { evaluateRules, matchMessage } from "./rules";
import { getSignals } from "./signals";
import {
  pushActivity,
  pushAlert,
  pushOrder,
  store,
} from "./store";
import type { Alert, Order } from "./types";

function id(prefix: string): string {
  return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 7)}`;
}

export interface CycleResult {
  at: string;
  matches: number;
  alerts: Alert[];
  orders: Order[];
  live: boolean;
  broker: string;
}

/**
 * Runs one automation cycle: pull the latest signals, evaluate the active
 * rules, raise an alert for every match, and place an order through the
 * configured broker (paper by default).
 */
export async function runCycle(): Promise<CycleResult> {
  const s = store();
  const at = new Date().toISOString();
  const broker = getBroker();
  const signals = await getSignals();
  const matches = evaluateRules(s.rules, signals);

  const alerts: Alert[] = [];
  const orders: Order[] = [];

  for (const match of matches) {
    const message = matchMessage(match);

    const alert: Alert = {
      id: id("alert"),
      ruleId: match.rule.id,
      ruleName: match.rule.name,
      symbol: match.signal.symbol,
      message,
      createdAt: at,
    };
    pushAlert(alert);
    pushActivity({ id: id("act"), at, kind: "alert", message });
    alerts.push(alert);

    const order = await broker.placeOrder({
      symbol: match.signal.symbol,
      side: match.rule.action,
      amountUsd: match.rule.amountUsd,
      price: match.signal.price,
    });
    pushOrder(order);
    pushActivity({
      id: id("act"),
      at,
      kind: "order",
      message: `${order.status.toUpperCase()} ${order.side} ${order.symbol} $${order.amountUsd} via ${order.broker}${order.note ? ` — ${order.note}` : ""}`,
    });
    orders.push(order);
  }

  s.lastRunAt = at;
  pushActivity({
    id: id("act"),
    at,
    kind: "cycle",
    message: `Cycle complete: ${matches.length} match(es), ${orders.length} order(s) via ${broker.name}.`,
  });

  return {
    at,
    matches: matches.length,
    alerts,
    orders,
    live: isLiveEnabled(),
    broker: broker.name,
  };
}
