# Stylo verification roadmap

This tracks the six milestones agreed for the local verification project.
A milestone is complete only when its stated evidence has been checked and its
implementation and claims have received independent agent review. Work stays
local; Try pushes and patch submission are outside the current authorization.

## Baseline

At `44a48f048844`, the runner checks 23 Lean theorems, ten Rust regression tests,
and three differential tests including 27,661,824 comparisons. Two browser
regressions passed three local runs after a native rebuild. These establish
filter arithmetic, valid-history preservation, and conditional ancestor
rejection safety. They do not establish caller hash completeness or cache
lifetime correctness. See [README.md](README.md) for assumptions and reproduction.

## Milestones

| Milestone | Status | Required evidence |
| --- | --- | --- |
| 1. Strengthen differential checking | Complete (`c2c0c4afcc31`) | Adversarial hashes, deeper trees and nested selectors, automatic failure reduction, and instrumentation establishing filter execution. A controlled faulty hash provider must demonstrate that the oracle and reducer detect and retain a real mismatch. |
| 2. Close hash-normalization gap | Complete (`fc3af7e2b69a`) | Checked equivalence of raw and masked hashes for insertion, removal and lookup; a composed history/packing/rejection theorem using raw element hashes. |
| 3. Exercise Gecko state changes | Complete (`700d5df737ab`) | Local browser checks of class/ID/attribute mutation, reparenting, removal/reinsertion, namespaces/case, shadow roots and slot reassignment, with style flushes and independent expectations. Assess feasibility of a test-only filter bypass and document coverage limits. |
| 4. Prove StyleBloom recovery and clearing | Clear proof committed (`a0bd75a11f4e`); recovery and adapter contracts in progress | An invariant connecting ancestor path, hash stack, filter contributions and saturation history; valid removals, required-hash retention, and empty state after clearing. Account for siblings, ancestors and separate roots; connect extracted production transitions to the invariant. |
| 5. Verify relative traversal and caching | Production extraction succeeds; loop/cache proofs in progress | Termination, region coverage and boundary preservation for the production walk; conservative handling of unavailable hashes and correct children/subtree cache reuse under explicit DOM/lifetime assumptions. |
| 6. Prove selector hash collection soundness | Extraction and iterator refactor in progress | A declared selector subset with a production connection: matching implies every collected rejection hash is represented in the appropriate DOM region. Extend through combinators, is/where and relative selectors; enumerate unsupported constructs. |

## Recommended next sequence

The priority is connecting the checked filter operations to their production
callers. The first three milestones already provide differential, composition,
and browser evidence; the remaining work targets the assumptions those checks
currently leave open.

1. **Preserve the checked clearing result as a reviewable commit (done).** Commit
   `a0bd75a11f4e` contains the production clear helper and its thirteen audited
   theorems separately from recovery work, retaining exact theorem and axiom checks. The integrated
   suite currently passes 49 theorems; the native build with the current caller
   refactors also succeeds.
2. **Finish milestone 4: ancestor recovery.** Prove that rebuilding, trimming,
   finding a common parent, and flushing pending ancestors produce the required
   ancestor path. Connect the production adapter's element and hash stacks to
   the filter history and historical maximum. Check pending-stack reversal,
   finite-depth assumptions, and `usize` arithmetic bounds. Cover separate roots
   and both recovery configurations. Completion requires discharging the adapter
   obligations; conditional theorems about an abstract stack are intermediate
   results.
3. **Finish milestone 5: relative traversal and cache reuse.** Integrate the
   production traversal proofs for termination, exact child/descendant coverage,
   root boundaries, and unavailable hashes. Then check hint-to-region selection,
   sibling anchors, cache keys, and entry transitions. State the map-library
   contract and establish the caller's immutable-DOM/stable-identity cache epoch.
   A failed filter build must never publish a partial filter for rejection.
4. **Finish milestone 6: selector hash collection.** First resolve extraction
   of the actual collector and iterator operations. Then prove, for an explicit
   selector subset, that a match supplies every collected hash in the correct
   region, including singleton `:is()`/`:where()`, combinators, quirks handling,
   and the four-hash limit. Compose this with the existing raw-hash rejection
   theorem. Record unsupported constructs and provider assumptions explicitly.
5. **Validate the final production changes together.** Regenerate all models
   from the final source, audit all integrated proofs, run the Rust regressions
   and differential corpus, rebuild Firefox, and repeat all five browser tests.
   Any new defect needs a reduced case that fails before its fix and passes
   afterward. The final browser rerun is still pending.
