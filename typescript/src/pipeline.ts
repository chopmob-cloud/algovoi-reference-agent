/**
 * Pipeline: emit + self-verify in one call.
 *
 * Composes ReferenceAgent.emit() with a local verification step that
 * re-canonicalises the receipt dict and confirms the bytes round-trip.
 */

import { canonicalizeBytes, sha256Jcs } from "@algovoi/substrate";

import {
  type EmitOptions,
  type EmitResult,
  ReferenceAgent,
  type ReferenceAgentOptions,
} from "./agent.js";

export interface VerifyResult {
  readonly canonical_bytes_match: boolean;
  readonly receipt_hash_match: boolean;
  readonly overall_pass: boolean;
}

export interface EmitAndVerifyResult {
  readonly emit: EmitResult;
  readonly verify: VerifyResult;
}

export interface EmitAndVerifyOptions
  extends ReferenceAgentOptions,
    EmitOptions {}

/**
 * Run one emit cycle and immediately self-verify the canonical bytes.
 *
 * Verification re-derives the canonical bytes and the SHA-256 hash from
 * the receipt dict and confirms they match the emit-time values. Any
 * mismatch indicates non-determinism in the emit path.
 */
export function emitAndVerify(
  opts: EmitAndVerifyOptions = {},
): EmitAndVerifyResult {
  const agent = new ReferenceAgent({
    agent_id: opts.agent_id,
    settlement_provider_did: opts.settlement_provider_did,
  });
  const emit = agent.emit({
    settlement_result: opts.settlement_result,
    jurisdiction_flags: opts.jurisdiction_flags,
    asset_id: opts.asset_id,
  });

  const canonical_bytes_again = canonicalizeBytes(emit.receipt_dict);
  const receipt_hash_again = sha256Jcs(emit.receipt_dict);

  const canonical_match =
    canonical_bytes_again.length === emit.canonical_bytes.length &&
    canonical_bytes_again.every((b, i) => b === emit.canonical_bytes[i]);
  const hash_match = receipt_hash_again === emit.receipt_hash;

  const verify: VerifyResult = {
    canonical_bytes_match: canonical_match,
    receipt_hash_match: hash_match,
    overall_pass: canonical_match && hash_match,
  };

  return { emit, verify };
}
