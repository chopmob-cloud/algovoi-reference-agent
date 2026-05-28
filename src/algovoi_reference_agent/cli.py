"""
Command-line interface.

Provides `algovoi-agent emit` and `algovoi-agent verify` subcommands
when the package is installed.
"""

from __future__ import annotations

import argparse
import json
import sys

from algovoi_reference_agent.pipeline import emit_and_verify


def _cmd_emit(args: argparse.Namespace) -> int:
    emit, verify = emit_and_verify(
        agent_id=args.agent_id,
        settlement_provider_did=args.provider_did,
        live_rpc_url=args.rpc_url,
        tx_hash=args.tx_hash,
        settlement_result=args.result,
        jurisdiction_flags=args.jurisdiction.split(",") if args.jurisdiction else None,
    )

    output = {
        "receipt": emit.receipt_dict,
        "action_ref": emit.action_ref,
        "receipt_hash": emit.receipt_hash,
        "verification": {
            "canonical_bytes_match": verify.canonical_bytes_match,
            "receipt_hash_match": verify.receipt_hash_match,
            "overall_pass": verify.overall_pass,
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if verify.overall_pass else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="algovoi-agent",
        description=(
            "Reference agent that emits AlgoVoi settlement-attestation-v1 "
            "receipts for Base chain transactions. Apache 2.0."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    emit = sub.add_parser("emit", help="Emit and self-verify a receipt")
    emit.add_argument(
        "--chain",
        default="base",
        help="Target chain (currently only 'base' is implemented)",
    )
    emit.add_argument(
        "--amount",
        default="0.001",
        help="Settlement amount (descriptive only in stub mode)",
    )
    emit.add_argument(
        "--agent-id",
        default="did:web:reference-agent.algovoi.co.uk",
        help="Agent identifier for action_ref derivation",
    )
    emit.add_argument(
        "--provider-did",
        default="did:web:api.algovoi.co.uk",
        help="Settlement provider DID for the receipt",
    )
    emit.add_argument(
        "--rpc-url",
        default=None,
        help="Optional Base RPC URL for live transaction lookup",
    )
    emit.add_argument(
        "--tx-hash",
        default=None,
        help="Optional Base tx hash for live mode",
    )
    emit.add_argument(
        "--result",
        default="SETTLED",
        help="Settlement result. One of: SETTLED, PENDING_FINALITY, REVERSED.",
    )
    emit.add_argument(
        "--jurisdiction",
        default=None,
        help="Comma-separated jurisdiction flags (e.g. 'GB,EU')",
    )
    emit.set_defaults(func=_cmd_emit)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
