# Direct typed-attribute substitution observations

Four serial fresh iframes compare a CSS-animated variable reached through typed attr, an untainted attr reference, a literal attr value, and a matched direct var reference. Each uses one paused 2000 ms CSS effect held at 750 ms after readiness. The two non-tainted controls animate only constant opacity. This standalone research page does not change the existing 106-case suite or the sealed alias probe.

| Mode | Attribute text / sink | Active source --v | Active expectation |
| --- | --- | --- | --- |
| tainted-attr | data-v="var(--v, vertical-lr)"; writing-mode:attr(data-v type(<custom-ident>), vertical-rl) | horizontal-tb from CSS keyframes | vertical-lr, nested var fallback interpretation |
| untainted-attr | same attr expression | ordinary horizontal-tb | horizontal-tb |
| literal-attr | data-v="vertical-lr"; same attr sink | ordinary vertical-rl | vertical-lr |
| direct-var | writing-mode:var(--v, vertical-lr) | horizontal-tb from CSS keyframes | vertical-lr, matched direct substitution interpretation |

The parent is vertical-rl. Thus the literal attribute control separates valid typed syntax from unsupported syntax/inheritance or outer attr fallback. The untainted control separately separates recursive attribute-text substitution from failure choosing outer fallback. In the tainted case horizontal-tb, vertical-rl and vertical-lr distinguish animated-value admission, outer failure/inheritance, and the proposed nested fallback. An output alone does not identify the internal path.

The script records computed --v, sink, fixed duration/progress, currentTime, playState, and retained animation/effect identity before creation, during activity and after cancel. The first active/cancel sink getter and three passive frame samples precede detailed reads and membership. Initial effect acquisition/readiness can already flush. Detail fields are sequential, not atomic.

All before/cancel var-dependent sink values remain policy observations. CSS keyframes rules remain after cancellation. Only the literal attr sink is a reference check across all phases. Active predictions are isolated in activeExpectation {expectedSink, kind, matches}; a false match neither destroys the raw values nor changes collection completion. referenceChecks contains timing, custom-value, identity, lifecycle and literal support calibrations separately. policyVerdict stays null. The direct-context normative reasoning belongs to the separate typed-attr spec follow-up; no alias infection requirement is asserted here.

window.directAttrObservations exposes plain JSON. Errors retain partial rows; nonfinite numeric values get explicit encodings. There is no page watchdog and a hung collection may not transport partial state. The separate disabled runner supplies a 180-second watchdog and adds only a reporting script. No browser result or first-getter correctness is claimed by this preparation.

Static checks: 82304a/0 JavaScript syntax; 70f3f7/0 four positives, outside-active policy neutrality, four wrong active expectations retained, eight calibration/control negatives and partial expectation handling. Node evaluates pure functions only, not the DOM.
