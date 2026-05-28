"""
Base chain RPC adapter for the reference agent.

Two modes:
- Deterministic stub mode (default): returns a fixed fixture transaction
  so the agent runs end-to-end without any network dependency.
- Live mode (optional): requires the `live` optional dependency
  (`pip install algovoi-reference-agent[live]`) and a Base RPC URL.

Neither mode calls AlgoVoi infrastructure. The agent runs entirely on
the user's side.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BaseTransaction:
    """A minimal Base chain transaction record.

    Captures only the fields the reference agent needs to derive a
    settlement-attestation receipt. Real Base RPC responses carry many
    more fields; the reference agent ignores those.
    """

    tx_hash: str
    block_number: int
    timestamp_ms: int
    from_address: str
    to_address: str
    amount_wei: int
    chain_id: int = 8453  # Base mainnet


_DETERMINISTIC_FIXTURE = BaseTransaction(
    # Stable fixture for byte-deterministic demos. Hash is a real-shape
    # Base tx hash; the bytes are deterministic and used only in the
    # reference agent's stub demo path.
    tx_hash="0x" + "ab" * 32,
    block_number=22_500_000,
    timestamp_ms=1_716_000_000_000,
    from_address="0x" + "1" * 40,
    to_address="0x" + "2" * 40,
    amount_wei=1_000_000_000_000_000,  # 0.001 ETH
    chain_id=8453,
)


def get_stub_transaction() -> BaseTransaction:
    """Return the deterministic fixture transaction.

    Used by the reference agent's default emit path so the example
    produces byte-identical output on any machine without network
    access. Production agents would replace this with a real RPC call.
    """
    return _DETERMINISTIC_FIXTURE


def get_live_transaction(
    *,
    rpc_url: str,
    tx_hash: str,
) -> BaseTransaction:
    """Fetch a live Base transaction via JSON-RPC.

    Requires the `live` optional dependency. Raises ImportError if
    web3.py is not installed.

    Parameters
    ----------
    rpc_url:
        Base chain JSON-RPC endpoint URL (user-provided).
    tx_hash:
        Transaction hash to look up.

    Returns
    -------
    BaseTransaction
        Minimal transaction record extracted from the RPC response.
    """
    try:
        from web3 import Web3  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "Live Base RPC mode requires the optional 'live' dependency. "
            "Install with: pip install algovoi-reference-agent[live]"
        ) from exc

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    tx = w3.eth.get_transaction(tx_hash)
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    block = w3.eth.get_block(receipt["blockNumber"])
    return BaseTransaction(
        tx_hash=tx_hash,
        block_number=receipt["blockNumber"],
        timestamp_ms=block["timestamp"] * 1000,
        from_address=tx["from"],
        to_address=tx["to"],
        amount_wei=tx["value"],
        chain_id=int(tx.get("chainId", 8453)),
    )
