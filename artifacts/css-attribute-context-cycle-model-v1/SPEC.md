# Bounded specification trace

Question: Does differing URL context authorize separate attribute recursion identities or permanent name-wide invalidity?

Scenario: one element and fixed attributes/device; a typed attr consumer evaluates nested substitutions. A registered property in the nested chain is non-inherited with a valid initial value. The implementation-specific chrome env exposure is a source premise, not a CSSWG-defined environment variable.

1. [Values 5 attr substitution, step 6](https://drafts.csswg.org/css-values-5/#attr-substitution) substitutes the attribute text with context `«"attribute", attr name»`, then parses the requested syntax. URL context is not part of that guard identity. The other routes in SPEC-TRACE.log handle the first argument or fallback; they do not add URL to the identity.
2. [The guard definition](https://drafts.csswg.org/css-values-5/#guarded) marks the participating contexts when a matching context is guarded again during the active guard.
3. [Substitution, steps 1 and 3](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function) checks the cyclic mark on entry and again after nested evaluation. A nested property's usable default cannot erase an ancestor's existing mark.
4. [Variables 2 var replacement, step 2](https://drafts.csswg.org/css-variables-2/#replace-a-var-function) obtains the property's computed value. The model's B initial is conditional on the actual native non-inherited registration branch pinned in SOURCE.json; it does not attempt a complete registered-property computation proof.
5. [Values 5 attr security](https://drafts.csswg.org/css-values-5/#attr-security) makes tainted URL use invalid. It does not make all non-URL attr results independent of implementation environment exposure.

**Verdict: INCONCLUSIVE** for a persistent multi-root cache policy. The active-invocation constraints above are explicit; the cited rules do not establish a global attribute tombstone or a cross-root cache-reuse theorem. The executable model enforces those local constraints without claiming the broader result.

The saved current trace found four routes at depth nine without a truncation notice. Querying guessed registered-property anchors initially failed; no claim relies on those missing sections. Current primary content was read on 2026-11-02; the Values 5 draft is dated 27 October 2026. The native implementation's env gate, namespace-aware key and current graph differ from the abstract spec vocabulary and are identified separately in SOURCE.json.
