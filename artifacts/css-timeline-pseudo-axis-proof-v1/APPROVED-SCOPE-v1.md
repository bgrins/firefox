# Pseudo-scroll timeline logical axes: proposed formal implementation plan

18 October 2026. **Plan only. Root approval is required before implementation.**
The scope is source selection, resolved-frame snapshots, and cached sampling
through arbitrary finite resampling sequences. An axis truth table alone does
not satisfy this plan. If the complete required native boundary or theorem
scope cannot be implemented, stop and submit a versioned scope revision rather
than silently reducing it.

## Accepted repair and evidence boundary

The independent review and root decision accept the bounded non-root generated
pseudo defect: logical-axis selection uses the originating host frame's writing
mode, but scroll availability and geometry come from the pseudo's resolved
scroll container. The candidate passes that already-resolved container's
`WritingMode` to `ComputePhysicalAxis`. Its argument is named `aWritingMode`.

| Source | Original SHA-256 | Candidate SHA-256 |
| --- | --- | --- |
| ScrollTimeline.cpp | `4a93fb400e233981b65dd0d44c0b0c3b97d5aa6b2783aea9deeec2a70f3fa812` | `66fa2fd7d0a90d8ca56b3969c7b0f9273649cdcd778c26bc81426a852b2d10df` |
| ScrollTimeline.h | `64a063b1c48123b042d59d67e6981275b93b1755d7030371ec16d859bac6bf86` | `4f20b092f7555debd3fe4a90fb868781499465bc3717b899a5efe12b2f718d4f` |

`verify.py` reconstructs the exact candidate from the retained originals, with
one caller replacement, one complete helper replacement, and one declaration
replacement. Other native behavior is unchanged by this repair.

The retained baseline records 44 new WPT cases: 16 axis failures, four separate
recreation-opacity failures, and 24 passes. An existing vertical view-timeline
failure is separate. Root owns paired browser acceptance; this plan neither
asserts paired success nor treats rendering recreation as proved by sampling
correctness. Baseline binary pins are historical facts, never a requirement
that the live build continue to match an older binary.

