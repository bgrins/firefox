# Recursive registered-provider default proposal

Uncompiled research proposal, not an accepted fix. Only captured files are changed. `native.patch` changes one original-HEAD Rust file; the candidate WPT is a new 32-case supplement. No A2, writing-mode graph expansion, zoom prerequisite, browser run, or new accepted-bug count is claimed.

## Observed defect

The saved mixed-length run completed 30 PASS / 2 FAIL (including 16 passing container assertions). The separate line-height-only reduction completed 14 PASS / 2 FAIL. Both failing cases use the invalid registered provider with provider-first declarations and either query order. Its computed registered value is vertical-rl while the consuming writing-mode remains horizontal-tb. In the reduction, all custom/ordinary/consumer lengths are correctly 40, 60, 40 pixels. Thus the mismatch does not require a selected logical length; the unused raw provider fallback still contains 1vi. OBSERVED.json preserves exact messages, result/assessment/outer bindings and completed preservation evidence.

## Source route and proposed change

An unresolved registered provider is stored as a universal token value. Recursive var substitution currently returns selected raw bogus before admitting it to the provider registration. An early line-height helper ensures writing-mode; that longhand sees bogus, defaults to horizontal, and is marked applied. Later normal provider admission correctly replaces the value by its registered vertical initial. Changing root visitation order does not solve this generally: an unused 1lh in the provider itself can trigger the same early application.

The patch admits selected provider text using its actual registration, URL context, property identity, and attribute taint. Grammar failure returns the same initial/inherited value as normal IACVT handling; substituted CSS-wide keywords use the same existing keyword policy. The recursive call does not publish into the custom-property map. Valid admitted values remain uncomputed, and the existing recursive seen-name guard and error/fallback branches are unchanged. This is an invalid/default-provider repair, not a complete resolver for all valid contextual providers.

Initial and inherited default selection are shared with the normal handler. Inherited registrations clone the actual parent computed value, including its taint. Invalid noninherited declarations compute the registration initial with the existing initial-value taint policy. CSS-wide inheritance keeps INHERITS_RESET_STYLE. Existing substituted revert policy and its CSSWG issue comment are retained; the supplemental revert tests check provider/consumer consistency without choosing between disputed initial/inherited policies.

## Relation to A2

The pinned A2 proposal prepares a provider only when its own graph node is visited. If the length node is visited first, its valid 1lh still requests line-height and the unchanged early writing-mode callback recursively reads the still-unadmitted provider. A2 recursive substitution and callback remain unchanged. Consequently A2 does not close this source route; this is a source analysis, not an executed A2 comparison for these cases. No separate count is inferred from it.

## Tests and limits

The original frozen mixed and reduced fixtures must remain in the eventual comparison. The new supplement preserves their four control families and declaration/query-order combinations, then adds unused-lh, inherited vertical-lr versus initial vertical-rl, inherit/unset, revert consistency, and valid contextual-provider controls. It retains the failing property-name indices for the added cases in separate iframes. These added cases have not run. Registration syntax is extended with vertical-lr and a parent value is supplied, so the supplement does not replace the exact historical fixture.

Static checks cover Rust syntax/format, exact forward/reverse patch transport, JavaScript syntax, and 32 distinct test identities. They are not compilation or semantic proof. The shared invalid-initial helper still computes the initial value at this earlier point: intrinsic color-scheme and other initial-value effects require targeted review/testing before general acceptance. Specified parsing can have parser bookkeeping effects and is repeated later. True cycles, attribute-tainted defaults, CSS-wide edge cases and valid contextual values require real regression coverage; retaining the recursion guards alone does not prove unchanged whole-run cycle behavior. No canonical Lean coverage is added.

The next experiment is a native build and paired run of both original 16-case readiness fixtures plus this supplement and existing registration/cycle/attribute regressions. A pass would address the observed invalid-provider category; it would not settle the held genuine writing-mode/if cycle policy or missing logical-unit scheduling.
