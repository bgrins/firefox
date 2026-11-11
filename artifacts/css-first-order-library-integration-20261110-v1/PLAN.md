# First-order tooling integration plan

## Recommendation

Add an opt-in `CssDerivation` library target to the existing Lake package. Keep
`CssSemantics` as the unchanged default. Install relocated modules beneath
`CssDerivation/`, retain existing declaration namespaces, and register tooling
proofs in `derivation_check.py` rather than the CSS feature inventory.

A second package would introduce a local-path package dependency for only two
existing scalar/input modules and complicate source-only reproduction. Placing
this tooling under `CssSemantics` would make its generic codec theorems appear in
the CSS theorem/coverage registration and couple the default build to research
frontends. A second library in the same package avoids both costs while keeping
the existing APIs and coverage accounting intact.

The exact staged tree is `overlay/`; `integration.patch` is relative to the
standalone library root. `base/` contains only changed-file baselines, the two
reused dependencies, and the toolchain pin. It is a validation fixture, not extra
library content. Do not copy the capsule directory wholesale into the library.

## Scope

Transfer the first-order backend/IR/lowering, typed constructor codec, actual
JSON-value schema/reader/encoder laws, and escape correspondence. Preserve all
old theorem names and source hash provenance. The import relocation is the only
Lean source change. No ParserIR/consume-number extensions are required.

Reuse `CssSemantics.CssInput` and `CssSemantics.CssEscape` directly: each is
byte-identical between accepted source and canonical baseline. The existing
finite-code-point, DOMString, and streaming APIs are unaffected. No change to
`coverage.json`, `CssSemantics.lean`, `check.py`, or `tests/Audit.lean` is proposed.
The checked CSS fragment remains consume-an-escaped-code-point, now exposed
through the tooling pipeline; there is no added CSS feature-coverage claim.

The legacy helper module retains its old unproved JSON fold because its alias
and outer-document helper definitions are dependencies. Actual document ASTs
route through the new proved reader. Splitting those helpers is a subsequent
semantic refactor, not a condition of this import-only integration.

## Parent-owned landing steps

1. Confirm the canonical base remains signed `2d13828cd078dde80d097bc590988bc701be79d4`
   or review any intervening changes against `BASE.json`. Authenticate the patch
   and source allowlist from this capsule.
2. Independently replay the scoped checker with `replay.py`. Review the import
   map, JSON-value/text boundaries, fixed legacy adapter, and unchanged coverage.
3. Apply `integration.patch` at the canonical library root. It modifies only
   `README.md` and `lakefile.lean`; all other patch paths are new files.
4. Run `python3 check.py --coverage-only` and the default `lake build` in the
   integrated checkout. All existing CSS source/test bytes are unchanged, so
   this scoped integration gate need not repeat every immutable runtime case and
   negative control. Root may additionally run the full `check.py --lake ...`;
   record explicitly whether that broader historical suite was re-executed.
5. Run the installed `derivation_check.py --lean ... --out ...` and record both
   gate receipts. Commit the standalone library change separately, then the
   parent artifact/review evidence according to the existing workflow.

All work here is local and staged. No live canonical files, native code, browser
fixtures, Git index, or commits are modified by this task.

## Validation separation

The installed checker reconstructs the accepted sources by reversing exact
import lines and requires every original byte hash to match the signed manifest.
It runs the unchanged accepted harness, including six compiling semantic mutants
and three provenance controls. It separately compiles all relocated modules,
compares the exact theorem inventory and axiom dependency sets, executes all three
actual-file runners, and exercises the opt-in Lake facade. The semantic mutation
runs are on the exactly restored layout; they are not falsely reported as new
mutations of the relocated path names.

`SOURCE-ONLY.json` plus `replay.py` reproduces these scoped checks from copied
sources without canonical working-tree access. `BASE.json` and `ORIGINS.json`
record directly authenticated Git objects. Existing coverage registration is
checked read-only and reports 11,923 declarations; the full existing CSS proof
suite is not re-executed here; the parent chooses the scoped gate above.

No claim is made that JSON text parsing, duplicate-key policy, prose extraction,
all document orchestration, or native browser execution has become verified.

`LAKE-CLOSURE.json` records the pinned Lake implementation and facade import
closure. Default globs select only the facade and its imports; all CLI `main`
modules are outside that closure. Static/shared module collection uses the same
closure. This capsule checks the default Lean-artifact facet, not native linking.
