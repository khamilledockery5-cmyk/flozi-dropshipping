import type { Order } from "../types";
import { Broker, OrderRequest, newOrderId } from "./types";

/**
 * Live broker adapter — a STUB. It is intentionally not wired to any real
 * exchange. To go live you must:
 *   1. Set TRADE_AI_LIVE=true and provide BROKER_API_KEY / BROKER_API_SECRET.
 *   2. Implement `placeOrder` against your broker/exchange REST or FIX API.
 *
 * Until you implement the call below, every order is rejected so that enabling
 * live mode without finishing the integration cannot move real money.
 */
export class LiveBroker implements Broker {
  readonly name = "live";
  readonly live = true;

  constructor(
    private readonly apiKey: string | undefined,
    private readonly apiSecret: string | undefined,
  ) {}

  async placeOrder(req: OrderRequest): Promise<Order> {
    const base: Order = {
      id: newOrderId(),
      symbol: req.symbol,
      side: req.side,
      amountUsd: req.amountUsd,
      price: req.price,
      quantity: 0,
      status: "rejected",
      broker: this.name,
      createdAt: new Date().toISOString(),
    };

    if (!this.apiKey || !this.apiSecret) {
      return {
        ...base,
        note: "Live broker rejected: missing BROKER_API_KEY/BROKER_API_SECRET.",
      };
    }

    // TODO: Replace this block with a real API call to your broker, e.g.:
    //   const res = await fetch("https://api.yourbroker.com/v1/orders", {
    //     method: "POST",
    //     headers: { Authorization: `Bearer ${this.apiKey}`, ... },
    //     body: JSON.stringify({ symbol, side, notional: amountUsd }),
    //   });
    //   ...map the response into an Order...
    return {
      ...base,
      note: "Live broker not implemented. Wire up lib/brokers/live.ts before trading real money.",
    };
  }
}
