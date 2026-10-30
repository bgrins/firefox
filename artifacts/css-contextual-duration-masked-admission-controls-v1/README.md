# Masked duration admission controls

This unexecuted fixture tests whether the proposed broad normal-restyle admission changes timing when its inputs have not changed, and whether it preserves script ownership of duration. It is separate from the fixed V81 checkpoint and changes no sealed predecessor.

The isolated tests tree contains two pages and seven callbacks. The original masked font-change page is copied byte-for-byte from the sealed isolation package: its final authored and animated fonts are both 32 px, so its first-read opacity remains .375 and effect duration 2000 ms. The new page adds six controls:

| Target | Mutation | Oracle |
| --- | --- | --- |
| Element or `::before` | Add an outline class | Both observed animation durations and progresses, and rendered opacity, remain equal to the stable pre-mutation measurements. |
| Element or `::before` | Assign the same authored font input | The same preservation checks; the setter may be optimized away, so PASS does not establish internal task dispatch. |
| Element or `::before` | Set effect duration to 1250 ms, then change authored font from 16 to 32 px | The fade remains at 1250 ms, progress .6 and opacity .6 at held time 750 ms. The other animation stays at 2000 ms. |

Every callback uses a fresh iframe, two named paused CSS animations, and retained animation/effect references. The fixed-font animation masks the base font with a constant 32 px output. The element begins with an inline 16 px font declaration. In the pseudo variant, the host supplies an unregistered `--font: 16px`, inherited by `::before` and used as its base `font-size`; the host has no animation. The font-changing ownership case updates that inherited value to 32 px. No custom property is animated or registered: these cases do not cover animation-taint policy, registered-property interpolation or arbitrary custom-property cycles.

After acquisition and explicit seeks, three frames precede baseline collection; a further frame separates two baseline samples. Baseline stability is asserted without choosing 1000 or 2000 ms for the unresolved initial contextual duration. After the single mutation, the first operation is the target's computed-opacity read. Timing, membership and identity observations follow it; another sample follows one frame later. All four observations are collected before final assertions, and assertion messages retain their complete JSON. There is no private receiver, run ID or POST. Initial acquisition failure can prevent later collection, and a passing callback does not persist the full trace separately.

The explicit style assignments are deliberate test operations: the same-value setter and CSSOM base-input change are the behaviors being tested. Outline changes use a class. Both targets have an explicit zero-width baseline outline and the outline callback verifies 3 px after mutation. Each observation checks current membership, retained effect identity, two animations, held times and paused state. Getters can flush; the later timing/membership snapshots are not atomic measurements of the first opacity query. The bounded setup frames are not proof that every internal pending task has drained.

The suite is intended to falsify an overbroad admission experiment. A control failure is evidence to investigate, not permission to weaken the final masked test. These are authored behavioral expectations, not dispatch-count, cost or native-liveness assertions. A passing same-value case cannot replace a repeated-work performance test. No browser run has occurred, and no native patch is supplied here.

## Validation and future use

`check.py` uses the existing WPT manifest implementation with explicit paths, registers the callbacks inertly with Node, and runs WPT path/content lint. Its audit hook refuses Git subprocesses; Git-ignore/repository-wide lint scanning is deliberately excluded. It also checks that the original final test and both harness resources are unchanged. This is static validation, not DOM execution or pseudo-element acquisition evidence.

Use this package's `tests/` and `MANIFEST.json` in a future isolated WPT config. `ROSTER.json` contains the exact seven names on the two `/css/css-animations/` pages. No private-record environment variables or testing-tree writes are needed. The captured branch and original-build preference declare typed arithmetic enabled by default; no enabling `.ini` is added. The capability assertion still verifies support in the actual future browser. This does not claim separately measured release-profile behavior.

The initial execution should compare the restored original and the one-file admission experiment with the original manager/compositor. The separately tested four-source timing prototype may be a useful additional arm, but its masked PASS does not establish minimal source necessity. Future run bindings, execution and performance measurements remain root-owned.
