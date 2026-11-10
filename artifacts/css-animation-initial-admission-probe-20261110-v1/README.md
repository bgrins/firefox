# Initial style admission during animation traversal

A default-configuration probe is viable through SVG SMIL display animation.
CSS/WAAPI display animation is disabled by default and is not the proposed
first experiment. The prepared fixture has not run in a browser; neither
native initial-admission coverage nor a new bug is claimed.

## Support and source path

| Mechanism | Inspected configuration | Evidence |
| --- | --- | --- |
| CSS/WAAPI `display` animation | `layout.css.display-animations.enabled` defaults to false | `StaticPrefList.yaml`; `KeyframeUtils::IsAnimatableProperty` rejects display while false; CSS keyframe processing skips it |
| Existing CSS display WPTs | Explicitly enable that preference | `css/css-animations/display-interpolation.html.ini` and `css/css-display/animations/display-interpolation-none.html.ini` |
| SVG SMIL `display` animation | Allowed independently of that preference | `SMILCSSProperty::IsPropertyAnimatable` includes display; `SMILCSSProperty::SetAnimValue` writes the SMIL override style |

`NATIVE.json` pins exact local source objects at
`341eff530ede217c5ba6efbeac192fb0d3fdfae1`, plus the separately authenticated
7036 combined-drain StyleDocument body. `NATIVE-EXCERPTS.txt` preserves the
inspected source. Searchfox discovery output is separate from local source
authority; its commands and exits are retained in `DISCOVERY.json`.

The proposed path is:

1. A styled SVG host has `display:none`; its descendants have not been queried
   for computed style. A paused SMIL display animation is explicitly sampled
   at its hidden position.
2. One seek changes the sampled display to inline.
   `SVGSVGElement::SetCurrentTime` flushes pending style before changing time,
   then synchronously samples animations. This operation cannot be treated as
   an inert timestamp assignment.
3. `SMILAnimationController::PreTraverseInSubtree` posts `RESTYLE_SMIL` through
   `PostRestyleEventForAnimations`. `ServoStyleSet::PreTraverse` invokes this
   controller before subtree traversal.
4. `Servo_TraverseSubtree` can run its animation-only prepass before ordinary
   traversal. A display change yields a nonempty child recascade hint through
   `accumulate_damage_for`; `recalc_style_at` examines children when that hint
   is nonempty and the host is no longer display:none.
5. Missing primary style is admitted before the animation-only restrictions
   in `element_needs_traversal` and `ElementData::restyle_kind`.
   `process_animations` likewise permits task construction when old primary
   style is absent. The previous progress-contract capsule pins those exact
   gates.

This is a source-supported reachability hypothesis. A successful display
reveal or correct font value alone does not establish the path: ordinary
traversal or `StyleNewSubtree` could perform the first styling instead.

## What the SMIL route cannot establish

The combined candidate's repeated inner loop invokes
`EffectCompositor::PreTraverse`, not full `ServoStyleSet::PreTraverse`, and
does not resample SMIL. The paused fixture makes one explicit seek, with no
script callback between that seek and the first leaf getter. Therefore its
SMIL stimulus is finite work injected before the loop, not evidence of
recurring SMIL-driven destruction/recreation inside that loop.

Expected useful coverage is initial animation-only styling during the first
subtree traversal, followed by descendant CSS animation requests that the
later drain must deliver. Native logging must distinguish this from
initialization during a repeated drain iteration. Initial descendant
creation can satisfy the existing descending phase relation and is not a
cycle. No new same-rank native renewal route has been demonstrated.

## Prepared fixture

`initial-animation-admission.html` contains three callbacks, each using a
fresh iframe and four nested font consumers under SVG foreignObject:

| Callback | Reveal | Font chain | Purpose |
| --- | --- | --- | --- |
| smil-animated | Paused SMIL seek from 0 to 75 seconds of a 100-second discrete display animation | Four constant paused CSS font animations | Initial animation-only admission and subsequent dependency delivery |
| normal-animated | Class changes display from none to inline | Same CSS animations | Ordinary reveal comparison; actual native phase must still be classified |
| smil-literal | Same SMIL seek | Ordinary 2rem/2em declarations | Reveal/initialization control without descendant CSS animation work |

