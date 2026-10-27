# Ordered contained-quote calculation

The extension proves equality of two executable calculations for every finite ordered scope tree, not only one fixed child. It retains generated text, depth-before, nested scope identity by structural position, and empty scopes. This is standalone implementation support, not native extraction or a CSS coverage increment. It is not a prerequisite for accepting independently reviewed browser evidence.

`QuoteAppend.lean` is byte-identical to the existing delivery model. Its natural-number depth transitions, text provider, append algebra, dirty-history result and childless freshness theorem are reused without new proof credit. The new code is in OrderedScopes.lean and Examples.lean; no canonical source or shared compiler output changes.

## Two distinct algorithms

`Content` is an ordered forest: empty; a parent-owned quote followed by the rest; or a child scope with its own content followed by the parent's rest. Each scope's subtree is contiguous, each quote belongs to exactly one nearest scope, and sibling order is preserved. These are explicit structural input assumptions. Native scope construction, flattened-tree ordering and ownership must refine this representation; they are not inferred from the theorem.

`reference` scans contained content directly. A parent quote changes the current parent depth. A child recursively starts at that depth, but its exit depth does not change its parent's continuation. This is a declarative contained-content scan, not a call to the staged implementation.

`staged` first runs `parentPass` over the entire current scope, skipping all child bodies and recording each parent quote's generated cell and depth-after. Only afterward does `assemble` consume that table and calculate children. Its cursor initially contains the ancestor start, then the depth-after of the last consumed parent entry. Child calculation does not consume or change the parent's remaining table. Nested scopes repeat these two stages. A missing entry takes a total-function error branch; the equivalence theorem uses the freshly calculated exact table, so it never licenses arbitrary stale or malformed tables.

`staged_and_assemble` proves both the whole algorithm and its assembly invariant by structural induction, with separate induction hypotheses for child content and the remaining parent content. `staged_eq_reference` exposes the result for arbitrary provider, initial natural depth and finite tree. The proof does not define delivery as reference rendering.

## Preceding-parent lookup and empty ancestors

`scopePositions` records how many parent-owned quotes precede each immediate child. `positions_bounded` proves all these indices lie within the parent list. `precedingLookup` returns the last entry in such a prefix, or the inherited ancestor start for the empty prefix. It is a linear executable lookup, not a claim about Gecko's search implementation.

`parentPass_eq_table` connects the tree projection to the plain parent list. `lookup_parent_prefix` proves lookup equals the mathematical depth after precisely that prefix. `lookup_child_starts` proves that looking up every child position in the complete parent table yields exactly the child entry depths encountered by direct contained-content scanning. Thus a quote after a child is not incorrectly included merely because the whole parent list was computed first. An empty parent list passes the inherited start through any number of nested empty-list scopes. Siblings do not inherit each other's contained quote effects.

`childless_fastpath` proves the staged algorithm reduces to the existing quote-list scan for every childless list. It does not add a scheduler requirement to the already proved leaf append fast path.

## Witnesses and evidence limits

The retained old theorem `QuoteAppend.original_misses_delivery` still demonstrates a missed dirty obligation. The extended `stale_append` witness adds a parent no-open quote before three retained children: one ordinary pair, one nested pair, and one empty scope. Reusing the old child render is unequal to current staged rendering. `new_delivery` proves the exact new depth/text tree. `ordered_starts` exercises interleaved child positions 0, 1 and 2; `end_is_not_preceding` refutes assigning all children the parent's final depth. Seven additional closed examples cover empty ancestors, sibling isolation, empty scopes, zero-depth close saturation, inherited-start lookup and parent-list projection.

Four same-claim false controls reject stale append rendering, using the parent's final depth for every child, losing an inherited ancestor start, and accepting a missing parent table. The last control initially failed to reduce, and the strict diagnostic gate rejected that run. Its retained original log is now an explicit gate regression. The corrected control unfolds the same concrete assembly expression before `decide +kernel`; it decisively proves the same equality false. No proposition or table invariant was weakened. Malformed, unknown-identifier, multiple-error and successful-exit logs are rejected too.

The final pinned Lean4.35.0-rc4 replay uses one thread, audits 13 extension declarations and three existing declarations, and checks the four decisive rejections. These declarations include supporting algebra and concrete examples, not 13 independent CSS obligations. Audited dependencies are limited to propext/Quot.sound. There is no added axiom, sorry or native_decide. Temporary `.olean` files are removed after each replay; initial failed diagnostics remain visible.

## Native correspondence boundary

The pinned archived `nsQuoteList::Calc` obtains the previous same-list depth, or `GetDepthBeforeFirstQuoteNode` searches ancestors for the last preceding quote. The model's cursor and prefix lookup cover those mathematical depths **provided** native ordered lists and ancestor search select the represented prefix. Under contiguous scoped subtrees, no outer-scope quote lies between a child scope boundary and one of its contained descendants, which justifies passing the inherited start through a locally empty prefix. This tree-order premise is not a proof of native search, anonymous/pseudo placement, shadow flattening or scope reconstruction.

The pinned `ContainStyleScope::RecalcAllQuotes` recalculates the parent then visits children, corresponding to the staged schedule. The theorem assumes an actual complete traversal and stable deterministic text provider. It does not prove dirty-signal delivery, script blocking, reentrancy, fallible text publication, locale/font changes or machine signed-depth bounds. Existing delivery-history results stay conditional on actual delivery. Dynamic insertion/removal histories across arbitrary trees remain a later obligation; this extension proves complete current-tree calculation and concrete stale append witnesses, not that every mutation requests it.

Replay: `python3 -I -S -B artifacts/css-quote-ordered-scopes-model-v1/replay.py --output ABSENT_ABSOLUTE_DIRECTORY`. The compiler and Init.olean are external pinned dependencies. No browser, native build, Git, ledger or canonical operation is performed.
