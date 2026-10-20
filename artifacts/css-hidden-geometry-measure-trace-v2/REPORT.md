# Hidden flex measurement and skipped layout experiment

Four instrumented variants completed both browser probes and rebuilt successfully.
Each variant measured 160 fixed-size stages and 240 shrink/descendant stages.

| Variant | Fixed-size mismatches | Shrink/descendant mismatches |
| --- | ---: | ---: |
| Original with tracing | 32 | 12 |
| Containing-block key omitted | 0 | 12 |
| Direct item dirtied on measurement miss | 0 | 4 |
| Principal children dirtied when flex layout is skipped | 0 | 0 |

The original trace records a clean hidden item whose containing-block key changes
from unconstrained block size 1073741823 to 0 app units. Its computed size remains
1440×1920 app units. The skipped measuring reflow installs 0×0 while the frame
remains clean. Removing the containing-block key avoids that fixed-size exposure,
but leaves the release-derived shrink failures and reopens the caption cache bug.
The direct-item repair leaves four clean descendant insertion stages stale at
100×32 instead of 50×32. MarkPrincipalChildrenDirty at the hidden ReflowChildren
return passes both matrices, including those descendants.

This is diagnostic evidence on the shared tree, with tracing enabled. It is not
native acceptance, an uninstrumented WPT run, a performance measurement, or proof
of correctness for positions, continuations, out-of-flow frames or dirty histories.
The direct-item Lean model has a narrower scope than the broader source candidate.

Fix101's containing-block key requires a landing hold pending the skipped-layout
repair and dependency review. The separate installed Firefox158 shrink probe
establishes preexisting exposure; this experiment additionally shows the key's
contribution to the fixed-size fixture. Neither key omission nor the partial repair
is the final proposal.

All original source bytes were restored and the restoration build exited zero.
BEFORE and FINAL match for HEAD, index and all25 pinned source files. The rebuilt
browser includes committed rectangle fix103 and the preserved native prototypes.
No candidate repair remains installed. Binary byte identity is not claimed.
