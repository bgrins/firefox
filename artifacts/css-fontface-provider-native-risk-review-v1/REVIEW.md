# Focused native risk review: FontFace provider candidate v2

## Verdict

No concrete new source blocker was found in this narrowed review of the exact v2 candidate. This is a source-review verdict for root's controlled local macOS validation, not runtime acceptance or an all-platform/lifetime proof. The candidate build was still root-owned and pending when this review began; no candidate browser result is certified here.

Candidate FREEZE: `b8f0ccd0bf557b5abc7611cd328fdb852be45ca4a4fc4ee6a01fc98d08f3c4e7`. Integration FREEZE: `a5fd5a73cb71da6e176fbc20b1ba5992d847b050795cdbd70dd35910de9b39ac`. Both manifests and every source input were authenticated before replay. Complete source dependencies, current harness/comparator and baseline raw receipts are retained. The author previously packaged integration-v1 but did not author these native changes; this review is independent of candidate implementation, not independent of the earlier packaging.

## Concrete hypotheses examined

### Replacing a native-loaded entry might strand the pending DOM promise

Not found on the inspected completion path. `FontFaceImpl::Entry::SetLoadState` first writes native state, snapshots strong FontFaceImpl references and queues `SetStatus(status)` on each face's owning thread. The queued callback captures the face, not its old entry. The setter selects the new provider path using main-thread native STATUS_LOADED, which includes the worker interval before that callback. It attaches the replacement with `SetUserFontEntry(entry, false)`, preserving current DOM status and avoiding a second eager status transition. The original queued callback can still finish the same face; `UpdateOwnerPromise` dispatches a face-owned callback. A window main-thread completion normally updates status directly, so the special pending interval is principally the worker path.

The clone marks only its detached native wrapper loaded, without invoking its virtual owner notifications. No new load or promise is created. Repeated setters before the callback remain attached to the same face and preserve this targeting. This source trace excludes the proposed lost-callback mechanism; ordinary awaited-load tests still do not prove scheduling/liveness under cancellation. If dispatch is dropped during shutdown, eventual promise delivery is not established here.

### Worker synchronous reentry or shutdown might expose dangling borrowed state

The new runnable owns RefPtr set/entry/result plus an owned attributes value. Unlike the older update runnable, it borrows no worker-stack attributes/result. `WorkerMainThreadRunnable::Dispatch` retains worker lifetime with a ThreadSafeWorkerRef and returns failure through ErrorResult. `MainThreadRun` returns true after producing a result; it does not confuse a false sync-loop result with a normal clone failure. No entry/set mutex spans dispatch.

After dispatch, the setter checks the face owner, descriptor object identity and entry identity. Destroy clears the owner and entry; a successful nested descriptor publication changes the descriptor identity. A loaded-path result rejected by these checks has not been published to a family or global font cache. Its wrapper destruction proxies platform-entry release to main. The raw set pointer in a fresh Entry is covered by the runnable's and face's strong set references during preparation/publication.

The inspected sync loop explicitly processes control work and can encounter shutdown/non-control work through notification handling. This review does not assume arbitrary reentry is impossible. The guard is not a proof that every set/worker shutdown invariant holds: it checks the FontFace owner and identities, not all possible owner-set state. No concrete reachable use-after-free or publication counterexample was identified from that distinction. A controlled shutdown/timing test remains an open gate.

### The changed setter might mutate peers on no-op or not-yet-loaded input

Unchanged descriptors return before provider preparation and membership invalidation. With no existing entry, v2 retains GetData() and the previous in-place parse behavior; this removes the extra constructor-descriptor clones from v1. The retained Servo glue delegates to the existing Rust descriptors.set operation; its parse-before-assignment contract was reviewed previously and is a dependency here, not a new parser proof. The no-entry adaptation preserves that existing operation. With an entry, parsing occurs on a detached rule even when the native entry is not loaded.

The nonloaded branch deliberately calls the legacy `UpdateUserFontEntry` on the existing wrapper. It can still mutate a wrapper shared by peers, and a later shutdown/stale-publication failure cannot roll that mutation back. A DOM-loaded face whose native provider was reset can also enter that branch. This is a concrete retained limitation, not transactional coverage. The v2 candidate does not broaden its loaded-clone guarantee to this path. The review finds no additional regression introduced by the conditional-clone adaptation, but does not approve wording that claims all FontFace states are isolated.

### Provider clones might borrow a dying handle or copy stale caches

