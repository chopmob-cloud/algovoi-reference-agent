"""
Conformance test against chopmob-cloud/algovoi-jcs-conformance-vectors.

For each receipt vector in the settlement_attestation_v1 vector set,
this test reconstructs the receipt from the vector's inputs using the
public algovoi-settlement-attestation primitive, canonicalises with
algovoi-substrate, and asserts the canonical bytes and SHA-256 hash
match the corpus-published expected values.

The test passes only if every vector produces byte-identical output to
the AlgoVoi conformance corpus. This is the byte-determinism guarantee
the substrate-author position rests on.

Conformance corpus location is searched in this order:
1. ALGOVOI_CONFORMANCE_DIR environment variable (if set)
2. ../algovoi-jcs-conformance-vectors (sibling repo)
3. ../../algovoi-jcs-conformance-vectors
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path

import pytest

from algovoi_substrate import canonicalize_bytes, sha256_jcs
from algovoi_settlement_attestation import build_settlement_attestation


def _find_corpus() -> Path | None:
    env_path = os.environ.get("ALGOVOI_CONFORMANCE_DIR")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p

    here = Path(__file__).resolve().parent
    candidates = [
        here.parent.parent / "algovoi-jcs-conformance-vectors",
        here.parent.parent.parent / "algovoi-jcs-conformance-vectors",
        Path("C:/algo/algovoi-jcs-conformance-vectors"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


CORPUS = _find_corpus()
VECTOR_FILE = (
    CORPUS / "vectors" / "settlement_attestation_v1" / "settlement_attestation_v1.json"
    if CORPUS
    else None
)

pytestmark = pytest.mark.skipif(
    VECTOR_FILE is None or not VECTOR_FILE.exists(),
    reason=(
        "Conformance corpus not found. Clone "
        "https://github.com/chopmob-cloud/algovoi-jcs-conformance-vectors and "
        "set ALGOVOI_CONFORMANCE_DIR or place it as a sibling of this repo."
    ),
)


def _load_vectors() -> dict:
    assert VECTOR_FILE is not None
    with open(VECTOR_FILE, encoding="utf-8") as f:
        return json.load(f)


def _build_receipt_from_vector(vector: dict, fixed_fields: dict) -> dict:
    """Construct a receipt by overlaying vector fields on the fixed fields."""
    fields = dict(fixed_fields)
    fields.update(vector.get("receipt", {}))
    # The build function takes keyword arguments.
    return build_settlement_attestation(
        settled_payment_ref=fields["settled_payment_ref"],
        settlement_result=fields["settlement_result"],
        settlement_timestamp_ms=fields["settlement_timestamp_ms"],
        settlement_provider_did=fields["settlement_provider_did"],
        settlement_amount=fields["settlement_amount"],
        settlement_chain=fields["settlement_chain"],
        jurisdiction_flags=fields["jurisdiction_flags"],
        canon_version=fields.get("canon_version", "jcs-rfc8785-v1"),
    )


def test_corpus_metadata_anchors_to_algovoi() -> None:
    data = _load_vectors()
    anchored = data.get("anchored_to", {})
    assert "draft-hopley-x402-settlement-attestation" in anchored.get("ietf_id", "")
    assert "AlgoVoi-authored" in anchored.get("ietf_id", "")
    assert "urn:x402:canonicalisation:jcs-rfc8785-v1" in anchored.get(
        "canonicalisation_discipline", ""
    )


@pytest.mark.parametrize("vector_index", range(8))
def test_each_vector_byte_identical(vector_index: int) -> None:
    """Each receipt or chain-row vector must produce byte-identical output."""
    data = _load_vectors()
    vectors = data.get("vectors", [])
    if vector_index >= len(vectors):
        pytest.skip(f"Vector {vector_index} not in corpus (corpus has {len(vectors)})")

    vector = vectors[vector_index]
    fixed_fields = data.get("fixed_receipt_fields", {})

    # Receipt vectors carry a "receipt" payload; chain-row vectors carry "row".
    if "receipt" in vector:
        receipt = _build_receipt_from_vector(vector, fixed_fields)
        payload = receipt
    elif "row" in vector:
        payload = vector["row"]
    else:
        pytest.skip(f"Vector {vector_index} has neither 'receipt' nor 'row'")

    actual_bytes = canonicalize_bytes(payload)
    actual_hash = sha256_jcs(payload)

    expected_b64 = vector.get("expected_jcs_bytes_b64") or vector.get(
        "expected_row_jcs_bytes_b64"
    )
    expected_hash = vector.get("expected_content_hash") or vector.get(
        "expected_row_content_hash"
    )

    if expected_b64:
        expected_bytes = base64.b64decode(expected_b64)
        assert actual_bytes == expected_bytes, (
            f"Vector {vector_index}: JCS bytes do not match corpus"
        )
    if expected_hash:
        assert actual_hash == expected_hash, (
            f"Vector {vector_index}: SHA-256 does not match corpus "
            f"(got {actual_hash}, expected {expected_hash})"
        )
