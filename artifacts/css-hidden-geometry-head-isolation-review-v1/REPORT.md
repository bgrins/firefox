# Exact-HEAD hidden-geometry isolation driver review

## Final prepared checkpoint

**READY for root-owned reversible execution of the final pinned driver.** Root read the corrected driver and approved the recovery/roster guards. `FINAL-PREFLIGHT.json` binds HEAD dbfb428e2134fff1a4ef73f48438481b4eb6438f and the empty index. The 20 original/live and 20 HEAD source snapshots remain unchanged; all 43 payload pins authenticate. The precise 20-file dirty native roster also still matches. `final-prepared/` retains the executable input bytes.

The final INPUTS sets both historical `staged_paths` and operative `expected_staged_paths` to zero. Earlier checkpoints below describe the superseded pre-signing inputs. No driver, build, browser or fault-injection execution was performed by this reviewer; the readiness judgment is source review plus syntax/pin/role checks. The correction itself was implemented by this reviewer and separately read by root. Actual experiment/restoration outcomes remain future evidence.

## Correction checkpoint

The requested artifact-only corrections are implemented. `CORRECTION.json`, `correction.patch` and `corrected-awaiting-head/` pin the revised source. Both scripts parse, but the reviewer has not executed the driver or fault-injection tests. All HEAD/index/old staged-count pins remain unchanged pending root's signing result. The new `expected_staged_paths` field is explicitly zero and required by preflight; the historical `staged_paths: 229` field is retained but no longer used as the execution gate. **Execution remains pending final root pins/review.**

Recovery uses authenticated originals preloaded before any mutation, attempts every write independently (including a missing live file), attempts rebuild despite failed restoration receipts or log-open failure, and attempts final verification. Failures are accumulated in `recovery_errors` and force terminal failure. Primary build/probe failures also force failure after cleanup. A persistent write error can still leave a file unrestored; this is reported rather than claimed recoverable.

Result validation now requires each of the 32 boolean/API configurations exactly once, five ordered phases and finite numeric response shapes for all three repeated reads. Empty/multiple client rectangles remain valid diagnostic responses. The runner now derives its source roster from authenticated INPUTS plus five fixed source paths declared in the pinned script; it no longer reads an external standalone receipt. INPUTS itself is hashed before/after the probe.

Initial verdict: **HOLD pending restoration and evidence guards**. This is a source-only review; the reviewer did not execute the driver, browser, build or any Git mutation.

The initial complete inputs are retained under `initial/`. All 43 supplied pins authenticate; both Python entrypoints parse. Their pre-import isolated/no-site/nonoptimized guards are correctly placed. The two repository-root calculations resolve correctly, and the probe writes the same `case/project/RESULT.json` path that the parent consumes. Fresh output and BEFORE paths were absent.

Independent read-only Git checks establish all 20 original snapshots equal the live files, all 20 HEAD snapshots equal `git show HEAD:path`, and the complete modified native roster in layout/dom/servo equals INPUTS. The staged diff and index entry digests match; HEAD is 99a9ca84f08370c1797720db8688bcb3747f6985 and the staged roster contains 229 paths. `SOURCE-ROLE-CHECK.json` retains the results. The runner's source roster currently includes all 20 files.

## Required corrections

1. Restoration must continue after an individual missing/unreadable live file or a state-log write error. The initial finally block writes STATE before restoring, then reads each live file without a guard; either failure can skip remaining restorations and the rebuild. Attempt all restores, collect failures, attempt rebuild and final checks, and fail explicitly if recovery is incomplete. A removed source should be rewritten from its retained original snapshot.
2. Validate the exact 32 unique configuration keys and five ordered phases per row, and numeric result shapes, before reporting the number of bad stages. `len(rows) == 32` alone admits duplicate keys or truncated stage arrays. Geometry discrepancies remain diagnostic and must not prevent restoration.
3. Pin the external standalone FINAL.json used to discover the runner's source roster, or embed its exact roster in authenticated INPUTS. The initial 43 pins do not bind this transitive input.

`INITIAL-REVIEW.json` records these findings. This review is not permission to execute an altered driver whose new bytes have not been checked.

## Interpretation and recovery limits

This experiment separates the complete dirty tracked native set from HEAD. That set contains accepted pending repairs as well as unaccepted prototypes. A changed outcome would not identify a particular fix. The source experiment also does not isolate every frontend/configuration difference from installed Firefox 158.

Numerical outcome counts are diagnostic; a complete valid POST is the probe-completion gate. Browser exit after deliberate termination is not itself success evidence. Ordinary exceptions should trigger cleanup, but process kill, machine loss or persistent filesystem failure still require recovery from retained snapshots. No Python finally can guarantee restoration under those conditions. The driver must never reset, stage or overwrite the user's index.
