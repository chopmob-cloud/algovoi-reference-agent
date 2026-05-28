# @algovoi/reference-agent

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![npm](https://img.shields.io/badge/npm-%40algovoi%2Freference--agent-blue)](https://www.npmjs.com/package/@algovoi/reference-agent)

Apache 2.0 reference implementation of an agent that emits an AlgoVoi
`settlement-attestation-v1` receipt for a Base chain transaction.
TypeScript port; byte-for-byte parity with the Python
[`algovoi-reference-agent`](https://pypi.org/project/algovoi-reference-agent/).

## What this is

A minimal open-source agent that:

1. Returns a deterministic stub Base chain transaction (no network)
2. Emits a `settlement-attestation-v1` receipt under
   `urn:x402:canonicalisation:jcs-rfc8785-v1`
3. Derives an `action_ref` per the AlgoVoi-authored discipline
4. Self-verifies the canonical bytes

The receipt format is normatively specified in IETF Internet-Draft
[`draft-hopley-x402-settlement-attestation`](https://datatracker.ietf.org/doc/draft-hopley-x402-settlement-attestation/).
The canonicalisation discipline is specified in
[`draft-hopley-x402-canonicalisation-jcs-v1`](https://datatracker.ietf.org/doc/draft-hopley-x402-canonicalisation-jcs-v1/).

## Install

```bash
npm install @algovoi/reference-agent
```

## CLI

```bash
npx algovoi-agent emit --jurisdiction GB,EU
```

Output: a JSON `settlement-attestation-v1` receipt to stdout, the
derived `action_ref`, and a local self-verification result.

## Programmatic use

```ts
import { emitAndVerify } from "@algovoi/reference-agent";

const { emit, verify } = emitAndVerify({
  jurisdiction_flags: ["GB", "EU"],
});

console.log(emit.receipt_hash);   // 6c76ed1b7d... (same as Python)
console.log(emit.action_ref);     // 3704c9221b... (same as Python)
console.log(verify.overall_pass); // true
```

## Cross-language parity

The TypeScript port produces byte-identical output to the Python port
for the same inputs. Run the same operation on both, get the same
`receipt_hash` and `action_ref`.

## Composed packages

| Package | Purpose |
|---|---|
| [`@algovoi/substrate`](https://www.npmjs.com/package/@algovoi/substrate) | JCS canonicalisation, action_ref derivation |
| [`@algovoi/settlement-attestation`](https://www.npmjs.com/package/@algovoi/settlement-attestation) | Settlement attestation receipt format |

## Conformance

Validates byte-identically against
[`chopmob-cloud/algovoi-jcs-conformance-vectors`](https://github.com/chopmob-cloud/algovoi-jcs-conformance-vectors)
on the `settlement_attestation_v1` vector set. Eight vectors PASS on
every run.

## Adopters Registry

If you ship a derived agent that emits AlgoVoi-format receipts, you are
welcome to submit your project to the
[Substrate Adopters Registry](https://docs.algovoi.co.uk/adopters). The
registry is the AlgoVoi-controlled attestation route, byte-deterministic
against the public conformance corpus.

## Substrate authorship

The receipt format and canonicalisation discipline this agent emits are
sole AlgoVoi authorship, anchored on the IETF Independent Submission
stream. The reference implementation libraries are published under
AlgoVoi authorship on PyPI and npm.

## License

Apache 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

Apache 2.0 grants permission to USE, MODIFY, and DISTRIBUTE this
reference code. It does not grant permission to republish the normative
receipt format, the canonicalisation discipline, or the AlgoVoi name in
ways that imply endorsement, certification, partnership, or
substrate-author co-authorship.

-- AlgoVoi (chopmob-cloud)
https://docs.algovoi.co.uk/acquisition
