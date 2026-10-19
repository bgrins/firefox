# Final parser depth-recovery native/browser review

**Accepted: candidate native/browser gate.** Formal acceptance remains a separate gate. This additive review preserves the earlier independent normative/source assessment and does not repeat or broaden its universal proof claims. Review date: 2026-10-19.

## Exact source and vendor checksum

The candidate parser SHA `2ac2c7f820ff5095c705446ff8a0f31507affe08e68bf6cc3735d5fb5bc38788` is exactly the previously reviewed one-line insertion: consume the rejected block with the existing iterative helper before returning `TooManyNestedBlocks`. Reconstructing the whole candidate from the original establishes that there are no other parser changes. The earlier independent FREEZE/MANIFEST/report identities are retained and checked.

The vendored `.cargo-checksum.json` changes only `files["src/parser.rs"]`, from the exact original parser hash to the exact candidate hash. Its package field, file roster and every other file digest remain identical. This checksum update is necessary vendor bookkeeping, not another semantic repair.

## Final WPT oracle

I read the entire combined 22-case WPT. It preserves all twenty earlier cases across inline/stylesheet, padding-left/width, depths 1/74/75/76 and truly external blue-declaration controls. It adds two deep-value-followed-by-green cases. The new controls check that cleanup also resumes at a genuine following declaration; they pass both before and after this repair.

All 22 names, expected colors and original/candidate status predictions are independently enumerated in `ORACLE.json`. The deciding failure remains inline padding-left at depth 76: blue occurs inside the still-open outer function and cannot become an outer declaration. Expected red follows the preceding explicit declaration and does not require support for the deep invalid calculation. The green controls have a semicolon after the actual outer closer, so green is an external declaration. Existing UA-limit and error-handling analysis remains in the retained prior review; these controls do not enlarge the claimed supported math depth.

Elements/styles are removed by per-test cleanup. The cases are synchronous and reuse the target ID only after cleanup. No layout measurement, font availability, timing threshold or malformed reference parser is involved.

## Raw paired results

The independent checker parses raw JSONL, rejects duplicate outcome keys, verifies summary/raw/console hashes and compares all outcomes by identity rather than execution order:

- New WPT: **1 FAIL / 21 PASS → 22 PASS**, both harnesses OK.
- Exactly one changed key: inline padding-left with 76 nested functions.
- All **46 other outcomes** remain identical, including prior endpoint controls and syntax/nesting regression files.
- Across **69 total outcome records**, 68 are unchanged. Baseline exits 1; candidate exits 0.

Within each run, before/after source/configuration/binary pin records match. Across runs, the only fixed-input changes are the parser and its vendor checksum. The WPT bytes are identical and bound to both runs. The retained root `PAIR-RESULT.json` agrees with the independently computed result.

## Build and formatting evidence

Three retained phases all exit zero, with every phase log hash checked: offline cssparser cleanup, forced Rust library rebuild, then binaries link. The Rust log explicitly recompiles cssparser and style; the link log names XUL. Build fixed inputs remain unchanged, build-before binaries equal baseline browser binaries, and build-after binaries equal candidate browser binaries. Both Firefox and XUL hashes change. Thus the final browser evidence is bound to the intended rebuilt candidate, not merely a source-file edit.

Rustfmt output and WPT lint records are retained; lint reports zero problems. The Mach performance-environment notice does not represent a test or lint failure. No browser, Mach, Git, live source or WPT mutation was performed by this reviewer.

## Scope and replay

This closes the final local native/browser binding gate. It is shared-tree local evidence, not an isolated upstream build or performance result. Root's standalone three-file patch packaging remains its own check. The producer's new formal artifact has not been independently accepted by this final browser review.

Authenticate the manifest/checker with the handoff hashes, then:

```
python3 -I -S -B artifacts/css-parser-depth-recovery-final-review-v1/check.py --manifest <manifest-sha256>
```

Commit exactly all manifest entries plus `MANIFEST.json` and `FREEZE.json`. No built binary or Rust library is included.
