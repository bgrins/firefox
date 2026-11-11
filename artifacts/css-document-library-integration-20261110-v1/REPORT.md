# Document library integration staged and verified

Prepared an exact standalone-library patch against canonical commit
`898fb45815c115362093116d81c09715ba94fcab`. All transferred Lean bodies are unchanged;
only import lines relocate. The patch also contains necessary Python checker and
registration changes, so the integration as a whole is not called import-only.
This agent made no canonical/native or Git index/commit changes.

## Integration

- Reuse 21 canonical Lean modules and three existing fixture/provenance inputs.
- Relocate the two prior weakening modules and nine document modules beneath
  `CssDerivation`, preserving declaration names and the old fixed reader/API.
- Extend the existing opt-in public facade with generic document laws and the
  escape correspondence. Tests and CLI entrypoints stay outside its closure.
- Transfer four independent review proofs with explicit attribution, including
  the concrete counterexample to the unclaimed whole-document converse.
- Add `document_check.py`. Adjust the existing checker to authenticate and compile
  every public-facade dependency through the exact 30-source `FACADE.json` registry.
  Its original 143-theorem audit and semantic-control inventory remain separate.

Only four existing files change: `CssDerivation.lean`, `derivation_check.py`, and
two READMEs. Lake configuration, default CSS semantics sources, scalar/input APIs,
the main checker, and normative coverage registration are untouched. No new Lean
semantics, CSS feature coverage, or independent proof credit is claimed here.

## Fresh source-only verification

`verification/report.json` passes both installed checkers in isolated copies:

| Gate | Result |
| --- | --- |
| Existing first-order/JSON checker | 143 exact axiom audits, 13 rows in each of three runners, its nine original controls, enlarged-facade compilation and opt-in Lake build pass. |
| Document checker | 160 exact audits: 156 accepted declarations plus four attributed review declarations. All 25 actual-file rows and the accepted eight refusal/four semantic/three provenance controls pass. |
| New facade controls | Missing dependency, changed dependency bytes, authenticated unsupported import syntax, and excess registry entry all refuse with exact diagnostics. |
| Patch transport | Applied in an isolated base and compared byte-for-byte with every staged file; no new-path collision against canonical checkout. |
| Cleanup | All fresh build workspaces removed; no owned compiled caches remain. |

The semantic mutants run on exactly reverse-relocated accepted sources; separate
relocated compilation, audits, real-file execution, and Lake builds verify the
installed module layout. The four new facade controls are executable registration
checks, not formal semantic theorems. The two audit inventories overlap and must
not be summed as CSS coverage.

The actual default CSS build was not run by this lightweight capsule. Per root's
instruction, root owns that post-application gate using the canonical cache, plus
coverage registration, opt-in build, and an installed document CLI smoke check.
Author and independent fresh scoped replays suffice for semantic acceptance;
a third full installed checker pair is optional if review or changed sources
justify it. See `PLAN.md` for the exact handoff sequence.

## Freeze and provenance

- Source-only manifest: `e9ad5b48f5e47dae1ff8502b57bab17fdb32f83eaedddd5a3330db57c54ea832` (79 inputs).
- Integration patch: `8a64b3c4f04b45f21deb489a3446441226d0dd784fb4fa22d52f30351143a718`.
- Accepted origin: Firefox research commit `f3949d2992abdc02536b9a61e51dc7d603ce0868`.
- Canonical baseline: standalone commit `898fb45815c115362093116d81c09715ba94fcab`.

`ORIGINS.json` and `BASE.json` authenticate the Git source objects. The installed
transport records authenticate every source and reverse only exact import lines.
`origin/REVIEW-REPORT.md` and its pinned hashes preserve independent review credit.
`PATCH-CHECK.json` and `COLLISION-CHECK.json` record application checks.

`CANONICAL-STATE.json` and `CANONICAL-HANDOFF.json` verified the clean tracked
baseline and sole untracked `.DS_Store` before handing the patch to root. Finder
metadata remained byte-identical with SHA-256
`21e80780f65feb251cfd08d4faef1f230a97c6009b4454361ea58b3a2bf45498`.
The patch and cleanup contain no `.DS_Store` path. Root may now apply/commit the
canonical change independently of this frozen capsule.

```sh
python3 -B replay.py --lean /path/to/lean/bin/lean --out /new/report/path
```

Install `integration.patch` relative to the standalone library root. `overlay/`
is the exact changed/new file set; `base/` is only the scoped replay fixture and
must not be copied wholesale over the canonical repository.

The underlying claim boundaries remain unchanged: full definition-list iff,
accepted-document soundness, all-JSON escape-wrapper equivalence, and selected
canonical-use noncapture. No whole-program alias converse, all-raw-use-layout
claim, JSON text parser proof, native-link claim, or mechanical CSS prose
interpretation is introduced. The original Boundaries paragraph in the existing
derivation README describes its 143-audit milestone; the appended document section
introduces the scoped orchestration and singleton-weakening results. It should
not be read as retracting those newly integrated bounded results.
