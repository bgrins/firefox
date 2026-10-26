# Block-to-table-to-column identity trace proposal

Status: **uncompiled temporary diagnostic patch and unrun paired fixture**. No production edits, compiler, browser, build or Git operations. Intended for a later root-owned experiment, after the uninstrumented campaign completes.

## Scope and pinned source roles

`trace-only.patch` adds calls in exactly three complete methods: candidate `nsBlockFrame::ReflowLine`, candidate `PresShell::UpdateHiddenContentInForcedLayout`, and unchanged `nsTableFrame::SetColumnDimensions`. It also adds one temporary header, `layout/base/HiddenColumnIdentityTrace.h`. All helper symbols live in the distinctive `mozilla::HiddenColumnIdentityTrace` namespace with inline definitions, avoiding generic static names in unified builds.

The block and PresShell inputs are the running boundary campaign's selected candidate snapshots; the table input is its retained HEAD snapshot. `SOURCE-PINS.json` authenticates each against that campaign's INPUTS payload hashes. No evolving live CPP is captured. Complete selected before/trace bodies are retained in `bodies/`; full sources remain at the pinned original artifact paths. This small proposal is not a self-contained full-source build capsule.

Removing complete trace-call lines from each selected body recovers its original body byte-for-byte. Includes and the new helper are the only other source additions. `check-patch.py` applies this generated unified patch in memory against those exact inputs and checks all four expected output hashes; it writes no native file. This establishes text applicability, not compilation or semantic noninterference. The temporary helper uses POSIX getpid and is scoped to the local macOS/Linux diagnostic, not a portable production change.

## Fixed fixture identity

`paired-fixed-ids.html` keeps only the two original outer-width cases, col and colgroup, in original order. The source eight-case fixture is preserved as `original-eight.html`; `unlabeled-two-case.html` is its exact loop-roster subset. No CSS, stage mutation or geometry-read sequence changes.

Each target/reference host and every existing element receives a unique fixed ID **before host insertion**. Examples: `cvjoin-col-target-host`, `cvjoin-col-target-item`, `cvjoin-col-target-table`, `cvjoin-col-target-col0`. Reference IDs use a distinct role. There are no per-stage attributes, style changes, event hooks or additional queries. The native observer reads existing outer `narrow` and subject `hidden` classes without computed-style/layout APIs.

The trace is filtered to those four exact host IDs. Each record contains process ID, a per-process main-thread event serial, case ID, document/content/frame addresses, DOM node ID, kind, parent address/node/kind, table-provider address/node, two independent dirty bits, previous/next continuation addresses, and the current stored rectangle. The optional actor identifies the source block or publishing table. The provider is resolved independently at each record using checked col→group→table parents; it is never substituted for the queried frame or retained across a flush.

DOM ancestry is bounded at12 levels. Principal-frame snapshots are bounded at depth8 and32 frames; a cut or exhausted budget explicitly marks incomplete evidence. This fixture has no float, abspos, fragmentation or text dependency. Principal-list traversal is deliberately not a claim to cover overflow/OOF lists or arbitrary anonymous frame graphs.

## Events and intended join

| Event | Actual source site | Evidence sought |
|---|---|---|
| line-before-mark / line-after-mark | Before/after each existing MarkSubtreeDirty call in the hidden-line return | Same selected child subtree, including wrapper/inner-table/provider and pruned columns, before/after bits |
| query-entry | Helper entry | Original target, its current parent chain and currently resolved provider state |
| query-reject-kind / query-reject-provider | The corresponding existing early return | Which gate rejected this exact case/node |
| query-admitted | After existing readiness gates | Original queried frame admitted, with its own and provider dirty bits still separately visible |
| query-hidden-ancestor / query-queue | Existing hidden ancestor selection and before FrameNeedsReflow | Original ancestry used and selected forcing root |
| publish-before / publish-after | Immediately surrounding existing group/column SetRect | Actual publishing table actor and exact target DOM/frame, with old/new stored rectangles |

The useful witness is a *case-specific chain*: at narrow=true/hidden=true the line marking changes the relevant inner table's pending state while the col/group remains clean; the selected query resolves that same table DOM provider and passes the new gate; the publisher writes the selected column/group; raw CSSOM first/repeat results then match the calibrated visible peer. These are desired observations, not results already obtained.

The source query helper's no-forcing event is distinct from gate rejection: admission need not find a hidden ancestor. A query-queue record only establishes the call decision, not completion. Publication and resulting raw geometry must be observed separately. We add no post-FrameNeedsReflow access to the original target, avoiding an extra retained-pointer use after that call.

## Later paired experiment

1. Use a fresh root-owned process/profile and run the exact fixed-ID fixture once with the uninstrumented both-repair source. Preserve two subtest statuses/messages and both complete five-stage raw rows. An optional uninstrumented unlabeled subset, or the corresponding original campaign rows, checks ID-only observable equivalence.
2. Apply the trace patch only to its exact pinned source roles, build, and run the **identical fixed-ID HTML** once. Retain stderr plus raw rows and before/after source/binary pins. Require exact status/message and full row equality with the uninstrumented fixed-ID run; retain any difference as a failed diagnostic comparison.
3. Correlate only within a known phase/process/test document and case-role. Target and reference records must never mix. Existing class states distinguish changed/narrow state; ordered query records and the fixed source read sequence distinguish warm/hide/restore/show and first/repeat. Do not guess stage labels if unexpected query counts or extra document loads make the sequence ambiguous. No trace was added to mutate the DOM to carry stage labels.
4. Reject complete-tree claims on `tree-cut`/`tree-budget-exhausted`, unknown fixture state, unexpected continuations, missing node identity or pointer/node inconsistencies. Inspect the actual frame tree and table actor, not just rectangle values.
5. The driver must treat the new header as a temporary path: verify initial absence, pin it, remove it on restoration, restore all modified CPP files and rebuild. Do not apply this patch to the currently running campaign or silently layer it onto a different source version.

## Lifetime and perturbation boundaries

Fixed IDs identify fixture DOM roles, not native allocation generations. Document/content/frame addresses corroborate a current snapshot; repeated addresses do not prove survival or exclude reuse. Within a single source-selected principal snapshot the actual parent/provider edges are read afresh. Across callbacks or separate queries, this first diagnostic may show a consistent same-node relation but does not prove one frame allocation survived. Reconstruction, destruction, reparenting, a reused ID/document/process or changed continuation ownership requires separate lifetime evidence. There are intentionally no allocation/destruction hooks or global pointer registry.

The observer reads attributes/getters and writes stderr. It does not intentionally change layout state, invoke JS, flush layout or introduce per-stage author mutations; nevertheless string allocation, IO and elapsed time may affect scheduling. **Matching geometry does not prove instrumentation preserved dirty-state timing.** It only establishes the paired observable outcomes for that run. Native causal claims remain bounded to the actual source events captured, with event-order and lifetime qualifications.

## Static checks

`PATCH-CHECK.json`: exact generated four-file patch applies in memory to authenticated inputs and produces the pinned bytes. `FIXTURE-CHECK.json`: Node syntax and exact two-name registration pass; full stage mutation/read code is unchanged between unlabeled and fixed-ID fixtures. No test callback or native code was executed.

Fresh Searchfox discovery confirms the non-flushing Element attribute signature, nsINode parent-element accessor, principal-list accessor and string conversion class location. Failed/misdirected symbol lookups are retained and are not treated as complete definitions. Actual changed-method binding uses the retained candidate sources, not Searchfox's indexed revision.
