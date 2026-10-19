# FontFace repair: resource cloning, worker publication and rollback

This is a second, artifact-only design review. No production implementation or browser gate was run by this agent. The first successful-transaction Lean model remains sealed in `css-fontface-provider-proof-v1`; this report does not upgrade it to native correctness. Bug 1072149 remains the known family.

## Recommendation

Use a **separate user-font provider clone operation**, with a fresh descriptor-bearing `gfxFontEntry` and retained native resource ownership. Do not relax the installed-system-font `Clone()` precondition. For data fonts, reconstruction from retained sanitized FontData is available now; retaining native handles as below can avoid platform reactivation failures and also cover local resources. In either case detach the changed face's wrapper first, as the first report describes.

The exact small implementation is clear for CoreText and DirectWrite. Linux/Android have a material distinction: preserving a currently loaded FreeType handle is feasible, but other consumers reopen its filename. A claim of preserving the exact resource bytes after uninstall/replacement therefore needs more than copying that handle. The smallest patch that promises only the same existing lazy resource semantics is different from a stronger snapshot-preserving repair. This report identifies that unresolved choice rather than silently approving it.

## Proposed platform API and concrete constructors

Conceptual new operation: `CloneUserFontEntry(weight, width, style)`, callable only on the platform entry of an already loaded user font. The returned entry has a new pointer/cache identity; common descriptor and metadata initialization happens before publication. Backend ownership below is source-derived, but these proposed methods are not compiled patches.

| Backend | Fresh entry retaining the admitted resource | Required details |
|---|---|---|
| CoreText | Existing `CTFontEntry(Name(), mFontRef, weight, width, style, dataFlag, localFlag)` | The constructor `CFRetain`s the supplied `CGFontRef`; both current local and data load paths supply an initialized handle. Read under existing entry lock, retain through construction. Never resolve the PostScript name again. The ordinary Clone does resolve by name and asserts no user font. |
| DirectWrite local | Existing `gfxDWriteFontEntry(Name(), mFont, weight, width, style)` | Retains `IDWriteFont`. The shared-font-list local path also produces `mFont`, confirmed through complete `CreateFontEntry` and `LookupInSharedFaceNameList`. Preserve backend `mForceGDIClassic`, `mMayUseGDIAccess`, and relevant system/bundled classification; do not replace requested ranges with actual font ranges. |
| DirectWrite data | Existing file/stream constructor with the old `mFontFile` and `mFontFileStream` | Also preserve the already analyzed `mFaceType`; the constructor alone does not initialize it. No `Analyze`, file load or network request is necessary. Use a constructor parameter/member assignment with the actual interface type, not an unchecked cast of the stored `IDWriteFontFileStream`. |
| FT2 | Fresh `FT2FontEntry(Name())` with retained `SharedFTFace`, original filename/index and new ranges/flags | Take a new strong reference before assigning the atomic owning pointer; each entry must own its reference. Do not transfer the old pointer, copy `mMMVar`, or share weak font-instance caches. If the local entry has not opened its lazy face, copying filename/index preserves existing lazy semantics but does not create an immutable byte snapshot. |
| fontconfig | New explicit constructor accepting retained `FcPattern`, optional retained `SharedFTFace`, initialization state, ranges and source flags | Avoid `CreatePatternForFace`/name lookup for a clone. Preserve base platform features from the pattern exactly once, then append new CSS feature descriptors. Do not copy the old combined feature list and append new values, or overwrite platform defaults. Fresh unscaled-font and derived metric caches. |

`gfxFontconfigFontEntry`'s current local constructor obtains fontconfig feature defaults; the downloaded-data constructor does not. The clone needs to preserve that distinction. Its pattern is refcounted; inspected entry consumers read it rather than modifying the shared pattern in place.

Common initialization must copy metadata rather than moving it: actual successful source/index, URI/principal/private mode, buffer flag, original name, WOFF metadata/compression, format/technology flags and retained FontData. No reload or status transition. Keep old platform cache associations intact; the new clone can remain uncached initially.

## Exact-resource boundary on FreeType and Fontations

The source does not support the assertion that copying an FT_Face preserves every later resource read:

- fontconfig `GetHBFace` uses `hb_face_create_from_file_or_fail` when the pattern has `FC_FILE`, even if an old FreeType face already exists.
- fontconfig variable instances use `CreateFaceForPattern` when no backing data provider exists; it opens the filename.
- FT2's absolute-filename variation branch calls `Factory::NewSharedFTFace` using the path.
- `FTUserFontData::CloneFace` uses retained bytes only for its `mFontData` branch. Its filename branch opens the file again.
- fontconfig `InitSkrifaFont` opens and maps the path. Copying an owning raw Skrifa pointer would instead double-delete it; leaving it null can cause a new file read.

Searchfox currently shows newer SharedFTFace/Fontations helpers that are absent from this local checkout. The report uses the copied local complete bodies; newer indexed APIs cannot be called by this patch without an explicit port.

Two valid engineering directions, with different scope:

