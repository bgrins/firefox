# Independent exact traversal review

**GO for the reversible Gecko build, browser regression and performance experiment. This is not approval to land or a claim of browser/performance acceptance.**

Reviewed producer: `css-cssom-exact-traversal-proposal-v2`, outer FILES `b553dbebc08b6e82b635c30f2e90b254558d513faab385cad3e840abb9465f8c`, patch `9ecbf1c84bd59754bf343cd1324a6e6aa6c39eb664489e1aff0d4a614fe4451f`. All 298 outer payloads authenticated. The 26-input inner capsule was independently authenticated, copied by manifest to `native-source`, and freshly replayed. No producer, native, Git, browser or build inputs were changed.

## Source verdict

The corrected implementation resolves both substantive objections retained in `DOMAIN-CHALLENGES.json`: an ancestor subtotal can exceed signed32 despite every rectangle-relative prefix fitting, and an exact translation can exceed signed32 despite the translated rectangle fitting. `AppUnitTranslation` and checked signed64 ordinary accumulators preserve these cases without executing the old overflowing `nsPoint` additions. The previously reviewed bounds component establishes the required difference bounds for every finite v1-admitted trace, without a frame-count assumption. That mathematical result and its manual source projection remain separately recorded in immutable `bounds-review-v1`.

This establishes a source-based argument for **inclusion** of the v1 exact domain, not equal acceptance. The new path can safely accept a rectangle at x=1 billion translated through +1.5 billion and −2 billion: v1 rejects the first rectangle prefix, whereas the final 500-million coordinate is representable. The extension is deliberate. No intermediate clipping is being removed from the original ordinary translation traversal. Final edge/dimension checks remain necessary.

I read the complete changed `GetTransformMatrix`, `GetTransformToAncestor`, new `TransformClientRectToAncestor`, both header changes, and the surrounding `BoxToRect`/publication integration. Findings:

- Existing callers default to null metadata and retain the original grouped `nsPoint` arithmetic and scaling. The new carrier is a namespace type, with a forward declaration in `nsLayoutUtils.h`; it does not require a nested type of an incomplete `nsIFrame`. Indexed caller discovery found no function-pointer use, but only the full build establishes header/caller compilation.
- Opt-in traversal preserves old-defined matrix values: each wide subtotal equals the corresponding original integer subtotal; at differing APD it passes the same representable operands to the original `ScaleToOtherAppUnits`; at equal APD that provider is identity. Float conversion and subsequent multiplication/project-to-2D ordering remain unchanged. This source argument is stronger than, and distinct from, finite agreement in the affine facade.
- Metadata is reset before self/root/transformed returns. It is available only when the first ordinary segment reaches the requested ancestor with empty flags, layout viewports, the same context, and no excluded SVG/transformed frame in the traversed route. A later segment cannot restore it. The target's own transform is outside the coordinate system being converted and is correctly excluded.
- `BoxToRect` opts in only for root-relative, non-outer-SVG requests that already account for transforms. Content/padding/margin/ink rectangles can have nonzero origins; the new checked addition uses that actual origin. Other caller routes remain intact. The actual caller skips `outer == relativeTo`; the wrapper's zero-length case is nevertheless checked independently.
- Final width/height nonnegativity plus checked x/y/right/bottom and nscoord limits justify narrowing both coordinates. A failure on either axis sends the complete rectangle through the original fallback. Source SVG-text rejection precedes precomputation, preserving its original recursive handling.
- On ordinary fallback, the already computed matrix is supplied as a populated cache to the original rectangle converter. The source converter consumes that cache; it does not walk the ancestry again. Transformed/perspective/SVG/viewport/clip behavior is still supplied by existing native providers, not proved by the extracted affine facade.

### Explicit arithmetic limit

Checked64 failure, or differing-APD scaling with an unrepresentable signed32 ancestor subtotal, restarts the old null-metadata method. This is outside both the old-defined arithmetic domain and the v1-admitted same-context exact domain. **That restart can still execute legacy undefined arithmetic.** The retained cross-document witness intentionally demonstrates it under UBSan. This review does not approve a universal arithmetic-safety claim or call every possible path a single traversal. No early saturation or new rounding policy is introduced.

Actual frame/context topology, getter purity and lifetime stability, cross-document scaling, platform graphics, perspective/3D composition, SVG recursion and layout flushing remain native/provider assumptions. No universal native source-translation theorem or full safe-origin F1–F12 closure is claimed.

## Independent execution

The relocated replay completed at both `-O0` and `-O2` with actual retained Mozilla CheckedInt headers and UBSan:

- 168 original/candidate matrix, ancestor, operation-trace and method-count configurations per optimization; candidate opt-out and opt-in results also agree on these old-defined cases.
- 2,048 v1-admitted generated finite chains per optimization and the two decisive wide-domain witnesses.
- Five separately compiled semantic mutants rejected at both optimizations.
- Original grouping/translation witnesses fail UBSan as expected; candidate versions pass. The separate legacy-restart witness fails for both variants, as expressly required by its negative oracle.

`Challenges.cpp` adds ten independent case families at both optimizations: both-axis grouping overflow; both-axis translation beyond signed32; negative translation beyond signed32; deliberate acceptance extension; exclusion of target-coordinate transforms/SVG flags; one-axis final edge rejection using the cached fallback; metadata reset on identity; identity final-edge clipping; and positive/negative old-defined near-boundary matrix agreement. All passed. The tests compile complete extracted methods but retain the producer's explicit frame/graphics/rectangle providers; they are not full Gecko executions.

The compiler executable hash was independently checked before execution. SDK, standard library and compiler semantics remain external. Temporary executables were removed by scoped temporary-directory cleanup after terminal results; sources and logs remain. The producer's verifier is an externally pinned payload checker, not a general untrusted archive validator: this review additionally checked canonical input paths, regular entries and the manifest-only relocation before executing it. Empty-directory/FIFO closure is not claimed as a property of the producer verifier itself.

## Experiment readiness

The reviewed driver snapshots are in `driver-reviewed`, with exact hashes and scope in `DRIVER-REVIEW.json`. Its baseline rebuild and comparison against the previous DOM-only run, candidate four-file replacement, final source restoration/rebuild, HEAD/index/fixed-native checks and WPT removal are suitable for this reversible experiment. It compares exact test/subtest keys and file-end outcomes, preserving expected failures. Final execution must pin the finalized candidate, scripts, tests and retained baseline before mutation.

The benchmark validates geometry, checksums, visibility and before/after stability for six ordinary/near-leaf-transform/near-root-transform cases. Two baseline-before, two candidate and two restored runs are useful local measurements. Their fixed order and small process count do not justify a broad no-performance-regression claim; review individual batches and restored-baseline drift. No owned compiler process remains running to contaminate the timing window.

Required next gates: actual four-file/header Gecko build; exact four-case integer WPT and unchanged existing transform/SVG/iframe/scroll/zoom/observer outcomes; actual-source formatting checks; measured hot-path behavior. A build failure or browser/performance regression requires revisiting this recommendation. The earlier v1 browser results are historical calibration, not successor v2 runtime evidence.

## Recheck

Run the independent `verify.py` with the external review FILES pin to authenticate this report, retained source and receipts. A new extraction replay can be run from `native-source/replay.py` with its pinned inner FILES and an absent external output directory. The separately sealed bounds review is preserved byte-for-byte and has its own verifier.
