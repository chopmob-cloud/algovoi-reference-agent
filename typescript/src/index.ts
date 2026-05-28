/**
 * @algovoi/reference-agent
 *
 * Apache 2.0 reference implementation of an agent that emits an AlgoVoi
 * settlement-attestation-v1 receipt for a Base chain transaction.
 *
 * TypeScript port; byte-for-byte parity with the Python
 * algovoi-reference-agent.
 *
 * References:
 * - IETF I-D draft-hopley-x402-settlement-attestation
 * - IETF I-D draft-hopley-x402-canonicalisation-jcs-v1
 * - chopmob-cloud/algovoi-jcs-conformance-vectors
 *
 * Author: AlgoVoi (chopmob-cloud)
 * License: Apache-2.0
 */

export { type BaseTransaction, getStubTransaction } from "./baseRpc.js";
export {
  buildSettlementReceipt,
  type BuildReceiptOptions,
} from "./receiptBuilder.js";
export {
  type EmitOptions,
  type EmitResult,
  ReferenceAgent,
  type ReferenceAgentOptions,
} from "./agent.js";
export {
  emitAndVerify,
  type EmitAndVerifyOptions,
  type EmitAndVerifyResult,
  type VerifyResult,
} from "./pipeline.js";

export const VERSION = "0.1.0";
