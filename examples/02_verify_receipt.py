"""
Example 02: verify a received receipt locally.

Demonstrates how a third-party consumer would verify a receipt they
received from an agent. The consumer takes the receipt dict, re-derives
the JCS canonical bytes and the SHA-256 hash, and confirms they match
what the emitter advertised.

This is the entire verification surface. No AlgoVoi infrastructure or
authority is needed; the receipt is byte-deterministic and locally
verifiable from public Apache 2.0 code.

Run with:
    python examples/02_verify_receipt.py
"""

from __future__ import annotations

import json

from algovoi_substrate import canonicalize_bytes, sha256_jcs

from algovoi_reference_agent import ReferenceAgent


def main() -> int:
    # Emit a receipt as a sender would.
    agent = ReferenceAgent()
    emit = agent.emit(jurisdiction_flags=["GB", "EU"])
    sender_receipt = emit.receipt_dict
    sender_advertised_hash = emit.receipt_hash

    # Simulate transport: serialise to JSON, deserialise on the receiver.
    transmitted = json.dumps(sender_receipt)
    received_receipt = json.loads(transmitted)

    # Receiver-side verification using only the public Apache 2.0
    # substrate primitives. No call to the emitter's infrastructure.
    received_canonical_bytes = canonicalize_bytes(received_receipt)
    received_hash = sha256_jcs(received_receipt)

    print("=== Receiver-side verification ===")
    print(f"Receipt canon_version: {received_receipt.get('canon_version')}")
    print(f"Receipt settlement_result: {received_receipt.get('settlement_result')}")
    print()
    print(f"Sender-advertised hash: {sender_advertised_hash}")
    print(f"Receiver-derived hash:  {received_hash}")
    print(f"Match: {sender_advertised_hash == received_hash}")
    print()
    print(f"Canonical bytes length: {len(received_canonical_bytes)} bytes")
    print(f"Bytes verify locally: {received_canonical_bytes == emit.canonical_bytes}")

    if sender_advertised_hash != received_hash:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
