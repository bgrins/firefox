# FontFace loaded-provider candidate: macOS API review

## Result

No concrete C++ API or access-control blocker found in the reviewed macOS/common paths. This is source review, **not compilation or integration approval**. The 55-input candidate package authenticated before use; all 16 current production files byte-match its frozen originals. No production source, Git state, build or browser was changed. Existing broad lifetime/platform review remains in `css-fontface-provider-integration-review-v1`; this report does not replace its open gates. This reviewer previously authored the common/backend proposal; the present pass is a targeted self-review, not an independent implementation author.

## API findings

| Check | Source evidence / conclusion |
| --- | --- |
| Derived return conversion | `mfbt/AlreadyAddRefed.h` has the implicit `already_AddRefed<U>&&` constructor and explicitly documents the derived `RefPtr::forget()` return pattern. CTFontEntry publicly inherits gfxFontEntry. Returning `fe.forget()` to `already_AddRefed<gfxFontEntry>` is supported. `RefPtr.h` supplies the corresponding convertible constructors. |
| CoreText constructor | Existing public user-resource constructor accepts name, CGFontRef, weight, width, slant, data-user and local-user flags in exactly the proposed order. It retains CGFontRef, initializes fresh lazy/cache state and records the ranges/flags. The destructor releases the resource. Existing local/data admission uses this same constructor; clone does not reactivate or relookup the font. |
| Const source lock | `gfxFontEntry::mLock` is mutable; CT's font reference and initialization flag are guarded by it. The clone's read lock covers those reads and construction/retention. It ends before common descriptor initialization and `SetFamilyName` acquire the new entry's lock. The helper is inherited protected access from a CT member. |
| Common initializer access | `gfxFontEntry` explicitly friends `gfxUserFontEntry`, allowing its call to protected `SetSkrifaFont`. `gfxUserFontSet.cpp` already includes StaticPrefs_gfx and the Fontations generated header under the matching guard and imports mozilla/mozilla::gfx. FontData has the called const Data()/Length() methods. User-font data fields are public and their reference/array copies match existing types. |
| Source-list ownership | SourceList returns a const nsTArray reference; nsTArray::Clone is const and returns a new array through Assign. gfxFontFaceSrc consists of copyable scalars, strings and owning reference types. No unique-buffer copy constructor is required; retained FontData is shared by RefPtr. |
| Worker signatures | The runnable's constructor, boolean MainThreadRun and Dispatch(worker, Canceling, ErrorResult&) match WorkerMainThreadRunnable. The nested class can access the set's protected preparation helper. Inputs and result are owned fields. Caller propagates dispatch failure before taking the result; parsing's Servo write lock has returned before dispatch. |
| DOM declarations | SetUserFontEntry's new definition matches its declaration/default argument. GetAttributesFromRule already has a default third argument. ErrorResult exposes ThrowUncatchableException and the candidate immediately returns. New preparation helpers are declared in the corresponding headers. |
| Loading publication | Existing Entry::SetLoadState snapshots owning FontFaceImpl references and queues a lambda targeting that face, not a later lookup through the old wrapper. SetUserFontEntry(entry, false) does not inherently disconnect an already queued completion. This is source causality only; shutdown/reentry ordering still requires integration testing. |

## Recommended small revision: avoid cloning with no wrapper

The candidate clones the whole Servo rule on every SetDescriptor call. FontFace::Constructor creates FontFaceImpl, calls SetDescriptors, and only afterward initializes URL or buffer source. SetDescriptors creates mDescriptors and calls SetDescriptor for 12 fields; URL initialization adds the src parse. At these points mUserFontEntry is null. The candidate introduces 12 (or 13) unnecessary rule clones per successful constructor, including unchanged/default descriptors. This is an allocation/copy observation, not a measured performance regression.

Use a strong reference to GetData() when previousEntry is null; retain detached cloning whenever an entry exists. An explicit if avoids relying on conditional-expression deduction between raw/already_AddRefed forms:

```cpp
RefPtr<StyleLockedFontFaceRule> descriptors = GetData();
if (previousEntry) {
  descriptors = Servo_FontFaceRule_Clone(descriptors).Consume();
}
```

Why this preserves the original no-entry behavior:

- SetDescriptor rejects HasRule first, so GetData returns this object's mDescriptors. Its RefPtr retains the locked rule; the copy does not deep-clone it.
- Servo_FontFaceRule_SetDescriptor calls the generated Descriptors::set under its write lock. Each arm parses entirely into a temporary and uses `?` before assigning the member. Invalid parsing cannot partially assign the descriptor; the existing quoted-family retry remains valid.
- With no entry the preparation/worker-dispatch branch is skipped. There is no new post-parse fallible provider transaction to roll back, and no new event-loop boundary introduced here.
- SetDescriptors still resets the entire rule to an empty rule if any constructor field fails. This preserves its all-descriptor error behavior.
- The existing-entry branch, including unloaded/loading entries and native-loaded/DOM-loading state, still clones and retains the candidate's transaction/reentry checks. Do not weaken it based merely on DOM status.

Recommend making this small artifact revision before integration. It is supported by the actual caller and parser bodies; no additional architecture or semantics decision is needed. This review has not applied the change, and the sealed proposal remains the always-cloning version.

## Remaining gates and limits

Actual macOS compilation (including enabled Fontations configuration), formatting, platform builds and the prepared runtime matrix remain necessary. Source review cannot establish SDK availability, linker completeness, thread interleavings or all allocation/failure behavior. Base CloneUserFontEntry still returns null after an unreachable assertion; the common initializer release-asserts a clone, so unreviewed provider subclass admission must not be inferred from these macOS checks. Windows/FT/fontconfig declarations are retained for identity, but their compile status is not claimed here. Worker termination, native-loaded/DOM-loading completion, shared-provider isolation and lazy local resource semantics remain the existing integration boundaries.

## Replay

`python3 artifacts/css-fontface-provider-macos-compile-review-v1/check.py`

The checker authenticates all retained inputs before structural source checks. It does not compile or execute C++/Rust. `SOURCE-IDENTITY.json` records the exact original/candidate comparisons; current production changes after capture do not change this review's identity.