All cases use a literal 32px document root. The expected leaf font is 512px.
The getter order is first leaf, repeated leaf, then host/timing/animation
controls. No descendant style getter runs while hidden; DOM lookup alone
locates the leaf. CSS animation identities are checked after the primary
observations via the four named target IDs. An explicit style flush here is
the measurement, not a production UI pattern.

`IA_PROBE` JSON markers distinguish stimulus entry/return, getter entry/return,
and completion. They are emitted only when `dump` exists. Records are also
stored in `window.initialAdmissionObservations`; completion logging only
serializes saved values. Missing return markers mean incomplete execution,
not a measured font value. Markers have no native PID/document token, so
native joins need independent call/document/target attribution.

Run with `dom.window.dump.enabled=true` and explicitly leave
`layout.css.display-animations.enabled=false`. The latter preserves the
intended default-config distinction even if a local profile changed it.
`check2/INPUTS.json` names exact page and harness bytes; `check2/ROSTER.json`
contains the three callback names. No preference metadata or live WPT was
installed by this task.

## Native acceptance gates

`TRACE-GATES.json` records the required observations. In particular:

- Identify the tested document, host, and descendant IDs/pointers in one
  StyleDocument call; distinguish startup/seek flushing from the first getter.
- Attribute the host update to `RESTYLE_SMIL`, then observe a tested descendant
  with `initial=true`, `AnimationOnly`, and `MatchAndCascade`.
- Record `process_animations` old-style absence and the actual nonempty task
  mask for that descendant. Existing installation logging alone does not
  record this producer mask.
- Attribute each such event to first traversal/iteration 0, repeated drain
  iteration, or StyleNewSubtree/final-animation traversal. Only the actual
  branch observed is covered.
- Join resulting CSS requests to hints, admission and installation before
  getter return, preserving full pseudo/cascade identity and newer requests.

For this probe, any initial admission in iteration 0 is evidence about finite
initial work. A claim about recurring initialization requires separate
destruction/recreation and causal-request evidence in later iterations;
neither a repeated pointer nor multiple style installations supplies it.

If only normal initialization occurs, report the animation-only gate as
uncovered. The next bounded follow-up would inspect why the SMIL child hint
did not admit the subtree; enabling the experimental CSS display pref is a
separate, explicitly labeled alternative, not a default-browser result.

## Specification and existing tests

The current [CSS Display animation section](https://drafts.csswg.org/css-display-4/#display-animation)
describes special interpolation around none; its retrieved section and source
hash are saved in `display-spec.md`. The probe instead explicitly uses SMIL
discrete sampling, as defined by [SMIL Animation](https://www.w3.org/TR/smil-animation/),
at unambiguous hidden and visible positions.

The existing `svg/animations/animate-display-to-none-001.html` seeks a paused
SMIL display animation between hidden and visible states. Its metadata has
an intermittent Windows opt expectation and an assertion allowance; its
presence is evidence of intended test coverage, not a new runtime result.
The probe extends that construction with initial descendant CSS font work.

## Preparation checks

`python3 -I check_wpt.py <new-output-directory>` performs Node syntax checking,
inert registration of the three callbacks, primary-getter ordering checks,
and genuine WPT HTML/path lint and manifest generation in disposable staging.
`check2/RESULT.json` records successful final fixture validation. These are
preparation checks only. No browser, build, native patch, live test, objdir,
Git index, or commit was changed.

The webspec-index SVG/SMIL legacy-anchor lookups failed to resolve sections;
their stderr is retained. The primary W3C SMIL document was subsequently read
with the web tool. An initial sandboxed Searchfox recascade fetch failed DNS;
the successful fetch is separately recorded. No failed query is counted as
successful source evidence.
