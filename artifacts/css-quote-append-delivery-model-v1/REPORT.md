# Contained-quote append: local demand conservation

**Result:** the focused append/dirty-delivery obligation is proved in Lean, with a concrete counterexample to the original shortcut. It is useful supporting evidence for the separately reviewed native repair, not a prerequisite to indefinitely postpone a demonstrated browser fix. There is no canonical integration, new accepted bug, native extraction, or full containment theorem.

No existing quote-depth Lean model was found in the named probe/fix capsules or canonical quote modules; root confirmed no known module beyond the formal-target draft. This is a new bounded companion grounded in the pinned quote implementation. The unrelated string/token quote models were not reused. Only the existing pinned Lean toolchain and its implicit Init import are used, read-only. The very broad FORMAL-TARGET-DRAFT remains historical proposed scope, not accomplished work.

## What is represented and proved

`Op` has open/no-open/close/no-close. `after` increments opens and saturates closes at zero. `cell` retains depth-before and generated text, including no output for non-real quotes and close at zero. `scan` is a declarative fold over operations and a deterministic provider; it never reads cached values. `finish` gives the parent exit depth.

`State` has an ordered parent prefix, cached parent exit/depth/text, an optional retained child list, its independent cached depth/text, and the global dirty bit. The child is fixed after the parent prefix in flattened order. Some empty child list still denotes a child scope, distinct from no child. Appends are last in the parent list and before this child. Parent entry depth and provider are fixed for the history.

`append` uses the **cached** parent exit to compute the appended node, preserves all prior parent cache cells, leaves the child cache untouched, and ORs child presence into pending dirtiness. Its initial invariant requires parent caches already correct; it allows an arbitrary stale child cache when dirty. `deliver` explicitly models the delivered parent-first recalculation and text publication. It does not model scheduler fairness or claim that requesting a flush immediately performs it.

The main conclusions are:

- `scan_append` / `finish_append`: immediate last-node calculation preserves the earlier parent prefix and produces the same parent result as declarative traversal.
- `append_conserves`: correct parent caches plus either pending dirty demand or correct child cache remains true after candidate append. A clean-state freshness assumption is not silently imposed on the child.
- `histories_conserve` / `delivered_history_fresh`: for arbitrary finite sequences of these appends and delivered flushes, demand is conserved, and one final **actual** delivery yields declarative depth/text. Repeated edits may cancel the net depth change while dirty remains set.
- `leaf_append_unchanged` / `leaf_append_fresh`: without a child, candidate and original append states coincide, and a fresh leaf remains fresh without requiring delivery.

There are 13 named declarations (including algebra/support and four concrete facts), five closed examples and three decisively rejected false controls. This is not 13 new independent CSS obligations and does not change canonical counts.

## Concrete witness and false controls

Start at depth zero with no parent quotes and a retained child `[open, close]`, whose cache contains `(0,"A"),(1,"A")`. Append a parent `no-open` before that child. Immediate parent calculation produces exit depth one; the child's declarative cache becomes `(1,"AAA"),(2,"AAA")`.

The original shortcut leaves dirty false, so a subsequent delivery attempt does no work and retains A/A. The candidate sets dirty, but **before** delivery its child cache is still A/A. A real delivery changes it to AAA/AAA. A third false control clears the demand before delivery and likewise remains stale. Each false claim is rejected by a single anchored `decide` diagnostic proving the proposition false; reduction/type/import failures do not satisfy the gate.

With the explicit Ahem provider from the historical WPT (20px per A), this pair corresponds conditionally to 40px versus120px. Font/layout correctness is not proved here. The fixture contains both open/no-open, two initial depths and nested/order controls; historical browser evidence is referenced, not rerun or newly validated by this model.

## Exact native correspondence premises

| Native source/API | Model relationship and outstanding premise |
|---|---|
| `nsQuoteNode::InitTextFrame`: Insert, IsLast, Calc, return HasChildScopes | `append` only covers the last-parent insertion branch. Native insertion must maintain the assumed flattened order and preserve node ownership. Earlier-list insertion and arbitrary removal are not modeled. |
| `nsQuoteNode::DepthAfter`, Depth, IsRealQuote | Four operations and zero clamp match mathematical natural depths. Native signed-depth overflow/resource limits remain excluded. |
| `nsQuoteList::Calc` | Appended node obtains preceding cached parent depth; parent-prefix correctness is explicit. Ancestor/preceding lookup is assumed to identify this modeled prefix. |
| `HasChildScopes`, scope manager child ownership | Some child causes demand even when its own quote list is empty. Native recursive ownership makes grandchildren imply a direct child; the model does not prove that construction/lifetime invariant or recursively evaluate grandchildren. |
| Frame-constructor InitTextFrame caller → QuotesDirty | Returning true must reach the global sticky dirty bit and layout-flush request. `dirty || child.isSome` models this coalescing, not a new per-node queue. |
| `RecalcQuotesAndCounters` → manager → `ContainStyleScope::RecalcAllQuotes` | Delivery must actually happen, remain lossless under its script blocker and visit parent before children. `deliver` assumes the completed traversal; no fairness, reentrancy or machine execution theorem. |
| `nsQuoteList::RecalcAll` → changed-depth Text publication | `deliver` records resulting current text. Equivalence to native conditional SetData requires existing text/depth consistency, stable provider, real-quote/text-node conditions and successful publication. This is a correspondence premise, not proved by assigning a reference cache. |
| `nsQuoteNode::Text` | Provider is deterministic and stable. Exhausted explicit pairs can be represented by the provider; automatic language lookup, UTF conversion, locale changes and its known language bug are unproved. |

The patch conservatively dirties scopes that precede the appended node too; the model does not assert that every child is affected. Its dependency case is the concrete child-after-prefix witness. General tree ordering, binary search, empty ancestor traversal, scope creation/destruction/reconstruction, shadow distribution, removals, dynamic provider changes and changed-entry histories remain outside this local theorem. They are not concealed in a universal scope claim.

## Replay and evidence

Command:

```
python3 -I -S -B artifacts/css-quote-append-delivery-model-v1/replay.py --output ABSENT_ABSOLUTE_DIRECTORY
```

Actual final replay: session85412, terminal e2b73d, exit0. Lean4.35.0-rc4 runs with `-j1` and `LEAN_NUM_THREADS=1`; model, audit and each false control use owned temporary files. Scratch `.olean` outputs are deleted afterward. The model has no added axiom, sorry or native_decide; audited dependencies are empty or subsets of propext/Quot.sound. Initial draft syntax/decidability failures are retained separately and receive no evidence credit. Final replay logs and generated false-control claims are under `replay/`.

No canonical `.lake` write/full check, native/index/ledger mutation, browser run or build occurred. This is an independent source-grounded formal companion; the native review and actual original/candidate/restored browser validation remain separate evidence.
