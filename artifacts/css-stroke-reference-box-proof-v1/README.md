# CSS reference-box alias companion

This package connects an independent CSS reference-box contract to a bounded test of the exact native function. It does not formally verify all transform geometry.

## Contract and repair

[CSS Transforms 1 transform-box](https://drafts.csswg.org/css-transforms-1/#transform-box) groups CSS-layout reference boxes into two equivalence classes: FillBox/ContentBox and StrokeBox/ViewBox/BorderBox. SVG elements use a separate mapping. The retained primary snapshot and its identity are in `SPEC-v1.json`.

The repair removes only the TODO and early return following the non-SVG StrokeBox case in `TransformReferenceBox::EnsureDimensionsAreCached`. StrokeBox then takes the existing border rectangle path. The whole-file preservation checker compares the archived before and candidate files byte for byte, allowing only that two-line deletion. The unchanged SVG helper, early SVG dispatch, cache guard, unzoom lambda, content path, border dimensions, and downstream transform code are covered by this preservation check; textual preservation is not a semantic proof of those bodies.

Candidate native SHA256: `c0a371e663c328e36319844aa42df07fe518ac4c932f8a16d4312690e6dc9ae9`.

## Lean scope

`ReferenceBox.lean` states `Uses` and `Alias` relations independently from the implementation switch. Its selector contract connects a simple classification function to those relations. Payloads are universally quantified over an arbitrary type; they are not restricted to the finite native fixtures or integer rectangles. An arbitrary pure `unzoom` function preserves equality of aliased payloads. The SVG provider is arbitrary and may return a different payload for every box keyword.

Fourteen audited statements establish:

- Selection agrees with the normative `Uses` relation.
- The reflexive, symmetric and transitive alias relation preserves the selected payload, including the three basic aliases.
- Applying the same optional normalization preserves aliases.
- SVG resolution delegates to the opaque provider, CSS resolution uses the CSS selector, and disabled normalization is identity.
- An uncached state is initialized with the resolved payload; a cached state is retained; repeated initialization is idempotent; initial storage does not affect a cache miss; equivalent CSS aliases initialize equal caches.

The cache model assumes fixed frame inputs and pure providers when interpreting the resolved value. It proves no freshness after a frame/style mutation, cache lifetime rule, or invalidation mechanism. Its hit theorem describes retained storage, not whether retaining it is appropriate after changed inputs. The model is not an operational proof of C++ evaluation order; native counters separately check finite call behavior.

`check.py` compiles every theorem with Lean and reads its exact `#print axioms` output. Only `propext` is permitted; missing audits, unexpected diagnostics, untrusted declarations, and altered semantics must fail. There are no admitted proofs or native-decide trust shortcuts.

## Native bridge and premises

`bridge.py` extracts the complete `EnsureDimensionsAreCached` definition from the archived native file, including the original conditional-compilation text. It appends that unmodified definition to explicit adapters in `bridge-prefix.cpp` and `bridge-suffix.cpp`. Both original and candidate functions are compiled and executed independently.

Adapters provide:

- Five named transform-box tags and the SVG frame-state predicate.
- Fixed CSS content rectangle, frame border rectangle, and opaque SVG rectangle.
- A four-int32 rectangle with Width/Height accessors.
- An instrumented Style/EffectiveZoom/Unzoom path.
- Cache fields and the frame pointer, including cached objects with no frame.

The adapter `Unzoom` divides all components by a positive integer. Fixtures use exact multiples for factors 1, 2 and 3. This validates branch choice, invocation count, and preservation of all four components through a nonidentity adapter. **It neither extracts nor proves Gecko's actual StyleZoom arithmetic.** The Lean normalization theorem is stronger about equality preservation but assumes the same pure normalizer is applied to both aliases. Actual frame rectangle computation, typed units, float rounding, zoom factors, overflow behavior, and native header layout are source-reviewed bridge premises rather than executed Gecko implementations.

The ordinary build branch has `UNIFIED_CONTINUATIONS` undefined, matching the source's disabled define. That is the branch compiled by the capsule. The disabled continuation-union branch is retained and protected by whole-file preservation but is not executed or proved.

For CSS content aliases the expected payload is the supplied content rectangle, including its origin. For border aliases it is `(0,0,frameWidth,frameHeight)`, not the frame's position. For SVG the expected payload is the opaque provider rectangle regardless of the CSS alias classes. Optional unzoom then applies once. Cached inputs preserve their old payload and make no frame/provider calls. A second invocation with fixed inputs preserves both the result and cumulative call counts.

The native suite has 850 fixtures: all five keywords × CSS/SVG × cached/uncached × unzoom/no-unzoom × factors1/2/3 × seven geometries, plus ten null-frame cache hits. The geometries distinguish content/border/SVG payloads, nonzero and negative origins, zero dimensions, unequal dimensions, and larger positive dimensions. Each fixture invokes the function twice. Expected values and call counts come from the independent alias classification; original StrokeBox behavior has a separately stated expected oracle.

Seven Lean semantic mutations, six Lean diagnostic guards, nine native semantic mutations, four compiler/runtime diagnostic guards, per-input source corruption guards, and four whole-file-preservation mutations are required to fail or disagree as appropriate. Native semantic mutations must compile without diagnostics and return a different observed result; a compiler failure is not counted as detecting a semantic mutation.

## Executed development result

The complete development checker exited 0. All 14 Lean audits passed (only `propext` where listed), all 850 candidate native fixtures matched, and the original function matched its separate legacy oracle. Exactly 42 original fixtures disagreed with the specification oracle, all uncached non-SVG StrokeBox cases. All seven Lean mutations, six Lean diagnostic guards, nine native mutations, four native diagnostic guards, 16 input identity guards, and four preservation guards were detected. Final frozen production of this companion is authenticated by `PREPARATION-v1.json`; independent replay remains a separate acceptance step.

## Reproduce

```sh
PYTHONDONTWRITEBYTECODE=1 python3 artifacts/css-stroke-reference-box-proof-v1/check.py --out artifacts/css-stroke-reference-box-proof-v1/replay-new > artifacts/css-stroke-reference-box-proof-v1/replay-new.log 2>&1
```

The output directory must not exist. A successful run writes `RECEIPT-v1.json` with theorem axioms, extracted-source hashes, exact fixture count/hash, original counterexample count, and all control results. Compiler flags are `-std=c++17 -O1 -Wall -Wextra -Werror -fsanitize=undefined,implicit-integer-truncation -fno-sanitize-recover=all`. The actual Lean/clang executable hashes and versions are pinned in `TOOLCHAIN-v1.json`. Receipt content excludes output-directory paths to permit independent comparison; diagnostic logs naturally contain replay-local paths.

`prepare.py` writes source identities and the source-only `tooling-paths-v1.txt`. Run preparation only before freezing; it is not a replay step. The companion belongs in a tooling commit preceding the separate native+WPT repair. Generated binaries, mutation fixtures, logs and replay outputs are evidence artifacts, not source companion paths.

## Boundaries

The source-preservation check and finite C++ execution bridge the mathematical model to the native branch; neither turns the Lean theorem into a universal proof of compiled C++. Providers, enum correspondence, rectangle accessors, frame state, header-field meaning, and preprocessing configuration are explicit assumptions. There is no proof of SVG bounding boxes, CSS/SVG layout, percentage resolution, transforms, transform-origin, perspective, painting, hit testing, cache invalidation, or WPT/browser behavior. Browser before/after acceptance is recorded separately by the root and its independent reviewer.
