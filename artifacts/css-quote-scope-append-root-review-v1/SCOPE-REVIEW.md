# Quote append scope review

Status: root source/spec and retained-evidence review; full formal implementation and independent acceptance remain required.

The current [CSS Containment draft](https://drafts.csswg.org/css-contain-2/#containment-style) requires quote operations to inherit the surrounding entry depth while keeping internal changes inside a contained subtree. Elements without a principal box do not establish this boundary. The 15 October 2026 draft was checked on 19 October. This is the reference contract; cached native depth is not an oracle.

## Native chain

`ContainStyleScopeManager::GetOrCreateScopeForContent` walks flattened parents, excludes display:contents, and recursively constructs the enclosing scope before linking a new child. The constructor links even an empty intermediate scope. Therefore a dependent grandchild implies a direct child; the new `HasChildScopes` predicate must not be modeled as only checking child quote lists for nonemptiness.

`nsQuoteNode::InitTextFrame` inserts and calculates an appended node immediately, then returns the new child-presence dirtiness result. The frame constructor dispatches a true return to `QuotesDirty`, which accumulates the dirty flag and requests a layout flush. `RecalcQuotesAndCounters` clears the flag before traversal under a script blocker. `ContainStyleScope::RecalcAllQuotes` recalculates its list before recursing into children. The theorem needs this actual ordering and an explicit delivery premise; a dirty flag is not a completed refresh.

`GetDepthBeforeFirstQuoteNode` checks ancestor lists until it finds a preceding quote. Its search compares the original scope content against flattened-tree pseudo-frame content at each ancestor, rather than replacing the search anchor with the ancestor boundary. The independent ordering model must preserve this distinction, empty ancestors, and pseudo ordering. The source search uses a binary search, so ordered-list construction is an obligation, not an assumed consequence of a correct lookup.

`RecalcAll` publishes changed text only when cached depth changed, a text node exists, and the quote is real. Correct-depth implies correct-text only with a stable quotation provider. Explicit pairs, exhausted pair lists, no pairs, zero-clamped closing, UTF conversion and automatic language selection need separate provider contracts. Language mutations are not repaired by this candidate.

## Coverage and limits

The retained 64-case WPT combines all four operations, initial depths zero/one, direct/nested boundaries, optional trailing quote and before/after insertion. Its Ahem calibration, explicit expected widths, fresh equivalents and removal restoration distinguish stale generated text from invalid input or a broken font. The five-loop product is 4 × 2 × 2 × 2 × 2 = 64. Twelve recorded baseline failures become passes. Additional retained tests include three unchanged expected failures; they are not new regressions or successes.

No native semantic defect was found in this read. This is not an independently completed native review or a formal acceptance. Before acceptance, the promised model must retain arbitrary finite edit/flush histories, deferred stale caches, lazy scope ownership, destruction/reconstruction, shadow distribution/order and changed-text publication. `DestroyScope` recursively removes children before the parent; `DestroyQuoteNodesFor` walks the owning scope and ancestors, so lifetime/cleanup correspondence must cover both mechanisms. Machine depth overflow, allocation, text notification reentrancy and native scheduler/lifetime behavior remain explicit boundaries until discharged.

`INPUT-IDENTITY.json` authenticates the existing gates and pins current source. No new browser run or isolated upstream build was performed here. Searchfox was used for caller discovery; local candidate and caller bodies were inspected. The webspec-index executable was unavailable, so the primary draft was read directly.
