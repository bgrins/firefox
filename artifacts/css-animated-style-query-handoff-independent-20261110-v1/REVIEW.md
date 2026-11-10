# Independent review: animated style-query handoff

**Verdict:** the revised two-file candidate is sound enough to proceed to a native
build and the bounded browser controls below. No blocking correctness issue was
found in the reviewed handoff. An initially quadratic ancestry walk was identified
and corrected before this verdict. This is source review, not successful native
compilation, runtime validation, or a proof of general animation convergence.

Reviewed final patch: `reviewed-final.patch`, SHA256
`75ab9dc8feec80bae0ac17a4b3cdf141373372283c2cb6721491dd7ea3993d1b`.
The final binding differs from the reviewed semantic version only by moving the
`Mutex` import before the existing atomic import. This format-only difference
was independently checked; all other candidate bytes are unchanged.
`check.py` independently authenticates 11 source files against Git revision
`d82e1bf0282ecb524b016cedfbba4f6d4188d449`, reconstructs the exact two-file patch,
and verifies the existing font capture condition/body and replay block are
byte-identical. `candidate-final/` freezes the reviewed source. The original
`reviewed-v1.patch` is retained only to document the addressed performance finding.

## Why this repairs the observed handoff

`accumulate_damage_for` produces different child hints for unnamed style queries
and named containers. `recalc_style_at` returns these generated hints after its
animation traversal work. During an animation-only traversal, query-dependent
selector matching is deliberately not performed; preserving a query hint alone
does not make ordinary traversal discover it without a normal dirty ancestry path.

The candidate records the exact generated query mask with its producing element.
After `driver::traverse_dom` returns, it reapplies that mask to each styled
traversal child and marks the path from the producer to the returned traversal
root. The existing subsequent normal traversal can then consume the work. No
document-level drain loop, scheduling retry, unconditional subtree matching, or
change to animation sampling is introduced.

The measured color fixture is a suitable regression: the source changes and
ordinary matching yields the expected color, while animation-only updates leave
both named and unnamed consumers stale even after frames. It does not rely on
the separate animation-tainted `var()` question or timeline-registry behavior.

## Checks and remaining assumptions

| Area | Assessment |
| --- | --- |
| Exact masks | The collector intersects the generated child hint with `RESTYLE_IF_AFFECTED_BY_STYLE_QUERIES` and `RESTYLE_IF_AFFECTED_BY_NAMED_STYLE_CONTAINER`, then inserts that same mask. It neither upgrades unnamed hints to named hints nor substitutes the font hint. Existing nonanimation propagation retains the named hint across deeper descendants and handles unnamed consumers at the appropriate next level. |
| Producer location | Recording each producer is necessary. Replaying an unnamed query hint only at the traversal root would miss deeper producers because that hint does not propagate arbitrarily. The candidate retains the actual producer rather than one traversal-global boolean. |
| Dirty root | Marking begins at the producer, because its styled children receive the hint, and ends at the root returned by `traverse_dom`. This is the traversal-token root, not an assumed document root. The replay must remain within that fixed flattened traversal tree; the existing `traversal_children`/`traversal_parent` relationship supplies that invariant. No dirty bits above the actual root are needed for the immediately following normal traversal. |
| Rooted-path early stop | The revised candidate stops only at an ancestor in its own replay-local set. It does not trust preexisting dirty bits. Newly discovered paths are marked from rootward end toward the producer, then entered in the set, so every certified node already has a complete dirty path to the traversal root. All child hints are inserted before this ancestry shortcut; a previously certified producer does not suppress a new mask. |
| Pseudos | The candidate uses the same traversal children as ordinary hint propagation and does not change pseudo matching or dependency flags. Element-backed pseudos follow that traversal. Eager pseudo styles rely on existing dependency recording/matching behavior; the patch does not prove that behavior complete, so one descendant `::before` consumer is a useful control. |
| `display:none` | A producer that becomes `display:none` has its descendant style data cleared by existing traversal code. The replay skips children without styles, so it does not recreate data or set new descendant bits for an empty styled subtree. Later reveal uses normal initial styling. The preorder traversal processes a parent before queuing children, preventing the replay list from retaining an already-processed descendant that a later ancestor visit clears within the same traversal. |
| Borrowing and threads | Worker code drops the producer's data borrow before locking the collector. The mutex protects only the producer/mask list. Replay happens after the scoped parallel traversal and thread-local traversal contexts have completed. Each child's mutable data borrow ends before ancestry flags are written. No worker mutates dirty ancestors through this new path. |
| Lifetimes | `SendElement<GeckoElement<'le>>` remains scoped to the traversal object and is consumed inside the same `traverse_subtree` call. It is not persisted to a task queue. Safety relies on the existing traversal guarantee that DOM topology and node lifetimes remain stable during this call; the patch adds no script entry or DOM mutation. Rust compilation must still validate the new lifetime parameter and auto-trait bounds. |
| Existing font fix | The `AtomicBool` field, capture condition/body, accessor and root-child font replay remain intact. The query collector is separate. `CHECK.json` verifies the capture and replay blocks byte-for-byte. Runtime font behavior should still be covered by the existing #160 regression. |
| Scheduling scope | Only generated query work from animation-only traversal enters the new collector. The normal traversal is already called after that traversal by `Servo_TraverseSubtree`. The patch does not alter `ServoStyleSet::StyleDocument`, its second animation traversal, or any drain loop. |

## Addressed performance finding

Version 1 marked the entire child-to-root path for every styled child of every
producer. An inherited custom property can change at every node of a deep chain,
so repeated ancestor walking can require a quadratic number of steps.

Version 2 first seeds all children and then marks ancestry once per producer with
at least one styled child. Its private rooted-path set makes each newly discovered
ancestor enter the marking path at most once; later producers terminate on an
already certified path. Apart from expected hash-table costs, ancestry work is
bounded by the number of distinct visited ancestors plus producer lookups. Child
enumeration remains proportional to the children of recorded producers. Collector
mutex contention and allocation are still costs, but there is no remaining
quadratic ancestor walk in this candidate.

## Bounded browser controls

Keep the existing four color callbacks and four timeline callbacks. Add at most
five focused configurations, sharing helpers and ordinary-update controls:

1. A named animated producer below a shared traversal root, with a deep consumer
   and an intermediate local custom-property override. This requires the named
   hint to reach the consumer without depending on inherited-value propagation.
2. An unnamed nearest-container case with the intermediate override. The nearer
   container's unchanged value must govern the query; compare an ordinary update.
3. Two sibling animated producers with on/off/on samples. This exercises OR-ing
   multiple pending masks, root selection below the document, and repeated
   consumption without stale state. A modest wide sibling variant can exercise
   parallel collection without introducing a separate stress suite.
4. A query affecting a descendant's `::before` color/content, with an ordinary
   mutation control. This checks existing pseudo dependency routing.
5. A hidden subtree revealed after the sampled value changes. Assert the query
   result after reveal and use a normal-control counterpart; do not demand
   retained style data under `display:none`.

Rerun the existing #160 animated-font regression. A short deep-chain check can
guard the addressed ancestry cost, but there is no need for a broad performance
investigation before the focused fix compiles and its correctness cases pass.
Use deterministic paused animation samples and computed-style reads; do not make
waiting for extra frames the repair criterion.

No live native file, index, build, browser process or commit was changed by this
independent review. The review does not establish bug novelty; the companion
investigation identified bug 2085413 as relevant prior art.
