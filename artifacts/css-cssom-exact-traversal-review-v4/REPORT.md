# Independent v4 traversal review

Verdict: **GO for the reversible Gecko correctness/performance experiment only.** Final proposal authentication, relocated extracted replay and independent dispatch checks pass. This is not native landing approval or measured performance evidence.

## Source reasoning

V4 changes only the dispatch at the end of `GetTransformMatrix`. It evaluates the common-layout predicate first and selects `<false, true>` when the output pointer is null. The other three combinations retain the same selection conditions. The source transformed/zoom early branch and the shared traversal definition are unchanged.

The fourth instantiation is valid because empty flags exclude IgnoreScrolling and StopAtStackingContextAndDisplayPort, while a layout target excludes visual-root stopping. Plain GetPosition and IsTransformed-only stopping therefore produce the same provider choices as the generic legacy mode for that call. Target equality remains checked before the stopping predicate. Selecting the common mode does not assert that the current frame, target or all ancestors are otherwise eligible for exact output.

TrackWide remains false in this new mode. The original nsPoint additions, APD flush/reset order and scale calls remain in use; it neither introduces checked64 arithmetic to null callers nor changes any exact-result eligibility. Nonnull outputs still select the same wide modes as v3. Thus the source argument preserves v3's full checked-wide exact domain, including its deliberately expanded domain beyond the older v1 helper, and preserves old-defined matrix behavior.

A numerical restart from a wide mode may now enter common legacy mode. It receives the same arguments, and the predicate makes its position/stopping operations equivalent to the generic legacy mode. It does not make the preexisting overflow outside supported domains safe. The exception remains explicit.

Moving the predicate ahead of the null check adds entry work to some null calls, while adding a fourth specialization may change code size/inlining. The predicate itself reads enum/flag values and has no callback. These facts support semantic review, not a speedup claim. Actual compilation and the transformed-path cost concern remain experiment gates.

## Independent validation

Authenticated all 62 outer payloads and copied the 36-input source capsule by its closed manifest. External outer FILES pin is `9cb90bc4e1739c482b2b20785389b002cfeb297bc958b42684e58d37fa4e4770`; inner pin is `e5171412e9d35ae3280fe194e803b3a2a6674242d262e70abdc4ddee62b1f720`. The producer verifier passed. SOURCE-CHECKS independently reconstructs the exact dispatch replacement and checks the other four candidate files and retained facade/harness/reference against sealed v3. No wrapper, carrier, header, early-return or traversal-body difference is hidden by that comparison.

Fresh manifest-only relocated replay (session 68488, exit 0) compiled 26 role/optimization configurations with UBSan. Original/v2/v3/v4 match all 168 old-defined matrix/operation/ancestor rows per optimization. The complete v2/v3/v4 normal observations match, including 2,048 v1-domain chains and the expanded-domain witness. Original grouping and rectangle-origin cases overflow as retained; wide roles pass. The cross-document legacy-restart witness still overflows in all roles, outside the claimed supported domain. Eight injected accumulator controls per role/optimization remain private-state guard checks, not reachability claims.

The corrected mutation oracle is material: forcing common dispatch for both output modes exits zero but produces **49 original-reference ROW differences** at each optimization. This review independently recomputes those differences from retained raw rows. Exit status or agreement of two equally wrong paths is insufficient. The null-only missing-flags and missing-visual-target mutants fail the intended `270` and `277` assertions. Other mutants fail their named semantic assertions; the unchecked overflow mutant is rejected by injected positive/negative doc-x controls. Initial failed and intermediate replay controllers are preserved in producer-evidence/development, not substituted for the final replay.

Independent v3 and v4 extracted programs pass at O0 and O2 with UBSan (session 62737, exit 0): 48 combined dispatch cases, 16 SVG mask cases, four exact/fallback geometry controls and 81 SafeAdd/CheckedInt comparisons per program. Four additional null-output checks assert concrete results: ignored-scrolling positions, stacking-stop ancestor identity, visual zoom scale/call count, and the same zoomed ancestor under layout coordinates. These expected values do not rely only on wide/null agreement. All four programs have identical stdout.

Both compiler sessions are terminal. Temporary-directory executables were removed automatically; source, compilation logs, runtime logs and result receipts remain. No Gecko build/browser or native/Git mutation occurred in this review. Runtime script authorization and fresh source/index pins remain root-owned.

## Remaining gates and boundaries

Full graphics/scale/frame-lifetime providers remain explicit facades/admissions. Injected extreme accumulators test failure sequencing, not reachable small frame histories. V3's finite browser success and mixed performance evidence cannot be transferred to untested v4 machine code. No full safe-origin or whole CSSOM closure is claimed.
