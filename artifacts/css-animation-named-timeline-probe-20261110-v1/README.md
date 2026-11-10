# Named timeline admission probe

Prepared artifact only. No browser run, native edit, live WPT installation, build, index change or commit was made by this task. The first preparation run passes Node syntax, inert registration, WPT lint and manifest generation. These checks do not establish runtime eligibility or same-call queue injection.

## Three callbacks

The roster is `Named timeline admission: ${mode}`:

| Mode | Reveal | Newly styled definition | Expected post-read timeline source |
| --- | --- | --- | --- |
| smil-scroll | One paused SVG SMIL display seek | `scroll-timeline: --t block` | provider |
| normal-scroll | Class changes display to inline | Same scroll definition | provider |
| smil-scope-only | One paused SMIL seek | Unrelated `timeline-scope: --scopeProbe` | fallback |

Each callback uses a fresh iframe. Fixed native IDs are `outside`, `fallback`, `svg`, `host`, and `provider`. The CSS animation target `outside` is a visible ancestor of the hidden provider. It declares `timeline-scope: --t` and has a running font-size CSS animation driven by `--t`. The visible fallback appears earlier in tree order; the new provider appears later inside a foreignObject under the hidden SVG host. There is no intervening `--t` scope to exclude the new provider from the ancestor's candidate set.

The fallback has a 200px scroll range and is scrolled to 100px. Before the stimulus, bounded frame waits require a settled running CSS animation, source `fallback`, nonnull progress approximately 0.5, and font approximately 20px from the 12px/28px endpoints. The running-state requirement matters: changing finite timelines clears start/hold time and schedules pending play, whereas a paused animation can preserve its previous progress and miss the timing-change discriminator. Preparatory layout/style/timing queries access only the visible outside/fallback and hidden host itself. No getter or animation enumeration targets the unstyled provider or its descendants.

After preparation there is no await, timer, animation enumeration or timing read between stimulus and the first outside font getter. For SMIL, `setCurrentTime(75)` is itself the synchronous seek and can flush/sample; this must be attributed by native call markers. The first font value is saved and immediately emitted in `getter-return`. Only then are timeline source, timing, repeated font, host and identity controls observed. No new-provider timing or pixel value is predicted. The scroll cases assert source `provider`; the scope-only control asserts source `fallback` and preservation of the first baseline font. Post-getter source controls do not prove that rebinding occurred during the primary getter.

## Required preferences

- `dom.window.dump.enabled=true` enables native-log-compatible markers.
- `layout.css.scroll-driven-animations.enabled=true` enables animation-timeline, timeline-scope and scroll/view definitions. It already defaults to true in the source audited by the preceding capsule; the explicit setting makes the probe reproducible.
- `layout.css.display-animations.enabled=false` retains the SMIL-only display stimulus distinction.

The probe makes no claim about release exposure. It does not use CSS display animation or an assumed direct display-animation default.

## Marker schema

`NT_PROBE` JSON records use exact modes above and phases `stimulus-begin`, `stimulus-return`, `getter-begin`, `getter-return`, `complete`. `getter-return` includes `value`, the saved first font. `complete` includes the saved `observation`; marker emission performs no new style/timing reads.

`window.namedTimelineObservations` retains the same observations. Each includes:

- `mode`, current `phase`;
- `before`: `font`, `timing`, `timelineSource`, `timelineTime`, `playState`, `pending`;
- `firstFont`, `after` (same animation-state fields without font), `repeatFont`;
- `hostDisplay`, `paused`, `time`, `fallbackScrollTop`, `sameAnimation`.

Timing includes `progress`, `currentIteration`, `localTime`, `activeDuration`, `endTime`. Numeric values remain numbers; CSS numeric values are serialized to strings, and null remains null. The baseline and post-read states are observations at their explicit access points, not native timestamps. The markers contain no PID/document identity; native joins must establish those separately.

## Native acceptance

`TRACE-GATES.json` defines the exact gate. A global named-timeline update visit alone is not success. Require initial provider admission, actual timeline task execution, changed concrete binding on the outside ancestor, conditional eligible Animations request, and that request's delivery in the same StyleDocument call before getter return. Distinguish stimulus-time flushes, the getter call and later controls. The unchanged-source scope control should show a global visit without assuming an outside request.

A newly created concrete ScrollTimeline may have unresolved current time before frame construction; that differs from an UnresolvedTimeline sentinel. The fixture deliberately leaves this runtime outcome to measurement. A missing native request or a later-only delivery is a failed coverage gate, even if all three WPT callbacks pass their web controls.

## Preparation replay

```sh
python3 -I artifacts/css-animation-named-timeline-probe-20261110-v1/check_wpt.py NEW-DIRECTORY
```

The checker stages only the fixture and WPT harness files in a temporary directory. It checks callback registration, syntax, measurement ordering, actual WPT HTML/path lint and testharness manifest classification, then removes staging. It does not execute callbacks or emulate browser behavior. `check1` contains the initial successful receipts; the final frozen preparation is identified separately.
