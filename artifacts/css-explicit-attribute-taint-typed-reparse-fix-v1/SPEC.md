# Explicit attribute provenance through registration change

Retrieved 2026-11-02 America/Los_Angeles (2026-11-03 UTC). webspec-index query failed with a readonly database; SPEC-ATTR.log preserves that failure. Current primary draft sections were read through the web tool instead, including their anchor-bearing section links. No exhaustive algorithm graph or native refinement is claimed.

Scenario: a present data-ticket attribute supplies a string to --source under universal registration. The registration changes to <string> while the attribute changes from fixed public image A to B. A real discrete transition exists and is paused at 25% and75%; registration, endpoints and timing are calibrated.

1. [Values5 replace-an-attr-function, steps3 and5](https://drafts.csswg.org/css-values-5/#replace-an-attr-function): the present attribute with omitted type returns its string value. No missing-attribute or fallback branch is involved.
2. [Values5 attr-security](https://drafts.csswg.org/css-values-5/#attr-security): values produced by attr carry provenance; arbitrary substitution values derived from them are tainted as a whole. This applies to registered properties' equivalent token sequences. A URL consumer must reject such taint. Changing a representation is not a laundering exception.
3. [Properties and Values API1 animation-behavior](https://drafts.css-houdini.org/css-properties-values-api-1/#animation-behavior): animation uses computed values according to parsed type; changing registration can change computed values and start or interrupt a transition. [substitution](https://drafts.css-houdini.org/css-properties-values-api-1/#substitution) uses the registered computed value's equivalent token sequence.
4. [Transitions2 transition-behavior-property](https://drafts.csswg.org/css-transitions-2/#transition-behavior-property): allow-discrete enables discrete transitions; their values switch at50%. Normal behavior does not start them. The WPT verifies an actual transition and its selected endpoint rather than treating elapsed time as evidence.

Verdict: REACHED for blocking an attribute-derived sampled string used as an image URL, conditional on the explicitly calibrated transition/endpoint facts. The draft does not specify Rust representation transport. The source-backed universal→Unparsed→typed path explains the implementation loss; the Lean transport proof remains conditional, not native refinement.

The equal-token registration-only probe is corroborating observation only. The WPT changes endpoint payloads and does not require every representation-only registration change to start a transition. Clean literal A→B is a positive URL control. No external receiver, unknown attribute value or exfiltration outcome is tested.
