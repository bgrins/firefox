# Untracked-file audit — 28 October 2026

**No unexpected CSS project paths or changed recorded project bodies were found.** The uncollapsed root inventory contains 565 untracked files. Repeating the requested read-only command produced the identical list.

| Scope | Untracked files | Finding |
|---|---:|---|
| CSS native prototype companions |15|Exact canonical `untracked_native` list; all recorded hashes and identities match where pinned.|
| CSS WPT files |55|53 match committed recovery records; two match the separately recorded random-WPT installation, including their owned identities.|
| `.claude/` |5|Names only; contents and provenance not inspected.|
| `browser/base/content/tabcanvas/` |183|182 under `node_modules`, one under `test-results`; names only.|
| `claude-docker/` |286|Names only; contents and provenance not inspected.|
| `perf-lab/` |20|Names only; contents and provenance not inspected.|
| `test-results/` |1|Names only; contents and provenance not inspected.|
| **Total** |**565**|70 project files plus 495 paths in the known unrelated directory groups.|

The 75-entry [committed recovery inventory](../css-worktree-recovery-20261028-v1/SOURCE-PINS.json) exactly matches its blob at signed HEAD `6a6e0da75589378b38f5a1da27a68afd9cb64080`. All 75 current project bodies, sizes and modes match that inventory. Seven are currently tracked: the held custom-properties source and six accepted page-fix WPTs. The latter were untracked when recovery was captured; their historical `tracked:false` flags do not describe the current index. The remaining 68 recovery entries plus the [two random WPT installations](../css-random-counter-wpt-install-v1/INSTALLED.json) account for all 70 current CSS project untracked paths, with no missing or extra path.

The signed canonical epoch records 15 untracked native companions, not 12. Its 22 present pins among the 70 untracked project files all match; all present canonical identities match too. Files without a canonical live-path pin are accounted for by the separate recovery/installation records rather than being silently treated as canonical matches.

The nested CSS Lean repository reports only `?? .DS_Store`; no tracked or staged change is reported there. That file was not opened or hashed. Unrelated directory membership is a name-based classification, not an assertion that their unknown contents are safe or disposable.

[inventory.json](inventory.json) retains every uncollapsed path, project-only hashes/identities and exact classification joins. No unrelated file contents or secrets were read, and no unrelated hashes were computed. Nothing was deleted, moved, staged or edited outside this new audit artifact. Commands used `--no-optional-locks` and disabled fsmonitor. This is a scoped untracked inventory audit, not a substitute for the separate whole-epoch guard-drift investigation.
