# Independent FontFace provider integration review

## Decision and blockers

**Ready for a controlled integration and native build. No concrete source-level blocker was found in the exact sixteen-file candidate. Not approved for landing or an all-platform correctness claim.** This review is independent of both the candidate author and the producer's second-pass review.

The acceptance blockers are validation gates: the candidate has not been compiled on any backend in this review; there is no exact candidate browser result here; invalid/no-op setters, calibrated local sources, and the native-loaded/DOM-loading interval are absent from the retained browser matrices. Root will prepare the additional tests. These gaps are not concealed by the successful source replay.

The repair concerns already loaded, script-created FontFaces. It retains the existing non-loaded in-place update path, CSS-connected setter exclusion, platform font-list reset behavior, and lazy local resource semantics. It is not a complete font-loading implementation or a closure of the broad ownership/formal project.

## Exact review unit

`DEPENDENCY.json` pins the existing `css-fontface-provider-integration-review-v1` closure (66 inputs), including the signed common candidate and its **embedded** corrected backend dependency. Common patch SHA-256: `8ddd7408598399ea0aa074d454d1b66f135aead44e38eee766cced5cb0a1a0f7`. Backend patch: `484422eadb16285f7a787beb883c2eab2d37d4dcdcf078f2b4c077123f57abf8`. Six common and ten backend files are changed. The older standalone backend draft is not interchangeable.

All dependency files were authenticated before executing either checker/generator. The producer replay regenerates the sixteen candidate files and both patches; the independent checker additionally applies both patches to a temporary original tree, compares every output byte, and reverses both patches back to every original. This is source reconstruction, not compilation. The second-pass recorded live comparison is historical evidence; this review neither refreshed live sources nor assumes they remain unchanged during root work.

The package carries complete affected files, worker dispatch, document/worker family rebuild, Servo clone/setter, array ownership and font data context. The live supplemental glue file differs as a whole from the older context, but the two relevant complete Servo definitions are identical. No native API from Searchfox tip was substituted for these retained bytes.

## Setter, publication and worker ownership

`SetDescriptor` clones the actual locked Servo rule and parses the candidate before touching the current descriptors or provider. Invalid syntax and unchanged parsed values return without a provider update. The family quoting compatibility behavior is preserved. A previously absent wrapper is still not loaded or created by descriptor setting.

With a wrapper, `GetAttributesFromRule` builds a fresh descriptor tuple and Unicode-range map. `UpdateFontFaceDescriptorOnMainThread` checks native load state. For native-loaded input it constructs a fresh `FontFaceImpl::Entry`, clones the platform provider, initializes its descriptors and metadata, then returns it without registering a face, inserting a family, caching the provider or sending load notifications. The old wrapper and platform provider are untouched. Thus another face sharing either level retains its old descriptor/provider state.

The worker runnable owns the set, old entry, attributes and result. It has no borrowed worker-stack output. No entry/set mutex is held across its synchronous dispatch. The retained `WorkerMainThreadRunnable::Dispatch` holds worker lifetime through the sync loop and uses ErrorResult for dispatch/shutdown failures; `MainThreadRun` returns true after preparation. A false runnable result would instead be an uncatchable failure, so it is correctly not used as a recoverable clone-error convention.

After dispatch, the owner thread checks the owning DOM object and both old identities before publishing. For the loaded path, abandoned candidate destruction leaves old descriptors/provider unchanged. `gfxUserFontEntry` proxies platform destruction to main. The runnable retains the raw-set dependency while preparing; the owning FontFace retains its primary set while attaching; `AddFontFace`/`RemoveFontFace` maintain raw association under the entry lock. This is a concrete ownership trace, not a proof of arbitrary heap or shutdown schedules.

The main native-loaded check correctly covers the interval before the queued worker DOM completion. `Entry::SetLoadState` captures a strong FontFaceImpl and status, not the old wrapper. `SetUserFontEntry(entry, false)` preserves the pending/settled DOM promise and lets that queued callback finish the same face. No new loader or promise is created. Awaited-load WPT does not exercise that interval, so a controlled runnable test remains useful.

