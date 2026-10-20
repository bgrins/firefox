# H1/H2 v2 root review

Verdict: HOLD on the original full machine/caller scope. The 162 audited results and all retained native/model comparisons pass a fresh root replay. No unsound Lean theorem was found. The current complete caller theorem does not yet supply all executed native arithmetic bounds.

## Authenticated inputs and replay

SOURCE-AUTHENTICATION.json verifies all 417 files, 29 directories and supplied outer/checker/report hashes. replay-v1 is a fresh terminal-success run: 14 modules, 162 audits, four times 2,224 native cases, 4,448 axis observations, 2,224 absolute-rectangle observations, 11,898 endpoint observations and 38 direct helper cases. All 13 native mutations and six Lean mutations retain their required distinctions. Standard Lean axioms only. The producer pins tool executables; standard libraries/SDK/compiler/runtime and source interpretation remain trusted as documented.

The prior review's R1 rectangle operation gap is substantively addressed in StickyAbsolute: actual FromRect overflow handling, both axes, intersection cross-axis zeroing, empty/clamp branches, discarded edge writes and temporary MoveBy arithmetic. The new endpoint branch expressions retain strictness, truthiness and optional defaults. This is stronger than the v1 subset. Those improvements do not resolve the caller gap below.

## R3: both coordinates execute before axis selection

StickyEndpointCaller.complete_machine_axis_caller maps Frame2 through project before EntrySafe. Its range and shift admissions inspect only the requested coordinate. In the extracted source, GetStickyScrollRangesForAxis calls ComputeStickyLimits for the whole rectangle when the requested axis is active. ComputeStickyDisplacement also subtracts complete nsPoints before selecting shift.x or shift.y. Therefore the other coordinate can overflow despite every stated chosen-axis premise holding.

CrossAxisChallenges.lean supplies three kernel-decided witnesses, with only propext reported:

1. Chosen x EntrySafe and CallerSafe hold while currentY minus normalY is outside signed32.
2. The same premises hold while the unselected y normalization expression is unsafe.
3. The unselected y normalization remains unsafe with its scrollport and both explicit insets inside the ordinary coordinate range, and with both inset encoding premises satisfied.

The third case uses scrollport 1,073,741,823 and insets -1,073,741,823 and -2 app units. Their sum fits signed32, but subtracting it from the scrollport does not. This cannot be dismissed merely by restricting each input to the ordinary coordinate range.

CrossAxisDriver.cpp executes the complete extracted combined ComputeStickyDisplacement caller with the producer's visible providers. challenges-v4 records an ordinary positive control and all three counterexamples at -O0 and -O2 with UBSan: both controls return shift 10 and Latest(50) 500; all six negative runs diagnose the predicted signed overflow. Compilation failures are not evidence. The point subtraction witness occurs in the declared nsPoint adapter; the core witnesses occur in the extracted ComputeStickyLimits body. This establishes a missing source-model admission, not browser reachability or a new accepted browser bug. The initial two Lean development failures and earlier two-witness native run remain preserved.

## Required correction

Keep both Frame2 coordinates through the selected-ancestor entry stage. Under the actual early-return guards, require and compose both ComputeStickyLimits axis domains whenever the whole helper executes, and both nsPoint subtraction domains when displacement is returned. Derive the selected result from this complete machine execution; do not replace the original caller claim with an isolated-axis claim. Keep no-container, no eligible ancestor, multiple ancestors, missing offsets and all-auto selected-axis paths branch-sensitive so unexecuted operations are not required. Prove that these witnesses are rejected and ordinary nonempty cases admitted; calibrate the complete entry admission against native calls.

Do not change the H1/H2 native snapshots or absorb the positional-sentinel/explicit-offset repairs. Preserve existing v1/v2 artifacts. The new negative-inset browser probe is a separate reachability investigation.

## Replay

First authenticate the producer and run its check.py into replay-v1 as in SOURCE-AUTHENTICATION.json. Then run `python3 -I -S check_challenges.py /absolute/new/output` from this directory. The challenge runner authenticates producer files/tool executables and the root replay manifest before rebuilding all 14 modules from authenticated source; it records commands, generated source and raw observations. It is a review runner, not a standalone proof library.
