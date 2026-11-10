# Query-selected timeline feedback

The current local browser completes all four diagnostic callbacks. Opposed and
aligned offsets repeatedly expose a pending animation with its underlying `idle`
value; the constant-query and stable-underlying controls settle on the later
provider. This is evidence for further scheduling investigation, not another
accepted bug, an infinite loop, or a conformance verdict about the final value.

Native source revision: `3a6a6bfe2b0d3d551b2392206179f251002cfc7e`.
The browser is authenticated against
`../css-style-query-current-build-20261110-v1/build-result.json`, including repair
`90e0949346b5`. No native changes or compilation were part of this experiment.
The runner requested `STYLO_THREADS=1` and enabled style queries, scroll animations,
and dump output; `run.py` records the exact invocation and preferences.

| Mode | Four synchronous reads | Twelve frame reads |
| --- | --- | --- |
| Opposed offsets | `idle`, fallback, pending, null animation time/progress | Same |
| Aligned offsets | `idle`, fallback, pending, null animation time/progress | Same |
| Constant query | `idle`, provider, pending, null animation time/progress | `on`, provider, ready, 75% progress |
| Stable underlying value | `on`, provider, pending, null animation time/progress | `on`, provider, ready, 75% progress |

Every mode first establishes a running, nonpending animation at 75% on the
fallback, with playback rate 1. All modes retain animation identity and fixed
scroll offsets. The literal timeline declaration selected by the query avoids
animation-tainted `var()` substitution into a nonanimatable property.

The 4 PASS / 1 OK result checks those setup and identity assertions. It does not
assert a settled state after arming. Each observation reads the gate, effect
timing, timeline, animation timing, provider style, and gate again in that order.
Those getters can cross multiple flushes, so a row is not an atomic native
snapshot. A resolved 75% fallback timeline does not imply resolved animation
timing. Twelve pending observations cannot distinguish persistent pending state
from readiness followed by rebinding between reads.

`ANALYSIS.json` authenticates and groups all 80 records. `check_analysis.py`
rejects wrong test identity, callback failure, missing observations, unknown
modes, a pending baseline, and a malformed prefix. These checks validate the
record parser; they do not prove the browser's sampling schedule.

`ROOT-RESTORATION.json` independently confirms the complete application and
associated build files were restored, binary hashes match the current build,
HEAD/index stayed unchanged, tracked files are clean, the owned process group is
gone, and the temporary WPT and backups were removed. The existing 29 untracked
paths were preserved. `verify_restoration.py` is tied to that historical HEAD;
do not treat its HEAD check as applicable after later commits.

Reproduce analysis without a browser:

```sh
python3 -I artifacts/css-style-query-feedback-runtime-20261110-v1/analyze.py
python3 -I -B artifacts/css-style-query-feedback-runtime-20261110-v1/check_analysis.py
```

The next experiment needs native phase markers for style calls, sampling,
readiness, and actual timeline-object rebinding. The companion
`css-style-query-timeline-feedback-source-20261110-v1` and
`css-style-query-timeline-feedback-review-20261110-v1` reports establish the
conditional pending barrier and its unproved native re-entry assumptions.
Repair #160 remains held; the browser repair count remains 169.
