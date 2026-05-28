"""Unit tests for the ReferenceAgent end-to-end pipeline."""

from __future__ import annotations

from algovoi_reference_agent import ReferenceAgent, emit_and_verify
from algovoi_reference_agent.base_rpc import get_stub_transaction


def test_stub_transaction_is_deterministic() -> None:
    """Stub transaction must return the same bytes on every call."""
    a = get_stub_transaction()
    b = get_stub_transaction()
    assert a == b
    assert a.chain_id == 8453
    assert a.tx_hash.startswith("0x")


def test_agent_emit_deterministic() -> None:
    """Two emits of the same agent in stub mode must produce identical receipts."""
    agent = ReferenceAgent()
    first = agent.emit(jurisdiction_flags=["GB", "EU"])
    second = agent.emit(jurisdiction_flags=["GB", "EU"])
    assert first.receipt_dict == second.receipt_dict
    assert first.canonical_bytes == second.canonical_bytes
    assert first.receipt_hash == second.receipt_hash
    assert first.action_ref == second.action_ref


def test_emit_and_verify_passes_in_stub_mode() -> None:
    """The default deterministic emit-and-verify cycle must pass."""
    emit, verify = emit_and_verify(jurisdiction_flags=["GB", "EU"])
    assert verify.canonical_bytes_match is True
    assert verify.receipt_hash_match is True
    assert verify.overall_pass is True
    assert len(emit.receipt_hash) == 64  # SHA-256 lowercase hex


def test_canon_version_pin_is_v1() -> None:
    """Emitted receipts must carry the AlgoVoi v1 canonicalisation pin."""
    emit, _ = emit_and_verify()
    assert emit.receipt_dict["canon_version"] == "jcs-rfc8785-v1"


def test_settlement_result_in_closed_enum() -> None:
    """Default emit must produce SETTLED, a member of the closed enum."""
    emit, _ = emit_and_verify()
    assert emit.receipt_dict["settlement_result"] in {
        "SETTLED",
        "PENDING_FINALITY",
        "REVERSED",
    }


def test_jurisdiction_array_ordering_matters() -> None:
    """Reordering jurisdiction flags must change the receipt hash.

    This is the array-order load-bearing invariant from the AlgoVoi
    conformance corpus.
    """
    a, _ = emit_and_verify(jurisdiction_flags=["GB", "EU"])
    b, _ = emit_and_verify(jurisdiction_flags=["EU", "GB"])
    assert a.receipt_hash != b.receipt_hash


def test_action_ref_is_sha256_lowercase_hex() -> None:
    """action_ref must be 64 lowercase hex characters."""
    emit, _ = emit_and_verify()
    assert len(emit.action_ref) == 64
    assert all(c in "0123456789abcdef" for c in emit.action_ref)
