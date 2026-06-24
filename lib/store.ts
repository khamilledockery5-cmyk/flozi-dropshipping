import type { ActivityEntry, Alert, Order, Rule } from "./types";
import { DEFAULT_RULES } from "./rules";

// Simple in-memory store. State resets when the server restarts — fine for a
// scaffold. Swap for a database (Postgres, SQLite, Redis, …) for persistence.
interface State {
  rules: Rule[];
  alerts: Alert[];
  orders: Order[];
  activity: ActivityEntry[];
  lastRunAt: string | null;
  autoEnabled: boolean;
}

// Persist across hot-reloads in dev via globalThis.
const g = globalThis as unknown as { __tradeAiStore?: State };

function init(): State {
  return {
    rules: structuredClone(DEFAULT_RULES),
    alerts: [],
    orders: [],
    activity: [],
    lastRunAt: null,
    autoEnabled: false,
  };
}

export function store(): State {
  if (!g.__tradeAiStore) g.__tradeAiStore = init();
  return g.__tradeAiStore;
}

const MAX_LOG = 200;

export function pushAlert(alert: Alert): void {
  const s = store();
  s.alerts.unshift(alert);
  s.alerts = s.alerts.slice(0, MAX_LOG);
}

export function pushOrder(order: Order): void {
  const s = store();
  s.orders.unshift(order);
  s.orders = s.orders.slice(0, MAX_LOG);
}

export function pushActivity(entry: ActivityEntry): void {
  const s = store();
  s.activity.unshift(entry);
  s.activity = s.activity.slice(0, MAX_LOG);
}

export function setRules(rules: Rule[]): void {
  store().rules = rules;
}
