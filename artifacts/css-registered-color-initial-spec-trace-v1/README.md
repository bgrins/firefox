# Contextual colors as registered initial values

Current primary text supports rejecting `CanvasText` and `light-dark(red, blue)` as `<color>` initial values passed to `CSS.registerProperty()`: their computation depends on a CSS-controlled element color scheme. This is separate from preserving the local implementation’s accepted dynamic-initial behavior. The current Editor’s Draft has a narrower `@property` descriptor paragraph than the published specification; its exact stylesheet invalidation route remains a qualification.

**Scenario.** A fresh valid name, syntax `<color>`, either inheritance flag, and explicit initial `CanvasText` or `light-dark(red, blue)`. Consider normal light/dark rendering where the system palette responds to the element scheme. No browser was run for this trace.

1. [`registerProperty()` §4.1](https://drafts.css-houdini.org/css-properties-values-api-1/#the-registerproperty-function) invokes registration with the supplied dictionary. [Step 4](https://drafts.css-houdini.org/css-properties-values-api-1/#register-a-custom-property) parses the initial, then checks independence:
   > If parsed initial value is not computationally independent, throw a SyntaxError and exit this algorithm.
   [Independence](https://drafts.css-houdini.org/css-properties-values-api-1/#computationally-independent) permits the property’s own value and global information unaffected by CSS. Parsing successfully is insufficient.
2. [Computed-value behavior §2.4](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values) sends `<color>` to color resolution. [Color 4 §15.5](https://drafts.csswg.org/css-color-4/#resolving-other-colors) gives system colors their corresponding computed color; [§6.2](https://drafts.csswg.org/css-color-4/#css-system-colors) makes them respond to the element scheme. A UA/OS palette origin does not make the entire computation CSS-independent.
3. [Color 5 §7](https://drafts.csswg.org/css-color-5/#light-dark) makes the color form compute to one argument’s computed color according to the element scheme. `red` and `blue` are individually independent, but choosing between them is not. Despite “used scheme” terminology in older text/headings, this rule resolves the color at computed-value time, not merely during painting.
4. [The element scheme](https://drafts.csswg.org/css-color-adjust-1/#element-color-scheme) can be overridden by `color-scheme`; [its effects](https://drafts.csswg.org/css-color-adjust-1/#color-scheme-effect) include system colors and `light-dark()`. Returning to registration step 4, these dependencies trigger rejection before appending the registration.

The same expressions can still occur in ordinary declarations after registration with an independent initial such as `red`. Color 4’s `currentcolor` computes to itself and resolves against another color at used-value time: this illustrates why a used-value dependency alone is insufficient for the argument, without separately deciding its registration validity. Color 4 permits fixed used system-color values for privacy; that is not an explicit registration-validation exemption. No claim requires every UA palette to yield different numeric colors. No exemption for these two initial forms appears in the deciding sections inspected.

## Stylesheet route and captured versions

The published Properties & Values API snapshot (26 March 2024, SHA `959d45c4`) explicitly requires independence for a non-universal `@property` initial and invalidates the rule otherwise. It is also the body served by `webspec-index`; the saved one-hop trace belongs to that snapshot.

The directly captured Editor’s Draft (6 August 2026, SHA `2e733339`) retains JavaScript’s guard. Its [initial-value descriptor](https://drafts.css-houdini.org/css-properties-values-api-1/#initial-value-descriptor) now states syntax parsing only, while [§3](https://drafts.css-houdini.org/css-properties-values-api-1/#at-property-rule) still describes equivalent registrations. Omission alone does not authorize contextual initials; precise descriptor-versus-rule invalidation needs clarification rather than silently importing the older bullet.

Color 4/5 captures are dated 29 October 2026; Color Adjustment is dated 7 May 2026. `PRIMARY.json` pins complete bodies retrieved on 30 October, and `EXCERPTS.json` joins eleven sections. Indexed anchors validated; one initial Color 5 network failure succeeded on full-URL retry. The initial cache-write failure is preserved. Neither failure was treated as semantic absence.

## Discussion and consequences

[Issue 13628](https://github.com/w3c/csswg-drafts/issues/13628) requests relaxing independence, explicitly motivated by `light-dark()`. It remains open with zero comments in the captured API record. [Issue 13836](https://github.com/w3c/csswg-drafts/issues/13836) proposes used-time resolution; its 21 captured comments include the 13 May discussion ending without consensus. It does not supersede the computed-value rule. [Issue 13719](https://github.com/w3c/csswg-drafts/issues/13719) is closed after clarifying system-color resolution. This is a bounded inspection, not an exhaustive absence search.

The sealed native finding proves a source path accepting these initials, not normative permission. The System/light-dark default and cycle cases remain **conditional research preservation tests**. A separate JavaScript registration test could require `SyntaxError`, using fresh names and a successful independent `red` control. No such test or native run occurred here. Successful registration and subsequent default recomputation must not become conformance requirements based on the preservation observations.

**Verdict: REACHED** — the non-independence rejection guard is reached for the stated JavaScript scenario. This does not settle the newer `@property` descriptor/rule-invalidity gap, establish a native regression, or authorize a native fix.
