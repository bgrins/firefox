# Independent all-shorthand ordering adjudication

Date: 2026-10-19. Verdict: **REACHED** for the relational CSSOM ordering
requirement. The retained browser discrepancy is a valid observable ordering
bug under the specification's canonical-expansion interpretation described
below. It is not yet an accepted native repair, rendering bug, or new universal
formal-verification result.

## Normative trace and the unresolved absolute order

Scenario: writable inline style, supported padding longhands, valid all value,
valid priority, same feature configuration and shorthand expansion provider.

1. [CSSOM setProperty, steps 5–8](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-setproperty)
   parses the value and applies each shorthand longhand in canonical order.
2. [Set a CSS declaration](https://drafts.csswg.org/cssom/#set-a-css-declaration)
   requires the target after every same-group declaration with different mapping
   logic. It also preserves other declarations. Equal value/priority does not
   exempt this ordering requirement.
3. [CSS Logical Properties](https://drafts.csswg.org/css-logical-1/#logical-property-group)
   places physical and flow-relative padding longhands in one logical group.
   [all](https://drafts.csswg.org/css-cascade-5/#all-shorthand) includes both;
   its exclusions are direction, unicode-bidi and custom properties.
4. [CSSOM item](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-item)
   exposes declaration order, making the difference directly observable without
   a rendering assertion.

Let A and B be the tested opposing-mapping pair. Whichever is processed last
must end after the other. Updating any later, different identity preserves their
relative order. Therefore the final pair order follows the expansion order and
is independent of their initial positions. Fresh expansion obtains that order
without prescribing which member must come first.

The open [CSSWG issue 5741](https://github.com/w3c/csswg-drafts/issues/5741)
means the absolute canonical longhand order is not fully specified. This review
accepts the narrow interpretation that canonical order for a fixed shorthand
and provider context is stable, rather than chosen from destination order.
The algorithm gives no destination parameter to select canonical order, and
otherwise “canonical” would supply no constraint. The test intentionally does
not demand physical-first or logical-first across engines. If CSSWG explicitly
permits destination-dependent expansion, this relational oracle would need
revisiting; no such exception was found in the current primary text/history.

Rejected routes: invalid value/priority would return before setting, but these
inputs have a successful fresh expansion and passing controls. A same-mapping
ordering exemption does not apply to this pair. Lack of an absolute order does
not excuse retaining an opposite order for the same expansion context.

## Historical issue review

Current retrieved issue 5741 state is open. Issue 1898 discussed all/logical
ordering and setter placement; its comments record the resolution to append
setters, and PR 2516 was merged on 2018-04-11. It provides no all exception.
The current CSSOM text is authoritative over simplified old discussion.
Bug 1410028 and the subsequent setter work are historical context, not proof of
novelty or proof this precise remaining branch is already fixed. Bounded public
searches found no exact new duplicate; no novelty claim is made.

I independently opened current CSSOM/Cascade/Logical and GitHub issue pages with
the web tool. Direct API fetching failed DNS; dated producer-retained primary
API/HTML responses were copied and read independently. Their provenance and
hashes are retained. The web issue 5741 page was cached; its state agrees with
the dated API response. No external bug or issue was filed.

## Actual implementation and caller/provider chain

Complete source snapshots bind the following path:

- C++ ParsePropertyValue/ModifyDeclaration reaches Servo set_property with fresh
  SourcePropertyDeclaration; successful parsing reaches set_property_to_declarations.
  That function creates a fresh update plan, prepares under a read lock, invokes
  the mutation closure once only if needed, and updates under a write lock.
- PropertyDeclaration::parse_into records all in separate AllShorthand storage.
  AllShorthand::declarations and its complete iterator use All.longhands for
  both CSS-wide and WithVariables values. The generator builds logical-first,
  then physical/other properties, excludes direction/unicode-bidi and filters
  applicable content/pref entries. The generated iterator preserves order.
  This actual fixed order supports the test's provider-context premise but is
  not itself a normative physical/logical ordering rule.
- Ordinary prepare_for_update scans backward. A later opposing-mapping member
  selects AppendAndRemove even for equal values. Otherwise it chooses None,
  UpdateInPlace or Append. The executor preserves aligned value/importance
  storage and repairs indices after removals.
- The special all preparation checks only presence, value and importance. Its
  executor updates existing slots in place and appends missing entries. Neither
  consults the ordering condition. This exactly explains the stale pair order.
- Parsing extend/push has different importance precedence and replaces by
  removing/appending. It explains the cssText control; it is not a drop-in
  CSSOM setter because normal parsed declarations cannot replace important ones.
- IndexedGetter exposes the vector through Servo GetAt. SetCSSDeclaration and
  nsStyledElement wrap the resulting block directly; no hidden reparse repairs
  ordering on the ordinary div path.

The current padding metadata independently confirms same group `padding`, with
logical true only on padding-block-start. Complete planner/executor and provider
bodies were read. Searchfox discovery found prepare_for_update successfully;
this installed CLI does not support the requested --permalink option. Exact
retained local bodies, not a fabricated Searchfox revision, bind this review.

## Actual browser observations

The committed diagnostic closure authenticates all fourteen inputs. Per-phase
source/config/binary pins are stable; raw and console digests match. There are
24 subtests and one harness OK: eight all-order FAIL, sixteen controls PASS.
Values are initial, inherit, revert and var(--all), each normal/important.
Fresh order is calibrated as padding-block-start before padding-top.

Each failure is the first seed, padding-top then padding-block-start, which
remains in that order. The assertion aborts before the second seed executes in
that failing subtest. Both seeds execute in passing longhand/cssText controls.
The eight failures therefore establish the first-seed discrepancy; they do not
establish runtime observations for an unexecuted second all seed. Neither
property values nor rendering divergence are measured by this diagnostic.
The shared project build contains earlier repairs; no isolated upstream or
release-browser claim follows.

## Minimal repair constraints and preparation gate

Factoring the existing ordinary decision into a private per-declaration helper
is a suitable narrow design. Normal batching can retain its behavior. All
preparation must consult that helper including ordering; all execution must
compute each decision against the updated current block. It must not materialize
all into the smaller ordinary shorthand buffer or reuse stale per-batch indices.

The proposed initial-state any(non-None) preparation gate is sound for existence
of a changing sequential step. If every initial decision is None, induction
keeps the initial state throughout. Otherwise take the first initial non-None:
all preceding None steps preserve the state, so that decision is still changing.
This argument requires deterministic/stable expansion, identity/equality/group
metadata, and None implying state identity. It is not a proof that final
serialization differs.

In fact, setting an identical fully expanded all can move logical declarations
after physical ones, then physical declarations back after logical ones, ending
in the original order. The gate can still return true. CSSOM permits true even
when final serialization is unchanged; its suggested remove/append algorithm
has this behavior. Do not turn the gate into a “no MutationObserver event”
assertion or demand equality with final cssText inequality.

For execution: None skips; UpdateInPlace replaces value and aligned importance;
AppendAndRemove removes both aligned entries then appends; Append inserts ID and
appends value/importance. Keeping the membership bit during internal
remove-and-reinsert is valid only without an intervening observer. Public
uniqueness/set/vector agreement must be restored before returning. Preserve
custom/direction/unicode-bidi and pref filtering, normal-over-important CSSOM
assignment, and the outer one-call mutation policy. Parsing push is unsuitable.

Sequential all retains linear scans and can add vector shifts; an O(n²) bound
is plausible just as existing scans already cost O(n²), but constants can grow.
No performance measurement was run. Benchmark a concrete regression risk if
needed; do not change ordinary batching merely to simplify the proof.

## Exact draft candidate source review

Root candidate declaration_block.rs is
`8474218db02f8787c212f47a08be33a468553b4ab809e774f2d26d4ae098812a`.
Its complete original/candidate and native.patch are retained. The new private
declaration_update method is an exact whitespace-only transfer of the former
ordinary map closure, verified independently. Ordinary batching calls it with
the same inputs; counters/removal fixups and final zip are otherwise unchanged.
The all preparation and sequential executor implement the design above, including
None, in-place update, aligned remove-and-append, and the membership insertion.
No new fixed-capacity materialization or stale-plan reuse appears. Artifact-only
patch apply/reverse reproduces exact complete source bytes.

No source blocker was found. This is candidate source approval, conditional on
the existing canonical-input/metadata/non-reentrant provider premises. Its native
build, expanded final WPT pair and standalone upstream applicability are root
work and remain outside this frozen discovery review. No candidate browser
success is claimed here. There is no universal refinement theorem in this audit.

## Targeted next gates and formal boundary

Required candidate controls should include unchanged-value preparation:
set all:initial, set padding-block-start:initial to reorder it, then set
all:initial again. Current values already match, so the old preparation can
incorrectly return false. Also test prior important to normal replacement,
excluded properties, and existing ordinary logical setter/all serialization
WPTs. The fixed-order relational oracle should remain independent of any
particular expansion ordering.

The producer's proposed source-bound planner/executor proof is useful, but it
is future work. It must derive None/state identity, sequential all refinement,
aligned storage and first-change admission under actual caller/provider
premises. Ordinary batched refinement requires its real generated shorthand
mapping assumptions; unique identities alone do not justify arbitrary mixed
mapping lists. The present result came from static source/spec inspection and
root's browser probe, not a new Lean verifier finding or universal proof.

## Replay

Authenticate this review's freeze, then run `python3 -I -S check.py`. It checks
its closed roster, copied browser manifest/pins/raw identities, exact source
hashes and primary issue status. It runs no producer imports, network, compiler,
Git or browser. This capsule is an independent discovery/design recommendation;
root owns candidate source, build, paired regression and repair acceptance.
