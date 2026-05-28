"""
Example 03: full end-to-end pipeline in one call.

Uses the `emit_and_verify` orchestrator to run the entire pipeline:

1. Fetch a transaction (deterministic stub mode)
2. Build a settlement-attestation-v1 receipt under
   urn:x402:canonicalisation:jcs-rfc8785-v1
3. Derive the AlgoVoi-discipline action_ref
4. Self-verify the canonical bytes round-trip

Run with:
    python examples/03_end_to_end_pipeline.py
"""

from __future__ import annotations

import json

from algovoi_reference_agent import emit_and_verify


def main() -> int:
    emit, verify = emit_and_verify(jurisdiction_flags=["GB", "EU"])

    payload = {
        "receipt": emit.receipt_dict,
        "action_ref": emit.action_ref,
        "receipt_hash": emit.receipt_hash,
        "verification": {
            "canonical_bytes_match": verify.canonical_bytes_match,
            "receipt_hash_match": verify.receipt_hash_match,
            "overall_pass": verify.overall_pass,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))

    return 0 if verify.overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
