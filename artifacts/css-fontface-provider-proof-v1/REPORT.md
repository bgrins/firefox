# Loaded FontFace provider repair design

19 October 2026. Artifact-only source review and small abstract Lean contract. No native patch, WPT edit, browser execution, Gecko build, or Git operation by this agent. This remains within the broad known bug 1072149 family.

## Result and recommended implementation boundary

For a successfully loaded **data-backed** face, rebuild a new descriptor-specific platform entry from its retained sanitized `FontData`, and associate it with a fresh loaded user-font wrapper owned by the changed `FontFace`. Preserve the old wrapper, platform entry, and their cache associations for other faces. Notify every set containing the changed face so selection and text runs refresh. This handles both buffer and URL resources without another load.

This is an actionable design, not an implemented or validated repair. Loaded `local()` fonts require an additional resource-preserving backend operation or an explicitly justified relookup policy. Do not claim the downloaded-data design fixes every source type. Allocation/backend failure, in-flight loads, CSS-connected updates and worker publication require the decisions listed below.

Root's separately owned `system-browser.json` reports Firefox 158: five failures, four passes. Fresh 100% and 50% faces produce 80px and 40px; all five loaded mutation observations remain 80px, including mutation before first set addition/rendering. That primary case excludes stale old text-run reuse and membership generation as the sole explanation. This capsule copies and hashes that external receipt; it does not substitute for root's forthcoming local-build WPT gate.

## Two independently shared layers

1. `gfxUserFontSet::FindExistingUserFontEntry` searches an existing family for matching source/descriptors and returns the same wrapper. `FontFaceImpl::Entry` has multiple `mFontFaces`. Therefore distinct FontFace objects can share a wrapper, not just its platform entry. `DescriptorUpdated` currently updates that wrapper in place.
2. URL loading uses `UserFontCache::GetFont`, assigning its platform entry directly to `mPlatformFontEntry`. Different wrappers can therefore share the provider. Cache equality includes family, style/weight/width, range flags, feature/variation arrays, language and metric overrides, size adjustment, URI/principal/private mode. Mutating this provider changes another face and potentially invalidates the cache's key assumptions.

Buffer entries are explicitly excluded from UserFontCache, but remain useful for proving the stale-provider defect independently. They do not exercise URL provider sharing. Neither a successful buffer-only repair test nor checking a wrapper's reference count establishes isolation of URL-backed faces.

## Proposed transaction

These are conceptual operations, not existing API names or an exact patch.

1. On a changed descriptor of an already loaded data-backed face, retain its old wrapper and old provider. Gather parsed attributes and the actual successful source/resource identity before changing any shared object. Fast-return for semantically unchanged attributes if desired.
2. Create a new `FontFaceImpl::Entry` for the face's primary set using copied source records and the new attributes. Do not deduplicate it with a wrapper whose ownership would then be mutated. The existing entry's source records are available even though a buffer record's payload has been consumed. Copy successful source index/principal/local-source bookkeeping as needed, but do not transfer active loader ownership or restart loading.
3. Get `oldProvider->mUserFontData->mFontData`. Call the existing `MakePlatformFont` with that retained resource and the new wrapper's weight, width and style ranges. This allocates a new entry and fresh instance-cache identity. All four inspected backends support this route. The data has already been sanitized; do not invoke OTS or network loading again.
4. Initialize the newly created entry before publication with the same descriptor assignments performed by `LoadPlatformFont`: features, variations, language override, family, auto-range flags, ascent/descent/line-gap overrides and size adjustment. Keep unicode-range on the wrapper as in the existing design; do not replace the platform's actual character map with CSS coverage.
5. Copy the old provider's `gfxUserFontData` metadata into an independently owned record, retaining its `RefPtr<FontData>` and immutable URI/principal resources. Preserve source index, private/buffer flags, original full name, compressed WOFF metadata, format and technology flags. Do not move metadata out of the old entry. Recreate the optional Fontations/Skrifa reference from the same bytes, following the existing load path; don't copy raw ownership pointers or previously initialized entry/font caches.
6. Set the new wrapper's platform pointer and loaded state before attaching it to the face. `SetUserFontEntry` can then detach just this face from the old wrapper and attach the already loaded new one. Existing `FontFaceImpl::SetStatus` early returns on equal status; no new promise, backward status transition, pending download, or repeated loading event is needed. The model proves preservation only when this publication discipline is followed.
7. Rebuild affected sets from actual current face membership and force their generation/reflow notification. Old wrappers/providers stay alive as long as other faces or old font instances retain them. They remain immutable; existing cached old instances may finish their work safely, while new selection obtains the new provider.

For a first narrow data-backed size-adjust repair, always detaching a loaded target avoids a new uniqueness analysis. Optimizing the single-owner case can come later. A helper that only regenerates `mPlatformFontEntry` on the existing shared wrapper is insufficient.

### Cache handling

Keep the old UserFontCache association; it is still correct for unchanged users. A fresh mutated provider can initially remain uncached, making the first repair smaller. If caching it, use the ordinary cache insertion only for URL data and after complete metadata/descriptors are installed. Buffer and local entries must not be passed into URL cache insertion. `CacheFont` expects source metadata/URI and only explicitly skips buffer entries.

Do not call `ForgetFont(oldProvider)` merely because one face changes. Do not repurpose `UpdateAttributes`' existing `ForgetFont(this)`: it passes a wrapper, whereas cache records hold platform entries and ForgetFont matches pointers. Cache omission may cost reuse but preserves old users; in-place provider mutation breaks correctness. The old entry's normal destructor removes its cache entry when its lifetime ends.

## Existing construction pathways and limits

