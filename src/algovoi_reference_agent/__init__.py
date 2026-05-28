"""
algovoi-reference-agent
=======================

Apache 2.0 reference implementation of an agent that emits an AlgoVoi
settlement-attestation-v1 receipt for a Base chain transaction.

End-to-end worked example demonstrating the AlgoVoi-authored substrate
discipline. Composes the public Apache 2.0 packages algovoi-substrate
and algovoi-settlement-attestation. No internal AlgoVoi infrastructure
trust required.

References
----------
- IETF I-D draft-hopley-x402-settlement-attestation
- IETF I-D draft-hopley-x402-canonicalisation-jcs-v1
- chopmob-cloud/algovoi-jcs-conformance-vectors

Author: AlgoVoi (chopmob-cloud)
License: Apache-2.0
"""

__version__ = "0.1.0"
__author__ = "AlgoVoi (chopmob-cloud)"
__license__ = "Apache-2.0"

from algovoi_reference_agent.agent import ReferenceAgent
from algovoi_reference_agent.receipt_builder import build_settlement_receipt
from algovoi_reference_agent.pipeline import emit_and_verify

__all__ = [
    "ReferenceAgent",
    "build_settlement_receipt",
    "emit_and_verify",
    "__version__",
]
