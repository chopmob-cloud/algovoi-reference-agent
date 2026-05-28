"""
Receipt builder.

Composes the AlgoVoi-authored substrate primitives into a single
`build_settlement_receipt` function that takes a BaseTransaction and
returns a SettlementAttestation receipt under the AlgoVoi
canonicalisation discipline.
"""

from __future__ import annotations

from typing import Any

from algovoi_settlement_attestation import (
    SettlementAttestation,
    build_settlement_attestation,
)

from algovoi_reference_agent.base_rpc import BaseTransaction


def build_settlement_receipt(
    txn: BaseTransaction,
    *,
    settlement_provider_did: str = "did:web:api.algovoi.co.uk",
    settlement_result: str = "SETTLED",
    jurisdiction_flags: list[str] | None = None,
    asset_id: str = "base:8453/erc20:0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
) -> SettlementAttestation:
    """Build a settlement-attestation-v1 receipt from a Base transaction.

    Parameters
    ----------
    txn:
        The Base chain transaction the receipt attests to.
    settlement_provider_did:
        The DID of the party emitting the attestation. Defaults to the
        AlgoVoi production DID for the reference agent demonstration;
        downstream forks should set this to their own DID.
    settlement_result:
        Categorical settlement result. Must be a member of
        algovoi_settlement_attestation.SETTLEMENT_RESULTS.
    jurisdiction_flags:
        ISO 3166-1 alpha-2 country codes plus regulatory tags (e.g.
        ["GB", "EU"]). Defaults to an empty list.
    asset_id:
        The CAIP-19 style asset identifier (chain prefix + contract).
        Defaults to USDC on Base mainnet.

    Returns
    -------
    SettlementAttestation
        The receipt object, ready to be JCS-canonicalised and signed by
        any downstream emitter.
    """
    jurisdiction_flags = jurisdiction_flags or []

    amount: dict[str, object] = {
        "asset_id": asset_id,
        "amount_minor": str(txn.amount_wei),
    }

    receipt = build_settlement_attestation(
        settled_payment_ref=txn.tx_hash,
        settlement_result=settlement_result,
        settlement_timestamp_ms=txn.timestamp_ms,
        settlement_provider_did=settlement_provider_did,
        settlement_amount=amount,
        settlement_chain=f"base:{txn.chain_id}",
        jurisdiction_flags=jurisdiction_flags,
    )
    return receipt


def receipt_to_dict(receipt: SettlementAttestation) -> dict[str, Any]:
    """Convert a SettlementAttestation receipt into a JSON-ready dict.

    The dict is the canonical pre-canonicalisation representation. Pass
    it through `algovoi_substrate.canonicalize_bytes` to get the bytes
    that downstream verifiers will hash.
    """
    if isinstance(receipt, dict):
        return dict(receipt)
    if hasattr(receipt, "to_dict"):
        return receipt.to_dict()  # type: ignore[no-any-return]
    if hasattr(receipt, "model_dump"):
        return receipt.model_dump()  # type: ignore[no-any-return]
    if hasattr(receipt, "__dict__"):
        return dict(receipt.__dict__)
    raise TypeError(
        f"Cannot serialise receipt of type {type(receipt).__name__}; "
        "expected a SettlementAttestation with to_dict/model_dump/__dict__."
    )