`LoadPlatformFont` already stores a strong reference to sanitized bytes in `gfxUserFontData::mFontData`. CoreText creates a new `CGFont` using a data provider retaining those bytes. DirectWrite creates a custom font-file stream retaining them. FreeType/fontconfig creates a new user-font face from `FTUserFontData`; FT2 creates a new font entry retaining the data. These complete factory bodies are pinned, not just declarations. Backend resource allocation can still fail; successful reuse is a premise, not a proven native guarantee.

The general `gfxFontEntry::Clone` contract explicitly permits **only installed system entries**. CoreText and DirectWrite implementations assert `!IsUserFont()`. Using it on the loaded platform entry is wrong even if it seems to work on one backend.

Resetting loaded state and calling `LoadNextSrc` is also wrong for the primary buffer case: `DoLoadNextSrc` already consumed its `gfxFontFaceBufferSource::TakeBuffer`. It can additionally redownload URL resources, rerun source selection, and perturb loading status/events.

For `local()`, metadata records the successful local name but has no FontData. `LookupLocalFont` constructs new descriptor-specific entries in the current code, but repeats name/visibility lookup and can fail or change resource after font-list changes. A resource-preserving local clone would need backend-specific native handle ownership, rather than the generic Clone API. The existing local constructors demonstrate a route on CoreText/DirectWrite and fontconfig; FT2/shared font-list alternatives need further inspection. No claim of a complete local-font repair is made here.

## Invalidation is a separate required part

`DescriptorUpdated` currently calls `MarkUserFontSetDirty` for every membership. The document implementation requests a style flush and marks the document. But `FontFaceSetDocumentImpl::UpdateRules` initializes `modified` from `mNonRuleFacesDirty`; reinserting unchanged non-rule records does not set it. It increments font generations only when modified. `Document::FlushUserFontSet` calls `nsPresContext::UserFontSetUpdated()` only if UpdateRules returns changed. That method queues reflow, and recascade when font-metric-dependent units are in use.

Add an explicit per-set descriptor/provider-change notification. Under the existing mutex, record a rebuild-relevant modification (a dedicated bit is clearer than falsely describing it as membership change), then request the owning thread's existing dirty/flush pathway. Every set containing the changed face needs the notification, including additional documents. Before-add mutation needs no layout notification, but the new provider must already be correct when Add later rebuilds.

Worker `FlushUserFontSet` also gates generation on `mNonRuleFacesDirty`. Unlike document UpdateRules it does **not** first detach family entries. Replacing wrappers requires rebuilding worker family membership in order, or a fully correct removal of obsolete entries. `gfxUserFontFamily::AddFontEntry` can append duplicate pointers; `RemoveFontEntry` removes one occurrence. Simply reinserting the new wrapper may leave stale selectable entries after deletion, coverage or family changes. Preserve ordering and other faces that still own the old wrapper.

The worker setter already synchronously dispatches `UpdateUserFontEntryRunnable` to main thread for platform work. A fresh-wrapper result must be safely returned and then attached on the face's owning thread. Do not attach a worker-owned FontFace from the main-thread runnable or expose partially initialized provider fields to font metrics workers. Exact lock/dispatch publication and worker teardown are implementation review obligations.

## Focused verification requests for root

Keep the original calibrated nine rows and add only discriminating cases for repair risks:

- Capture `face.loaded` before mutation; identity and resolved face remain equal afterward, status stays loaded, and no new loading sequence occurs.
- Two same-family/same-URL/same-descriptor faces loaded in one set to reach wrapper sharing. Mutate the last face to50%: it measures40; delete it: the unchanged first face measures80; re-add:40. Source identity alone does not prove sharing, so a native debug identity check is useful if the browser test passes unexpectedly.
- Same family/resource/descriptors in two same-origin documents to reach platform cache reuse without sharing the wrapper. Mutate one face: its width40, the other's80. A later fresh100% face must still render80. This distinguishes copy-on-write from shared-provider mutation.
- Active existing and new consumers, and deletion/re-addition, must pass independently; font-group refresh alone is not a substitute for provider freshness. Worker OffscreenCanvas measurement plus delete/re-add is the corresponding membership case if worker support is in the patch.

These are proposed tests, not authored/running WPT or execution evidence. The primary source-isolated failure is already root-reproduced; the aliasing cases are repair controls, not additional confirmed bugs.

## Small formal contract

`FreshProvider.lean` models separate face, wrapper, provider, resource, promise/status and set-generation identities. Thirteen kernel-checked theorems prove successful detached publication observes the new scale, retains the resource and all promises/statuses, preserves old provider/cache state and untouched faces under explicit fresh-allocation premises, and notifies all containing sets. Closed witnesses show wrapper-only updates stay stale and shared-provider mutation changes a peer, while detached publication changes only the target.

The model uses exact natural-number percentages to expose identity; it does not prove IEEE font scaling. It abstracts a successful allocation/publication transaction and direct generation notification. It does not execute native constructors or prove C++ heap safety, callback scheduling, parsing, resource authenticity, worker locking, cache lookup equivalence, font metrics, or layout. Native failure and pending-load paths remain open. Source review above binds the roles; there is no compiled native-to-Lean refinement claim.

## Evidence and replay

Complete current local source snapshots, Searchfox discovery results, root's system-browser receipt and prior same-day authoritative spec retrieval are retained. The current primary Font Loading3 and Fonts5 sections were reopened during this task; their setter/size-adjust semantics and the Font Loading explanatory-list omission are unchanged. No claim of novel bug-family discovery beyond1072149.

The checker authenticates every manifest input before invoking Lean, checks the compiler binary identity/version, and rejects nonstandard theorem axioms. It uses the specified installed Lean toolchain; the entire compiler/standard-library distribution is not vendored, so this small capsule is not a hermetic toolchain proof. No browser/native execution or broad font implementation proof is implied by a successful check.
