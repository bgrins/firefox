# Active winning-value animation taint experiment

This uncompiled four-file Rust proposal addresses the demonstrated active unregistered custom-property writing-mode substitution gap. Root's strengthened V2 observations use noninitial vertical-lr fallback, animated vertical-rl and ordinary horizontal-tb: Chrome direct/alias/literal observations pass; Firefox direct and alias consume vertical-rl. These observations motivate this experiment; they do not establish the complete property-name-global policy or prove Chrome's exact internal path. No native source, index, application or browser was changed here.

`native.patch` uses the captured held provider preimage (2675b33b). `native-clean-provider.patch` applies the same taint transformation to the committed provider preimage (8a4adc90), with identical other three postimages. Both patches apply and reverse exactly in isolated scratch. This demonstrates source applicability without importing the held recursive/defaulting redesign; it does not demonstrate clean-provider runtime correctness or independent landability. SOURCE-ROLES and CLEAN-PROVIDER bind complete pre/postimages.

The four paths are custom_properties.rs, custom_properties_map.rs, properties_and_values/value.rs and properties/cascade.rs under servo/components/style. No timing manager, snapshot, scheduling or animation-input-selection code changes.

## Producer and metadata

Only a winning unregistered CSS Animations cascade value gets new source provenance. Existing importance/seen/reverted-priority checks run first. A revert declaration returns before marking any previous/inherited map entry. Effective incoming provenance participates in the fast equality check; map dedup compares both attr and animation metadata. Ordinary same-token replacement can therefore remove animation provenance, and an ordinary important winner is not marked merely because an animation declaration was visited.

REGISTRATION.json captures the deciding pinned-branch functions. The initial draft's syntax.is_none test was wrong: unregistered() has Some(universal), just as registered universal syntax can. The final test uses pointer identity with the unique static Descriptors::unregistered() returned by Stylist only when both registries miss. Registered descriptors are separate owned values. This is a branch-specific representation contract, not a syntax-name inference.

Value and VariableValue carry separate animation provenance, preserving existing attr-taint behavior. Conversions and concatenated substitutions propagate it; animation interpolation ORs endpoint metadata. A successful substituted CSS-wide keyword replacement retains its originating substitution provenance; absent/invalid replacements remain absent. This does not settle the broader CSS-wide/inheritance or registered-property policies.

## Alias evaluation and sink

An explicit internal boolean suppresses only animation-taint sink rejection while recursively resolving a custom value. It does not change property_id, attr context, cycle bookkeeping or provider defaulting. The recursive call gets true; its caller retains its own boolean. Only after complete custom resolution does an ordinary non-animatable outer sink reject a tainted var value and execute the existing outer fallback. Fallback recursion inherits the caller's boolean, so a tainted fallback reference is checked too. Animatable/custom contexts keep tainted tokens.

This distinction prevents a staged alias from incorrectly choosing its inner fallback instead of the consuming property's outer fallback. Ready-map and deferred-map evaluation must agree. No global registry of names occurring in keyframes is added, and no transition/SMIL producer is added. Inherited/cloned metadata and registered conversions may carry provenance, but their full policy is not certified by this scope.

## Actual checks

`python3 -B artifacts/css-animation-active-value-taint-proposal-v1/check.py` reconstructs all postimages, applies/reverses both patches in owned temporary directories, and checks the actual Lean result/source join. Final static receipt c6db5f/0 passed 46 exact edits across four files; scratch was removed. Earlier be320b/1 exposed the different held/committed CSS-wide branch shapes; the common post-selection propagation fix now applies to both.

AliasGuard.lean is a small finite token/taint model. Actual isolated Lean session 77058, terminal e7b866/0, proves ready/deferred equivalence, arbitrary finite alias-chain custom resolution, outer-only rejection and fallback/metadata controls. Four axiom audits and three rejected semantic false controls are retained in lean-run1. This proves the stated abstract equations, not native resolver refinement. Cycles, registered defaults, CSS-wide parsing and inheritance are outside that model. No canonical coverage increment is claimed.

FROZEN-CENSUS.json scans the 301 saved style Rust files for affected struct literals and internal arities. Public Searchfox discovery is retained separately (14d660/0; initial restricted-network attempt e597bf/1 failed DNS). This bounded census is not a whole-branch compile guarantee. The final constructor/arity/derive/layout integration still requires a real crate build and relevant tests.

Before any native trial: independently review the exact patch, authenticate current/HEAD/build source applicability, compile, and exercise strengthened direct/alias/noninitial-fallback controls plus ordinary important winners, same-token provenance changes, nested aliases, tainted fallback and active CSS-wide inherited replacement. No execution owner or acceptance is created here. Current primary CSS Variables retains animation-taint restriction; known value-versus-property-name policy differences and animation-control base-input interpretation remain unresolved.
