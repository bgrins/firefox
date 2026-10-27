# Counter containment append audit

Status: concrete source-level stale-cache hypothesis; no browser observation, accepted fix, or new bug count.

`AddCounterChangeNode` inserts a RESET, SET, or INCREMENT into one containment scope's named counter list. A non-last insertion marks the name dirty and returns true. A last insertion only calculates that node and returns the existing dirty state. Retained contained-child USE nodes are in other lists, so they do not prevent this last-node optimization.

`nsCounterList::SetScope` explicitly lets a first child USE search ancestor containment scopes for a preceding same-name counter. `mScopePrev`, `mScopeStart`, `mCrossesContainStyleBoundaries`, and the resulting `mValueAfter` are retained. Therefore inserting a new last parent-local change before that child can change the child's required source/value without recalculating it. This is the same dependency shape as the quote append defect, although counters have separate scope and reversed-counter rules. The native candidate is not assumed to fix counters.

A clean literal counter name is the discriminating case: start with sibling reset 1, retain a contained child displaying the counter, then insert sibling reset 3, set 3, or increment 2 immediately before the child. Expected child value becomes 3. The immediate post-insertion width is saved before any fresh-construction calibration can incidentally dirty the shared name. A parent-scope USE after the child forces the inserted change off the last-node fast path and serves as a control. Empty intermediate containment scopes exercise ancestor lookup.

The retained source establishes a repair route: `SetDirty` operates on the manager's shared dirty-name set, and `ContainStyleScope::RecalcAllCounters` processes its own counter manager before its child scopes. `RecalcAll` rebuilds node scopes and calculates every node with notification. `DestroyNodesFor` already marks any affected name dirty, so removal is a separate control rather than the hypothesized missing invalidation. Content-based reversed resets can also cause dirtiness during scope setup; the diagnostic deliberately uses ordinary explicit small values. `ValueBefore` isolates non-USE changes crossing containment boundaries; this audit does not propose removing that isolation.

The specification permits this dependency: style containment scopes counter changes, but does not prevent `counter()` or `counters()` from referring to counters established outside the subtree. Counter inheritance precedes reset/increment/set/use. The diagnostic has only one counter nesting level, so both formatting functions have the same expected output. It does not test multilevel counters-stack changes, list-item preference behavior, overflow, reversed counters, or moving/removing an entire containment scope.

Sources: [CSS Containment style containment](https://drafts.csswg.org/css-contain-2/#containment-style), [CSS Lists counter inheritance](https://drafts.csswg.org/css-lists-3/#inheriting-counters). This is an implementation hypothesis supported by those rules, not a fresh complete normative trace.

## Retained evidence and diagnostic

The counter source/header were retrieved using Searchfox and matched the current pinned checkout byte-for-byte; hashes are in SOURCE-PINS.json. The fetched containment manager differs from the known current archived body only in `std::make_unique` versus `MakeUnique` at scope allocation. Relevant counter routing, name dirtiness and traversal bodies agree. The archived current manager is `css-quote-scope-append-probe-v1/candidate-v2-sources/layout__base__ContainStyleScopeManager.cpp`. `caller.log` retains the narrow frame-constructor AddCounterChanges call-site discovery, not a complete frame-constructor body or independent delivery proof.

`counter-scoping-append-invalidation.html` contains 24 proposed cases: three changes, two formatting functions, direct/nested contained uses, and last/non-last insertion. Each records initial, immediate mutated, fresh, post-fresh and removed widths. Ahem and fresh/removal calibrations precede target verdicts. No predicted failure count is enforced. Syntax and inert registration passed; callbacks, WPT lint and browser execution remain unrun. No fixture was installed.

## Smallest next boundary

Run this unchanged fixture on the current browser, retaining complete histories and calibration failures without a prescribed failure count. If the last-change cases alone reproduce stale output, a bounded native experiment can mark the name dirty when a counter change is appended to a scope with child scopes, preserving the leaf fast path and existing parent-before-child recalculation. Verify all three operations and removal controls before proposing a fix. Do not infer that pure USE append, arbitrary counters-stack identity, or all dynamic containment mutations are covered by that experiment. No native patch or controller is included here.
