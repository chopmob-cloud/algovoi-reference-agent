/**
 * ReferenceAgent: the end-to-end agent class.
 *
 * Wraps the baseRpc adapter, the receiptBuilder, and the substrate-side
 * canonicalisation into a single object an integrator can instantiate
 * and call.
 *
 * Produces byte-identical output to the Python reference agent for the
 * same inputs.
 */

import { actionRef, canonicalizeBytes, sha256Jcs } from "@algovoi/substrate";

import {
  type BaseTransaction,
  getStubTransaction,
} from "./baseRpc.js";
import {
  buildSettlementReceipt,
  type BuildReceiptOptions,
} from "./receiptBuilder.js";

export interface EmitResult {
  readonly transaction: BaseTransaction;
  readonly receipt_dict: ReturnType<typeof buildSettlementReceipt>;
  readonly canonical_bytes: Uint8Array;
  readonly receipt_hash: string;
  readonly action_ref: string;
}

export interface ReferenceAgentOptions {
  readonly agent_id?: string;
  readonly settlement_provider_did?: string;
}

export interface EmitOptions extends BuildReceiptOptions {}

export class ReferenceAgent {
  readonly agent_id: string;
  readonly settlement_provider_did: string;

  constructor(opts: ReferenceAgentOptions = {}) {
    this.agent_id = opts.agent_id ?? "did:web:reference-agent.algovoi.co.uk";
    this.settlement_provider_did =
      opts.settlement_provider_did ?? "did:web:api.algovoi.co.uk";
  }

  /** Return a Base transaction (deterministic stub mode only in this port). */
  fetchTransaction(): BaseTransaction {
    return getStubTransaction();
  }

  /** Run one emit cycle: fetch txn, build receipt, derive action_ref. */
  emit(opts: EmitOptions = {}): EmitResult {
    const txn = this.fetchTransaction();

    const receipt = buildSettlementReceipt(txn, {
      settlement_provider_did:
        opts.settlement_provider_did ?? this.settlement_provider_did,
      settlement_result: opts.settlement_result ?? "SETTLED",
      jurisdiction_flags: opts.jurisdiction_flags ?? [],
      asset_id: opts.asset_id,
    });

    const canonical_bytes = canonicalizeBytes(receipt);
    const receipt_hash = sha256Jcs(receipt);

    const a_ref = actionRef({
      agent_id: this.agent_id,
      action_type: "payment.settled",
      scope: "algovoi:settlement",
      timestamp_ms: txn.timestamp_ms,
    });

    return {
      transaction: txn,
      receipt_dict: receipt,
      canonical_bytes,
      receipt_hash,
      action_ref: a_ref,
    };
  }
}
