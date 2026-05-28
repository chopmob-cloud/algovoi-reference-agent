/**
 * Unit tests for the ReferenceAgent end-to-end pipeline (TypeScript port).
 */

import { describe, expect, it } from "vitest";

import {
  emitAndVerify,
  getStubTransaction,
  ReferenceAgent,
} from "../src/index.js";

describe("baseRpc", () => {
  it("stub transaction is deterministic", () => {
    const a = getStubTransaction();
    const b = getStubTransaction();
    expect(a).toEqual(b);
    expect(a.chain_id).toBe(8453);
    expect(a.tx_hash.startsWith("0x")).toBe(true);
  });
});

describe("ReferenceAgent", () => {
  it("emit produces deterministic output across calls", () => {
    const agent = new ReferenceAgent();
    const first = agent.emit({ jurisdiction_flags: ["GB", "EU"] });
    const second = agent.emit({ jurisdiction_flags: ["GB", "EU"] });
    expect(first.receipt_dict).toEqual(second.receipt_dict);
    expect(first.receipt_hash).toBe(second.receipt_hash);
    expect(first.action_ref).toBe(second.action_ref);
  });

  it("canon_version pin is v1", () => {
    const { emit } = emitAndVerify();
    expect(emit.receipt_dict.canon_version).toBe("jcs-rfc8785-v1");
  });

  it("default settlement_result is SETTLED", () => {
    const { emit } = emitAndVerify();
    expect(emit.receipt_dict.settlement_result).toBe("SETTLED");
  });

  it("action_ref is 64 lowercase hex characters", () => {
    const { emit } = emitAndVerify();
    expect(emit.action_ref).toMatch(/^[0-9a-f]{64}$/);
  });

  it("jurisdiction array ordering is load-bearing", () => {
    const a = emitAndVerify({ jurisdiction_flags: ["GB", "EU"] }).emit;
    const b = emitAndVerify({ jurisdiction_flags: ["EU", "GB"] }).emit;
    expect(a.receipt_hash).not.toBe(b.receipt_hash);
  });

  it("self-verifies cleanly", () => {
    const { verify } = emitAndVerify({ jurisdiction_flags: ["GB", "EU"] });
    expect(verify.canonical_bytes_match).toBe(true);
    expect(verify.receipt_hash_match).toBe(true);
    expect(verify.overall_pass).toBe(true);
  });

  it("cross-language parity: matches the Python reference hash for GB,EU stub", () => {
    const { emit } = emitAndVerify({ jurisdiction_flags: ["GB", "EU"] });
    expect(emit.receipt_hash).toBe(
      "6c76ed1b7dbe9373721e1fc92d9f67f9a4500c0fd0937ce4720d24ccc9eda2a5",
    );
    expect(emit.action_ref).toBe(
      "3704c9221b75ef0f931094f2a63edba9dd6150c2c783d8505ec04a6275490930",
    );
  });
});
