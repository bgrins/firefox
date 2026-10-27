# Focused native follow-up

These tests are proposed, not executed. Extend the existing real `KeyframePresentation` and `AnimationRuleSample` host fixtures; do not replace the native composition call with a Python or host-only collector.

1. Create five explicit custom-property keyframes with a distinct .5 authored descriptor. Sample at .125 through `KeyframeEffect::ComposeStyleRule`, obtain the actual rule source, and assert four ordered segment records with the middle descriptor retained despite not being in the selected or final segment. Repeat with the other `WITNESSES.json` declaration. Do not assert a cyclic numeric result.
2. Retain the rule source, release the effect/keyframes, and inspect the same descriptor's declaration index, property, original tokens, URL/namespace context and shared context identity. Inspect both occurrences of a shared endpoint; do not infer identity from equal numeric values or local keyframe indices alone.
3. Use the existing transition-start mutator fixture: a non-null synthesized from value with its descriptor cleared must produce `Concrete`, preserve taint/value ownership, and remain distinct from a genuinely null implicit endpoint producing `Underlying`. The to descriptor must remain unchanged.
4. Compose two effects on the same property, with the second replacing the first arithmetic root. Assert both input groups survive in call order while the concrete composed result is unchanged. A separate property must not alias either group's descriptors. Reject invented effect identity based only on pointer spelling.
5. Exercise missing-required-underlying composition. The existing no-insertion behavior and warning remain; no successful input group is appended. Check owned references are released when that unsuccessful local capture is dropped.

After a real scheduler is connected, reuse the unchanged ten-case provider diagnostic and all existing controls. Its four red-phase failures are the repair gate; these ownership tests alone cannot replace it. Add two-endpoint error-order and shared-provider tests at the real cascade boundary, and keep cyclic observations unjudged until their oracle is established.
