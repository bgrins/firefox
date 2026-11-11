# CSS unordered combinator prototype

This opt-in research slice adds `||` for nonnullable complete operands while preserving the earlier grammar/parser files. It proves a reusable relation over distinct bounded component occurrences, connects it to executable lowering and the postfix/JSON path, and proves the pinned text-transform language has exactly the independently specified 38 normalized keyword sequences.

The reviewed support restriction matters: nullable operands are explicitly refused, although CSS permits them. Grouping is not flattened. `a || a` has two occurrences and can accept two `a` tokens. `&&`, production references, full Bikeshed processing and raw CSS tokenization remain unsupported here. Read `MAPPING.md` for the precise conditional/specification/runtime boundaries.

Reproduce from sources only:

```sh
python3 -I -B artifacts/css-unordered-combinator-20261110-v1/replay.py \
  --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --out /tmp/css-unordered-replay
```

The output directory must not exist. `SOURCE-ONLY.json` binds the exact inputs; the separate earlier `PROPOSAL-FILES.json` preserves the pre-proof contract/oracle/source checkpoint. The checker compiles a fresh temporary dependency closure, audits every theorem, executes the real JSON file and compatibility cases, and tests compiling semantic mutations and refusals. Temporary compiled files are removed on success or failure; command logs and hashes remain in the output directory. No network, Git, canonical library, browser or native build is used by replay.

`REPORT.md` records the completed counts and limitations. Baseline/parser source provenance is in `PRESERVED.json`; additional old fixture/source provenance is in `COMPATIBILITY-SOURCES.json`. These are exact local artifact copies; the checker does not independently authenticate remote Git object provenance.
