# Animated style-query producer handoff

Source-pinned review and unbuilt candidate, 2026-11-10. Native basis: `d82e1bf0282ecb524b016cedfbba4f6d4188d449`. No live native/test edits, browser executions, builds, or commits by this capsule.

**Conclusion:** this is the already reported [bug 2085413](https://bugzilla.mozilla.org/show_bug.cgi?id=2085413), not a newly discovered upstream issue. The inspected implementation produces normal style-query hints during animation recascade but does not ensure their normal traversal is reachable. The two-file `query-handoff.patch` retains each producer's actual query mask, replays it after worker completion, and marks the necessary ancestor paths. Existing #160 font behavior is unchanged. No repeated-drain change is included.

## Evidence and prior report

The parent-owned timeline calibration has two animated failures and two ordinary passes, with an OK harness. In each animated case the container's `--gate` value changes to `on`, but the literal color declaration inside the query stays black. Thus failure precedes the timeline-source assertion. No `var()` occurs in the literal timeline declarations; the animation-taint substitution problem is separate. The parent reports a color-only reduction in both named and unnamed cases, still stale after repeated reads and two animation frames and repaired by a class-induced rematch. That reduction was not executed or independently authenticated by this agent; the copied four-callback runtime is the authenticated input here.

[Bug 2085413 comment 0](https://bugzilla.mozilla.org/show_bug.cgi?id=2085413#c0), opened October 23, 2026, describes the same split: animated `--flag` changes a `var()`-driven background while the descendant style query never matches. The fetched bug is NEW, S3/P3, unassigned. Its author reports Nightly 161 failure and Chrome success; those are reporter observations, not our cross-browser measurements. The current local calibration adds controlled source toggling and reduction evidence. No new bug count, release regression attribution, or security claim follows.

[CSS Conditional 5 style queries](https://drafts.csswg.org/css-conditional-5/#style-container) test the container's computed values. Its [animated-containers rule](https://drafts.csswg.org/css-conditional-5/#animated-containers) requires query evaluation changes caused by animation effects to participate in a style change event. This directly supports re-evaluating the literal descendant rule; it does not require admitting an animation-tainted value into a nonanimatable destination.

## Exact source path

| Stage | Pinned implementation and consequence |
| --- | --- |
| Change detection | `GeckoRestyleDamage::compute_style_difference` compares inherited and noninherited custom-property maps and reports `custom_properties_changed`. |
| Producer | `MatchMethods::accumulate_damage_for` emits `RESTYLE_IF_AFFECTED_BY_NAMED_STYLE_CONTAINER` for a named container, otherwise `RESTYLE_IF_AFFECTED_BY_STYLE_QUERIES`. A container-name change also emits the named mask. |
| Query dependency | `StyleQuery::matches` records `DEPENDS_ON_CONTAINER_STYLE_QUERY` before evaluating the condition, including a false query. |
| Animation limitation | `ElementData::restyle_kind_for_animation` selects recascade/replacement, never selector matching. |
| Hint storage and admission | `recalc_style_at` combines its newly generated child hint with propagation. `note_children` inserts it into child data, but animation admission uses animation/recascade hints and sets animation dirty ancestry. `RestyleHint::propagate` preserves nonanimation bits on the element while returning no normal propagation during that pass. Retained child hints alone do not make an otherwise clean ancestor path reachable. |
| Missing handoff | Committed `RecalcStyleOnly` records only the font/writing-mode child mask in its AtomicBool. `traverse_subtree` replays only that font mask at traversal-root children. It has no query handoff. |
| Consumer | The next ordinary `traverse_subtree` is already called by `Servo_TraverseSubtree`. If admitted, `needs_to_match_self` recognizes the query mask plus the dependency flag and returns matching work. Named masks propagate further; unnamed masks intentionally do not propagate blindly through the subtree. |

This is a source explanation consistent with the browser observation, not an instrumented observation of each native edge. Do not describe the bug as unconditional hint deletion: the missing reachability and the lack of matching during animation traversal are central.

## Candidate scope

The candidate adds a separate query queue to `RecalcStyleOnly`, storing `(SendElement, RestyleHint)` only when an animation pass generates a nonempty projection onto the two query masks. It preserves the existing font AtomicBool, font predicate, and font replay block exactly. Normal traversals create no query records.

After `driver::traverse_dom` returns, the queue is consumed. Each immediate traversal child with existing styled data receives the exact queued mask by union. A missing/unstyled child is skipped; its initial-style obligations remain with existing traversal machinery. No hint is put on the producer itself. If at least one child was seeded, the producer-to-root path is marked with normal dirty-descendant bits, including the traversal root. The normal pass can then discover and match those children. A named mask uses existing deep propagation; an unnamed mask keeps its existing narrower semantics.

The first draft walked an ancestor path for every child and risked quadratic work on inherited-property chains. The retained candidate marks one path per producer and uses a local set of fully rooted paths. It stops only at a path certified by this replay, never at a preexisting dirty bit. It installs each newly discovered prefix from rootward end to producer before certifying it. Under a finite stable traversal tree, path work is bounded by distinct visited ancestors plus producer admissions, in addition to enumerating producer children. Hash-set complexity is expected/amortized; no adversarial worst-case hashing claim is made.

The queue is protected by a mutex and element-data borrowing ends before queue insertion. `traverse_dom` uses a scoped pool; queued raw element wrappers are consumed after that scope completes, within the same restyle operation. `SendElement` provides the existing cross-thread wrapper, not ownership or a new lifetime proof. Stable DOM/traversal-parent identity, root ancestry, no intervening script mutation, and existing pseudo/initial-style conventions remain native assumptions requiring review and runtime controls.

## Relation to held #160 and convergence

`fix160.patch` preserves the committed font repair for comparison. The separately copied `combined-semantic.patch` replaces its root-level boolean with producer-local font replay and changes `ServoStyleSet::StyleDocument` to repeat an animation drain. That combined patch still filters only the font mask: it does not include either query class. Its earlier successful font comparisons therefore do not certify this query handoff.

This candidate neither adopts the combined producer implementation for font work nor changes `ServoStyleSet.cpp`. It does not release #160's hold. It can be reviewed as a separate query repair on this branch; a clean-upstream version would need adaptation around the branch's existing font collector. The patch is not presented as a standalone cherry-pick onto an untested upstream revision.

The finite queue replay is not a proof that animation/style dependencies globally converge. Query matching can install literal animation or timeline declarations that produce more animation work. The color-only case deliberately avoids such feedback. The named-timeline experiment must be rerun only after the basic query repair passes; then any new requests are a separate scheduling/convergence obligation. No global convergence theorem or broad drain loop is justified by this patch.

## Existing coverage and validation boundary

The pinned `custom-property-style-query-change.html` tests named/unnamed registered and unregistered values changed with inline `setProperty`; it has no animation driver. Its current metadata has a conditional 32-bit optimized CRASH expectation, not a specific animation-query annotation. `animation-container-size.html` animates width and checks a size query, not a custom-property style query. Targeted Searchfox discovery and canonical WPT directory listing found this neighboring coverage; this is not a full WPT inventory.

Root should build and run the color-only named/unnamed calibration first, then depth, multiple children, several producers, registered noninherited input, pseudo targets, display-none/reveal, and ordinary-change controls. Add a bounded deep-chain diagnostic to ensure ancestry replay is not quadratic. Only after those checks should timeline source changes or transition-start behavior be claimed. No callback has run with this candidate yet.

`check.py` authenticates 15 source/config/test files against the pinned Git revision, applies the candidate only in a temporary copied-source directory, compares exact result bytes, and checks that the original font blocks remain unchanged. Temporary replay copies are removed. `FILES.json` freezes the capsule. Rustfmt with the explicit Servo config reports the same preexisting font-store line-wrap difference in both baseline and candidate; the candidate adds no further formatting difference. The initial check without the Servo config is retained as a failed preparation attempt, not a successful formatting check. No native compilation or test pass is claimed.
