# Column runtime driver delta review

Verdict: **GO for the bounded reversible experiment** on draft `88cb92504c508a51837d5ce9d7c2957fe9d500d41e0071334d369cf56ed7b9ee`. No must-fix blocker found. This is source review, not runtime or native acceptance.

Authenticated 41 draft payloads and all 16 cost-v4 payloads under externally supplied manifest `f979247dcb21cbe442ef246792fed70c24840cd919faf2afc482d2adce792d98`. All six copied execution inputs match that cost capsule. Exact observed hashes are retained in CHECKS.json.

## Native and WPT roles

The two added native targets, PresShell.cpp and nsTableFrame.cpp, appear in both the 23-file write/restoration roster and the 28-file guard roster. Preparation checks their selected before snapshots against the requested post-signing HEAD, along with the flex and absolute baselines. Each normal phase explicitly reinstalls the before snapshots; the sole trace phase installs the two trace snapshots. Existing per-phase source checks and final original-byte restoration therefore include both additions.

The run now performs baseline/both on seven files with 66 exact subtests, plus an optional both-column trace on two files with 16 exact subtests. Original-key and previous OOF trace repetitions are intentionally absent. The unchanged WPT wrapper requires exact ordered names, complete OK file ends, one suite end and stable resource/source/binary pins while preserving actual FAIL outcomes.

The eight new ordinary-block/table-width cases compare visible and hidden selected-frame rectangles after an outer-only flush. Visible reference and outer-flush calibration assertions precede target assertions. Separate col/colgroup and td/table controls retain the unresolved boundary; there is no relaxed column oracle or filtering of failed cases.

## Trace scope

PresShell instrumentation logs the queried table/column/group frame, its two dirty bits and immediate table provider before the existing dirty-eligibility early return. The table instrumentation logs column/group rectangles after the real SetRect operations. Diffs contain observations without changing the gate or publication arithmetic. Provider pointers are guarded before dereference.

This is the useful missing observation seam, but merely counting QUERY/PUBLISH lines does not establish causality. Runtime review must join actual process/frame identities and event order, distinguish table queries from column queries, and avoid treating reused pointers or unrelated publication as a matched recovery. No publication/query proof is inferred before execution.

## Cost and cleanup

Both normal phases use the same controlled child environment: disable the safe-mode key and early update processing, remove inherited safe-mode restart, and record the inherited-presence bit. The parent requires matching STARTUP-ENV, SPAWN and RESULT receipts. The environment adjustment is confined to the direct cost child; no global setting or installed-profile change occurs.

The parent retains exact source/binary/six-input joins, reauthentication, original-group terminal/no-live-member checks, empty cleanup-error lists and actual profile absence. It additionally checks raw persisted progress sequence/count and, for successful measurements, the exact 220-event script/config/start/batch/result roster. Incomplete measurements may continue only after stable identities and verified cleanup; they remain incomplete. Missing receipts, drift or cleanup ambiguity abort into restoration.

The optional traces receive no timing run. Progress awaits occur outside individual measured timing buckets but can perturb scheduling/cache state; only the same instrumented baseline/both fixture is comparable. Fixed phase order, coarse timers, full-geometry mismatches and original-group-only cleanup limits remain disclosed. The 13 synthetic hook controls are producer evidence, not an independently executed browser test.

No reviewer browser, compiler, build, source or Git mutation occurred. Preparation must bind the actual current HEAD and empty index; successful future restoration and all runtime outcomes require their own review.
