# Registered-number clean-HEAD WPT comparison

This immutable capsule serves the exact sealed fixture from `css-registered-number-wpt-fixture-v2` in both original and candidate phases: **58 target assertions, 446 unchanged regression assertions and six reftests** across 22 pages. Four reference documents and all recorded resource/header/metadata inputs are captured. Every payload of the fixture package, including its independent review and oracle notes, is authenticated by `REFERENCES.json`. The disputed self-font numeric-division page is excluded from the manifest and acceptance gate.

The three original/candidate native source roles come from the sealed committed-HEAD preparation proposal plus its sealed collector. This compares the ordinary committed implementation, not the pending-demand overlay. Both phases require `registered_number_transition` with the matching role, `variant: committed-head`, and `compiled: true`. There is no inherited raw-attribute compilation exception. Native source hashes must also match the supplied epoch and live bytes; built binary hashes must match the same epoch. Source proposals and full fixture inputs are independently pinned.

The runner retains the prior capsule's full preservation, source/index/nested-repository checks, externally supplied epoch SHA, phase-specific application.ini symlink/identity/content and actual WPT BuildID binding, stable run_info equality, genuine WPT manifest, owned profile/process lifecycle and cleanup. Only the independently bound BuildID may differ across phases. The epoch HEAD must remain identical. Runtime run.py is identical to capsule-v1. Its changes from the raw-attribute runner were confined to the registered-number compilation gate and owned output prefix; inspect `ORIGINAL-RUNNER-DELTA.patch`.

The live new registered-number WPT file must remain absent during both phases. Accepted raw attr-cycle, raw-nested and used-fallback WPT files must remain installed at their pinned bytes. Both phases serve the same captured inputs. No metadata is changed. The original wrapper accepts a complete WPT failure as an observation, recording its actual child exit. Candidate requires all 58 target assertions to pass and an exact regression outcome/expectation/intermittent signature match. Unchanged baseline regression failures may remain in that signature; reviewers must report them explicitly before deciding acceptance. A green wrapper is not a substitute for inspecting raw outcomes.

From the repository root, after the main agent completes and pins each native build:

```sh
python3 -I -S -B artifacts/css-registered-number-wpt-capsule-v2/run.py CAPSULE_SHA original-1 ABSOLUTE_EPOCH_PATH EPOCH_SHA /Users/bgrins/code/firefox/artifacts/css-registered-number-wpt-runtime-original-1
python3 -I -S -B artifacts/css-registered-number-wpt-capsule-v2/run.py CAPSULE_SHA candidate-1 ABSOLUTE_EPOCH_PATH EPOCH_SHA /Users/bgrins/code/firefox/artifacts/css-registered-number-wpt-runtime-candidate-1 /Users/bgrins/code/firefox/artifacts/css-registered-number-wpt-runtime-original-1/ASSESSMENT.json ORIGINAL_ASSESSMENT_SHA
```

Replace the capitalized arguments with externally verified values. Each output must be absent. Redirect the outer invocation output to a separately owned artifact log and retain actual outer session/terminal exits. Do not overwrite a failed run or reuse its phase output directory; use the next phase suffix if a repeat is needed. A source or fixture change requires a new immutable capsule and matching original observation.

Static checks cover genuine manifest loading and identical regeneration, all captured origins and absence roles, all proposal/fixture hashes, assessment negative controls for every target, unchanged regression signatures, BuildID/revision mismatches, fourteen bad phase transitions and two stale epoch failures. The stale-epoch test stubs only capsule authentication to reach the real epoch digest check and prevents live metadata access; it launches no process. Application metadata tests operate on temporary files. No browser or build was run in preparing this capsule.

Version2 adds six noncyclic admitted-AST gates before either original or candidate browser run. Runtime run.py is byte-identical to capsule-v1; source roles are unchanged. All 21 regression manifest entries are unchanged. This version separately binds the expanded fixture review.