The non-loaded path still mutates the existing wrapper before owner publication. It is not transactional if shutdown happens afterward, and shared in-flight behavior is not repaired. A DOM-loaded object can enter this path after native local-font invalidation resets its provider. These are explicit scope limits, not claimed loaded-clone successes.

## Membership and cache identity

`DescriptorUpdated` now invokes `NonRuleFontFaceChanged` on each current membership. That method sets `mNonRuleFacesDirty` under the recursive mutex before the existing document dirtying hook. The worker hook alone is empty; the added flag is necessary for generation invalidation. Both complete rebuild paths detach old family entries and insert the current non-rule entry. The prerequisite worker-detachment repair is present in retained context.

A removed or never-added face does not become a member merely through mutation; later addition observes its current wrapper. Family changes do not mutate a peer's old family identity. Font-instance caches receive a new provider pointer. The fresh provider is not inserted into UserFontCache; `ForgetFont` removes entries by exact pointer, so later clone destruction cannot evict its source peer by descriptor equality.

`InitializeFromLoadedEntry` copies all fields of the retained `gfxUserFontData` definition into a distinct object, retaining FontData/URI/principal references and copying metadata storage. The source list is an owned nsTArray clone with retained refcounted members. Already consumed buffers are not consumed again. New CSS features/variations are appended to backend defaults rather than copied from the old CSS-populated array. Source index, principal and local-source admission state follow the old wrapper. Fresh status is assigned directly while detached, with no owner callbacks.

## Backend audit

| Backend | Exact ownership path checked | Remaining compile/runtime gate |
|---|---|---|
| CoreText | Clone holds source lock, constructs from admitted CGFontRef, constructor CFRetains it; fresh caches and requested ranges. Cmap/AAT/CFF data are derived again. | macOS compile; downloaded/buffer/local mutation and peer isolation. |
| DirectWrite | Local branch retains IDWriteFont; data branch retains IDWriteFontFile and IDWriteFontFileStream and copies face type. System/GDI policy flags retained. Stream parameter widened to the already stored interface type. | Windows compiler/SDK overload compatibility and both resource branches. |
| Android FT2 | Copies filename/collection index and AddRefs an initialized atomic SharedFTFace; otherwise retains lazy locator semantics. Fresh table/variation/font-instance state. | Android compilation and initialized/lazy local/data behavior. |
| Fontconfig | Refcounted pattern plus optional SharedFTFace; local platform feature defaults re-read; protected clone constructor uses direct new. | Linux compilation, Fontations enabled/disabled, retained-face and lazy-face paths. |

The base CloneUserFontEntry returns null for unsupported providers; common initialization release-asserts a non-null clone. Inspected successful local/data/cache paths initialize provider metadata. These assertions encode an invariant: they are not graceful handling of a future unsupported backend or arbitrary corrupt loaded state. The four concrete providers cover the surveyed creation paths; the user entry placeholder and abstract FT base are not additional platform targets.

Fontconfig's new Fontations hook is restricted to user clones with a retained initialized face. Installed/ordinary entries retain the prior hook behavior. A clone without a face uses existing GetFTFace initialization. GetSkrifaFont returns an existing pointer first, and SetSkrifaFont atomically installs only into null while destroying a loser. This avoids overwriting owned Skrifa pointers; it does not prove exactly one allocation or all backend concurrency.

CoreText's existing lazy Skrifa hook may look up by name later; FreeType/fontconfig may reopen retained file locators for derived data. Fresh cache construction therefore does not guarantee immutable underlying bytes after external font replacement. The candidate preserves existing lazy resource policy instead of doing a new visibility check or source activation during clone construction. Root should retain that boundary in any acceptance wording.

## Independent browser oracle audit

The retained exact WPT sources, Ahem, receipts and raw JSONL are under `evidence/`. They are baseline observations, not candidate runs. Receipt pins match the copied WPT/font bytes and before/after inputs are stable. Raw status parsing is replayable independently of the producer summary.

