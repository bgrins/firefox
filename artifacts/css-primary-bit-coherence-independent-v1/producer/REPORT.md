# Primary-bit coherence: stable publication, not universal callback closure

## Result

This component addresses R1 in `css-primary-cache-owner-review-v1`: native destruction tests `mIsPrimaryFrame`, whereas the earlier model tested the content's primary pointer. They agree at a read point **if** the cached-bit/own-content-pointer invariant holds there. The invariant is now proved for arbitrary finite admitted setter histories, including area aliases and clearing/replacement. It is not assumed as a property of the setter's intermediate state.

The source review derives a selected ordinary initialization callback footprint. It also narrows the area issue using actual frame-construction suppression and image-map alias cleanup. It does **not** close the actual destructor callback history, frame identity/lifetime representation, all construction callers, or full allocation F1–F16/F11/F12. The earlier `HOLD_NATIVE_PROJECTION` remains for that universal join. No new native defect or browser outcome is claimed.

## Source facts and interpretation

`SOURCE-BINDINGS.json` retains 26 complete definitions from pinned full files. The source files have different explicit origins in `SOURCE-PROVENANCE.json`; current indexed files are not silently substituted for the old frozen native role. Extraction is a lexical check of these inspected C++ definitions, not translation validation or a general C++ parser.

### Setter order and stable-state contract

`nsIContent::SetPrimaryFrame` first calls `SetIsPrimaryFrame(true)` on a non-null target, except a foreign-content area alias. `SetIsPrimaryFrame` changes the bit and, on the false-to-true transition, synchronously calls `InitPrimaryFrame`. Only afterward does `SetPrimaryFrame` assign `mPrimaryFrame`. The null branch clears the old frame's bit first, with the same area exception, then publishes null. A same-bit call returns before initialization.

`PrimaryBit.setPrimary` implements those bit/pointer writes. `Publication.ownProtocol` includes the initialization interval and its same-bit early return. `publication_gap` proves that fresh publication actually violates the stable invariant during that interval. This is an expected protocol state, not evidence that a reachable callback destroys a frame there.

The stable invariant relates each tracked frame's bit to the primary pointer of **its own content**. `Routed` additionally requires a non-area content pointer to refer to a frame owned by that content. These are different conditions: coherence alone does not exclude a foreign pointer stored on an unrelated content node.

The history preserves both conditions from an initially empty state or any coherent/routed initial state. Its admitted steps are:

- own-frame publication, with old pointer null or already equal to that target;
- area-alias publication;
- null publication.

`NoAreaOwner` limits this particular alias history theorem to a fixed tracked frame universe with no area-owned frames. This is not a claim that every pseudo/native-anonymous/special constructor satisfies the restriction. The history has arbitrary finite length and arbitrary identities; it does not model allocation, address reuse, changed content ownership, or deallocation.

The native ordinary replacement constraint is a debug assertion, not a release guard. A theorem hypothesis must not be promoted merely because that assertion exists. Inspected real protocols include the release guard in `nsSubDocumentFrame::Init` (publish only if no primary exists), explicit clearing before first-letter replacement, and destruction of the old letter frame before other replacement publication. A complete constructor/callback induction across every listed caller is still open. `own_replacement_without_clear_breaks_coherence` and `bad_replacement_old_destroy_clears_new_pointer` show why this caller obligation matters, without asserting that those states are produced natively.

### Area aliases

The ordinary HTML tag path reaches `FindHTMLData`, which maps `area` to `SUPPRESS_FCDATA()`. `FindElementData` returns that non-null tag result before display/content-image fallback; `AddFrameConstructionItemsInternal` returns on `FCDATA_SUPPRESS_FRAME`. This is stronger than a reliance on an overridable UA `display:none` rule, but the selected ordinary tag path is the scope: special pseudo dispatch and every other frame producer are not covered by this inspection.

`nsImageMap::AddArea` assigns its image frame to the area's primary pointer. That frame is owned by the image content, so this alias must not change the image's bit. `AreaRemoved` clears only if the area's current pointer still equals this image frame. The source therefore permits one image's stale removal to leave a newer image alias alone. The Lean witnesses cover both alias replacement and alias clearing while the image's own primary bit remains true.

