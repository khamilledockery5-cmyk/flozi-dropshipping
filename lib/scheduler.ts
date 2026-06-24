import { runCycle } from "./engine";
import { pushActivity, store } from "./store";

// In-process scheduler. Started from instrumentation.ts when AUTOMATION_ENABLED
// is "true". The interval (seconds) is configurable via AUTOMATION_INTERVAL_SEC.
const g = globalThis as unknown as { __tradeAiTimer?: NodeJS.Timeout };

export function startScheduler(): void {
  if (g.__tradeAiTimer) return; // already running

  const seconds = Number(process.env.AUTOMATION_INTERVAL_SEC ?? 60);
  const intervalMs = Math.max(5, seconds) * 1000;

  store().autoEnabled = true;
  pushActivity({
    id: `act_${Date.now().toString(36)}`,
    at: new Date().toISOString(),
    kind: "cycle",
    message: `Scheduler started: running every ${intervalMs / 1000}s.`,
  });

  g.__tradeAiTimer = setInterval(() => {
    runCycle().catch((err) => {
      pushActivity({
        id: `act_${Date.now().toString(36)}`,
        at: new Date().toISOString(),
        kind: "error",
        message: `Cycle failed: ${err instanceof Error ? err.message : String(err)}`,
      });
    });
  }, intervalMs);

  // Don't keep the process alive solely for this timer.
  g.__tradeAiTimer.unref?.();
}

export function stopScheduler(): void {
  if (g.__tradeAiTimer) {
    clearInterval(g.__tradeAiTimer);
    g.__tradeAiTimer = undefined;
    store().autoEnabled = false;
  }
}
