# v4: common-layout traversal with null metadata

Status: artifact proposal; **no Gecko build, browser result, timing result or native acceptance for v4**.

## Exact change

`v3-to-v4.patch` changes only the final dispatch in `nsIFrame::GetTransformMatrix`. The existing empty-flags/layout-source/layout-target predicate is evaluated before metadata selection. Its null-metadata case now instantiates `traverse<false, true>`; other null calls retain `traverse<false, false>`. Both wide instantiations are unchanged. The early transformed/zoomed-source branch, traversal body, exact-result eligibility, arithmetic, overflow restarts, providers and rectangle wrapper are byte-identical to v3.

`proposal.patch` also packages the whole proposal against the same retained pre-v2 source as v3. It changes four files; DOMRect is unchanged. Both this patch and the one-file v3 delta apply and reverse byte-exactly in disposable directories. This is source applicability, not an isolated Gecko build. `BASE-AUTHENTICATION.json` records authentication of all 463 sealed v3 payloads and its 31-input closed capsule against the independent review's recorded pins.

## Why the new dispatch preserves behavior

For a null pointer and the common predicate:

* Empty flags make `IgnoreScrolling` false, so the generic position selector returns exactly `GetPosition`.
* A layout target makes the visual-viewport stopping clause false. Empty flags make the stacking-context/display-port clause false. The surviving stop test is exactly `IsTransformed`.
* `TrackWide=false` retains the original `nsPoint` additions, APD conversion grouping, narrowing/provider behavior and final matrix conversion. It makes exact metadata eligibility false; no null metadata write is introduced.
* Ancestor equality is still tested before transform stopping. Parent/context calls and the reached ancestor are unchanged. Numeric restarts retain null mode and now select the common instantiation only under the same predicate.

This reasoning uses the existing pure flag/viewport access and stable frame/provider assumptions. It does not replace cross-document scaling, transforms, SVG, graphics or frame lifetime with a new model. It preserves the admitted v3 exact domain, including wide cancellation and expanded rectangle origins; no prefix filter or depth restriction was added. The existing legacy signed-overflow outcome on the cross-document restart witness remains explicit in all roles. This proposal is not universal arithmetic safety.

## Extracted calibration

The corrected v3 facade, harness, v1-domain reference and Mozilla checked-arithmetic headers are copied byte-for-byte. The capsule compiles complete original/v2/v3/v4 traversal methods and the applicable exact wrapper at O0 and O2 with UBSan. Frame/context/viewport/scaling and limited affine matrix providers remain facades, not full Gecko implementations.

The final canonical and manifest-only relocated runs each cover 26 variant/optimization combinations:

* Original/v2/v3/v4 agree on 168 old-defined matrix/operation-trace/ancestor/call-count rows per optimization.
* v2/v3/v4 complete normal stdout agrees, including 2,048 generated admitted chains, exact self identity, stale metadata, SVG-state-bit-only fallback, wide cancellation, expanded-origin and cached fallback controls.
* Original fails the two deliberately overflowing wide witnesses; v2/v3/v4 return the expected exact result. All four retain the expected cross-document legacy-restart UBSan failure.
* All eight injected signed64 overflow states retain their expected guarded restart behavior. These are private-state boundary injections, not evidence that the small fixture reaches those states from production inputs.
* The seven prior semantic mutants remain discriminated. Two additional null-only dispatch mutants independently omit the empty-flags guard and the target-layout guard. They compile and fail the intended wide-versus-null comparison at `FAIL 270` and `FAIL 277`, respectively, at both optimizations. The former exercises nonempty flags; the latter reaches a zoomed ancestor with a visual target.

The first replay exposed a real calibration weakness: forcing the common path for **both** requested and null metadata makes their internal comparison agree even when both are wrong. The mutant exits zero but differs from the original in 49 of 168 rows. The final controller therefore additionally compares mutant rows against the original output, and retains both targeted null-only mutants. The initial failed control run and runner are preserved. This changes no candidate source or test oracle. An intermediate passing runner's original-reference difference counter was subsequently corrected from its not-yet-initialized comparison to zero; final replay uses that reporting correction.

The remaining mutations fail explicit semantic assertions; the overflow mutant is detected by the positive/negative injected doc-x controls. A compile failure or arbitrary runtime error is not accepted as a normal-path semantic mutation result. Exact results and retained logs are identified in `REPLAY-COMPARISON.json`.

## Cost hypothesis, not a performance claim

The new null common loop removes invariant flag/visual tests from ordinary untransformed segments, including segments encountered after an earlier transform or an exact-path fallback. It does not optimize the transformed-source branch itself.

There are now four potential traversal instantiations instead of three. Common null calls pay the predicate at entry before entering the specialized loop; noncommon null calls also pay that predicate before using the old generic loop. Compiler sharing/inlining, instruction-cache pressure and branch prediction may offset the saved per-iteration work. No extracted timing or production code-size measurement is claimed. A root-owned full build, unchanged WPT campaign and the established repeated browser timing protocol are still required before deciding whether to retain v4.

## Replay and integrity

Run:

```
python3 -I -S -B capsule/replay.py --files-sha256 e5171412e9d35ae3280fe194e803b3a2a6674242d262e70abdc4ddee62b1f720 /ABSENT/EXTERNAL/OUTPUT
```

The pre-import mode guard rejects nonisolated, site-enabled and optimized Python. The controller authenticates a closed regular-file/directory roster, source roles and compiler-driver pin before creating output, and reauthenticates after execution. Ten independent negative controls cover modes/shadow imports, changed source/pin, extra directory, symlink, internal output and a resealed wrong compiler-driver pin. They reject before output creation. Compiler backend, SDK, standard library, source selection/instrumentation correspondence and real provider semantics remain admissions.

The source proposal is intentionally separate from the sealed v3 runtime and all original allocation/lifetime proofs. It does not close any of their outstanding provider or whole-engine obligations.
