# Independent document-library integration review

Status: accepted for this bounded integration; no blocking finding. Independent
source authentication, scoped proof/runtime replay, and copied-tree collector
controls pass. This is an integration review, not a new proof of CSS behavior or
mechanical specification derivation.

## Authenticated inputs

The proposal is `css-document-library-integration-20261110-v1`, source manifest
`e9ad5b48f5e47dae1ff8502b57bab17fdb32f83eaedddd5a3330db57c54ea832`
(79 inputs), patch
`8a64b3c4f04b45f21deb489a3446441226d0dd784fb4fa22d52f30351143a718`.
`check.py` independently authenticated 91 immutable Git objects against:

- Standalone base `898fb45815c115362093116d81c09715ba94fcab` in
  `artifacts/css-spec-lean`.
- Firefox research commit `f3949d2992abdc02536b9a61e51dc7d603ce0868`, containing
  the accepted document implementation and its independent boundary review.

This authenticates object bytes and the correspondence to the stated revisions;
it is not a new cryptographic commit-signature verification. The accepted source
manifest is identical to the original 45-input document milestone manifest.

The independent check applies and reverses the patch in an isolated temporary
tree, comparing every file byte with the proposed overlay and original base.
The complete baseline Git tree also has no existing tracked-file collision at
any proposed new path; this does not make a claim about concurrent untracked files.
Only four existing files change: `CssDerivation.lean`, `derivation_check.py`, and
the top-level and derivation READMEs. The 45 transport records are unique in both
source and destination, and reverse exactly to their accepted bytes. The four
independent review proofs reverse exactly too, with their original review report
and attribution preserved. There are 12 changed import lines in the accepted
transport, plus the three relocated imports of the independent review module.

There are 24 shared inputs: 21 Lean dependencies and three fixture/data inputs.
In particular, the existing fixed `Codec.Json.Document` API, old runners, scalar
and input dependencies are preserved. The new generic document reader is an
additional interface; the old runner has not silently been rerouted through it.
Historical declaration namespaces remain unchanged.

## Checker and dependency review

The old checker could not build an enlarged facade from its original copy list.
The new collector fixes that narrow problem by following imports from
`CssDerivation`, verifying each local source against `FACADE.json`, and returning
dependency-before-dependent order. Its registry must equal the complete reached
set. Both staged checkers use this collector. The exact closure has 30 local
source files, including the root and two unchanged `CssSemantics` leaves; it
contains no CLI `main` module or test module.

The collector accepts a deliberately restricted line grammar, not all legal Lean
syntax. It permits single-module imports under `CssDerivation`/`CssSemantics`,
and external `Lean`/`Init`/`Std` imports. It rejects unsupported import forms,
other external packages, module/prelude headers, missing/unregistered/changed
local sources, cycles, and unused registry entries. Full-line `--` comments are
ignored. This is suitable for the exact authenticated sources. It is not a
general Lean parser, and source plus registry plus checker remain reviewable
trusted inputs; a jointly rewritten registry is not external authentication.

The old checker's other logic remains intact: it reverses the original accepted
transport, runs that unchanged semantic harness, compiles relocated modules,
requires exact theorem-name/axiom-map equality with the accepted run, executes
three actual-file runners, and builds the opt-in Lake target. Added facade
modules do not expand its 143-declaration audit silently. Both checkers capture
source hashes before and after verification and discard their fresh build trees.

The new document checker separately reverses all 45 accepted inputs and runs
their unchanged accepted harness. It compiles the relocated source and four
review declarations, checks the accepted 156-declaration axiom map exactly, and
allows only `propext`, `Quot.sound`, and `Classical.choice` in the complete audit.
It executes the generic reader on the same five real JSON files/profile pairs
and compares the complete rows with the accepted run. Semantic mutants exercise
exactly restored sources; relocated compilation, axioms, runtime, and Lake build
are separate checks. The report distinguishes those operations.

The author's four collector controls cover missing and changed dependencies,
an authenticated unsupported multiple-import form, and excess registration.
Our separate copied-tree controls additionally reject an existing unregistered
dependency, an authenticated import cycle, a forbidden third-party import, and
both `module` and `prelude` headers. A comment-only import is a positive control
with unchanged closure. Each rejection requires its exact intended diagnostic.
These are executable Python checker tests, not kernel theorems.

