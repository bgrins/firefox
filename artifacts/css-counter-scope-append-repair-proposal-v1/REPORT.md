# Contained counter append: oracle and candidate

Source-level candidate GO for a controlled comparison, not acceptance. The unchanged 24-case diagnostic has no identified oracle error. This author also authored that diagnostic; this is a second source/spec scrutiny, not independent authorship. No browser result is inferred.

## Scoped specification trace

Scenario: generated boxes; ordinary explicit small counter values; seed and inserted change are siblings inside one containment scope; target scopes contain only counter reads. Ahem is loaded and measured.

1. [CSS Lists inheritance](https://drafts.csswg.org/css-lists-3/#inheriting-counters) obtains the counter set from the preceding sibling/parent and its matching value from the preceding element. Seed establishes value 1.
2. [Instantiation](https://drafts.csswg.org/css-lists-3/#instantiating-counters), step 2, removes a same-name counter whose origin is the element or a previous sibling before appending the new counter. Thus sibling reset 3 replaces seed 1; it does not add an ancestor nesting level. Set 3 and increment 2 operate on the existing counter.
3. [Style containment](https://drafts.csswg.org/css-contain-2/#containment-style) scopes changes, but explicitly says counter()/counters() may reference counters outside the subtree. Neither target scope nor its empty intermediate scope changes a counter.
4. [Output functions](https://drafts.csswg.org/css-lists-3/#counter-functions) select the innermost/all in-scope values. There is only one same-name counter here, so both produce the representation for 3, with no separator. Fixed symbols map 1 to AA and 3 to AAAA: 40px and 80px after calibrated 20px Ahem advances.

Verdict: REACHED for the fixture's value expectation. Removing the inserted sibling restores seed 1. The trailing USE changes neither value nor nesting. The counter-changing spans generate inline boxes despite having no text; they are not display:none. Static fresh construction and removal checks are independent calibrations, not replacements for the saved immediate mutation result. The immediate value is captured before constructing another fixture with the shared name.

This is a manual current-spec algorithm walk; the unavailable webspec-index CLI was not bootstrapped during the parent's experiment. Official anchors were read using the web tool. No exhaustive reference-graph enumeration claim is made.

## Actual native mapping

`AddCounterChangeNode` inserts into the parent scope's named list. The target's retained USE nodes are in contained lists and cannot make this insertion non-last. The old fast path computes only the new parent node and returns clean. `SetScope` allows the first USE to search preceding ancestor nodes, and following uses retain that crossing dependency. Their scope links and value/text therefore require recalculation after this parent change.

`SetDirty` inserts the counter name into the shared scope-manager dirty set. Returning true propagates through `nsCounterManager::AddCounterChanges` and `ContainStyleScopeManager::AddCounterChanges` to `nsCSSFrameConstructor::InitAndRestoreFrame`, which calls `CountersDirty`. The retained caller/notification bodies show the layout-flush request. `RecalcAllCounters` traverses own manager before child scopes, retaining the shared dirty name until traversal completes. Each affected list rebuilds scopes and recalculates node values/text. This is existing scheduling, not a new per-child update mechanism.

The two-file native patch adds `nsCounterList::HasChildScopes` and extends the existing non-last invalidation branch to last changes whose scope has children. It marks only the changed name. Pure USE insertion, `ValueBefore` cross-boundary isolation, operation arithmetic, counter styles, scope creation/removal and list-item preference behavior are untouched. It conservatively includes children preceding the new node or having no matching use; selecting only affected descendants would require more dependency bookkeeping. Multiple changes batch in the existing dirty set. No fields or new ownership are added.

Content-based reversed resets can already make insertion dirty through `SetScope`; this remains intact. The candidate does not bypass their full-list reversed initialization, initialize the reserved sentinel as an ordinary number, or clear existing dirtiness. Leaf scopes preserve their old path exactly. Explicit reversed counters may also feed contained uses, so child presence must not be exempted just because a counter is reversed. Removal already dirties affected names and is unchanged. Fresh named lists created after insertion use existing scope setup; retained dependencies are the target of this patch.

## Patch and validation boundary

`native.patch` changes only nsCounterManager.cpp/.h. `native-wpt.patch` also adds the byte-identical diagnostic at css/css-contain/counter-scoping-append-invalidation.html. Exact pre/postimages and hashes are retained. Counter native preimages matched the current checkout and the prior Searchfox archive; no dependency on quote changes is introduced. The existing scope-manager header already exposes GetChildren and is already included by the cpp. Native patch transport and reversal passed in an owned scratch directory, then scratch was removed. No compilation, WPT lint, browser or live patch application occurred here.

Before acceptance, retain the unchanged baseline histories, build this candidate, run the same diagnostic plus existing counter containment/reversed/removal regressions, then restore and repeat. Do not prescribe a baseline failure count. If failures occur at initial/fresh/removal calibration instead of the immediate mutation target, resolve that discrepancy before attributing it to this patch. The 24 cases do not establish general multilevel counters() stack semantics, dynamic scope reparenting, overflow, all reversed-counter behavior, or a performance bound. No native or formal bug count is awarded.
