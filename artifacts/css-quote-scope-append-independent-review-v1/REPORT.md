# Contained quote append: independent native and WPT review

**Source and fixture review GO, with validation qualifications below.** No correctness defect was found in the two native hunks or the 64-case oracle. This review does not accept/count the fix, claim a clean-base build, or replace the planned fresh original/candidate/restored comparison.

The current `nsQuoteList.cpp`, `nsQuoteList.h` and new HTML are byte-identical to the archived tested candidate. An owned scratch reverse/apply round trip recovered the exact two archived original native hashes, removed/recreated the new fixture, and recovered all three candidate hashes. The scratch tree was removed. The patch is three paths and does not require another prototype's source edits. Historical apply checks cover two retained revisions; neither is an isolated build claim.

## Native reasoning

`nsQuoteNode::InitTextFrame` still inserts the new node and immediately calculates its depth when it is last in its own quote list. A last node in a parent list can nevertheless precede an already-existing contained child: that child's quote nodes are in another list. Consequently the local last-node optimization does not establish that there are no dependent quote depths to refresh.

The new `HasChildScopes()` is a constant-time check of the owning scope's child array. It neither allocates nor flushes layout nor introduces a new retained pointer. `mScope` is the existing scope that owns the quote list. A non-last insertion still returns dirty exactly as before. A last insertion with no child scope retains the existing fast path. A later newly created child can calculate from the already updated parent list; it does not require a pre-existing child's invalidation.

The caller's existing `InitTextFrame` result handling calls `QuotesDirty`, which sets a coalescing Boolean and requests a layout flush. `RecalcQuotesAndCounters` clears that Boolean and calls the scope manager under its existing script blocker. `ContainStyleScope::RecalcAllQuotes` recalculates the current list before recursively processing its children. `GetDepthBeforeFirstQuoteNode` searches ancestors for the preceding quote, including through an empty intermediate scope. Thus the existing delivery path reaches both direct and nested affected scopes with the updated parent depth. These claims were checked against the exact archived caller/manager bodies, with Searchfox used for untouched-source discovery.

The test is deliberately conservative: it also dirties when children precede the appended node, or when a close operation at zero changes no depth. That causes possible extra work, not a false-negative invalidation. The extra delivery is the existing root-wide quote recalculation, so it is not appropriate to claim the work is limited to one affected child. There is no per-insertion descendant walk in the patch. No performance measurement was reviewed; pathological repeated flush costs remain unmeasured. Nothing found requires replacing this bounded fix with a speculative selective invalidation algorithm.

## Oracle and specification

Style containment scopes quote effects while retaining the starting depth implied by the surrounding context. Updating a preceding outside quote can therefore change the contained subtree's initial depth; changes inside the subtree do not leak back outside. This is the relevant requirement, not isolation of all incoming quote state. [CSS Containment §3.4](https://drafts.csswg.org/css-contain-2/#containment-style).

Open/no-open increase depth; close/no-close decrease it with a floor at zero. The no-quote forms emit no glyph. Opening and closing marks of the target pair use the same depth's selected string pair. With Ahem advance 20 and strings of lengths 1, 3 and 5, the target width is `40 * (2 * depth + 1)` over this fixture's depth range 0–2. A prefix after the contained scope does not change its input depth. [CSS Generated Content §4.2](https://drafts.csswg.org/css-content-3/).

**Scoped spec verdict: REACHED** for the fixture's outside-prefix change and inherited contained depth. Both official sections were read on 2026-10-27; `webspec-index` was unavailable, so official web retrieval was used. This is not a claim about every quote/scoping/flattened-tree combination.

The fixture waits for Ahem and checks the 20px advance, records initial width, records the immediate post-insertion width before constructing a fresh fixture, compares a fresh equivalent, records the old fixture again, removes the prefix, and records restoration. The order prevents a later fresh construction from hiding the first stale observation. Independent outer style containment isolates test fixtures. Seed 0/1, all four operations, before/after insertion, trailing parent quote present/absent and direct/nested scopes produce 64 distinct cases.

The expected width comes from quote depth, not from the fresh rendering alone. The fresh and removal observations are additional controls. A trailing parent quote makes the insertion non-last and exercises the existing dirty path. Open/no-open with either seed and close/no-close with seed 1 explain the 12 repairs when insertion is before the scope and no trailing quote exists. Close at seed 0 and insertion after the scope are meaningful no-change controls.

## Actual retained evidence

All hashes listed in ROOT-NATIVE-WPT-v1's evidence map authenticated. Direct raw reparse and receipt joins found:

* Original: 52 PASS, 12 FAIL, one OK harness, command exit 1. Every failure is the immediate inserted-width assertion, after the initial/fresh/removal assertions passed. The simplest witness records initial 40, mutated 40, fresh 120, afterFresh 40, restored 40.
* Candidate: all 64 PASS, one OK harness, exit 0. The other 52 rows retain exact status/message/expected/intermittent observations. Both runs retain one suite start/end and exact receipt/raw status equality.
* Regression candidate: the new 64 rows pass, 15 existing test ends pass, and three retained expected FAIL test ends remain visible; one OK harness, exit 0. This review does not invent an original regression run for comparison.
* Each original/candidate capture preserves its 25 guarded inputs. Their difference is exactly the two native sources and two built binaries. The regression capture preserves its 59 pins.

The recorded native build succeeded; its four export progress-monitor diagnostics remain disclosed. The fixture's `restored` measurement means DOM prefix removal within that case. It is **not** evidence of a separate original-native rebuild/restored-browser phase. No such third phase is established by this historical pair.

## Landing conditions versus broader research

The native change and oracle are sufficiently specific for an independently reviewable bug fix. A universal formal model of scope construction, flattened-tree ordering, lifecycle and all dirty delivery is not a prerequisite for accepting a demonstrated, reviewed native bug. A small companion may document the stale dependency and repair under explicit delivery assumptions; it must not be described as proving all those native premises.

Concrete readiness work still matters: run the already planned fresh scoped comparison against coherent original/candidate/restored binaries and current guards; retain the existing regression outcomes and unexpected diagnostics; verify the final three-path patch and selected reviewer. Do not identify the current dirty candidate browser as an original baseline. A clean-base build has not been performed, and the historical transport checks do not assert one.

One actual validation gap is the lint record. `lint-v1.log` contains only ESLint's ignored-file warning and exits 1. “Zero errors” is accurate but is not evidence that WPT lint processed this HTML. Run the appropriate WPT lint path on the exact fixture before describing lint as passed. Browser execution already establishes parsing/test registration for the tested body, but does not replace that lint gate. No speculative fixture rewrite is requested.

This review performed only artifact reads, official spec/Searchfox queries, raw reparse and scratch patch transport. It did not run a browser/build/linter or mutate live source, indices, ledgers or canonical research.