CoreText clones retain the admitted CGFontRef through the existing CFRetain constructor. Its fresh constructor resets derived cmap/AAT/CFF/variation/cache state and receives the new CSS ranges. Source locking covers the retained handle. DirectWrite retains IDWriteFont for local input or IDWriteFontFile plus IDWriteFontFileStream for data input; it copies the data face type and native policy flags. The widened stream parameter matches the already-stored interface type. The existing memory-reporting concrete downcast still relies on data streams originating as gfxDWriteFontFileStream; this clone preserves that provenance rather than accepting an unrelated new stream source.

FT2 and fontconfig acquire strong SharedFTFace references before handing ownership to the new entry. In the inspected source, these atomic pointers are installed once (compareExchange) and cleared in the entry destructor; keeping the original entry alive prevents the pointed face from being released between the load and AddRef. This is a concrete reason the new atomic pointer read is not an unprotected borrow from an independently destroyed entry. It does not prove all future mutation or face-use policies.

Fontconfig retains its refcounted pattern and reconstructs local platform feature defaults, rather than copying old CSS-populated feature arrays. Its added Fontations hook is gated by the clone flag and retained-face state. Ordinary entries keep the prior path. Common initialization appends new CSS features/variations once, sets family/metrics/size/range data from the new wrapper, and copies every field in the inspected gfxUserFontData definition into a distinct metadata object. FontData and source handles remain strongly retained. Sanitized data can initialize a new Skrifa object; no old owning raw Skrifa pointer or populated shaping cache is copied.

No new omission or dangling resource was identified in these exact constructors. This conclusion does not compile DirectWrite/FT2/fontconfig or establish immutable resource bytes. CoreText's preexisting lazy Skrifa path may look up a font by name, and FreeType/fontconfig may reopen a retained file locator. External replacement/removal and feature/variation/metric effects beyond the WPT matrix remain unproved.

### Destroying an uncached clone might evict or mutate its peer

The clone is not inserted into UserFontCache. `ForgetFont` iterates and removes only entries whose provider pointer equals the destroyed provider, so equal descriptor/resource identity cannot evict the old provider. Fresh provider identity also prevents reusing font-instance caches keyed by the old provider pointer. Family membership invalidation occurs after publication via NonRuleFontFaceChanged; removed faces remain removed. The existing worker-removal repair is pinned unchanged. This source trace supports peer isolation but does not prove a particular cache-sharing route occurred during a browser test.

## Comparison harness and raw integrity

Fresh source-only replay passes the candidate's exact conditional-clone transformation, recorded formatting delta, all 16 originals/candidates and patch apply/reverse, then the unchanged 68-case test registration. No formatter/compiler/browser ran in this review.

Both baseline directories were copied and independently passed the v2 comparator against raw JSONL, exact command shape, before/after hashes, fixed source/test/resource/config/metadata pins, exact test identities and receipt status summaries. Matrix baseline: 30 PASS / 38 FAIL, three OK harnesses. Regression baseline: 18 PASS / 1 FAIL subtests, plus four PASS / one FAIL / three OK harness endings. These are retained original observations, not candidate results or accepted regressions.

The matrix requires exact case multiplicities for all 12+28+28 subtests and three wrappers. The regression suite requires all eight harness IDs, including both existing worker-removal wrappers; compare.py additionally rejects duplicate result identities and requires identical baseline/candidate row keys. Actual and expected statuses are preserved separately. Paired comparison permits only reviewed native pins and binary/package identity to differ, and reports every changed status/expected tuple. It does not automatically turn a valid pair into runtime acceptance.

Three targeted negative checks were performed on disposable baseline copies: (1) change a raw status and update its raw-file hash but leave the summary, (2) rename a test in both raw and summary and update hashes, and (3) change a post-run binary hash and update its receipt hash. All are rejected. Thus the validation uses raw/summary agreement, fixed test identities and before/after equality beyond merely checking self-consistent file hashes.

Build success remains an explicit root attestation tied to before-build pins and a log hash. The comparison tool does not prove a compiler consumed every source, inspect the terminal build itself, prove no intermediate edits, or establish full working-tree/server/OS immutability. Root must review actual build completion and candidate raw outcomes. Candidate binaries should differ as expected after native compilation; a comparison record alone is not sufficient proof of that provenance.

## Remaining acceptance boundary

Proceed with the exact local macOS build and paired matrix/regressions if those root gates pass. Keep other backend compilation, controlled local fonts, native-loaded/DOM-loading scheduling, shutdown/reentry, full provider lifetime, legacy nonloaded sharing and broad formal correctness explicitly open. No source fix is requested by this narrowed review. No live source/WPT, Git/index, Mach, build or browser operation was performed by this reviewer.
