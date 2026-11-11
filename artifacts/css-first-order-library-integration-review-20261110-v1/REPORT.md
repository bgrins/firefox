# Standalone first-order tooling integration review

No blocking finding in the frozen import-only integration. It is suitable for
the parent-owned source-only replay and subsequent canonical integration gates.
This review does not claim that the patch has been applied to the standalone
repository or that its unchanged default build has been rerun.

Reviewed capsule: `css-first-order-library-integration-20261110-v1`.
Its 50-entry `SOURCE-ONLY.json` has SHA256
`56786d94c7ac2f341b52cf9964c7bb386eaab42c06eb9390fd3659fa97f741c4`;
`integration.patch` has SHA256
`540e1f0fe684690aff99b94e782b85e057e4ba4ae98f7db32aad1f5211a229ac`.

## Independent authentication

The review's `check.py` reads Git objects without modifying either repository.
It authenticates all nine recorded canonical baseline objects at
`2d13828cd078dde80d097bc590988bc701be79d4` in `artifacts/css-spec-lean`,
and all 34 accepted source objects at
`0dcfe7c2e7a8cd9924894449dd1d97d3c604d79c` in Firefox. This authenticates
object contents; it is not an independent cryptographic signature verification.

The checker independently reverses the 24-module import map using a separate
byte-level substitution, without importing the author's checker. All 34 restored
inputs equal the accepted Git object bytes exactly. The map is injective, both
input and destination rosters are exact, and no namespace, declaration, proof,
algorithm, or literal changes survive import reversal.

Both shared modules, `CssSemantics.CssInput` and `CssSemantics.CssEscape`, match
the canonical and accepted hashes. Neither is duplicated in the overlay.
The overlay intersects the complete canonical tracked tree only at `README.md`
and `lakefile.lean`; every other installed path is new. The patch applies in an
isolated copied baseline, produces exactly the overlay plus unchanged baseline
files, and reverses to the original baseline. Temporary files are removed.
`CHECK.json` records the independent results.

The first development run of this review checker expected an extra blank line
before the added Lake target and rejected the actual one-line append. The
checker was corrected to the exact frozen bytes. This was a reviewer checker
assumption, not a candidate failure. The final receipt reports the corrected run.

## Library and API boundary

`lakefile.lean` retains `@[default_target] lean_lib CssSemantics` and appends
only `lean_lib CssDerivation`. Pinned Lake `defaultTargetAttr` evaluation selects
the explicitly marked target; the additional unmarked declaration does not
replace it. Existing `CssSemantics.lean`, `coverage.json`, `check.py`,
`tests/Audit.lean`, and all existing module APIs are outside the patch. The
canonical coverage scanner searches `CssSemantics/`, so the new tooling laws
are not counted as additional normative CSS coverage.

The computed transitive local import closure of `CssDerivation.lean` has 22
modules: 20 in `CssDerivation`, plus the two shared `CssSemantics` dependencies.
All four CLI modules and `Tests.JsonCases` are excluded, and no global `main`
declaration appears in that closure. The facade nevertheless exposes lowering,
typed-data laws, actual-JSON schema laws, the document adapter, and escape
correspondence. CLI tools and cases remain available for explicit validation.

The pinned Lake implementation confirms root-only default globs, recursive
local imports, Lean-artifact default facets, and disabled precompilation.
`LeanLib.recCollectLocalModules` keeps imports from the same library, so its
collection for this target has 20 modules; the broader 22-module dependency
closure includes two modules belonging to the other library. Static/shared
collectors use the same-library collection. This distinction does not admit
the CLI `main` modules. Native linking is untested and is not inferred from a
Lean-artifact build. Lake source hashes are in the author closure receipt and
this review's `ADDITIONAL-PINS.json`.

The new tooling API deliberately preserves the accepted declaration namespaces;
module paths change, not declaration names. Consumers of the archived artifact
must update imports, as the transport table makes explicit. This is not a claim
that every historical artifact import path remains a public compatibility API.

## Harness and evidence review

The installed checker authenticates the exact transport roster, verifies every
installed hash, reverses imports to accepted bytes, and runs the accepted
checker in a fresh reconstructed tree. It separately compiles the relocated
modules, compares all theorem names and exact permitted axiom dependencies,
executes three actual-file runners, and builds the opt-in Lake facade. The
outer replay authenticates the 50 source inputs before and after execution
and reconstructs only the allowlisted baseline/overlay. Temporary builds are
removed on completion. No canonical checkout is required by this replay.

The author's frozen positive receipt reports 143 relocated audits, with the
same axiom sets as the accepted source layout, and 13 expected rows from each
of three relocated runners. The accepted harness also reports 35 kernel cases,
13 parser observations, four malformed-document refusals, six compiling
semantic mutants, and three provenance controls. These semantic mutations run
on the exactly restored accepted paths; they are not mutations of the new
module names. This is accurately disclosed in both installed and capsule docs.

Reviewed receipt hashes:

- `verification/report.json`:
  `b08d18784a4351e5f3a0b57c6887e2e9ee4bab5b6e38852f193aae3bcb966dfb`.
- `verification/accepted-regression/report.json`:
  `93bfedf5b624df42c6c959e283916b71fd76bb4011113998f507040588066afb`.

This reviewer independently ran transport, Git-object, patch, and closure
checks. Root owns the full fresh Lean replay; this report does not count that
concurrent work as a reviewer-run build. The parent's post-application default
Lake build and coverage registration remain the appropriate integration gates.
Repeating the entire unchanged historical canonical test suite is optional
broader coverage, not something performed by this capsule.

## Proof claims remain bounded

The transfer adds no new proof-discovery or CSS feature-coverage credit. The
manually interpreted escape algorithm remains the CSS fragment. Generic
typed-IR and actual-`Lean.Json` codec theorems retain their previously reviewed
scope. JSON text parsing, duplicate text keys, serialization, lexical number
spelling, prose interpretation, universal legacy-document orchestration, and
native/browser refinement remain outside those theorems.

`Codec.LegacyJson` retains old helpers and its unproved legacy AST fold; actual
document AST decoding imports and calls the new proved reader. Keeping those
bytes avoids an unrelated semantic refactor. The docs distinguish this
dependency from the execution route. No ParserIR/consume-number extension is
silently included.

No canonical source, browser/native source, Git index, or commit was changed
by this review. Existing untracked canonical files were not touched.
