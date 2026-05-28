"""
ReferenceAgent: the end-to-end agent class.

Wraps the base_rpc adapter, the receipt_builder, and the substrate-side
canonicalisation into a single object an integrator can instantiate and
call.

A production agent would extend this class (or use it as a reference
implementation pattern) to wire its own RPC source, its own emitter
DID, and its own downstream consumer. Nothing in this class is
AlgoVoi-internal; everything composes from public Apache 2.0 packages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from algovoi_substrate import action_ref, canonicalize_bytes, sha256_jcs

from algovoi_reference_agent.base_rpc import (
    BaseTransaction,
    get_live_transaction,
    get_stub_transaction,
)
from algovoi_reference_agent.receipt_builder import (
    build_settlement_receipt,
    receipt_to_dict,
)


@dataclass
class EmitResult:
    """Result of a single agent emit cycle."""

    transaction: BaseTransaction
    receipt_dict: dict
    canonical_bytes: bytes
    receipt_hash: str
    action_ref: str


class ReferenceAgent:
    """End-to-end agent that emits AlgoVoi settlement-attestation receipts.

    Parameters
    ----------
    agent_id:
        Stable identifier for this agent. Used in action_ref derivation.
        Production agents use a DID; the reference defaults to a stable
        demo DID for byte-deterministic output.
    settlement_provider_did:
        The DID under which this agent emits its receipts. Defaults to
        the AlgoVoi production DID for demonstration; integrators set
        this to their own DID.
    live_rpc_url:
        Optional Base RPC URL. If set, the agent fetches transactions
        live. If unset (default), the agent uses the deterministic
        stub transaction.
    """

    def __init__(
        self,
        *,
        agent_id: str = "did:web:reference-agent.algovoi.co.uk",
        settlement_provider_did: str = "did:web:api.algovoi.co.uk",
        live_rpc_url: Optional[str] = None,
    ) -> None:
        self.agent_id = agent_id
        self.settlement_provider_did = settlement_provider_did
        self.live_rpc_url = live_rpc_url

    # ------------------------------------------------------------------
    # Transaction fetch
    # ------------------------------------------------------------------

    def fetch_transaction(self, tx_hash: Optional[str] = None) -> BaseTransaction:
        """Return a Base transaction.

        If ``live_rpc_url`` is set on the agent and ``tx_hash`` is
        provided, fetches the live transaction. Otherwise returns the
        deterministic fixture.
        """
        if self.live_rpc_url and tx_hash:
            return get_live_transaction(
                rpc_url=self.live_rpc_url,
                tx_hash=tx_hash,
            )
        return get_stub_transaction()

    # ------------------------------------------------------------------
    # Emit
    # ------------------------------------------------------------------

    def emit(
        self,
        *,
        tx_hash: Optional[str] = None,
        settlement_result: str = "SETTLED",
        jurisdiction_flags: Optional[list[str]] = None,
    ) -> EmitResult:
        """Run one emit cycle: fetch txn, build receipt, derive action_ref.

        Parameters
        ----------
        tx_hash:
            If live mode is configured, the live transaction to fetch.
            Ignored in stub mode.
        settlement_result:
            Categorical settlement result for the receipt.
        jurisdiction_flags:
            ISO 3166 country codes plus regulatory tags.

        Returns
        -------
        EmitResult
            Full receipt artefacts: the source transaction, the receipt
            dict, the JCS canonical bytes, the SHA-256 receipt hash, and
            the AlgoVoi-discipline action_ref.
        """
        txn = self.fetch_transaction(tx_hash=tx_hash)

        receipt = build_settlement_receipt(
            txn,
            settlement_provider_did=self.settlement_provider_did,
            settlement_result=settlement_result,
            jurisdiction_flags=jurisdiction_flags or [],
        )
        receipt_dict = receipt_to_dict(receipt)
        canonical_bytes = canonicalize_bytes(receipt_dict)
        receipt_hash = sha256_jcs(receipt_dict)

        a_ref = action_ref(
            agent_id=self.agent_id,
            action_type="payment.settled",
            scope="algovoi:settlement",
            timestamp_ms=txn.timestamp_ms,
        )

        return EmitResult(
            transaction=txn,
            receipt_dict=receipt_dict,
            canonical_bytes=canonical_bytes,
            receipt_hash=receipt_hash,
            action_ref=a_ref,
        )
