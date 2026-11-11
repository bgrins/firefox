# Independent owned-generation source review

No blocking source finding. The copied prerequisite is suitable for a separately reviewed reversible build and preservation comparison. This is not acceptance of a missing-pseudo repair or validation of the new owned-refresh call sequence.

## Inputs and checks

Reviewed the complete four-file patch SHA256 `3d36502810ce70d334b0a3c8e80949ef93bcd387444bf9d802881e59e3f6e3c5` in `css-pseudo-animation-owned-generation-20261110-v1`, the twelve pinned native sources, source and test manifests, recorded Searchfox discovery, and the eleven-page test plan. The base is `d825b3e46700b1378820a591ff8f5a5c15bbc811`. This cumulative patch replaces the earlier completed-output snapshot candidate; it must not be stacked on that candidate. Composition extraction is separate.

Independently ran the frozen `check.py --check-git`: all twelve source pins, 34 test/metadata presence pins and two retained fixtures authenticated against immutable Git objects. Forward and reverse scratch patch application passed, as did the frozen complete-file manifest and structural extraction checks. `CHECK.json` pins the report, manifest and actual replay log. These are source checks, not C++ compilation or formal refinement. No live sources, tests, browser, canonical library or Git state were changed; no native build or browser run was performed. No temporary compiled outputs were created. Live restoration checks were deliberately not run during the root agent's exclusive native hold.

## Semantics and ownership

The generator body is unchanged except for explicit specified-array input and void return. Its helper functions, property membership calculation, stable range sorting, default easing/composite roles, implicit endpoint selection, null declaration sentinels and final array transfer are preserved. Generated keyframes are local to each property build. A snapshot cannot retain completed endpoints calculated before a later refresh because it has no completed-output member.

Virtual dispatch now captures optional CSS generation defaults. The sole recorded CSS override retains the JS-keyframe opt-out; base effects return no options. The public `GetComputedKeyframes` wrapper returns false without touching its output when no options are present, and otherwise regenerates from live keys. `GetKeyframes` itself remains unchanged, including its existing style flush and live offset update before generation. The CSS default composite and the effect composite are separate values and remain separate inputs.

Ordinary `BuildProperties` retains null-target admission, one specified-keyframe clone, attribute-output reset/forwarding, the debug specified-array equality check and unconditional move-back, including empty property results. It introduces no owned-offset refresh. The static builder uses the captured owning target and pseudo request, effect composite, and explicit style/timeline. It does not publish properties or restyles.

There is an intentional ownership/order change: formerly CSS generation read live keys and defaults after the defensive clone; now it reads the clone and captured defaults, with target/composite capture before generation. The inspected generation/default-capture code is synchronous array/value work without script dispatch or effect publication. This supports preservation for that path, not arbitrary reentrant overrides. The captured pseudo request no longer aliases the effect's live request across hypothetical retargeting. A strong element reference protects lifetime; it does not establish current target identity or style validity after mutation.

The snapshot owns its arrays and option values, but keyframe declaration blocks remain shared references. It is not deeply immutable, a cross-thread object, or a coherent snapshot of style, timeline, range, effect timing or provider state. Those remain caller obligations. Additional target references and option copies can change allocation/reference-count cost; no performance equivalence is established.

## Refresh boundary

`RefreshComputedOffsets` delegates to the existing offset routine on the private array. That routine modifies computed offsets, preserves specified values and uses the existing unresolved/non-view/zero-attachment-range behavior. Named-range mapping reads the timeline's cached state; this API does not tick the timeline, flush style, or certify that the cached data is current. Property generation after refresh sees the refreshed array, but only a future caller can establish that its timeline/range/style contexts agree.

There is currently no production caller of this new refresh method. Ordinary range tests exercise existing live refresh and the shared generator, not the new sequence of capture, owned refresh and property build. The type does not require refresh before a build, nor prevent use of previously returned property arrays after context changes. Direct coverage of that sequence and its isolation from renderer-owned arrays is required when a query caller is added.

## Preservation experiment readiness

The eleven-page inventory is appropriate for a bounded first comparison: CSS default easing/composition and implicit endpoints, JS replacement opt-out, effect replacement, target/pseudo lifetime and underlying values, named-range and unresolved/zero-range handling, and attribute-dependency forwarding. Existing failures must remain visible. The copied sources include the percentage-order changes; the separately accepted named-range ordering extension changes source/test provenance and requires a fresh baseline rather than reuse of historical callback counts.

No runtime wrapper is frozen for this seam yet. Before execution, pin actual source/configuration/browser and test bytes, review the reversible wrapper, and compare all record kinds, callback identities and statuses/messages with duplicate rejection, crash/error/terminal checks and full restoration receipts. A successful optimized experiment would support this refactor only. It would not cover the unused refresh API or close coherent timing, provider freshness, cascade/property masks, CSSOM cache/admission or transient pseudo-style obligations. The final missing-pseudo repair's debug validation, including the historical transform-hint failure, remains required.
