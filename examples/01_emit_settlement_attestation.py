"""
Example 01: minimal emit.

Runs the reference agent in deterministic stub mode and prints the
emitted settlement-attestation-v1 receipt as JSON.

Run with:
    python examples/01_emit_settlement_attestation.py
"""

from __future__ import annotations

import json

from algovoi_reference_agent import ReferenceAgent


def main() -> int:
    agent = ReferenceAgent()
    result = agent.emit(jurisdiction_flags=["GB", "EU"])

    print("=== Source transaction ===")
    print(f"tx_hash: {result.transaction.tx_hash}")
    print(f"chain_id: {result.transaction.chain_id}")
    print(f"timestamp_ms: {result.transaction.timestamp_ms}")
    print()

    print("=== Emitted receipt (JSON) ===")
    print(json.dumps(result.receipt_dict, indent=2, sort_keys=True))
    print()

    print("=== Derived artefacts ===")
    print(f"action_ref:   {result.action_ref}")
    print(f"receipt_hash: {result.receipt_hash}")
    print(f"canonical_bytes length: {len(result.canonical_bytes)} bytes")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