Normative interpretation is anchored in the retained Scroll-driven Animations 1
snapshot: logical axes refer to the scroll container and physical axes remain
physical; absent relevant overflow makes current time absent. The generated
pseudo has its own styleable box. Public Element-valued source exposure follows
the existing host-exposure implementation/WPT convention; the plan does not
invent explicit normative pseudo-exposure prose missing from that draft.
[Axis](https://drafts.csswg.org/scroll-animations-1/#scroll-timeline-axis),
[progress](https://drafts.csswg.org/scroll-animations-1/#scroll-timeline-progress),
[generated pseudo boxes](https://drafts.csswg.org/css-pseudo-4/#generated-content).

## Required exact native execution boundary

Whole definitions and relevant declarations must be extracted from pinned full
files, using unique signatures and lexical body boundaries. Preserve all guards,
branches, loops, initialization and early returns. Adapters may provide external
objects, but must not replace the methods below with rewritten mini-models.

| Exact extraction | Required coverage |
| --- | --- |
| Full `ScrollerInfo` declaration, constructors, `TypeFromStyleScroller`, both `Anonymous` overloads, `Named`, `IsAnonymous`, `Source` | All five source kinds; element and pseudo identity are carried together |
| `FindNearestScroller` | Complete parent-frame traversal, non-element skipping, root stop/fallback, pseudo conversion and missing-frame guards |
| `AnimationUtils::GetElementPseudoPair` | Full pair-conversion function, including ordinary and generated pseudo branches; unsupported synthetic variants must be explicit, not deleted from extraction |
| `MakeNamed`, `MakeAnonymous`, full `ScrollTimeline` constructor (initializer and body) and `SourceElement`/`GetSource` | Actual scroller/axis initialization and host-valued source exposure; allocation/registration are modeled external effects |
| `ComputeSnapshot`, `GetSnapshot` | Actual root classification, no-sample default, cached versus live distinction |
| Complete `StateSnapshot` fields, defaults and constructor | Separate principal-box and scroll-frame guards, captured axis/availability/style/APZ, source identity |
| `StateSnapshot::GetScrollContainerFrame` | Root PresShell path, pseudo lookup and ordinary provider path |
| `nsLayoutUtils::GetScrollContainerFrameFromContent`, content overload of `FindScrollContainerFrameFor` | Actual root-element frame substitution and scroll-target delegation, not a fabricated selected-frame answer |
| Original and candidate `ComputePhysicalAxis` | Exact host-mode versus resolved-container-mode read and complete axis expression |
| `UpdateCachedCurrentTime`, complete `CurrentTimeData` and equality | Reset before guards, second frame resolution, selected position/range dimension, exact return/change behavior |
| `TimelineDataDidChange` | Full animation list loop; fake animation methods record both notification calls in order |
| `ComputedTimelineData`, `ComputeTimelineData` | Absent versus present result and exact integer position/start/end |
| Both public current-time getters | Complete native absence and numeric branches in the bounded capsule; Typed OM/TimeDuration allocation/conversion endpoints are explicit adapters |

Exact source bodies of `WillRefresh`, `UpdateIfStale`, timeline registration and
manager construction routes will be retained and mapped, but the universal
sampling theorem begins at each explicit `UpdateCachedCurrentTime` invocation.
No theorem of browser event-loop delivery, timeline-manager name lookup,
registration, animation rendering, or compositor scheduling is claimed.
`ViewTimeline` shares the snapshot; its much larger view-range/sticky/inset
sampling implementation is retained for impact review and WPT regression scope,
not silently included in a theorem about ScrollTimeline's cached data.

Record each extracted definition's origin, full-body hash and byte span. Any
signature/namespace/access adaptation needs a counted transformation inventory,
before/after bytes and executable reversal to the original extraction. Keep
semantic statement order unchanged. Restore exact original/candidate sources
from any instrumented versions and compare bytes. Build both variants from the
same adapter implementation; the adapter must not branch on expected results or
variant name. No unchecked regular-expression partial-body extraction.

## World and provider model

Use distinct ID types and separately owned records for documents, originating
elements, pseudo elements, primary frames, scroll-target frames, and scroll
containers. A host and pseudo must never be aliases merely to simplify setup.
A fieldset-like primary frame can delegate to a different scroll-target frame.
Every frame carries its own writing mode, parent, content and frame kind.
Every scroll frame independently owns two-axis position/range, availability,
overflow style and the fields needed by external APZ providers.

Inputs must be raw graph/style/geometry facts. **Do not supply the expected
physical axis, expected source winner, active state, expected CurrentTimeData,
or expected change/notification result as a provider field.** Derive them through
the independently defined algorithms and the actual extracted native functions.

Required provider premises:

- Graph identities are valid, parent chains finite and acyclic, and pseudo/host
  backreferences consistent. Owners outlive all accesses in a sample. RefPtr
  adapters preserve the required element lifetime; between-sample frame deletion
  is represented by new generation IDs or tombstones, never dangling pointers.
- Source kinds whose native entry requires a target (Root/Nearest/Self) receive
  one. Explicit provided-null is legal. Missing host principal box, missing
  pseudo, missing pseudo frame, non-scroller, absent PresShell and absent root
  frame are distinct inputs. Do not call a native assertion violation a CSS
  counterexample.
- `GetPseudoElement(NotPseudo)` returns the originating element; generated pseudo
  lookup is keyed by request type/name. Ordinary, before/after and named pseudo
  identities are not collapsed. Full pair-conversion extraction includes other
  kinds; the main universal semantic domain is ordinary/before/after, and other
  pseudo kinds receive bounded identity controls with explicit support status.
- `GetScrollTargetFrame` is a raw frame-to-frame relation. The exact outer
  layout-utils provider performs its own substitutions. Correct real Gecko
  root/fieldset mappings remain assumptions checked by browser controls, not
  proved by a fabricated fake-frame answer.
- Provider graph and geometry are stable **within each sampling invocation**,
  including both calls to `GetScrollContainerFrame`. Between invocations, finite
  sequences may change any admitted record, including source type/axis, document
  root, pseudo existence, frame generation, availability and geometry.
- In physically valid ordinary-scroll cases, available directions agree with
  positive corresponding range lengths. Also include deliberately inconsistent
  provider records as clearly labeled diagnostics, outside normative active-time
  theorems; do not divide by zero and call it an implementation defect.
- APZ enabled/disabled/displayport facts are independent inputs, queried in actual
  short-circuit order. Prove axis/time noninterference separately from unrelated
  APZ state; do not assert all host changes preserve the entire snapshot.
- Allocation succeeds; callbacks used for notification logging cannot mutate the
  graph during a sample. Real reentrancy/lifetime/refresh guarantees are external
  premises, not established by the capsule.

The root flag is currently host equality with document.scrollingElement without
a pseudo exclusion. Retain and execute this exact behavior. Root-generated
pseudo resolution is a separate unconfirmed lead and is not repaired here.
The normative pseudo-source theorem requires a **non-root originating element**.
Generic native/model agreement can include root pseudos as diagnostics without
asserting the existing root classification conforms to the specification.

## Independent semantic definitions

Implement three distinct components, with no calls from one implementation to
another to choose winners, branches or outputs:

1. **Declarative source and sampling semantics.** Resolve source kinds over graph
   relations. For Nearest, filter the ancestor chain by eligibility before the
   root sentinel and take its first member; ordinary pair conversion is an
   independently specified relation. Resolve a scrolling frame through raw
   graph/document relations. Define logical-axis meaning from that frame's
   orientation, then construct the observation directly from the chosen axis's
   data. State last-observation/change/notification rules declaratively.
2. **Native-shaped Lean interpreter.** Keep the actual source-kind case split,
   frame traversal recursion, snapshot fields/defaults, root flag, two provider
   resolutions, cache reset/guard/emplace order and notification branches.
   Termination follows from finite ranked parent chains. Preserve enough trace
   information to expose the frame and mode actually queried.
3. **Independent Python oracle.** Read the same raw graph scenarios but implement
   the declarative relation directly. It must not import generated native output,
   the Lean interpreter, candidate axis labels or browser expected/pass fields.
   Compare complete structural observations, not merely a pass/fail count.

The source-selection correspondence establishes agreement with the declared
ordinary/before/after selection policy under provider premises. It is not a
claim to verify every current specification rule for anonymous nearest-source
selection: the pre-existing single-axis nearest-source gap remains separate.
Pin the policy/version and label the known gap instead of baking it into a
claim of full CSS conformance.

### Required universal Lean theorems

For every valid finite graph, admissible numeric state and arbitrary finite
sequence of admitted sampling worlds:

- **Source selection agreement and traversal completion:** declarative filtering
  and native-shaped source selection return the same element/pseudo pair; root
  stopping and missing-frame cases agree. The native-shaped traversal terminates
  under the graph rank, with no unexplained arbitrary fuel bound.
- **Resolved source consistency:** a present candidate snapshot's axis,
  availability and overflow-style dimension all use the same resolved scroll
  frame. Its sampled position/range refer to that frame under within-call
  stability. Pair identity survives named/provided/self resolution and pseudo
  conversion on nearest resolution.
- **Source exposure:** named pseudo internal identity retains the request while
  its public source exposes the originating element. This is a bridge/interface
  convention, separately labeled from normative axis meaning.
- **Axis laws:** x/y are orientation invariant; block/inline exchange with the
  resolved frame's orientation. Direction/sign changes alone do not exchange
  physical axes. These are supporting lemmas, not the complete result.
- **Host-mode noninterference:** for a fixed non-root named pseudo, changing only
  the host principal-frame orientation cannot change the candidate physical axis
  or time observation while pseudo/scroll-frame identity, mode, geometry and
  existence remain unchanged. Compare matching prior caches in a two-run proof.
- **Cache clearing and reconstruction:** inactive or unavailable samples clear
  previous time; a later valid sample uses current source/frame data regardless
  of previous cache. Source deletion/recreation and orientation changes between
  samples cannot retain the old selected dimension.
- **Exact cache state transition:** return value is equality/change of old and
  new optional CurrentTimeData; active entry or extent change invokes both
  notification methods on each animation; position-only change does not invoke
  TimelineDataDidChange; inactive early-return clears time and returns whether
  old time existed without inventing a notification absent in native code.
- **Cached getter coherence:** GetSnapshot returns the last sample, or default
  before any sample. ComputeTimelineData is absent exactly when cached time is
  absent; otherwise it preserves position, zero start and selected extent.
- **Finite-sequence correspondence:** fold both independently defined transitions
  over any admitted list of worlds and prove every sample's observable record,
  cached record, return flag and notification projection agrees. Induction must
  depend on source/frame/transition lemmas, not two aliases of one definition.
- **Repair preservation:** original and candidate semantic observations agree
  for physical axes, for inactive snapshots, and whenever the original host
  frame and resolved scroll frame have equal orientation. Lift this per-step
  result to finite sequences satisfying that premise at each sample. Provider
  read traces legitimately differ (the repaired mode read moves frames); do not
  assert raw trace equality across variants.
- **Rational progress projection:** on positive extent and representable signed
  offset, rational magnitude/extent depends on the selected dimension and stays
  invariant under the corresponding noninterference/preservation hypotheses.
  This theorem is about an explicit numeric interpretation, not all IEEE or
  CSS scroll-origin behavior.

Audit theorem hypotheses, rejected stronger claims and `#print axioms` output
for every exported theorem. No sorry/admit, synthetic expected-answer axioms,
unsafe proof shortcut or opaque imported conformance assertion. Standard Lean
foundations must be named. Record theorem dependency structure so a vacuous
premise or reflexive duplicate-model proof cannot masquerade as refinement.

## Numeric and native execution domain

Use signed 32-bit app-unit positions and nonnegative extents bounded by
INT32_MAX. For numeric getters exclude INT32_MIN before std::abs and require a
strictly positive selected extent. The core record/sampling theorems do not
need floating-point arithmetic. For ordinary browser-compatible numeric cases
use `abs(position) <= extent`; separately label synthetic out-of-range inputs.
Include positive/negative/zero positions and unequal x/y extents. Logical axis
orientation is distinct from negative scroll origins and RTL/sideways progress
policy (the native getter explicitly cites CSSWG #12893).

The capsule executes the actual double division/scaling expressions in both
getters. Compare raw integer records exactly; compare native percent/duration
payloads with an explicitly documented IEEE rounding oracle or bounded error
budget. Use dyadic progress cases for exact checks and nondyadic cases for
rounding checks. A fake TimeDuration or CSSUnitValue constructor records its
input and null/type dispatch; it does not prove Gecko's internal duration
quantization or Typed OM allocation. Do not claim the rational Lean theorem
proves these endpoint adapters or compiler floating-point execution.

## Bounded execution corpus and provider traces

No proof implementation or generated corpus exists yet. The implementation must
publish scenario generators, deterministic seeds (if any), exact row counts and
branch/transition coverage rather than claim coverage from a large number alone.
Required independent dimensions:

- All source kinds; ordinary, before, after; host/pseudo/scroll-target orientations
  independently horizontal/vertical, plus direction reversals; all four axes.
- Horizontal-only, vertical-only, both and neither direction availability;
  asymmetric position/range and overflow styles that expose wrong-axis reads.
- Distinct element primary versus scroll-target frames; root standards and quirks
  ownership records with differing html/body/root-frame orientations; missing
  root provider, absent PresShell and source/primary/pseudo-frame absence.
- Nearest chains with empty/non-element frames, multiple eligible ancestors,
  root sentinels, pseudo ancestors and no eligible source. Include same graph
  with differently positioned distractor frames, so selection is not hardcoded.
- No-sample default; active→inactive→active, available→unavailable→available,
  host-only change/restore, pseudo/scroll-mode change/restore, axis replacement,
  same-data new frame generations, extent-only changes, position-only changes,
  equal repeated samples, and old frame replaced by a different scroll target.
- Zero, one and several animation subscribers, checking both notification calls
  and traversal order. Raw provider traces identify sample number, receiver ID,
  operation and returned value for source/frame/mode/geometry reads.

Execute original and candidate extracted bodies on each valid scenario. Preserve
all observations and raw traces; compare their semantic projections to both
oracles and their detailed traces to the native-shaped interpreter. Inactive
snapshot fields documented meaningless by native code must be normalized only
in the declared semantic projection; retain raw values in diagnostic output.
Record explicit invalid-input rejections separately from valid negative controls.

## Executable semantic mutation gates

Every listed mutant must compile and execute a valid discriminating witness.
Compile failure is not a killed semantic mutant. For each mutant retain actual
process status, witness input, native output, independent expected output and
mismatch. Execute a corresponding Lean mutant witness as data (`#eval`/executable
check or a proved concrete inequality); merely making a theorem fail to compile
does not count as an executed counterexample.

1. Restore host-primary writing mode instead of resolved-scroll-frame mode.
2. Swap block and inline orientation.
3. Make physical x/y depend on orientation.
4. Lose pseudo request during named source selection or nearest pair conversion.
5. Select a farther eligible frame in Nearest or ignore the root stop.
6. Skip scroll-target delegation and use a primary frame as the scroller.
7. Retain previous cached time after inactive/unavailable input.
8. Read the wrong position coordinate or range dimension despite a correct axis.
9. Reuse a previous snapshot on a resampling call.
10. Break changed/notification logic: position-only notification or missing extent
    notification, with nonempty animation lists to make it observable.
11. Lose cached absence in ComputeTimelineData or return a nonzero start.

Mutants must change only their named semantic behavior, not the independent
oracle or expected outputs. Record source reversal and a fresh clean replay
between mutation batches. Include at least one candidate-preservation control
per witness where applicable. Mutant root/pseudo reclassification is outside
this repair; do not require the existing code to pass an unaccepted new contract.

## Source-only closure, review and delivery gates

Deliver a self-contained proof companion directory containing pinned original
and candidate native sources, required provider definitions, extraction/adaptation
scripts, C++ adapters, deterministic corpus/oracle code, Lean sources/toolchain
lock, specification/claim mapping, and verification entry point. Classify files
as required source inputs versus generated outputs. The verifier must authenticate
all source inputs **before importing or executing any local helper**.

The clean replay starts from only the enumerated source inputs in a fresh
temporary directory; it regenerates extracts, compiles both native variants,
runs corpus and semantic mutants, builds Lean, runs executable witnesses and
axiom audits, and compares independent results. It must not read the Firefox
checkout, old generated binaries/results, sibling artifacts, undeclared package
cache contents or browser build outputs. Record toolchain versions and invoked
commands. Dependencies must be explicitly pinned/declared; no hidden network
fetch can stand in for a source-only closure test.

Freeze the completed producer evidence, obtain independent formal/native-bridge
review, and have root replay the clean closure. Browser baseline/candidate/WPT
and standalone native patch review remain additional gates. Keep historical
receipts and build identities immutable; current source checks are optional
`--live` checks against candidate pins only. Proof/tooling/docs belong in the
preceding independently reviewable commit; the native repair and relevant WPT
remain their own standalone commit under the root's workflow.

### Implementation milestones after approval

1. Build exact extraction plus owning provider graph and record all adaptations.
2. Implement independent declarative oracle and native-shaped state/trace model.
3. Execute native corpus and original/candidate discrimination; resolve invalid
   provider assumptions before proving an overconstrained theorem.
4. Prove source-resolution, per-sample and arbitrary finite-sequence contracts.
5. Execute semantic mutants, numeric boundary controls and axiom audit.
6. Replay from source-only closure; freeze for independent and root acceptance.

A milestone is not complete if it omits its source-selection/frame-resolution
or cache connection. Difficulty compiling a full body must trigger a proposed
scope revision rather than replacement with an axis-only model.
