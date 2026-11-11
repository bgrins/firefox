# Typed number document transfer

The accepted CSS consume-number parser now runs from an actual JSON document through a proved typed decoder and the existing transactional backend. This is a separate research capsule; canonical library, Firefox sources and CSS coverage are unchanged.

The universal results cover all seven existing ParserIR combinators: actual-Json schema correspondence in both directions, typed encoder roundtrip, versioned envelope correspondence in both directions, and preservation of complete modeled input/error state through lowering. A pinned number document composes with the prior exact decimal `NumericResult` relation. Merely matching `NumberShape` does not establish that a different program implements CSS.

The source-only replay passes **325 axiom audits (57 new declarations), 30 kernel cases, 84 actual-file rows, nine malformed-file refusals, four compiling semantic mutations and three source-drift controls**. The changed valid document has observably different exponent handling. All 49 recorded source origins were also authenticated with read-only Git object retrieval.

Run from the Firefox checkout:

```sh
python3 -B artifacts/css-number-document-transfer-20261110-v1/replay.py \
  --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --out /tmp/css-number-document-replay
```

The output directory must not already exist. The replay copies only the 62 hash-bound inputs, compiles all 49 Lean modules from source, checks the complete named-theorem axiom inventory, executes both actual files, and runs the refusal/mutation controls. Its temporary proof builds are removed. The toolchain itself is external and version-checked.

`MAPPING.md` defines the theorem interfaces and limits. JSON text parsing, duplicate-key collapse, serialization, prose interpretation and native floating-point behavior remain outside the proofs. The JSON grammar and source-map object are research interchange data, not a claim that CSS prose has been mechanically translated.

`verification-1/report.json` and its command logs are the author source-only receipt. `SOURCE-ONLY.json` is the executable-input allowlist; `PRESERVED.json` identifies immutable origins and import-only relocations; `ORIGIN-CHECK.json` records the author Git authentication. No compiled objects are retained.