1. Preserve baseline lazy-source semantics. Retain existing native resource handles and lazy file descriptors/pattern identity; a fresh derived cache may load from that same locator just as other new instances already do. This avoids a new local-name/visibility search and preserves existing admission, but **does not** promise a snapshot across external font-file changes. Document this limitation and test ordinary fixed local resources on each backend.
2. Guarantee exact resource snapshot. Introduce a canonical refcounted backing resource containing the admitted bytes/native handles and make HB, variation, FreeType and Skrifa creation consume it. Retain it across all descriptor clones. This is broader than a minimal descriptor fix. A ref to the original entry can preserve old handles temporarily, but avoid an unbounded new-entry→previous-entry chain; retain a canonical root resource. HB callbacks and Skrifa ownership must remain valid after old FontFace objects disappear. No completed design/proof for this larger abstraction is claimed here.

Simply re-running `LookupLocalFont` is neither direction: it redoes name and visibility resolution and may select no font or a different font.

## Worker transaction: precise ownership and ordering

The existing setter performs `SetDescriptor` first, mutating the Servo rule, then `DescriptorUpdated`. Its main-thread runnable stores raw entry/set pointers and a reference to the attributes, relying on synchronous dispatch; dispatch errors are ignored. That structure cannot give rollback of a new provider preparation step.

Proposed replacement for the loaded-face path:

1. On the owning thread, clone the descriptors with existing `Servo_FontFaceRule_Clone(GetData()).Consume()`. Parse the requested descriptor into the clone. The Rust implementation creates a new locked rule from the cloned descriptor structure; it does not write the live rule. Preserve the existing family quoting fallback and syntax error behavior.
2. Derive attributes with `GetAttributesFromRule(candidate, attributes, Nothing())`, not `GetAttributes()` on the live face and not the old cached unicode map if coverage changed. Do not set `mUnicodeRangeDirty` until commit. Retain old entry and primary set strongly.
3. Run preparation on the main thread using a runnable owning the copied/moved inputs, strong set/old-entry references, and a result member. Do not keep borrowed stack fields as the new ownership API. Do not hold the set mutex or entry lock across synchronous worker dispatch: the main-thread code may need those same locks.
4. `MainThreadRun` prepares the detached loaded wrapper/provider only. It must not call `FontFaceImpl::SetUserFontEntry` or mutate worker-owned descriptor fields. Return true when the request was processed, and carry preparation failure in an explicit result. Returning false from `MainThreadRun` causes the existing sync loop to report failure, which Dispatch converts to an uncatchable exception; it is not a normal allocation result channel.
5. Pass the caller's ErrorResult through Dispatch instead of IgnoredErrorResult. Worker shutdown can fail before any main-thread work; retain the old descriptor/provider association in that case. Keep the result/primary set alive through transfer back to the owning thread. Use the existing main-thread-release discipline for abandoned provider references.
6. On successful return, commit the candidate descriptor rule and attach the fully initialized new loaded entry without a callback/reflow opportunity between them. If the implementation allows reentry while preparing, compare a captured descriptor/entry version before commit and reject/retry an obsolete result; do not overwrite a newer setter. Existing loaded status and loaded promise identity remain unchanged.
7. Notify all current set memberships. Rebuild document and worker family lists from membership order, then publish generation change. The document's existing dirty/style-flush route requests reflow. Worker family rebuild must detach old records before reinsertion; retaining obsolete wrappers after deletion is incorrect even if the latest face shadows them in the first measurement.

This is an ownership/locking prescription, not a proof of all worker cancellation interleavings. The existing synchronous worker runnable source and its stop-loop response are pinned.

## Failure behavior: what can and cannot be concluded

Preparation must not modify live descriptors, old providers, cache keys, memberships or promises. This allows clean rollback when parsing or dispatch fails. A clone that only retains existing backend handles avoids re-running platform activation and its ordinary null/error returns; normal Gecko infallible allocation remains a process resource boundary, not a recoverable-success proof.

If the chosen implementation uses fallible MakePlatformFont or resource snapshotting, it must explicitly decide how an unsuccessful preparation is reported. Returning normally after keeping the old provider while exposing the new descriptor recreates the bug. Clearing the entry or downgrading/rejecting the fulfilled loaded promise is not an acceptable substitute. Synthesizing a NetworkError for a descriptor setter has no established spec basis in this review.

For genuine OOM/shutdown, use the existing internal error/termination channel and leave live state unchanged. For a non-OOM backend failure on a previously valid resource, the spec's normal setter algorithm does not supply a new failure exception or rollback rule; this remains a design adjudication point. Retaining already-admitted native handles is preferable precisely because it avoids making valid setter success depend on another external lookup/activation. No native failure policy is approved by the conceptual model.

CSS-connected FontFace setters are currently rejected by `SetDescriptor` (`HasRule()` early return); fixing that larger bug is outside this repair. In-flight shared loads also require a different split/fanout design and must not accidentally enter the loaded-only helper. None of these existing limitations should be advertised as repaired.

## Review gate before implementation acceptance

Root's baseline is already recorded separately: buffer and URL controls pass; eight loaded mutations fail, with loaded promise/status unchanged. The proposed repair needs the same cases plus shared-wrapper, shared-platform, multiple-set, worker membership, unchanged-descriptor and abandonment controls. Ordinary local-font support needs platform-specific controlled resources; tests relying on an uncalibrated installed font are inconclusive. A fault-injection test should distinguish parse/dispatch/preparation failure from publication, and verify the old face and peers are untouched.

No additional test matrix or proof corpus was run here. This bounded review supplies concrete CoreText/DirectWrite and worker transaction paths, and explicitly retains the FreeType exact-snapshot and non-OOM failure-policy decisions. Those decisions are necessary before calling the design a robust all-source patch.
