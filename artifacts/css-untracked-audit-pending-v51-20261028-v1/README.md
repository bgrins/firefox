# Worktree audit, 28 October 2026

At HEAD `3bee146c52cda774f5e3796b5ec3f2c8ce5a686d`, the complete untracked list matches the saved 563-path baseline. No unexpected or missing names were found.

| Files | Count | Verification |
|---|---:|---|
| CSS WPT prototypes | 53 | Live contents, size, mode and filesystem identity match the saved inventory; contents match recovery copies in current signed HEAD. |
| Native and test-tool prototypes | 15 | Same checks as the WPT prototypes. |
| Other existing work | 495 | Names match; lstat metadata compared with the preceding inventory. Contents were not inspected. |
| **Total** | **563** | No unexpected paths or unsaved CSS project bodies. |

Other existing work consists of 286 paths under `claude-docker`, 183 under `browser/base/content/tabcanvas`, 20 under `perf-lab`, five under `.claude`, and one under `test-results`. No metadata changes were found. This does not certify those files' contents or identify them as disposable.

All 68 live project prototypes remain untracked, but identical recovery copies are already committed. These are unfinished experiments, not additional accepted fixes. Nothing was removed or staged by this audit.

The nested CSS Lean repository has only its previously recorded untracked `.DS_Store`. The sole unstaged tracked change is the held `custom_properties.rs` provider prototype, matching its recorded hash. The 233 staged research files match the saved failed-signing selection in both the index and working tree. Current HEAD and recovery commit signatures verify successfully.

The full machine-readable census and comparison are in [inventory.json](inventory.json). The actual audit completed with exit 0; the script only reads repository state and emits JSON. It makes no source, index, ref or runtime-control changes.

## Work and commit status

All **145 accepted native fixes** and **two test-only repairs** are committed locally. [The complete grouped table](../css-all-work-readout-20261028-v6/README.md) lists their commit hashes, research commits and dependency caveats.

| Additional work | State |
|---|---|
| Original Bloom milestones 1–6 | Completed within their declared profiles and assumptions; committed. |
| Canonical CSS Lean library | Committed; last recorded full check: 11,840 declarations, 12,438 executable cases, 173 false controls, 2,155 source fingerprints. These are inventory counts, not a percentage of CSS. |
| moveBefore old-parent invalidation candidate | Paired browser test: 21 failed callbacks repaired, 19 passing controls preserved, candidate 70/70 PASS. Research is in the 233-file staged checkpoint. Native installation/acceptance remains pending. |
| Cross-parent move model | Nine checked declarations and two rejected false controls; included in the staged checkpoint. |
| Same-parent reorder model | Eleven checked declarations and two rejected false controls; sealed and reviewed, not yet committed. |
| Signing recovery and this audit | Prepared locally; not yet committed. |
| Held provider and other live prototypes | Unaccepted; recovery copies committed, live working files retained. |

The pending research commit failed with `1Password: failed to fill whole buffer`. Its exact staging is retained for a signing retry; this audit did not retry signing. The moveBefore candidate is one defect family, not 21 independently counted bugs. Neither move model proves native Gecko refinement or increases the canonical CSS library totals.