6. **Prepare the local review checkpoint.** Review proof assumptions and Rust
   semantics independently, organize signed commits by result, and update the
   evidence and reproduction instructions. Leave the work local. This checkpoint
   is reached when milestones 4–6 meet their contracts, or a precise toolchain
   blocker prevents further production-connected proof work.

### Toolchain decision point

Selector collection currently has the greatest extraction risk: mutable iterator
borrows, associated types, and the monomorphized array-default translation have
exposed limitations in the pinned tools. Prefer small production refactors whose
semantics can be reviewed directly. If those cannot preserve a clear connection
to the original algorithm, retain a minimal tool reproducer and document the
unproved obligation. A surrogate model or additional trusted axiom does not
complete the milestone. Such a checkpoint leaves the affected milestone open.

Broader selector grammar, a browser filter-disable switch, another supported
platform, and removal of the unused iterator external dependency are follow-ups
after these caller obligations. Expand sooner only when a concrete proof or
counterexample requires it.

## Review and revision log

- Initial execution: milestones 1 and 3 use independent implementation agents;
  the main agent works on milestone 2. A separate reviewer audits the six-part
  plan and the extraction boundaries for milestones 4–6.
- Plan review: the existing counter relation permits stale saturated slots even
  when the live multiset is empty. Milestone 4 therefore needs a stronger
  exactness invariant under the historical stack bound, not merely the existing
  no-false-negative relation.
- Plan review: distinguish selector-DOM parent/child links from StyleBloom's
  traversal-parent relation. Relative cache proofs require stable DOM contents
  and element identities within a cache epoch. Browser mutations must test new
  style/query epochs rather than assume that retained maps tolerate mutation.
- Keep mathematical models, extracted Rust guarantees, bounded exploration and
  browser evidence distinct. A model proof alone does not complete a production
  proof requirement.
- For each defect, retain a minimized reproducer and demonstrate failure before
  the fix and success afterward. Commit changes in independently reviewable pieces.

## Evidence recorded during implementation

- Milestone 2: thirteen additional theorems pass in the full extraction pipeline,
  for 36 audited theorems total. Exact Result equalities cover insert/remove/
  lookup masking for all states, history normalization preserves raw-hash
  histories, and packing/rejection composition accepts a live collected prefix
  with zero padding (including lengths zero through four). No new external axiom
  was allowed. Independent contract review found no blocking issue; the committed theorem
  covers every planned collection length.

- Milestone 1: the expanded harness adds five hash profiles and 24-node chain,
  branching and multi-root shapes, including nested selectors through depth 16.
  The release corpus comprises 33,450,624 comparisons. Controlled omitted-class
  hashing proves reduction preserves ancestor and warmed-cache relative failures.
  Independent review required counting successful hash collection separately
  from disabled baseline attempts and preserving class/ID attribute consistency;
  both changes are implemented and covered by passing debug/release checks.
- Milestone 3: three new WPTs exercise dynamic DOM, shadow/slot, and quirks-mode
  cases. Three local repetitions passed all 33 checks. A production bypass would
  require plumbing through both ancestor and relative matching; it is deferred.
  Computed-style checks establish observable behavior, not internal hit counts.
- Milestone 4 extraction gate: Charon extracts the caller adapter, but Aeneas
  fails on the hash-producing closure and AtomicRefMut operations. The actual
  high-water and clear operations now live in a shared production helper that
  extracts successfully. Full recovery remains required and is being investigated.
- Milestone 5 extraction gate: the pinned Aeneas cannot translate an outer-loop
  break inside the nested subtree walk. Splitting the existing successor walk
  into a production helper permits extraction. Replacing the cache closure with
  explicit occupied/vacant entry branches also permits extraction of the caller.
  Hashbrown map entry operations still require an explicit library contract;
  the traversal and entry-update proofs are awaiting integration and review.

- Clear-proof review identified an adapter obligation: production pushes append
  to the hash stack while logical insertion histories prepend. A permutation or
  reversal argument must connect the actual stack to the history before applying
  the clear theorem. This was resolved by making HighWaterHistory append in
  production order and proving that optimized clearing establishes a fresh
  empty/high-water-zero history. Thirteen caller-clear theorems now pass in the
  main runner, bringing its total to 49. The recovery and adapter obligations
  remain open.

## Maintenance

Remove the unused iterator external dependency from the audited proofs if the
extraction can avoid it without altering production semantics. Check another
supported platform when one is available. Preserve exact theorem/axiom auditing
and reproducible tool versions throughout all six milestones.
