# JSON number program to numeric lexical model

This standalone milestone proves exact lexical agreement between the accepted decoded number program and the earlier byte-oriented numeric reference on normalized ASCII number-entry inputs. It covers the raw consumed prefix, remainder, three digit runs, sign presence and syntactic integer classification. It also composes the earlier full-token model without confusing its suffix with the numeric-core suffix.

See [MAPPING.md](MAPPING.md) for the theorem chain, caller domain, provenance and limits. This is a Lean-to-Lean bridge. Native Rust refinement, floating-point conversion, prose translation and JSON text parsing remain unproved.

Run a fresh source-only replay with Lean 4.35.0-rc4:

```sh
python3 -B artifacts/css-number-lexical-bridge-20261110-v1/replay.py --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean --out /tmp/css-number-lexical-replay
```

The output directory must not already exist. The script copies only the hash-bound source allowlist, builds dependencies afresh, audits every named theorem, runs both actual-file and reference paths, checks malformed documents and semantic/provenance controls, and removes its temporary compiled output. No canonical repository, native source, browser, Git index or commits are changed.

The reproducible runtime corpus includes signed zero, leading zeroes, fraction/exponent rollback, incomplete exponent plus dimension suffix, percentages, LF as a suffix, a 257-digit input, both initial model-error flags, and off-domain refusals. The changed valid JSON document provides a separate execution-dependence control. Final exact inventories and receipts are in REPORT.md and the verification output.
