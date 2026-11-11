# Integration staging accepted locally

Prepared an exact import-only integration of the accepted first-order backend,
IR/lowering, typed-data codec, and actual JSON-value schema codec as an opt-in
`CssDerivation` library in the existing standalone Lake package. The staged patch
modifies only `lakefile.lean` and a README entry; other patch paths are additions.
No live canonical source, native code, Git index, or commit was modified.

The 34 accepted inputs were authenticated directly against signed
`0dcfe7c2e7a8cd9924894449dd1d97d3c604d79c`. Nine canonical baseline files were checked
against signed `2d13828cd078dde80d097bc590988bc701be79d4`. Both reused scalar/input
dependencies match exactly. All theorem names/namespaces are preserved; only
module import lines change. ParserIR number extensions are excluded.

## Validation

- Exact patch application to an isolated baseline matches every staged file.
- Fresh source-only reconstruction passes the unchanged accepted harness:
  143 axiom audits, 35 kernel cases, 13 rows for each of three runners, 13 parser
  observations, four malformed-document refusals, six compiling semantic mutants,
  and three provenance controls.
- Fresh relocated compilation preserves the same 143 theorem names and exact
  allowed axiom dependency sets. All three relocated actual-file runners return
  the expected 13 rows each.
- `lake build CssDerivation` passes in the isolated tree. Pinned Lake globs select
  the facade and its imports; its 22-module local closure excludes all CLI global
  `main` definitions. Native-library linking was not run or claimed.
- Unchanged canonical coverage registration passes all 11,923 declarations.
  No CSS feature coverage is added. The full historical canonical test suite was
  not re-executed; parent integration should run the unchanged default build plus
  coverage registration, and may optionally repeat that broader suite.
- Temporary source/build workspaces were removed; no owned compiled caches remain.

`verification/report.json` records the relocated checks. The nested
`verification/accepted-regression/report.json` records the accepted semantic
controls on exactly restored original paths. Import-only transport is separately
byte-authenticated; those controls are not mislabeled as newly mutated relocated
modules. `PATCH-CHECK.json`, `BASE.json`, `ORIGINS.json`, and `LAKE-CLOSURE.json`
record patch, origin, and build-closure evidence.

## Reproduction and handoff

```sh
python3 -B replay.py --lean /path/to/lean/bin/lean --out /new/report/path
```

The 50-entry `SOURCE-ONLY.json` supplies the isolated reproduction inputs.
`integration.patch` applies relative to the standalone library root; `overlay/`
is the exact resulting file set. `base/` is only a local validation fixture and
must not be installed wholesale. See `PLAN.md` for parent-owned application and
review steps, and `overlay/research/derivation/README.md` for the tooling contract.

The JSON-value theorems do not verify JSON text parsing, duplicate-key policy,
prose interpretation, universal legacy-document orchestration, or native browser
refinement. The old JSON helper dependency is explicitly retained; actual runtime
AST decoding uses the new proved reader. Existing scalar/input APIs, CSS coverage
accounting, and the default semantics target remain unchanged.
