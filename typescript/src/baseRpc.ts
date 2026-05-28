/**
 * Base chain RPC adapter for the reference agent.
 *
 * Deterministic stub mode (default): returns a fixed fixture transaction
 * so the agent runs end-to-end without any network dependency. The bytes
 * match the Python reference agent byte-for-byte.
 *
 * Live mode is not implemented in this TypeScript port; users wanting
 * live Base RPC should fork and integrate ethers / viem / web3.js
 * directly. Apache 2.0 permits any such fork.
 */

export interface BaseTransaction {
  readonly tx_hash: string;
  readonly block_number: number;
  readonly timestamp_ms: number;
  readonly from_address: string;
  readonly to_address: string;
  readonly amount_wei: string; // string to preserve precision on large values
  readonly chain_id: number;
}

const DETERMINISTIC_FIXTURE: BaseTransaction = {
  tx_hash: "0x" + "ab".repeat(32),
  block_number: 22_500_000,
  timestamp_ms: 1_716_000_000_000,
  from_address: "0x" + "1".repeat(40),
  to_address: "0x" + "2".repeat(40),
  amount_wei: "1000000000000000", // 0.001 ETH
  chain_id: 8453, // Base mainnet
};

/**
 * Return the deterministic fixture transaction.
 *
 * Produces byte-identical output to the Python reference agent's
 * get_stub_transaction(). Used in the default emit path so the example
 * runs identically on any machine without network access.
 */
export function getStubTransaction(): BaseTransaction {
  return DETERMINISTIC_FIXTURE;
}
