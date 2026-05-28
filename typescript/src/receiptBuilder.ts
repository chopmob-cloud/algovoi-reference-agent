/**
 * Receipt builder.
 *
 * Composes the AlgoVoi-authored substrate primitives into a single
 * buildSettlementReceipt function that takes a BaseTransaction and
 * returns a settlement-attestation receipt under the AlgoVoi
 * canonicalisation discipline.
 */

import { buildSettlementAttestation } from "@algovoi/settlement-attestation";

import type { BaseTransaction } from "./baseRpc.js";

export interface BuildReceiptOptions {
  readonly settlement_provider_did?: string;
  readonly settlement_result?: string;
  readonly jurisdiction_flags?: readonly string[];
  readonly asset_id?: string;
}

/**
 * Build a settlement-attestation-v1 receipt from a Base transaction.
 *
 * Mirrors algovoi_reference_agent.receipt_builder.build_settlement_receipt
 * in the Python port. Produces byte-identical output for the same input.
 */
export function buildSettlementReceipt(
  txn: BaseTransaction,
  opts: BuildReceiptOptions = {},
): ReturnType<typeof buildSettlementAttestation> {
  const {
    settlement_provider_did = "did:web:api.algovoi.co.uk",
    settlement_result = "SETTLED",
    jurisdiction_flags = [],
    asset_id = "base:8453/erc20:0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
  } = opts;

  return buildSettlementAttestation({
    settled_payment_ref: txn.tx_hash,
    settlement_result,
    settlement_timestamp_ms: txn.timestamp_ms,
    settlement_provider_did,
    settlement_amount: {
      asset_id,
      amount_minor: txn.amount_wei,
    },
    settlement_chain: `base:${txn.chain_id}`,
    jurisdiction_flags: [...jurisdiction_flags],
  });
}
