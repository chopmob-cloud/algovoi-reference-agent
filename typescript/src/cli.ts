#!/usr/bin/env node
/**
 * Command-line interface for the TypeScript reference agent.
 *
 * Usage:
 *   algovoi-agent emit [--jurisdiction GB,EU] [--result SETTLED]
 */

import { emitAndVerify } from "./pipeline.js";

interface CliArgs {
  command: string;
  jurisdiction?: string;
  result?: string;
}

function parseArgs(argv: readonly string[]): CliArgs {
  const result: CliArgs = { command: argv[0] ?? "" };
  for (let i = 1; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--jurisdiction") {
      result.jurisdiction = argv[++i];
    } else if (arg === "--result") {
      result.result = argv[++i];
    }
  }
  return result;
}

function printUsage(): void {
  console.log(
    "Usage: algovoi-agent emit [--jurisdiction GB,EU] [--result SETTLED]\n" +
      "\n" +
      "Emits a settlement-attestation-v1 receipt under " +
      "urn:x402:canonicalisation:jcs-rfc8785-v1 for a Base chain " +
      "transaction (deterministic stub mode), and self-verifies the bytes.",
  );
}

function main(argv: readonly string[]): number {
  const args = parseArgs(argv);
  if (args.command !== "emit") {
    printUsage();
    return args.command ? 1 : 0;
  }

  const jurisdictionFlags =
    args.jurisdiction !== undefined ? args.jurisdiction.split(",") : [];

  const { emit, verify } = emitAndVerify({
    settlement_result: args.result ?? "SETTLED",
    jurisdiction_flags: jurisdictionFlags,
  });

  const output = {
    action_ref: emit.action_ref,
    receipt: emit.receipt_dict,
    receipt_hash: emit.receipt_hash,
    verification: {
      canonical_bytes_match: verify.canonical_bytes_match,
      receipt_hash_match: verify.receipt_hash_match,
      overall_pass: verify.overall_pass,
    },
  };
  console.log(JSON.stringify(output, null, 2));
  return verify.overall_pass ? 0 : 1;
}

process.exit(main(process.argv.slice(2)));
