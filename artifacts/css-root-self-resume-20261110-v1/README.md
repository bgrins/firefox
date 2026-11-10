# Root identity during animation-value computation

The animation context builds a derived style whose root-element flag defaults to false. Root font-size and line-height computations therefore use the current root metrics where CSS Values requires initial metrics to avoid self-reference. The repair supplies the actual target identity at all four animation-context callers and excludes pseudo-elements where those callers accept them.

The production unit is one Rust file and four WPT resources: two runnable pages and two SVG supports. It contains no dependency-drain or producer-handoff change. The source preimage at `4bd6f28f6e65803827cb00c9ea2e565d9a5b26f5` still matches the previously tested preimage exactly. `source-selection.json` pins the five candidate files and `source.patch` contains the Rust delta.

## Retained native evidence

On November 10, the existing saved-evidence verifier was rerun successfully. It authenticated 122 references, joined the original and candidate builds, replayed all 18 raw WPT streams, checked the historical restoration records, and rejected six altered evidence controls. Its output is `saved-evidence-check.json`; this was a read-only historical evidence check, not a new browser run or a current application-restoration claim.

The archived comparison used Firefox revision `a6f39620516a4cf76a5dbf5208960adc79068cf1`. It changed 120 PASS / 9 FAIL to 129 PASS, preserving all prior passing signatures and all 12 OK harness endings. Seven improvements belong to the root animation page and two to the SMIL page. Child, pseudo-element and literal controls are retained. These nine assertions describe one root-identity repair, not nine independent bugs.

The 18 original raw streams and both build result records are copied under `historical/`. Run `python3 check.py` to verify their fingerprints, exact source-role hashes, callback identities, aggregate results and preservation of passing signatures. This compact checker does not reproduce the older full restoration audit or prove that a reported build executed the claimed source; the original audit and the freshly rechecked record provide that separate evidence.

The two proposed WPT pages were also run against the current branch's existing browser on November 10. They reproduced the same nine failures, with twelve passing subtests and both harness endings OK. All three binary/application fingerprints matched the recorded #164 build, and the Rust source retained its original hash. `baseline-result.json`, `baseline-raw.jsonl` and `baseline-wpt.log` record this fresh baseline; candidate validation follows installation of the source fix.

## Boundaries and continuation

The current stack contains the earlier font-membership and cancellation repairs. The root-identity delta is separate from them, but its historical browser result is not an isolated current-upstream validation. Direct internal AnimationValue and Inspector callers have source review rather than direct browser regression coverage. No whole-animation convergence or native refinement proof is claimed.

The older publisher requires a research commit directly after the historical `a6f396` revision and cannot be used on the current branch. This continuation preserves that publisher and its failed-signing history. It uses explicit path staging on the current clean tracked tree, configured signing, and a research predecessor followed by the five-file native commit. It does not rewrite signed history or change the private IPC project.

The producer-only comparison mentioned as missing in the earlier roadmap is already complete: A and B both had 137 PASS / 27 FAIL; the combined producer-and-drain candidate had 164 PASS. The later broad-handoff trace identifies productive normal readmission and repeated changed-property requeue for the historical stalled combination. Those results supersede the old missing-middle plan. Keep #160 held for review of the combined mechanism and its remaining convergence assumptions; do not rerun either completed experiment.

## Fresh upstream and build checks

Installed Nightly 162.0a1 (application metadata BuildID 20261109214446) reproduced exactly the local baseline's 12 PASS / 9 FAIL and two OK endings on the two proposed pages. The installed application's executable, XUL and application.ini hashes were unchanged across this run. This establishes exposure in that installed Nightly, not a release-channel claim. See installed-nightly-before.json and installed-nightly-result.json.

The source delta also applies without fuzz to glue.rs from Searchfox-indexed Firefox revision 47f2a88cbab9072c8f8f156494b92d6891e488fb. upstream-application.json records that source-only check; no isolated upstream build was performed.

The current local candidate completed mach build binaries -j6 successfully. The first two-job attempt was deliberately interrupted to increase concurrency, after checking its owned process group. Both logs retain a Mach progress reporter KeyError for the export tier; the final native build exited zero. build-result.json records source and installed binary hashes. The spec-derivation research commit was made during the build and changed no native inputs. The candidate root-identity source remained uncommitted during compilation.

## Candidate browser validation

The freshly built local browser passed all 47 subtests across five pages, with five OK harness endings. The two matched target pages changed 12 PASS / 9 FAIL to 21 PASS, preserving every prior pass. The other 26 passing assertions are existing root-font invalidation and cancellation/depth controls; those three pages did not receive a fresh baseline run in this continuation. Binary and all five delivery-file hashes matched build-result.json after execution. See candidate-result.json and candidate-raw.jsonl. Scoped WPT lint and configured Rustfmt both exited zero.
