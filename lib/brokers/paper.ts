import type { Order } from "../types";
import { Broker, OrderRequest, newOrderId } from "./types";

/**
 * Simulated broker. Fills every order instantly at the quoted price and never
 * touches real money. This is the default broker and the safe place to develop
 * and test strategies.
 */
export class PaperBroker implements Broker {
  readonly name = "paper";
  readonly live = false;

  async placeOrder(req: OrderRequest): Promise<Order> {
    const quantity = req.price > 0 ? req.amountUsd / req.price : 0;
    return {
      id: newOrderId(),
      symbol: req.symbol,
      side: req.side,
      amountUsd: req.amountUsd,
      price: req.price,
      quantity: Math.round(quantity * 1e6) / 1e6,
      status: "filled",
      broker: this.name,
      createdAt: new Date().toISOString(),
      note: "Simulated fill (paper trading).",
    };
  }
}
