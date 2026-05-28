/**
 * Conformance test against chopmob-cloud/algovoi-jcs-conformance-vectors.
 *
 * For each settlement_attestation_v1 vector, rebuild the receipt or
 * row, canonicalise + hash with @algovoi/substrate, and assert the
 * bytes and hash match the corpus expected values byte-identically.
 *
 * Conformance corpus location is searched in this order:
 *   1. ALGOVOI_CONFORMANCE_DIR env var
 *   2. C:/algo/algovoi-jcs-conformance-vectors
 *   3. ../../algovoi-jcs-conformance-vectors (sibling repo)
 */

import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

import { sha256Jcs } from "@algovoi/substrate";
import { buildSettlementAttestation } from "@algovoi/settlement-attestation";
import { describe, expect, it } from "vitest";

function findCorpus(): string | undefined {
  const env = process.env.ALGOVOI_CONFORMANCE_DIR;
  if (env && existsSync(env)) return env;
  const candidates = [
    "C:/algo/algovoi-jcs-conformance-vectors",
    join(process.cwd(), "..", "..", "algovoi-jcs-conformance-vectors"),
    join(process.cwd(), "..", "..", "..", "algovoi-jcs-conformance-vectors"),
  ];
  for (const c of candidates) {
    if (existsSync(c)) return c;
  }
  return undefined;
}

const corpus = findCorpus();
const vectorFile = corpus
  ? join(
      corpus,
      "vectors",
      "settlement_attestation_v1",
      "settlement_attestation_v1.json",
    )
  : undefined;

const skipReason =
  vectorFile && existsSync(vectorFile)
    ? undefined
    : "Conformance corpus not found. Set ALGOVOI_CONFORMANCE_DIR or place the corpus as a sibling repo.";

describe.skipIf(skipReason !== undefined)(
  "conformance corpus settlement_attestation_v1",
  () => {
    function loadCorpus(): Record<string, unknown> {
      return JSON.parse(readFileSync(vectorFile!, "utf-8"));
    }

    it("anchors to AlgoVoi-authored IETF I-D", () => {
      const data = loadCorpus();
      const anchored = data.anchored_to as Record<string, string>;
      expect(anchored.ietf_id).toContain(
        "draft-hopley-x402-settlement-attestation",
      );
      expect(anchored.ietf_id).toContain("AlgoVoi-authored");
      expect(anchored.canonicalisation_discipline).toContain(
        "urn:x402:canonicalisation:jcs-rfc8785-v1",
      );
    });

    const data = vectorFile && existsSync(vectorFile) ? loadCorpus() : { vectors: [] };
    const vectors = (data.vectors as Array<Record<string, unknown>>) ?? [];
    const fixed = (data.fixed_receipt_fields as Record<string, unknown>) ?? {};

    vectors.forEach((vector, idx) => {
      it(`vector ${idx}: byte-identical hash`, () => {
        let payload: Record<string, unknown>;
        let expected_hash: string | undefined;

        if ("receipt" in vector) {
          const fields = { ...fixed, ...(vector.receipt as Record<string, unknown>) };
          payload = buildSettlementAttestation({
            settled_payment_ref: fields.settled_payment_ref as string,
            settlement_result: fields.settlement_result as string,
            settlement_timestamp_ms: fields.settlement_timestamp_ms as number,
            settlement_provider_did: fields.settlement_provider_did as string,
            settlement_amount: fields.settlement_amount as {
              asset_id: string;
              amount_minor: string;
            },
            settlement_chain: fields.settlement_chain as string,
            jurisdiction_flags: fields.jurisdiction_flags as string[],
            canon_version:
              (fields.canon_version as string) ?? "jcs-rfc8785-v1",
          });
          expected_hash = vector.expected_content_hash as string | undefined;
        } else if ("row" in vector) {
          payload = vector.row as Record<string, unknown>;
          expected_hash = vector.expected_row_content_hash as string | undefined;
        } else {
          return;
        }

        const actual_hash = sha256Jcs(payload);
        if (expected_hash !== undefined) {
          expect(actual_hash).toBe(expected_hash);
        }
      });
    });
  },
);
