# Wrapped flex line cross-size sum repair

Native/WPT candidate passes; independent source/formal review is in progress. No accepted-fix count or signed commit is assigned yet.

The two-file patch widens the initial cross-gap product and each line-size addition to signed64, then caps each result to nscoord_MAX before narrowing. It leaves line generation, item layout, cross-size provider selection and other packing arithmetic unchanged. The gap count is backed by a nonempty uint32-sized line array. With nonnegative signed32 gap/line inputs and a capped accumulator, both widened expressions fit signed64; stored results fit signed32. The arbitrary-list primitive proof is in the separately sealed discovery artifact.

The exact 144-case WPT changes 96 failures into passes; 48 passing status/message pairs remain identical. All numeric prerequisites are admitted on both Gecko runs. Only the flex CPP and two browser binary pins change. Cases cover three writing modes, both directions, row/reversed-row, wrap/reverse-wrap, plain large lines, independent large gaps and combined contributions. Each case checks its supported input range and a definite-size control before the unconditional bounded auto-size result.

A successful local build and zero-error scoped native/WPT lint are retained. The first typed-coordinate implementation failed to compile because of overload ambiguity; the complete failed source/log are preserved. The final implementation uses explicit signed64 expressions. No source formatting change followed the successful browser run.

The 27-file regression run exits zero with 914 passing subtests, 20 passing reftests and six OK harnesses. content-height-with-scrollbars.html produces its metadata-listed intermittent FAIL. That result is retained and is not counted as a pass; no baseline comparison is claimed for that file. There are no unexpected regression outcomes. The production change is identity for nonnegative totals within nscoord_MAX, but that arithmetic fact is not substituted for a fresh baseline of the intermittent reftest.

Standalone apply/reverse checks pass against both retained bases, with exactly the Gecko CPP and the new WPT. The resulting source snapshots and test bytes are retained. The real index and worktree are preserved by packaging. Browser runs use the shared development build; no isolated upstream build is claimed.

Scope remains explicit: optional absent max/min and aspect-ratio branches need independent consumer review; saturation above nscoord_MAX intentionally changes some old signed32-representable totals when no smaller maximum applies. It is not universal old-defined identity. Earlier per-item/baseline arithmetic, subsequent packing/position/overflow operations and all browser-reachable numeric safety are separate obligations. This repair is independent of the earlier baseline-group maximum sum and collapsed-item changes.
