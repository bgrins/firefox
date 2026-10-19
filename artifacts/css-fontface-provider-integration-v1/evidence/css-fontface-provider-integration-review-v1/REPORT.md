# Loaded FontFace provider integration readiness

## Decision

**Ready for root's controlled integration, build and fixed browser gates; not ready for unconditional landing or an all-platform correctness claim.** This bounded review found no concrete source-level compile, lifetime or publication defect requiring a new candidate before the first build. All sixteen edited-file originals match the current tree exactly. Both candidate patches regenerate byte-for-byte from authenticated sources. These checks are not a C++ compilation.

This is a second-pass integration review by the agent that authored the earlier candidate. It is not an external independent implementation review. Root should retain that authorship distinction when recording acceptance. Scope is the existing loaded-descriptor failure in the bug 1072149 family, with no novelty claim or redesign of unrelated font loading.

Reviewed package: `css-fontface-provider-common-candidate-v1`, manifest `8814399049cbf897b2dfb226cfd7f8fba74090eafd13c64f74c89736b2a8fd90`, checker `0eeb97fc8b41780ecbb9ca1938341094d0f6929b3f13b8f44eb2b22ee63d8ec0`. Common patch `8ddd7408598399ea0aa074d454d1b66f135aead44e38eee766cced5cb0a1a0f7`; embedded backend patch `484422eadb16285f7a787beb883c2eab2d37d4dcdcf078f2b4c077123f57abf8`. The embedded backend is the reviewed version, including the fontconfig clone-only lazy hook. Do not substitute the older backend draft.

## Current-tree admission

`LIVE-ORIGINALS.json` records exact equality for six common and ten backend originals, captured before root integration. `LIVE-CONTEXT.json` records eight equal contextual sources and one changed whole file: `servo/ports/geckolib/glue.rs`. The latter includes subsequent unrelated attr work. The complete `Servo_FontFaceRule_Clone` and `Servo_FontFaceRule_SetDescriptor` definitions are byte-identical between retained and live glue; `GLUE-COMPARISON.json` and the complete live file preserve that comparison. No whole-file equality is claimed for glue. The prerequisite worker family-detachment repair is present in the live and retained worker context.

## Publication and setter semantics

