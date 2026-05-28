"""
Pipeline: emit + self-verify in one call.

Composes ReferenceAgent.emit() with a local verification step that
re-canonicalises the receipt dict and confirms the bytes round-trip.

This is the "end-to-end" entry point most users want: one function,
deterministic input, byte-identical output, self-verified.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from algovoi_substrate import canonicalize_bytes, sha256_jcs

from algovoi_reference_agent.agent import EmitResult, ReferenceAgent


@dataclass
class VerifyResult:
    """Result of self-verification of an emit cycle."""

    canonical_bytes_match: bool
    receipt_hash_match: bool
    overall_pass: bool


def emit_and_verify(
    *,
    agent_id: str = "did:web:reference-agent.algovoi.co.uk",
    settlement_provider_did: str = "did:web:api.algovoi.co.uk",
    live_rpc_url: Optional[str] = None,
    tx_hash: Optional[str] = None,
    settlement_result: str = "SETTLED",
    jurisdiction_flags: Optional[list[str]] = None,
) -> tuple[EmitResult, VerifyResult]:
    """Run one emit cycle and immediately self-verify the canonical bytes.

    Verification re-derives the canonical bytes and the SHA-256 hash from
    the receipt dict, and confirms they match the emit-time values. Any
    mismatch indicates non-determinism in the emit path and fails the
    verification.

    Returns
    -------
    tuple[EmitResult, VerifyResult]
        The original emit artefacts and the verification outcome.
    """
    agent = ReferenceAgent(
        agent_id=agent_id,
        settlement_provider_did=settlement_provider_did,
        live_rpc_url=live_rpc_url,
    )
    emit = agent.emit(
        tx_hash=tx_hash,
        settlement_result=settlement_result,
        jurisdiction_flags=jurisdiction_flags,
    )

    # Recompute canonical bytes and hash from the receipt dict.
    canonical_bytes_again = canonicalize_bytes(emit.receipt_dict)
    receipt_hash_again = sha256_jcs(emit.receipt_dict)

    canonical_match = canonical_bytes_again == emit.canonical_bytes
    hash_match = receipt_hash_again == emit.receipt_hash

    verify = VerifyResult(
        canonical_bytes_match=canonical_match,
        receipt_hash_match=hash_match,
        overall_pass=canonical_match and hash_match,
    )

    return emit, verify
