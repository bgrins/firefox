# Disabled broader duration candidate V2

This prepares an experiment, not native acceptance. Only matching.rs is temporarily replaced with source proposal V2 c3b2ddf2. The executed one-file owner supplies exclusive source/app backup, `mach build binaries -j2`, process ownership, cancellation, and finally restoration. All 29 accepted payloads, accepted metadata absences, held provider, index flags, canonical controls, and original app are preserved by the existing guards. Resource floors and build timeout are unchanged.

The original-v2 capsule is pinned. Its runtime2 is still running at preparation: baseline binding, current controls, app metadata, and index flags remain null; both execution gates are false. Failed original runtime1 is not a baseline. Actual successful runtime2 must be frozen, fully replayed, and joined to freshly supplied current-state pins in a successor before execution. No live guards, browser, build, source, Git, or canonical writes were performed during preparation.

Candidate phases remain separate:

- Normative: exact 49 callbacks on 10 pages; four named improvement targets; all 45 control signatures and ten endings unchanged. Every originally passing signature stays unchanged. Both authored normative pages (eight callbacks) must pass.
- Reftest: exact one ending and no callbacks, with lifecycle, infrastructure, exit, and run-info checks; its original ending signature is preserved.
- Feedback: exact three callbacks and three owned JSON envelopes, eight samples each. Completion and acquisition are required; no numerical equality, finite-value, or convergence oracle is imposed. All sample fields remain available in the runtime.
- Restyle mochitest: runs on the candidate before restoration, reusing the original command and watchdog. Ordered 170 assertion signatures preserve 162 PASS and eight expected FAIL, plus one PASS ending and child exit zero. Missing expected means the observed status. Only the ending's validated elapsed-millisecond message/stack pair is normalized in addition to normal log transport timestamps/process identifiers; message, expectation presence, and other semantic fields remain exact.

Three WPT phases share the same candidate app metadata and complete state snapshot. The restyle phase verifies that same app. The outer result is written after restoration and reports each phase separately. Original raw streams and assessments remain immutable. The separate inactive/reactivation probe is not included in this capsule; a successor can add it after its original observation.

`candidate.py.diff` and `baseline.py.diff` compare the executed small duration owner; `comparison.py.diff` replaces its one-phase replay with three complete original replays; WPT and assessor diffs compare original-v2. `phases.py` and `restyles.py` are the small new phase orchestration and mochitest adapter. No browser frames or native source copies are duplicated.

Saved-only check: `/Users/bgrins/venvs/firefox/bin/python -I -S -B artifacts/css-contextual-duration-broader-candidate-v2/candidate.py --check <FILES.sha256>`.

Future root-only execution uses the same command with `--run`, but this disabled capsule deliberately cannot execute. Broader feedback safety and native acceptance remain unresolved.
