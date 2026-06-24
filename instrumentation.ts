// Next.js runs this once on server startup. We use it to optionally start the
// background automation scheduler. It stays off unless AUTOMATION_ENABLED=true
// so the app never trades on its own without opt-in.
export async function register() {
  if (process.env.NEXT_RUNTIME !== "nodejs") return;
  if (process.env.AUTOMATION_ENABLED !== "true") return;

  const { startScheduler } = await import("./lib/scheduler");
  startScheduler();
}