## Proof and compatibility boundaries

This transports established results without changing their propositions or proof
bodies. Flat-definition admission has an iff; whole-document acceptance has
soundness only. The all-JSON fixed escape-wrapper equivalence is retained.
Selected alias noncapture covers canonical `nodeJson "use" [name]` for admitted
definitions and arbitrary ambient tails, not every raw-use layout or complete
program alias evaluation. Map enumeration and shared lookup remain distinct.
The transferred boundary counterexample explicitly prevents interpreting the
soundness result as a general document converse.

Caller signature types, JSON text parsing and duplicate-text-key handling,
numeric lexical forms, source-map interpretation, and manually mapped CSS prose
remain outside these proofs. The overlapping 143 and 160 audit inventories must
not be added together as independent theorem or CSS-coverage totals.

The patch does not change `lakefile.lean`, default-target registration, canonical
`check.py`, or `coverage.json`. Their preservation and the opt-in closure were
inspected statically. This review does not build the unchanged default CSS
library, native-link a library, execute a browser, or mutate the canonical repo.
Root owns application and any post-application default-target gate.

One nonblocking documentation clarification is recorded in the author's final
`REPORT.md` (SHA-256
`6e533c1223b9b6b4c11861d52063f355133df7f3ee100ba10125f8270a5bd92c`):
the older derivation README paragraph disclaiming document orchestration and
weakening describes the original 143-audit milestone. The appended document
section introduces the newly integrated bounded results. It does not add a
whole-document completeness claim. The frozen patch was not changed for this
wording clarification. Root subsequently made the separate documentation-only
delta described below.

## Reproduction and execution

```sh
python3 -B artifacts/css-document-library-integration-review-20261110-v1/check.py
python3 -B artifacts/css-document-library-integration-20261110-v1/replay.py \
  --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --out artifacts/css-document-library-integration-review-20261110-v1/replay
```

The output directory for a new replay must not already exist. `CHECK.json`
records the completed independent object/transport/collector checks. The scoped
replay uses isolated source trees and builds both installed tooling targets;
it does not reuse the canonical library's compiled artifacts.

The independent replay exited zero. `finish.py` authenticated 207 saved command
logs and matched the author's exact audit maps, control rosters, facade hashes,
and document execution rows. `REPLAY-CHECK.json` records the results:

| Independent gate | Result |
| --- | --- |
| Original first-order/JSON contract | 143 audits, 35 kernel cases, 13 rows in each of three runners, four malformed-document refusals, six compiling semantic mutants and three provenance controls pass. |
| Generic document contract | 156 accepted audits plus four transferred review proofs, 20 kernel cases, 25 rows across five actual files/four caller profiles, eight malformed-file refusals, four compiling semantic mutants and three provenance controls pass. |
| Facade registration | Four author controls plus five independent rejection controls and one independent comment-only positive control pass. |
| Fresh opt-in builds | Both staged checkers build `CssDerivation` successfully in separate temporary source trees. |
| Cleanup | Temporary trees removed; no compiled outputs remain in this review capsule. |

No default CSS build, browser execution, native link, or canonical mutation was
performed by this reviewer. Root separately reports successful canonical default
and opt-in builds, unchanged 11923-declaration coverage accounting, and a 25-row
installed CLI smoke run. Those are root's operations, not additional builds by
this review.

## Final root documentation delta

`check-root.py` independently applied the root-only clarification to a temporary
README and checked all 32 installed overlay files against
`ROOT-FINAL-FILES.json`. The only difference from the frozen overlay is
`research/derivation/README.md`: its heading becomes `Original codec boundaries`
and a sentence links the generic document proof boundaries. All Lean, Python,
registry, fixture and other overlay bytes are unchanged.

The separate patch SHA-256 is
`b6d5854f4f16f22a09850004e443f857bcafb8c224550fd3cb528ac9eb5dd18b`.
`ROOT-DOC-CHECK.json` records the live read-only comparison and exact patch
application. This resolves the documentation ambiguity and does not require a
semantic rerun. The frozen proposal/replay remains unchanged; this extra delta
must accompany it when describing the final installed state.