At font-size 20px, four Ahem X advances total 80px at size-adjust 100%, 40px at 50%, and 60px at 75%. This expectation comes from the font fixture and descriptor scaling, not from the original buggy result. Fresh 100%/50% faces calibrate both source routes. CSS Font Loading defines setter serialization, effect descriptors and the retained loaded promise; CSS Fonts defines scaling of outlines/metrics. [FontFace](https://drafts.csswg.org/css-font-loading/#fontface-interface), [size-adjust](https://drafts.csswg.org/css-fonts-5/#size-adjust-desc).

The DOM test has 12 cases: four fresh calibrations and eight URL/buffer mutations across before-add, existing element, new element, and delete/re-add. It fixes computed font size, synthesis, optical sizing, spacing and line height; it checks loaded status/promise identity and reads geometry after readiness and animation frames. The baseline has 4 PASS and 8 FAIL with OK harness. The invalid first baseline is not used.

The canvas test has 16 cases per realm (window and dedicated worker). It checks fresh sizes, before-add/existing/new contexts, fallback after deleting a mutated face, and identical-descriptor versus differing-unicode-range URL peers, each with either changed or unchanged survivor. Deleting one peer makes the expected provider unambiguous. Identical descriptors target wrapper sharing; distinct Unicode ranges target separately matched wrappers that may share the platform cache. WPT observes isolation, not internal sharing identity, so native instrumentation would be needed to assert a particular sharing path occurred.

Raw canvas baseline is 8 PASS/8 FAIL in window and 6 PASS/10 FAIL in worker. Worker deletion failures precede the separately repaired family-detachment bug; do not count all ten as provider-only failures or use this old run as the final paired candidate baseline. Root must bind a fresh baseline with the prerequisite repair. Root confirmed there is no newer fixed matrix for this review.

The matrices do not contain invalid setter/no-op controls, local-font calibration, repeated successive mutations, feature/variation/metric-override effects, or a controlled native-loaded/DOM-loading race. Existing descriptor reftests broaden regression coverage but do not replace these omitted identity/resource gates. No test skips an unsupported API as a success; worker OffscreenCanvas absence would fail rather than silently pass.

## Required next gates

1. Format and compile the exact integrated common/backend candidate. Inspect every formatting delta; retain source/binary identities. macOS success does not close Windows/Android/Linux compilation.
2. Fresh original/candidate pair with the worker prerequisite present on both sides; run DOM/canvas tests and existing descriptor/worker-removal regressions. Keep promise, fallback and peer observations separate from geometry-only passes.
3. Add invalid/no-op and repeated setter controls, calibrated local sources (unavailable font means unresolved coverage), and relevant descriptor effects. Test membership before-add/removed/re-added without assuming internal deduplication.
4. Retain the queued load-completion interval as an explicit controlled-test gap if ordinary browser tests cannot deterministically reach it.
5. Record allocations/cache rebuild cost: each valid changed descriptor on a loaded face creates a new wrapper/provider, including descriptors that may have no useful post-load rendering effect. No performance measurement or optimized deduplication argument is supplied.

## Replay and packaging

Keep this review directory alongside the existing `css-fontface-provider-integration-review-v1` directory. The latter already contains the complete pinned candidate source closure; it is deliberately not duplicated here. Run `python3 check.py --checks --dependency ../css-fontface-provider-integration-review-v1`. The default dependency path is that sibling. To relocate, copy both directories or supply the exact sealed dependency elsewhere. The checker authenticates both manifests before executing any dependency code; Python executable identity is checked by the original package. Python 3.14.6 at the pinned hash, patch and Node are needed for the full source replay.

The new review's own manifest closes its local evidence. The external dependency manifest closes all native/generator inputs. Neither replay reads live native sources or invokes a compiler/browser. Fresh temporary relocation, exact apply/reverse and tamper rejection are retained in FREEZE.json. No Git operations or production/WPT edits occurred.
