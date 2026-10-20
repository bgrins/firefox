# View Transitions: static expansion scout

18 October 2026. Artifact-only audit. No browser, build, native extraction,
Lean proof, live Gecko/WPT edit, commit, or external submission was performed.
All five findings below are falsifiable source-derived hypotheses. None is an
accepted bug or a claim about a tested release browser.

## Recommendation

Start with the two type-set probes. They exercise enabled, ordinary API behavior,
have small independent oracles, and distinguish representation consistency from
restyle scheduling. Next test completion ownership and custom document timelines.
Keep paint-order work behind those gates: it has a concrete provider mismatch,
but it overlaps an existing open issue and needs a pixel/ordering calibration.

| Rank | Contract | Static prediction | First observable gate |
| --- | --- | --- | --- |
| 1 | One set shared by API and selector matching | Deleting an initially duplicated type leaves native selector membership | `types.has()` versus `matches()` immediately after delete |
| 2 | Type mutation invalidates dependent styles | A settled style remains stale after add/delete/clear | Computed color versus direct selector match, without other DOM edits |
| 3 | Finished transitions cannot mutate another transition's suppression | Natural completion leaves `PendingDone`; a later skip on that object unsuppresses its document | A requestAnimationFrame runs inside a newer unresolved update callback |
| 4 | Lifetime accepts all document timelines owned by the document | A non-default DocumentTimeline is excluded by pointer comparison | `finished` resolves while a pseudo animation remains paused |
| 5 | Capture order refines paint order | Equal-z children in different frame lists lose DOM tie order | Overlapping named absolute/in-flow siblings before/during capture |

These target distinct contracts. A duplicate-set repair would not address style
invalidation, and changing a timeline predicate would not repair terminal phase
ownership. Independently confirmed bugs should retain separate native/WPT commits.

## Feature reachability

The local `Document.webidl` exposes `startViewTransition` and
`activeViewTransition` without a pref. `ViewTransition.webidl` exposes promises,
`skipTransition`, and the setlike `types`. The local name parser implements
`none`, ordinary names, and `match-element`; classes and active-type selectors
are implemented. Bug 2001878 describes the type feature and its shipping work;
this audit establishes checkout reachability, not a release-version matrix.

`dom.viewTransitions.cross-document.enabled` defaults to false. The inbound
constructor exists, but the bounded Searchfox references to
`SetInboundViewTransitionParams` find only its declaration and definition.
Cross-document rules/events and their pref-enabled metadata do not establish a
complete navigation path. Do not promote the unchecked lazy-promise access in
`CreateCrossDocument` into a reachable browser bug on this evidence.

Current Level 2 additionally contains element-scoped transitions, nested groups,
`transitionRoot`, `waitUntil`, and `auto` naming. These are outside the implemented
slice identified here; unsupported features are not conformance findings.
`dom.viewTransitions.remain-active` defaults false and must remain false for the
lifetime probes. Avoid `none` and `-ua-` type strings: their selector treatment
has a live specification discussion, CSSWG issue 13141.

Primary drafts are saved in `specs/level1.html` and `specs/level2.html`, with
retrieval times in `PROVENANCE.json`. The Level 2 draft is broader than this
implementation. Apply its already implemented type-set contract without assuming
all its newer lifecycle extensions exist locally.

## 1. Initial duplicate types split API and native membership

