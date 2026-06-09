# algovoi-reference-agent

[![PyPI](https://img.shields.io/pypi/v/algovoi-reference-agent?label=PyPI)](https://pypi.org/project/algovoi-reference-agent/)
[![npm](https://img.shields.io/npm/v/@algovoi/reference-agent?label=npm)](https://www.npmjs.com/package/@algovoi/reference-agent)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Apache 2.0 reference implementation of an agent that emits an AlgoVoi
`settlement-attestation-v1` receipt for a Base chain transaction. End-to-end
worked example demonstrating the AlgoVoi-authored substrate discipline.

## What this is

A minimal open-source agent that:

1. Performs a Base chain transaction (live RPC or deterministic stub)
2. Emits a `settlement-attestation-v1` receipt under
   `urn:x402:canonicalisation:jcs-rfc8785-v1`
3. Derives an `action_ref = SHA-256(JCS(preimage))` per the AlgoVoi-authored
   discipline
4. Self-verifies the canonical bytes against the AlgoVoi conformance corpus

The receipt format is normatively specified in IETF Internet-Draft
[`draft-hopley-x402-settlement-attestation`](https://datatracker.ietf.org/doc/draft-hopley-x402-settlement-attestation/).
The canonicalisation discipline is specified in
[`draft-hopley-x402-canonicalisation-jcs-v1`](https://datatracker.ietf.org/doc/draft-hopley-x402-canonicalisation-jcs-v1/).

## Quick start

```bash
pip install algovoi-reference-agent
algovoi-agent emit --chain base --amount 0.001
```

Output: a JSON `settlement-attestation-v1` receipt to stdout, the derived
`action_ref`, and a local self-verification result.

## Pipeline

```
Agent action (Base txn, live or stub)
      |
      v
algovoi-substrate (JCS canonicalisation, action_ref derivation)
      |
      v
algovoi-settlement-attestation (receipt format)
      |
      v
{ canonical_bytes, action_ref, receipt_json }
      |
      v (downstream: any consumer)
   Reputation systems, audit chains, third-party verifiers, or any
   party consuming the AlgoVoi-format receipt under Apache 2.0.
```

## Conformance

This reference agent validates against
[`chopmob-cloud/algovoi-jcs-conformance-vectors`](https://github.com/chopmob-cloud/algovoi-jcs-conformance-vectors)
on every receipt emission. Byte-for-byte agreement against the
`settlement_attestation_v1` vector set is required.

## Composed libraries

| Package | Purpose | Registry |
|---|---|---|
| [`algovoi-substrate`](https://pypi.org/project/algovoi-substrate/) | JCS canonicalisation, action_ref derivation | PyPI / npm |
| [`algovoi-settlement-attestation`](https://pypi.org/project/algovoi-settlement-attestation/) | Settlement attestation receipt format | PyPI / npm |
| [`algovoi-audit-verifier`](https://pypi.org/project/algovoi-audit-verifier/) | Local conformance verification | PyPI / npm |

All Apache 2.0, AlgoVoi sole authorship.

## Adopters Registry

If you ship a derived agent that emits AlgoVoi-format receipts, you are
welcome to list your project at
[docs.algovoi.co.uk/adopters](https://docs.algovoi.co.uk/adopters). The
registry is the AlgoVoi-controlled attestation route. Submissions are
validated byte-deterministically against the public conformance corpus.

## Examples

See [`examples/`](examples/):

- `01_emit_settlement_attestation.py`: minimal emit example
- `02_verify_receipt.py`: verify a received receipt locally
- `03_end_to_end_pipeline.py`: agent runs txn, emits receipt, self-verifies

## Substrate authorship

The receipt format and canonicalisation discipline this agent emits are
sole AlgoVoi authorship, anchored on the IETF Independent Submission stream.
The reference implementation libraries are published under AlgoVoi authorship
on PyPI and npm. The conformance corpus is maintained at
[chopmob-cloud/algovoi-jcs-conformance-vectors](https://github.com/chopmob-cloud/algovoi-jcs-conformance-vectors).

## Tests

```bash
# Python (16 tests)
pip install -e .[dev]
python -m pytest tests/ -v

# TypeScript (17 tests)
cd typescript && npm install && npm test
```

## License

Apache 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

Apache 2.0 grants permission to USE, MODIFY, and DISTRIBUTE this reference
code. It does not grant permission to republish the normative receipt format,
the canonicalisation discipline, or the `settlement-attestation-v1` schema
under a different authorship.

-- AlgoVoi (chopmob-cloud)
https://docs.algovoi.co.uk/acquisition
## Attribution

This package is Apache-2.0. Use it freely and build whatever you are building on top of it. The only ask is the one the licence already makes: keep the NOTICE, and name who authored the substrate. To attribute it in your own product, add this to your NOTICE file:

```
This product includes the AlgoVoi substrate,
authored by Christopher Hopley / AlgoVoi (chopmob-cloud), Apache-2.0.
https://docs.algovoi.co.uk/canonicalisation-substrate
```

The full invitation is at https://docs.algovoi.co.uk/canonicalisation-substrate#adopt-the-substrate
