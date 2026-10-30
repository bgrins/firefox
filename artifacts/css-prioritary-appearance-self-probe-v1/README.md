# Appearance eligibility self-edge preservation supplement

This three-case Mozilla WPT draft challenges a potential regression introduced by the selected-declaration V2 prototype. It is separate from the immutable74 suite and all active execution owners. No browser result, new Firefox bug or accepted fix is claimed.

The candidate's reached APPEARANCE_BASE branch can visit Appearance while already traversing Appearance. That sets self_ref, marks Appearance invalid, discards the prepared chain and invokes the existing invalid-priority wrapper. The wrapper skips the unavailable gated entry, but converts a lower ordinary WithVariables Appearance declaration to Initial. Frozen longhand metadata gives Appearance::None. Base code instead skips the unavailable gated entry and evaluates the ordinary `var(--missing,base)` fallback, establishing base appearance and enabling eligible rules.

The target UA sheet is:

```css
.target { appearance:var(--missing,base); font-size:13px; outline:0 solid; }
@appearance-base {
  .target { appearance:var(--missing,base); font-size:var(--size); outline-width:7px; }
}
```

The target is a button under an ordinary non-base parent, with registered non-inheriting --actual:<length>, initial0px, authored --actual:2em and --size:20px then30px. The first custom getter demands FontSize; its gated declaration demands Appearance. The later, higher gated Appearance entry then supplies the self-edge. Controls replace the lower ordinary Appearance with literal `base`, or omit only the gated Appearance declaration. All three assert the original bootstrap outcome: appearance:base, marker7px, requested font20px/30px and registered40px/60px. For the self-variable target, V2 is predicted to yield none/no marker/font13px and registered26px if the proposed route is reached. These are causal predictions pending original/candidate observation.

Both complete phase records are collected before numeric assertions; each starts with a custom-property getter and three frame-separated samples, then timing-independent appearance/font/outline details. The hidden diagnostic element preserves the executed fixture's layout behavior. Registration, CSS.supports, literal reference font/width and UA marker checks remain explicit. This Gecko-only test uses the existing appearance-base pref and SpecialPowers agent-sheet loader; it is not a portable author stylesheet claim. Failure diagnostics contain the full captured record; a PASS does not independently archive it.

Root admitted exact parser/stylist bodies in css-prioritary-appearance-parser-source-v1 (receipt d81da2, source SHA recorded in REFERENCES). Read0b1c04/439a9b confirms chrome-enabled AppearanceBase uses ordinary nested-rule parsing; nested .target enters CssRuleType::Style and ordinary declaration parsing, while stylist attaches the flag to the containing rule. This supports parsing/flag reachability of Appearance in the rule. Searchfox discovery2668e4/9e3196/3f4574/7822f3/99cbe4 is supplementary; no conclusion rests on search absence alone. The frozen cascade/mod.rs/metadata establish the self-edge and invalid-wrapper route. Actual first-demand scheduling and original/candidate observable results remain unexecuted.

The separate uncompiled V3 proposal adds the minimal correction: to exclude `longhand == LonghandId::Appearance` from the missing-APPEARANCE_BASE dependency branch. It should let Appearance select its ordinary bootstrap while retaining reached FontSize→Appearance. That remains an artifact proposal, not an applied or compiled native patch. It does not solve general dependency ordering, custom-property taint, or additional appearance prerequisite cycles.

Other bounded review results: rollback selection uses the same allows_when_reverted predicate and retains evaluated rollback reads; no additional concrete rollback defect was established. ForcedColorAdjust edges are limited by the reached adjusted declaration and current ColorScheme-only prioritary metadata contract. Generated scheduling remains separate from semantic cycle edges. The existing V2 scheduling caveat is not resolved by this supplement.

Static e4cf34/0 produced a genuine explicit-path Mozilla manifest and three inert callback names. Path/content lint found only the two expected Gecko SpecialPowers notices; no other findings. The subprocess audit rejects Git. No callback, native build, browser, live source/application/index guard or canonical mutation was executed.
