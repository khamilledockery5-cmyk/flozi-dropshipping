import type { Order, Side } from "../types";

export interface OrderRequest {
  symbol: string;
  side: Side;
  amountUsd: number;
  price: number;
}

export interface Broker {
  readonly name: string;
  /** Whether this broker places real-money orders. */
  readonly live: boolean;
  placeOrder(req: OrderRequest): Promise<Order>;
}

export function newOrderId(): string {
  return `ord_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}