The [active types definition](https://drafts.csswg.org/css-view-transitions-2/#viewtransition-active-types)
uses `ViewTransitionTypeSet`; the startup algorithm clones supplied types as a
set. [Active-type selector matching](https://drafts.csswg.org/css-view-transitions-2/#the-active-view-transition-type-pseudo)
reads that same membership.

The exact local path is:

1. `Document::StartViewTransition` appends every input string to `types`, with
   an explicit TODO about deduplication.
2. The constructor moves it into `ViewTransition::mTypeList`.
3. `ViewTransition::Types` lazily populates a JS set through generated
   `SetlikeHelpers::Add`. Duplicate additions collapse only in that set.
4. `ViewTransitionTypeSet::Delete` deletes from the JS set, then calls native
   `mTypeList.RemoveElement`. `nsTArray::RemoveElement` removes one occurrence.
5. `Gecko_HasActiveViewTransitionTypes` checks the remaining native array.
   Stylo's `ActiveViewTransitionType` match also checks the root active-state bit.

Minimal witness: start with `types: ['a', 'a']` in a visible attached document.
Assert the returned object is active and that the public set enumerates `['a']`.
Delete `a` once. Expected: public `has('a')` and root
`matches(':active-view-transition-type(a)')` are both false. Source prediction:
the former is false and the latter true. This can be checked synchronously,
before capture, so neither rendering timing nor restyle invalidation is needed.

Controls: unique initial `['a']`; duplicates of an unrelated name; `clear()`;
two distinct case-sensitive names; initial duplicate order permutations.
Re-adding after deletion is a follow-up: the native Add assertion assumes no
remaining entry, so record debug-build behavior separately from release behavior.

Existing `view-transition-types-mutable.html` tests repeated Add into an initially
empty set, not duplicates in startup options followed by deletion and selector
matching. Its local metadata is absent; that does not mean this proposed witness
has been run or passes.

The finite handwritten projection exhausts 10,285 initial-list/delete/clear
traces over three names, finding 2,823 final membership disagreements. All 1,360
traces with unique initial lists agree. These numbers describe the projection,
not native executions or proofs.

## 2. Late type mutations appear to omit invalidation

`ViewTransitionTypeSet::{Add,Delete,Clear}` update the set and native array but
do not notify the owning root's style state. The captured generated binding
helpers only manipulate JS set storage; their method wrappers call these native
methods without an extra restyle callback. The root's active bit is added at
transition startup and removed during cleanup. Stylo declares active-type
selectors dependent on that bit, while their actual result also reads the type
array. Type mutations do not change the bit.

This is a stale-style hypothesis, not a stale-matcher hypothesis. With unique
types, `matches()` should observe the new array immediately, while computed style
may retain the previous cascade result. The [same selector definition](https://drafts.csswg.org/css-view-transitions-2/#the-active-view-transition-type-pseudo)
provides the observable oracle.

Use `html:active-view-transition-type(a) #probe { color: green }` over a red
default. Disable naming on `#probe`; keep the transition alive with a separately
named element and paused pseudo animations. Await `ready`, then two rendering
turns, and force/read the baseline computed color. Add `a` and immediately read
both root `matches()` and computed color, without changing a class, style,
stylesheet, DOM node, or animation in between. Repeat after rendering turns and
then independently test delete and clear, starting with matching settled styles.

Controls: startup types; mutation before the initial style flush; no-op add and
missing delete; explicit unrelated root restyle after recording the stale value;
a descendant selector and a root-only selector. Do not use a fresh clone as the
normative oracle. Its matching color is only a cache-control comparison.

`view-transition-types-match-early-mutation.html` mutates while startup already
needs restyle. The late-mutation reftest adds a type in `ready` and immediately
calls `takeScreenshot()`, whose actual helper removes the root's `reftest-wait`
class. Consequently it does not isolate a clean mutation from pending initial
style work and an additional root mutation. This is a possible coverage mask,
not a claim that that extra class removal necessarily invalidates every relevant
selector. Root should run the isolated computed-style gate before deciding.

## 3. Natural completion retains a nonterminal phase

[Frame handling](https://drafts.csswg.org/css-view-transitions-1/#handle-transition-frame)
ends the transition, and [skipTransition](https://drafts.csswg.org/css-view-transitions-1/#dom-viewtransition-skiptransition)
does nothing to a completed transition. Local delayed cleanup follows CSSWG
issue 12442 and bug 1980513: `HandleFrame` writes `PendingDone` and queues
`FinishDone`. `FinishDone` clears document ownership and resolves `finished`,
but neither it nor `ClearActiveTransition` writes `mPhase = Done`.

On that completed object, a subsequent `SkipTransition` therefore passes its
Done guard and executes `SetRenderingSuppressedForViewTransitions(false)`.
The identity guard applies only to clearing the document's active transition,
after that global suppression write. A newer transition's active pointer is
preserved, but its rendering suppression may be removed.

The observable provider path is captured: `Document::IsRenderingSuppressed`
reads that bit, and `nsRefreshDriver::RunVideoAndFrameRequestCallbacks` omits suppressed
documents when collecting requestAnimationFrame callbacks. Clearing suppression
also schedules rendering through `MaybeScheduleRendering`.

Probe plan:

1. Let transition A finish naturally; retain A and assert no active transition.
2. Start B with an async callback whose externally controlled promise is pending.
   Resolve a separate "callback entered" promise and register a rAF inside B's
   callback before awaiting its gate. This ensures B has captured and suppressed
   rendering before observation.
3. From a task after callback entry, call `A.skipTransition()` while B remains
   active and `B.updateCallbackDone` is unsettled.
4. Use a timer/parent controller to release B's gate; record whether the rAF ran
   before release. A rAF before release is the predicted observable violation.

Controls: no old skip; A was explicitly skipped before finishing; second call to
the same old skip; B skipped directly; old skip before B starts. Keep the pending
window comfortably below the 10-second implementation timeout. A bounded timeout
without a delivered rendering opportunity is inconclusive, so retain controller
frame/timer evidence. A controlled refresh-driver test can first establish the
state consequence, but a WPT should demonstrate it with platform observables.

Existing cleanup and active-pointer tests check finished timing and nullness,
not old-object operations during a later suppressed transition. The CSSWG issue
concerns when to finish, not permission for a completed object to change another
transition. This hypothesis does not dispute the asynchronous-cleanup policy.

## 4. A non-default same-document timeline is omitted from lifetime checks

Both fetched View Transitions drafts' [frame algorithm](https://drafts.csswg.org/css-view-transitions-1/#handle-transition-frame)
counts an eligible animation on a document timeline associated with the document.
`CheckForActiveAnimationsForEachPseudo` instead requires
`anim->GetTimeline() == &aDocTimeline`, where the caller supplied
`mDocument->Timeline()`.

The [Web Animations document timeline definition](https://drafts.csswg.org/web-animations-1/#document-timelines)
distinguishes that kind from the document's default instance.
`DocumentTimeline::Constructor` creates a new object associated with the current
realm's document and registers it with the document's timelines controller.
`Animation::SetTimelineFromJS` marks the CSS animation's timeline overridden and
forwards to the ordinary setter; no restriction to the default timeline appears
on that path. This distinguishes owner identity from timeline object identity.

Start a transition with long-duration pseudo animations, await `ready`, obtain
its existing CSS animation objects from `document.getAnimations()`, and verify
their pseudo targets. Move all relevant pseudo animations to one fresh
`new DocumentTimeline()` in the same realm, pause them, and await readiness.
This reuses generated named-pseudo animations; it does not depend on unsupported
construction of a named-pseudo KeyframeEffect. Retain object references and
check each timeline equals the supplied object and each play state is paused.
Expected: the view transition stays active and `finished` remains pending until
the animations are canceled or the transition is skipped. Source prediction:
the next lifetime check finds no default-timeline animation and finishes early.

Controls: leave animations on `document.timeline`; use a different originTime on
a same-document timeline; move only one animation while another default-timeline
animation remains paused; no active pseudo animations; a foreign-document
timeline as a deliberately excluded ownership control. Filter ordinary document
animations explicitly so they cannot keep the fixture alive accidentally.

No `DocumentTimeline` text hits were returned by the bounded Searchfox search in
the View Transitions WPT directory. This is not an exhaustive test-absence proof.
Bug 1928299 and CSSWG issue 9901 concern scroll timelines; the latter led to
`waitUntil`. Neither changes the inspected same-document DocumentTimeline rule.
The finite predicate model has six disagreements among 40 tagged timeline/
play-state/event cases, all for non-default same-document timelines.

## 5. Equal-z capture order uses child-list order

The [old-state capture algorithm](https://drafts.csswg.org/css-view-transitions-1/#capture-the-old-state)
requires paint-order traversal. The [CSS painting order](https://www.w3.org/TR/CSS22/zindex.html#painting-order)
orders equal-zero positioned stacking contexts by tree order.
Local `CollectDescendantStackingContexts` walks
all frame child lists, and the recursive consumer stable-sorts solely by z-index.
`nsContainerFrame::GetChildLists` appends its principal list before inherited
absolute lists. Thus stability preserves frame-list concatenation, not necessarily
the DOM tie order of equal-z sibling stacking contexts.

Use a positioned container with first child A absolutely positioned and second
child B relatively positioned/in flow. Give both explicit `z-index:0`, unique
transition names, equal 100px square geometry, and overlapping placement. B
should paint above A in the original document. The source traversal visits B's
principal-list frame before A's absolute-list frame; equal-z sorting preserves
that order. Captured group insertion can therefore put A above B.

First calibrate original paint with a screenshot and `elementsFromPoint`; the
latter alone does not prove capture pixels. Then start an unchanged transition,
pause its pseudo animations, hide root imagery, and select only old or only new
images in separate runs. Compare a central overlap pixel with an explicit B-on-top
reference. Keep group z-index at its default; do not inadvertently repair capture
order with author pseudo styling.

Controls: both siblings in flow; both absolute; reverse DOM order; distinct
z-indices (where the native comparator should repair list concatenation); no
transition; entering-only and exiting-only names after the primary witness.
The numeric model merely demonstrates the ordering projection: three tie cases
out of nine z-index pairs disagree. It does not execute frame construction,
display-list sorting, capture, or compositing.

This overlaps open bug 1926021's general paint-order requirement. Bug 1966192
added the current z-index sorting and the two existing paint-order WPTs; its
recorded witness used unequal z-indices. Claim a specific remaining tie/provider
case only after root reproduction, not a novel paint-order bug family.

## Formal extensions worth building

These are proposals, not delivered proofs. Each model must be written from the
retained spec contract before adapting the implementation. No proposal supplies
the expected decision as a native provider stub.

### A. Active type representation and invalidation

Model an ordered set of DOM strings, an owning transition/document/root identity,
the root's active state, and a dependent-style cache with a dirty version. Prove
for arbitrary finite successful operations that public enumeration, native
membership and selector membership agree; deletion removes membership regardless
of startup multiplicity. Separately prove every membership-changing operation
that can affect a selector invalidates its dependent styles before their next
observable read. No-op operations should preserve the cached state.

Smallest useful native closure: complete startup option projection and
`Document::StartViewTransition`, constructor, `Types`, all three type mutations,
generated helper/wrapper functions, `nsTArray` search/removal semantics,
`Gecko_HasActiveViewTransitionTypes` and its validity helper, Stylo's matching
branch and state dependency mapping, plus the selected notification/flush path.
A set-only model excludes the second lead; an invalidation proof needs actual
dirty-state providers. String/atom identity, successful allocations and valid
root ownership are explicit premises. Reserved keyword policy remains tagged.
Cost: small set theorem; medium mixed C++/Rust/provider bridge; potentially larger
restyle closure. Test long operation sequences and no-op mutation cost separately.

### B. Transition terminal state and document ownership

Use nominal transition/document/timeline identities, lifecycle phases, callback
queue membership, settled promise states, active-owner identity and suppression
owner. Prove exactly-once callback invocation, eventual terminal cleanup under a
fair scheduler, idempotent completed-object skip, and noninterference: operations
on completed A cannot change active B's tree, promises, or suppression. Prove
the lifetime predicate uses timeline kind plus document ownership rather than
the default timeline's object identity.

Closure: complete `StartViewTransition`, schedule/flush queue, pending operations,
setup, update callback with both handlers, activation, HandleFrame, FinishDone,
skip, clear, animation predicate/EffectSet iteration, and document suppression/
scheduler collectors. Include DocumentTimeline construction and animation setter
paths for the timeline witness. Model capture success/failure and animation state
as explicit inputs only for the lifecycle theorem; their producing algorithms
are separate obligations. Promise reaction ordering, realm exceptions, timeout
tasks, reentrancy and rendering fairness must be stated, not hidden in a
"valid scheduler" premise that already asserts the conclusion. Full JS/GC,
graphics reset and cross-document navigation are outside the first slice.
Cost: medium state theorem, large faithful task/promise bridge. Begin with the
terminal-owner counterexample and a fresh native lifecycle harness, then broaden.

### C. Capture maps, generated pseudo trees, and paint order

Independently specify filtered eligible element sequences in CSS paint order,
old/new unique-name maps, old-first/new-only insertion order, and generated trees.
Prove duplicate failure leaves no capture flags; successful capture has unique
names and exactly the specified old/new pseudo children; lookups return the
correct role/name; old-only classes survive and new-side classes replace them;
cleanup removes all flags and mappings. Match-element identity must remain
stable for the same live element and distinct for replacement elements.

Closure: collection/recursion/comparator plus actual frame child-list providers,
name and class resolution including tree scope, complete old/new capture,
`SetCaptured`, pseudo construction, lookup/dynamic-rule/class matching, and
cleanup. For a paint-order theorem, add ordinary display-list ordering and the
placeholder/out-of-flow provider relationship; merely assuming collection is in
paint order would remove the reported question. Frame/content lifetime,
fragmentation eligibility, shadow scope, and successful snapshot availability
are explicit boundaries. The raw-pointer match-element map needs a lifetime/
address-reuse analysis before claiming universal element identity. No allocator
reuse counterexample was demonstrated here. Graphics pixels, transform precision,
GPU resource lifetime and full restyle/layout remain additional bridges.
Cost: small pure ordered-map/tree laws, large frame-tree/paint-order refinement.

## Negative findings and coverage limits

Inspected complete ViewTransition definitions for callback scheduling, both
callback settlements, activation, old/new capture, duplicate rejection, pseudo
construction and lookup, dynamic-style updating, active-animation checks, skip
and clear. Inspected actual startup/type bindings, selector read/dependency
sites, custom DocumentTimeline creation/setter entries, frame-list providers and
render suppression consumers. Full snapshots also contain uninspected code;
their presence is not a claim of whole-file verification.

The existing early-skip/reentrant-callback path changes phase before invoking
script, consistent with the resolved CSSWG issue 10822 correction. Both old
duplicate failure and new duplicate failure have explicit capture-flag cleanup.
Name-map insertion retains old order and appends new-only names; pseudo lookup
handles absent old/new children distinctly. Class capture is refreshed at new
capture, while old-only captures retain old classes. The inspected per-frame
style update rejects missing/hidden/fragmented new frames and refreshes size,
transform, writing mode, direction, text orientation, blend, backdrop and color
scheme. These are negative static findings, not general correctness results.

The queue flush moves pending callbacks to a temporary array to tolerate
reentrancy; CSSWG issue 11943 remains open. No new callback-order violation was
established. Bug 2010608 already tracks MatchClassList's missing-map crash and
has a guard. Tree-scope history is bug 1970954; auto-name history is bug 1918218.
Do not report stale TODO comments as fresh defects without tracing current code.

Not inspected to closure: cross-document transport/navigation, scoped/nested
features, GPU/image-key destruction, device loss, all shadow/slot name provenance,
frame reconstruction during animation, 3D/perspective and zoom transforms,
fragmentation providers, pixel snapping, complete hit testing, accessibility,
printing, allocator reuse, or the full CSS cascade of generated pseudos. Ordinary
CSS transitions and animation-composite setter work are deliberately separate:
the round-12 transition/CSSOM reports and round-22 composition report were read.

Selected metadata preserves an inherited-pseudo-value expected failure,
unsupported auto/waitUntil results, and platform allowances on callback/skip
tests. The directory disables useDrawSnapshot runs, so any pixel probe needs an
actual supported rendering path. These existing conditions are not new findings.

## Evidence and replay

`INPUTS.json` identifies full local snapshots and explicitly absent selected
metadata. `discovery/` retains bounded Searchfox searches; `history/` retains
primary Bugzilla/CSSWG responses, including query limits and dates. Summary
searches are not exhaustive duplicate searches. No existing metadata inventory
is presented as a current test run. `PROVENANCE.json` records the unavailable
webspec-index command and direct primary-draft fallback.

`MANIFEST.json` covers every other file in the capsule, including the checker,
model, reports and evidence. Authenticate its digest from the handoff before
running `python3 -I -S check.py --manifest-sha DIGEST`. The checker authenticates
all model inputs before importing the local model and rejects extra files.
`--live` additionally compares checkout snapshots and absent metadata; unrelated
ongoing root work can legitimately make that optional check fail.

`MODEL-RESULTS.json` is deterministic finite arithmetic/state bookkeeping, not
an extracted program or formal verifier. Root browser gates, independent defect
adjudication and any native/Lean refinement remain future work.
