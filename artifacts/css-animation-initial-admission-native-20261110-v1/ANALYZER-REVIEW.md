# Runtime trace review

The measured trace establishes finite initial admission inside an
AnimationOnly prepass of StyleDocument, followed by delivery through later
drain iterations. It does not demonstrate recurrent initialization.

| Fixture mode | Initial admission | StyleDocument call / iteration | Initial tasks | Requests / delivered cohorts |
| --- | --- | --- | --- | --- |
| smil-animated | Four named descendants, AnimationOnly, MatchAndCascade | 11 / 0 | Four masks of 5 | 21 / 10 |
| normal-animated | Four named descendants, ordinary traversal, MatchAndCascade | 23 / 0 | Four masks of 5 | 22 / 10 |
| smil-literal | Four named descendants, AnimationOnly, MatchAndCascade | 38 / 0 | None | 0 / 0 |

All three use content PID 50509, separate identified documents, and return
512px on the first and repeated getters. The SMIL modes retain paused time
75; the animated modes report exactly the four expected paused CSSAnimation
targets. The WPT callbacks pass and the harness reports OK. The explicit
runtime preference keeps CSS display animations disabled.

In smil-animated, each initial descendant has a matching restyle, entry to
process_animations with old_present=false, task enqueue, primary-style
installation, task execution and callback return. The initial font is 11px;
this is an intermediate state, not a failed getter. Each animated mode then
delivers cohorts in groups 4, 3, 2, 1 over iterations 1 through 4. The final
leaf installation is 512px before the first getter returns. The literal
control initializes with the relative-font result without CSS tasks.

TASK-BITS-SOURCES.json authenticates the local definitions against Git blobs
and retains the relevant excerpts. The C++ enum assigns CSSAnimations=1 and
EffectProperties=4; the Rust constants use those generated values. Thus 5
requests CSS animation updates plus effect-property updates, while later
mask 4 requests effect-property updates alone. The wrapper return proves
that Gecko_UpdateAnimations returned. It does not by itself prove execution
of every conditional C++ branch; observed requests inside the callback and
the fixture's CSSAnimation roster provide additional evidence for this run.

The analyzer keeps the full compositor/target/pseudo/pseudo-identifier/level
key, all coalesced requests, actual hint insertion, admission and installation.
Initial throttled request records remain in the account until their same-key
upgrades and selection. Queue counts agree at every pre-queue and
pre-remaining snapshot. Fresh requests after an earlier cohort's removal
remain outstanding until their own delivery. This is a trace conservation
check for these observed requests, not a claim about arbitrary throttling.

Exact PID, document, node, fixed role, StyleDocument call, iteration, task mask
and execution/return order are checked. Selection and installation share the
same document call; installation occurs in the selected drain iteration.
Traversal and installation threads agree, as do callback entry/return
threads. C++ request records have no thread field, so synchronous callback
association additionally relies on the inspected source's execution model.

No malformed RFDP records occur anywhere in this run. Four well-formed events
from another PID occur in measured intervals and are excluded after the
tested document/PID is identified. One cap occurs later, at raw row 15927,
in unrelated PID 50458. It does not affect these intervals. The analyzer
rejects a tested-process cap at any point before the relevant getter returns,
and rejects any malformed tagged record inside a measured interval.

ANALYZER-CONTROLS.json records 22 rejected mutations of the actual trace,
including wrong document/call/iteration/process/thread, missing task queue,
callback return or installation, incorrect old-style state, missing same-call
SMIL mapping, pseudo-key/hint mismatches, missing coalesced or renewed request,
wrong callback target, malformed record, cap and incorrect getter value.
Ruff and explicit optimized/non-isolated Python rejection checks also pass.
Each mutation must raise ValueError with its specific expected validation
reason. KeyError, IndexError and unrelated validation errors fail the control
harness instead of counting as successful rejection.

The initial SMIL admission occurs at iteration zero, before repeated drain
work. Later effect-property updates generate more requests, which are delivered
in the bounded run. No repeated destruction/recreation, same-rank cycle,
general termination argument, native-to-Lean refinement, new bug, or
release-browser performance result follows from this experiment.
