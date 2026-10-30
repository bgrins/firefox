# Next standalone repair: language-sensitive line breaking

Recommendation: validate the final language candidate2 next. It is a smaller independent repair than hyphenation ownership: one native file and two existing WPTs, without a continuation-range rewrite. This is an artifact-only readiness review, separate from the current nowrap publication and V98. No native source, app, index, epoch, browser or Git state was changed. This capsule does not establish native acceptance.

| Candidate | Latest frozen nowrap pair, both roles | Historical corrected candidate | Smallest sound publication payload |
|---|---|---|---|
| Language-sensitive partitions | 331 PASS / 29 FAIL across 360 callbacks | 360 PASS; independent native/source review approved candidate2 | `dom/base/nsLineBreaker.cpp` plus the Latin-1 and text-partition WPTs below |
| Hyphenation limit ownership | 235 PASS / 54 FAIL in the 289-case ownership page; 19 dynamic and four pseudo controls PASS | Candidate4 retained ownership improvements and restored four pseudo controls; combined 19-page run had 720 passing subtests plus two passing reftests | Three native files plus ownership, dynamic and pseudo WPTs; use candidate4, never candidate1–3 |

These current counts were independently derived from the frozen nowrap runtime assessments, authenticated against runtime manifest `f4bb8776…`. They are unchanged between that pair's original and nowrap candidate. Historical language regression tests were candidate-only, and neither historical language nor ownership result was an isolated build of the final standalone patch. They therefore support choosing the next trial, not skipping it.

## Exact language payload and rebase

* `dom/base/nsLineBreaker.cpp`: exact nowrap preimage `a87f4210…` → proposed `7f6cf033f87adba635bfc4190e60d1f4d11a263e6f30ea5283ad8a49597d7fc9`.
* `testing/web-platform/tests/css/css-text/line-break/line-break-language-text-partitions.html`: unchanged `66845fdb…`, 324 callbacks.
* `testing/web-platform/tests/css/css-text/line-break/line-break-language-latin1-partitions.html`: unchanged `0b304a72…`, 36 callbacks.

`fix.patch` is the three-file proposed patch (`c815b801…`). Test copies are exact historical bytes, not newly authored tests. `rebase.py` applied all six language native hunks with exact ordered context, reproduced the historical standalone postimage `441570e5…`, and verified that language-after-nowrap equals nowrap-after-language byte for byte. Reversing the language change restores exact `a87f4210…`; all nowrap suppression changes survive. Configured formatting, build and browser validation of this new composition are still pending. No claim is made about a future committed HEAD.

The initial rebase check rejected a context shared by the UTF-16 and Latin-1 methods before writing any source copies. The final checker respects ordered unified hunks, uniquely locating the later byte-path contribution after the preceding hunk. `REBASE.log` preserves that checker failure; `REBASE-FINAL.log` records successful `bb5423/0`. No whitespace matching or discarded context is used.

## Why the language change is bounded

Immediate words currently use the previous buffered word's cached script flag. Candidate2 resolves the current contribution's language at both immediate provider calls and updates both Latin-1 buffering paths. The shared one-entry locale cache retains the existing shutdown/ownership pattern. Buffered delimiter-only contributions do not steal the preceding word's language. Candidate1's missing Latin-1 updates were a substantive defect, found and corrected before the retained candidate2 review; omitting the 36-case byte-path test would lose that protection.

The oracle uses uniformly labeled words, explicit language, loaded mplus, normal wrapping, and specified punctuation rules. Chinese/Japanese tailoring permits the tested punctuation breaks only in the specified strictness modes; the same word's preceding language or transparent DOM partition must not replace its own language. The current [CSS Text 3 line-break rules](https://drafts.csswg.org/css-text-3/#line-break-property) still supply that guarded distinction. This does not assert a normative policy for genuinely mixed-language words or unknown tags.

## Remaining gate and proof disposition

The next useful gate is a fresh isolated original/candidate pair after nowrap publication: authenticate the actual current source as `a87f4210…`, format the proposed delta, build both roles at the same HEAD, and run the existing 22-page resource closure. Reclassify the two language pages as the 360 targets; preserve the other 529 callback signatures and all 22 endings, including all 169 nowrap passes, the 54 ordinary ownership failures, and dynamic/pseudo controls. Require all 360 target callbacks to PASS. Preserve per-role build metadata and only the already reviewed, manifest/startup-bound reftest-port equivalence. Do not assume an old all-PASS regression count. Reuse exact tests, preferences and resources; run genuine installed manifest/lint checks before committing the two existing untracked tests by verified adoption.

The broad formal dossier has real unfinished statements: native caller-to-model admission, LF consumer equivalence, storage freshness, and failure/provider connections. Its unrestricted raw partition claim is actually false on retained LF/nowrap inputs; absence of a proof must not be confused with proving that claim. Those are substantive limits of the broad theorem, but they are not demonstrated regressions introduced by this language patch. They need not be completed to land this narrower observed language repair with source review and a fresh paired gate. Preserve the original full-scope research status instead of declaring it solved.

One concrete separate caller issue remains: implicit and explicit language flags can differ while sharing the same language atom and text run, and the first flow's flag then governs later flows. The saved native witness is real; its browser proposal remains unexecuted. Candidate2 does not repair that upstream admission issue. Keep it as a separate follow-up, not a new claim credited to the 29-case repair or a premise silently assumed true globally.

For ownership, broad font/dictionary/whole-consumer proofs likewise need not hold an otherwise sound local repair indefinitely. Its continuation coverage, two endpoint clamps, per-range sink offset, empty-range finalization, and first-nonempty suppression are substantive local correctness requirements: candidates1–3 actually missed some, including a four-case PASS→FAIL pseudo regression. Candidate4's reviewed correction retains them. Its next gate should be an exact current rebase and paired ownership/pseudo/dynamic validation with real dictionary calibration, not completion of all layout proofs. The [CSS Text 4 character-limit rule](https://drafts.csswg.org/css-text-4/#hyphenate-char-limits) supplies the uniformly styled seven-character-word prohibition; arbitrary mixed-style policy, supplementary dictionary completeness and whole mutable-cache semantics remain distinct research limits.
