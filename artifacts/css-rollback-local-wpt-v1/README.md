# Local rollback comparison

Prepared only; no browser or native build was run. This stages the exact retained A16+B16+D48 fixtures and testharness resources from `css-rollback-cutoff-e86-rebase-v1`. The live untracked WPT pages and real manifests are untouched. The D fixture has 48 callbacks; its 16 C-boundary callbacks remain in the predecessor artifact.

`staged/wptrunner.ini` is the prepared private configuration. `MANIFEST.json` lists exactly three testharness pages; the private Mozilla manifest is empty. Each execution creates another private fixture/metadata root in its fresh output directory. The copied server configuration uses automatic ports. The tools directory is a symlink to the local WPT tools, and existing testing profiles supply preferences. This is not a hermetic Python/harness environment.

```python
run(root: Path, output: Path, pins: dict, cancelled: Callable[[], bool]) -> dict
active_processes() -> tuple[int, ...]
```

Import with `python3 -I -S -B`, without optimization. The caller supplies a fresh binding:

```json
{
  "execution_enabled": true,
  "source_role": "baseline",
  "binary": "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox",
  "build_revision": "40-character revision associated with the completed build",
  "harness_revision": "40-character current HEAD revision",
  "files": {
    "root-relative input path": "SHA256"
  }
}
```

The file map must include the binary, sibling XUL, `Contents/Resources/application.ini`, and every source path in `SOURCE-ROLES.json`. The source role selects exact baseline or A+B+D candidate hashes; unchanged `stylist.rs` excludes the held C implementation. Include any other source/library pins needed to bind the completed build. The runner records and checks the supplied association; it does not prove source-to-binary provenance or build the application.

The CLI takes `--pins`, a fresh `--output` beneath the repository's artifacts directory, and explicit `--execute`. It installs SIGINT/SIGTERM cancellation handlers. An importing owner supplies its own cancellation callback. Root owns all actual execution, source changes and builds.

All three pages run once, headlessly with one process and an external 180-second deadline. `layout.css.revert-rule.enabled=true` is explicit, so the probe is valid even if a release-style build disables that preference. This does not establish release-default exposure. No test metadata changes expected failures into passes. The earlier rollback invocations relied on profile/build defaults; the pref is explicit here.

`EXPECTED.json` names all 80 callbacks. Assessment requires each once, one start/end per page, successful page harness completion, a complete suite lifecycle and valid raw JSON. Baseline assertion failures can be complete observations; `all_pass` remains false. CLI exit zero means a complete observation, not all tests passed. The native-fix acceptance field remains false even for 80 passes: comparison and regression acceptance belong to the owner.

Raw events, complete stdout/stderr, command, source/application pins, application metadata bytes, process-group identity, cleanup, post-run preservation and assessments remain in the output directory. Cleanup targets only the process group created by this runner. A failed group cleanup leaves `active_processes()` nonempty. Temporary profiles are removed only after group absence and directory-identity checks. Source/application hashes, HEAD and index semantics are checked before and after execution; this module never writes Git state.

Only `prepare_inputs`, `read_events` and owned-process cleanup are imported from the pinned font-runner helper dependencies. No signing, build, capture, restoration or old authorization entry point is called. `FILES.json` pins this prepared package; `CHECK.json` records browser-free validation.

After the A+B+D baseline/candidate comparison, the retained regression set is `inline-style-revert-layer-crash.html`, `revert-rule-basic.html`, `revert-rule-custom-property.html` and `revert-rule-cycle.tentative.html`. The last had two unchanged failures in historical runs and belongs to the unresolved stronger-rule/cycle policy. These controls are not silently included in this 80-callback lane; stage and assess them separately before accepting the repair. Do not run C's additional 108 callbacks as a prerequisite for this comparison.
