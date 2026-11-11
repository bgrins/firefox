# Document tooling integration proposal

Apply the staged patch against standalone library commit
`898fb45815c115362093116d81c09715ba94fcab`. It imports the document milestone signed
in Firefox research commit `f3949d2992abdc02536b9a61e51dc7d603ce0868`, with no new
Lean semantics or CSS coverage claim.

## Layout and compatibility

The existing opt-in `CssDerivation` Lake target is reused. The public facade adds
`Codec.Document.Laws`, `Codec.Document.AliasLaws`, and `Examples.GenericEscapeDocument`.
The original fixed `Codec.Json.Document` API and all 21 canonical dependencies are
reused byte-for-byte. The two prior prototype modules become
`FirstOrder.Weakening`/`WeakeningLaws`; their historical declaration namespaces stay
unchanged. Generic document modules live under `Codec.Document`. No invasive
helper extraction or namespace/API rename is mixed into this transport.

Transferred Lean source changes are import-line relocation only. The entire patch
is **not** import-only: it also adds a document checker, documentation, a facade
registry, and a necessary dependency-collection adjustment to the existing checker.
Only four existing files change: `CssDerivation.lean`, `derivation_check.py`, and
the two tooling entry READMEs. `lakefile.lean`, the default CSS target, scalar/input
APIs, `check.py`, and normative `coverage.json` are unchanged.

CLI and test sources remain outside the public facade closure. The exact registry
contains 30 local module sources, including the two reused CssSemantics leaves.
The pinned Lake configuration uses the root module and its transitive imports,
not all files beneath the library directory. Native linking is not claimed.

## Necessary checker adjustment

The existing checker originally copied only the first-order/JSON milestone's
source roster, then built the current public facade. That would fail once the
facade imports document modules. The narrow collector now authenticates and
copies every facade dependency through `research/derivation/FACADE.json` and
compiles dependencies in import order. It requires the registry to be the exact
closure and rejects missing/changed/unregistered/cyclic imports and unsupported
module-import syntax. It accepts the current single-module import style and
Lean/Init/Std external modules, not arbitrary Lean syntax or third-party packages.

The original 143-theorem axiom inventory and semantic controls stay separate and
unchanged. `document_check.py` runs the accepted document harness on exactly
restored sources, then separately compiles/audits relocated modules and the four
transferred independent boundary proofs: 156 accepted declarations plus four
review declarations. The four review proofs retain explicit authorship/acceptance
credit; they are not new work from this integration. They include a counterexample
to the deliberately unclaimed whole-document converse.

Four additional executable registration controls cover a missing dependency,
changed dependency bytes, an authenticated but unsupported import form, and an
excess registry entry. These are checker controls, not new formal semantic proofs.

## Reproduction and parent-owned application

```sh
python3 -B replay.py --lean /path/to/lean/bin/lean --out /new/report/path
```

The source-only replay installs `base/` then `overlay/` into a temporary directory,
runs both installed checkers, and removes temporary builds. Each installed checker
also builds fresh isolated source trees. `base/` contains only required pinned
sources and baselines; it is not a replacement copy of the full standalone repo.
`integration.patch` is relative to the standalone library root. Its application
was checked in an isolated base and compared byte-for-byte with `overlay/`.

Root should review/authenticate the exact patch, apply it, then run:

1. `python3 check.py --coverage-only` for unchanged normative registration.
2. The actual default `lake build` in the canonical checkout. It may reuse the
   existing cache; report that separately from these fresh tooling proof runs.
3. `lake build CssDerivation` to exercise the installed opt-in target.
4. An actual installed document CLI smoke check against the pinned successor
   fixture. The two full installed checkers may be repeated if review or changed
   sources justify it; author and independent fresh replays of the exact patch
   already supply the semantic acceptance gates. Avoid a third full pair by
   default. Their separate, overlapping audit totals must not be summed as CSS
   coverage.

Per root's instruction, this lightweight capsule does not copy or rebuild the
hundreds of unchanged default CSS modules. A real default build is a post-application
gate; neither static registration nor opt-in builds are reported as that gate.
Root owns canonical application, review receipts, and signing. This task modifies
no live canonical/native source or Git index/commit.

## Claim boundaries

Definition admission has a full iff; accepted-document semantics has soundness
only. The fixed escape wrapper is equal on every JSON value. Selected alias
noncapture covers canonical `nodeJson "use" [name]` under arbitrary admitted
definitions and ambient tails, not whole-program alias semantics or every raw-use
layout. Shared map lookup remains distinct from object key enumeration. JSON text
parsing, duplicate text keys, numeric spelling, source-map meaning, and hand-mapped
CSS prose interpretation remain unchanged boundaries.

`CANONICAL-STATE.json` records the read-only pre-application HEAD, tracked/untracked
status, and the existing `.DS_Store` hash. The patch contains no `.DS_Store` path;
neither source-only copies nor cleanup touch that metadata. Root should preserve
its bytes through application and verify that only the expected patch paths change
from this recorded baseline before committing.
