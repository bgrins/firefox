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
| 4. Prove StyleBloom recovery and clearing | Clear proof committed (`a0bd75a11f4e`); conditional recovery algorithm proved; production adapter open | An invariant connecting ancestor path, hash stack, filter contributions and saturation history; valid removals, required-hash retention, and empty state after clearing. Account for siblings, ancestors and separate roots; connect extracted production transitions to the invariant. |
| 5. Verify relative traversal and caching | Complete (`f77c6b0f6042`); combined extraction, 44 declaration audits, and independent review pass | Termination, region coverage and boundary preservation for the production walk; conservative handling of unavailable hashes and correct children/subtree cache reuse under explicit DOM/lifetime assumptions. |
| 6. Prove selector hash collection soundness | Extraction and iterator refactor in progress | A declared selector subset with a production connection: matching implies every collected rejection hash is represented in the appropriate DOM region. Extend through combinators, is/where and relative selectors; enumerate unsupported constructs. |

## Proposed next sequence

The priority is connecting the checked filter operations to their production
callers. The first three milestones already provide differential, composition,
and browser evidence; the remaining work targets the assumptions those checks
currently leave open.

1. **Integrate and commit milestone 5 (complete).** At `f77c6b0f6042`, the combined
   extraction and audit pipeline passed with 66 core theorems and 36 relative
   declarations plus eight bridge theorems. That combined result comprises
   110 audited declarations, including two concrete witness definitions.
   Exact axiom allowlists and the check that excludes the mock
   collector from extracted dependencies pass. The collector preparation
   refactor is separate in `042bf7484d3a`. Provider, map-library, and
   immutable-epoch contracts are documented; this result does not establish
   selector collection soundness.
2. **Discharge milestone 4's production storage obligations.** The recovery
   algorithm is already checked in `95ab84b3ff65`. Connect actual push, pop,
   clear, and pending-stack operations to the element path, hash history, and
   historical maximum. First review the method-by-method extraction prototype:
   its methods typecheck, but composing their borrow-return functions into the
   recovery interface still needs proof. Prove that successful hash production
   is exactly the recorded insertion sequence, including duplicate hashes and
   count/capacity bounds. Completion requires applying the recovery theorem to
   these checked production methods for both recovery configurations.
3. **Resolve the milestone 6 extraction gate before expanding its proofs.**
   Obtain Lean-checkable extraction of the production simple-component helper,
   then the collector and iterator. Keep tool changes and minimal reproducers
   isolated from the default verifier. Check every normalization and opacity
   boundary explicitly. Completion of this step means regenerated code
   typechecks with a reviewed connection to production; emitting Lean text is
   insufficient. If extraction requires broader unsupported tool features,
   record the exact blocker and leave milestone 6 open.
4. **Prove collection soundness incrementally.** Start with the supported simple
   selector components, then combinators and the four-hash limit, singleton
   `:is()`/`:where()`, quirks handling, and relative-selector regions. For each
   stage, state its selector subset and prove that matching supplies every
   collected rejection hash in the appropriate region. Compose those results
   with the ancestor and relative Bloom guarantees. Completion requires a
   production-connected theorem and an explicit list of unsupported constructs.
5. **Validate the final production changes together.** Regenerate all models
   from the final source, audit all integrated proofs, run the Rust regressions
   and differential corpus, rebuild Firefox, and repeat all five browser tests.
   Any new defect needs a reduced case that fails before its fix and passes
   afterward. The current caller-refactor snapshot passes all five browser tests
   for three repetitions (42 checks); repeat after further production changes.
6. **Prepare the local review checkpoint.** Review proof assumptions and Rust
   semantics independently, organize signed commits by result, and update the
   evidence and reproduction instructions. Leave the work local. This checkpoint
   is reached when milestones 4–6 meet their contracts, or a precise toolchain
   blocker prevents further production-connected proof work.

### Toolchain decision point

Selector collection currently has the greatest extraction risk. Generic
extraction encounters iterator borrows, generated trait-field naming, and
recursive selector types behind opaque `Arc` representations. Monomorphized
extraction encounters built-in `Box` representations and array calls whose
declarations are absent. A narrow experimental array-default metadata fix
passes its minimal reproducer but does not resolve collector extraction.
Prefer small production refactors whose
semantics can be reviewed directly. If those cannot preserve a clear connection
to the original algorithm, retain a minimal tool reproducer and document the
unproved obligation. A surrogate model or additional trusted axiom does not
complete the milestone. Such a checkpoint leaves the affected milestone open.

Broader selector grammar, a browser filter-disable switch, and another supported
platform are follow-ups
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
  Hashbrown map entry operations still require an explicit library contract.
  The traversal, entry-update, cache-epoch, and concrete Bloom bridge proofs now
  pass in the combined pipeline and have received independent review.

- Milestone 5 integration: the full runner passes 110 declaration audits
  (108 theorems and two concrete witness definitions), ten Rust regressions,
  and eight differential checks covering 33,450,624 comparisons. The matching
  production snapshot passed a native build and all five browser tests for
  three repetitions (42 checks). The relative audit rejects unexpected axioms
  and missing or duplicate reports; injected negative cases verify rejection.
  On case-insensitive filesystems, the main Lean directory must precede the
  relative directory to avoid its log directory shadowing generated modules.

- Clear-proof review identified an adapter obligation: production pushes append
  to the hash stack while logical insertion histories prepend. A permutation or
  reversal argument must connect the actual stack to the history before applying
  the clear theorem. This was resolved by making HighWaterHistory append in
  production order and proving that optimized clearing establishes a fresh
  empty/high-water-zero history. Thirteen caller-clear theorems now pass in the
  main runner, bringing its total to 49. The recovery and adapter obligations
  remain open.

- Recovery review found that an unconditional push contract could not describe
  the production containers. The checked contract now requires finite capacity
  and parent/root admissibility. Both recovery configurations pass under those
  conditions; production adapter extraction and hash-resource bounds remain
  required. Generated panic-message code introduced native evaluation axioms;
  equivalent explicit checks removed those dependencies instead of allowing them.

- Four additional storage-history lemmas connect append-order high-water
  histories to saturated-counter coverage and successful lookup at arbitrary
  historical maxima. They also establish the exact list and maximum after a
  batch of actual insertions. Independent review and the full pipeline pass:
  70 core theorems plus 44 relative declarations, or 114 audited declarations.
  Production storage/provider methods still need to establish these histories;
  milestone 4 remains open.

- The actual debug zero-check now uses an equivalent early-exit loop. Three
  checked theorems establish termination, the exact 4096-counter zero predicate,
  and success on a zero filter. The combined pipeline passes 117 declaration
  audits; all 73 core theorems now require only standard logical axioms. The
  relative audit also removes every iterator-external allowance. This closes
  the old unused-iterator maintenance item and supplies the zero-check fact
  required by the production storage adapter's debug assertion. A fresh native
  build including the collector iterator refactor (`ceaef3161627`) passes all
  five browser tests for three repetitions: 42 checks, no unexpected results.

## Maintenance

The unused iterator external dependency has been removed. Check another
supported platform when one is available. Preserve exact theorem/axiom auditing
and reproducible tool versions throughout all six milestones.