`nsImageFrame::Destroy` calls `DisconnectMap` before its superclass destruction. The latter invokes map `Destroy`, then `FreeAreas`, then `AreaRemoved` for the stored areas. This supplies a real cleanup ordering for the alias path. It does not prove event-listener removal, image-loading callbacks, or the intervening frame-destruction observers cannot reenter or mutate ownership.

### Selected actual initialization callback

For a new ordinary element frame with no query-container registration, no anchor reference/name, visible content visibility, no sticky handling, and no auto contain-intrinsic sizes, `HandlePrimaryFrameStyleChange(nullptr)` has this footprint:

1. set the context's hidden-by-content-visibility animation-update flag;
2. remove the element's last remembered block size;
3. remove its last remembered inline size;
4. remove the element from the document's observed-for-last-remembered-size set.

The full bodies show that the first is a Boolean assignment, the next two reset optional numeric slots if the slots exist, and the last removes a raw element pointer from a bookkeeping set. They do not dispatch a synchronous observer callback in these bodies. Native getter effects, collection primitives, memory validity and the owner/content/document projection remain representation assumptions.

`InitialDispatch` records the initial old-style-null branch selection. `plain_dispatch` derives that four-effect sequence; `plain_execution` joins it to the `ordinaryInit` operation. The latter changes the modeled bookkeeping fields while preserving bit/pointer fields. Other effects, including observe-registration and query/anchor/sticky/content-visibility registration, return `none` in the executable effect interpretation. An unsupported effect is not silently modeled as a no-op. This is a selected callback case, not a proof of all style variants or arbitrary native callbacks.

### Actual destruction read points

There are two relevant `IsPrimaryFrame()` tests in the retained `nsIFrame::Destroy`: the early bookkeeping/activity-transfer block, and the later null-publication block. Before the first are SVG observer invalidation and other frame operations. Between them are activity/animation/anchor/visibility and destruction notifications, including `NotifyDestroyingFrame` and possible `ClearFrameRefs`.

`destroy_read_agrees` proves the bit/pointer replacement at any coherent read point. `history_destroy_read_agrees` permits arbitrary admitted setter histories between stable points, rather than assuming every callback is a no-op. `read_after_preserving_callback` separately exposes a frame-projection-preservation contract. **Neither theorem derives the actual native callback trace.** In particular, the script-blocked assertion is not a proof that native callbacks preserve a live object, stable publication phase, or valid ownership. Both actual read points still need their callback-history/heap projection, and the pending-publication interval cannot be treated as a stable entry point.

## Evidence and limits

The six Lean modules expose 40 exact audited results: 26 general/local-protocol results, 11 concrete boundary witnesses, and three compiled model-mutant discrimination witnesses. The three deliberately false mutant-equivalence claims must fail in the kernel with a false proposition, after the mutant definitions and their distinguishing witnesses compile. These are model mutations, not compiled Gecko mutations.

The countermodels cover missing bit clearing, incorrectly marking an area alias, missing pointer publication, foreign ordinary pointers, replacement without clearing, and mutation during publication. They establish missing assumptions and ordering sensitivity. Actual producer reachability is not asserted for the bad states.

Replay authenticates the complete source-only roster, source bindings and exact audit names. It uses a pinned Lean executable with the installed toolchain libraries; this is not a compiler/stdlib reproduction proof. Source/body hashes establish identity, not C++→Lean fidelity. There is no new native build or browser run in this component.

## Next necessary joins

1. Derive actual callback-list events and their owner/content/frame effects at each destruction read point, including SVG and destruction notifications. A conjunction of separate callback and pointer lemmas is insufficient.
2. Extend the producer proof beyond selected ordinary construction: special pseudos, native anonymous frames, replicated/paginated frames, and all replacement paths. Do not infer the all-frame `NoAreaOwner` restriction from the ordinary area suppression alone.
3. Join fixed symbolic identities to live objects, allocation retirement and current-versus-primary cache ownership. Continue to distinguish primary selection from measurement/final-cache storage on a different frame.
4. Preserve the original full allocation obligation roster. This component neither closes F11 consumer noninterference nor F12 source arithmetic/representation joins.

Replay: `python3 -I -S replay.py --files-sha256 <external FILES.json SHA256> --output <fresh absolute external directory>`.