The current [CSS Font Loading descriptor setters](https://drafts.csswg.org/css-font-loading/#fontface-interface) parse the descriptor grammar, reject invalid values, and publish its serialized value. Font-affecting descriptors must affect subsequent use. Descriptor setting does not itself specify a new load/status promise. The candidate parses a detached Servo rule, preserves the existing family compatibility fallback, and publishes only after loaded-provider preparation. Invalid syntax and unchanged parsed values leave the current loaded provider untouched. Rule cloning actually clones the locked Rust rule. CSS-connected faces retain their existing exclusion; that known limitation is outside this repair.

The candidate branches on main-thread **native** load state, not the DOM status. That covers a native-loaded / DOM-loading interval where `Entry::SetLoadState` has queued owner-thread completion. The callback captures a strong `FontFaceImpl` and a status value, not the old wrapper. Replacing the wrapper with `SetUserFontEntry(entry, false)` therefore leaves that queued completion attached to the same face and avoids settling its promise eagerly. Already-settled promise identity is not replaced. This source trace is affirmative evidence about callback targeting; it does not simulate every shutdown or scheduling interleaving.

When the native entry is not loaded, the candidate deliberately invokes the existing in-place update. That branch is not fully transactional across sync-loop shutdown, and existing shared/in-flight ownership behavior remains. A DOM-loaded face whose native entry was reset after local-font-list invalidation may reach that branch. This report does not reclassify it as a successfully cloned loaded provider or claim complete all-state descriptor repair.

## Worker lifetime and cancellation

The runnable owns its set, old entry, attributes and result. No result or attributes are borrowed from the blocked worker stack. It holds no set or entry lock across `Dispatch`. The actual `WorkerMainThreadRunnable` obtains a strong worker reference, creates a sync loop and reports failure through the supplied `ErrorResult`. The candidate returns true from `MainThreadRun` after preparation; it does not use false as a catchable clone failure.

After dispatch, descriptor/wrapper identity and owner-liveness checks prevent publishing into an abandoned or replaced face. The guard's uncatchable failure uses the existing termination channel, not a new normal InvalidStateError for valid setters. The dispatch implementation already has shutdown InvalidStateError paths. Infallible allocation and the existing native-loaded/provider/metadata invariants remain required: this is not a general exception-safe allocation or arbitrary-reentry proof.

On the loaded path an abandoned fresh wrapper has not entered any family or global user-font cache. Its destructor proxies the platform-entry release to main. `Entry::AddFontFace`/`RemoveFontFace` update raw set association under the entry lock; the runnable and face hold the set strongly across preparation/publication. No new loader or load callback is created for the detached wrapper. The old wrapper/provider remain alive for peers and old family references until ordinary rebuild/ref release.

## Family and cache publication

After owner-thread publication, `DescriptorUpdated` marks each current membership through `NonRuleFontFaceChanged`: it sets `mNonRuleFacesDirty` under the set mutex and then invokes the existing document dirtying hook. This explicit flag is necessary for workers because their inherited hook does nothing. Document and worker rebuilds detach old family entries and reinsert current non-rule faces; `InsertNonRuleFontFace` uses the already-attached new entry. Generation invalidation follows the dirty flag. Removed/nonmember faces do not insert themselves; later first-add sees the already updated entry.

The new wrapper/provider is never deduplicated into an existing peer wrapper and is not inserted into `UserFontCache`. Font-instance caches key on provider identity. The cache's `ForgetFont` removes entries by exact provider pointer, so an uncached clone's destruction cannot evict its source peer by descriptor equality. Metadata is copied into a new `gfxUserFontData`, while sanitized `FontData` and source references retain ownership. Buffer sources whose data was consumed are not consumed again. Feature/variation settings are appended once to backend defaults, rather than copying old CSS settings and duplicating them.

## Backend readiness

| Backend | Retained resource and fresh state | Required platform validation |
|---|---|---|
| CoreText | Retains the admitted `CGFontRef` with the constructor's CFRetain; creates fresh entry/table/metric/shaping caches and CSS ranges. Local lookup and downloaded creation supply initialized font refs. | macOS compilation and URL/buffer/local mutation/isolation. |
| DirectWrite | Retains `IDWriteFont` for local faces, or `IDWriteFontFile` plus stream for data fonts; preserves data face type and native resource policy flags. Constructor parameter is widened to the stored stream interface. | Windows compilation and both constructors/local and downloaded behavior. |
| Android FT2 | Retains any initialized `SharedFTFace`, plus filename and collection index; empty face retains the old lazy locator behavior. Fresh entry owns its added face reference. | Android compilation, local/data and retained/lazy-face paths. |
| Fontconfig | Retains referenced pattern and optional `SharedFTFace`; re-derives platform feature defaults for local fonts. Fresh shaping/cache state and clone-only Fontations initialization. | Linux compilation with relevant Fontations configurations; local/data, initialized/uninitialized face and peer isolation. |

The abstract FT2 base and `gfxUserFontEntry` placeholder are not additional loaded platform providers. The four concrete overrides cover the inspected platform creation paths. The base fallback returns null, which the common release assertion rejects; this is an invariant assertion, not graceful support for an unforeseen backend.

Fontconfig's added hook acts only for user clones with an already-initialized FT face. Ordinary entries keep the prior no-op hook; a clone with no FT face still initializes through the existing `GetFTFace` path. `GetSkrifaFont` checks an existing pointer before initialization. `SetSkrifaFont` installs only into null and destroys a losing candidate. Repeated initialization does not overwrite an owned pointer. This does not prove exactly one allocation or the whole backend's concurrency.

Local resource semantics remain deliberately lazy. CoreText's existing `InitSkrifaFontFace` can perform a later name lookup, and FreeType/fontconfig derived data may later reopen the retained file locator. Clone construction itself does not repeat local-font visibility/admission or reactivate/download the source. A retained resource plus fresh derived caches is **not** an immutable-byte guarantee after external font replacement. The candidate follows the agreed baseline semantics rather than adding an unrelated file snapshot mechanism.

## Required gates and risks

1. Root formatting and a successful native build are still required. No backend has been compiled by this reviewer; passing macOS does not validate DirectWrite, Android FT2 or Fontconfig. Treat the explicit constructors/virtual declarations, protected fontconfig constructor, Fontations conditionals and stream type as platform compilation gates.
2. Run the fixed window/worker URL/buffer baseline/candidate matrices: existing/new/readded/pre-add faces; shared wrapper and shared platform peers; unicode-range-distinct peers; fallback after deletion; invalid/no-op setters; promise/status identity. Keep prior worker-removal controls as regressions, not clone proof.
3. For local resources, calibrate an actually available font on each platform and check repeated mutation plus an unaffected peer. A missing font is a skipped/unresolved admission, not a pass. Retain the native-loaded/DOM-loading callback interval as an additional controlled-runnable test opportunity; awaited-load WPT alone does not cover it.
4. Release assertions depend on loaded native entries having a provider and `gfxUserFontData`. The inspected local, downloaded, buffer and cache-hit success paths establish these fields. External font-list resets and in-flight states remain explicit boundaries, and should not be hidden by a DOM-status-only gate.

Every changed valid descriptor on a loaded face allocates a fresh wrapper/provider and may rebuild derived caches later. No performance measurement is claimed. This is a reviewable correctness-first candidate; optimizing special descriptors or deduplicating fresh providers is a separate change requiring its own identity argument.

## Evidence and scope

Searchfox discovery was used for SetDescriptor, worker sync dispatch and CoreText local lookup, followed by the exact retained complete definitions. Current primary CSS Font Loading text is preserved in `SPEC-READ.json`. The full authenticated candidate package and supplemental live glue are copied here. Source-only replay authenticates before importing generators and checks exact deterministic reconstruction; it does not execute native code. No live native/WPT changes, Git operations, browser or Firefox build occurred in this review.

Inspected: all native deltas, complete affected setter/publication helpers, current family rebuild paths, callback targeting, worker dispatch, loaded-provider metadata initialization, backend clone constructors/resource retention, cache removal, Fontations initialization, and source/body identity. Not proved: whole worker lifecycle, heap/race safety, external font mutation equivalence, all platform compilation, shaping equivalence, or arbitrary font-loading correctness. No conceptual Lean model is promoted to a proof of this implementation.
