# Provider defaults: ordinary restoration and remaining recursive boundary

Restore the ordinary IACVT handler to the exact committed implementation. Keep this as a partial experimental successor, not an accepted v5 repair: a recursive document-cache lookup is still not equivalent to computing a currently admitted contextual initial for the target.

## Exact source proposal

ordinary-restoration.patch changes sealed v4 only by restoring handle_invalid_at_computed_value_time and its three call sites to their committed forms. The handler again clones an inherited value for a non-root inherited registration; otherwise it computes the registered initial with compute_value and the target Context, then inserts/removes the result. The cascade source becomes byte-identical to committed HEAD. Participant marking, drop(state), recursive missing/invalid default classification and substituted CSS-wide handling remain exactly v4. Native-from-base therefore has one modified native file.

SOURCE-ROLES.json pins original/v4/restored bytes. Both patches passed check/apply/exact postimage/reverse checks in owned temporary directories, now removed. No native typecheck/build, live application, WPT execution or formatting claim is made. This restores an existing path with observed regressions; it does not certify the remaining new recursion.

## Why four repaired observations are insufficient

The completed775 comparison confirms that changing the ordinary handler to clone the Stylist initial cache changed four dark color snapshots from blue to red. Restoring that handler addresses the identified source of those changes without removing the readiness/participant work. Whether the contextual @property registration itself should be admitted remains unresolved; this restoration preserves existing ordinary behavior rather than adjudicating that policy.

The recursive helper still selects the document cache for non-inherited/root invalid providers. Original ordinary behavior can compute the same initial against the target context. These paths can disagree even when the initial is an admitted number rather than a color. Type names do not establish independence: a number may contain container-length division, a gradient may contain colors, and a list may contain a later contextual component.

## Concrete early-consumer route

The committed properties/data.py dependency table, captured from the fixed9abc commit after Searchfox discovery, makes LineHeight ensure FontWeight. The v4 custom-property graph has only FontUnits→FontSize, LhUnits→LineHeight and ColorScheme nodes. FontWeight is not a graph node. ensure_prioritary_property inserts its ensured bit and applies its prerequisites/longhand; that longhand substitutes through the immutable recursive provider path. Consequently, a 1lh custom value can cause font-weight substitution before another registered provider's ordinary IACVT finalization.

The probe uses registered --weight:<number> with initial calc(100cqw / 1px), a fixed unzoomed size container, and an invalid or missing selected provider. --length:1lh triggers early LineHeight application. font-weight consumes --weight. Source and context are acyclic in the intended conditional scenario; no font-metric value feeds the size container. The direct typed-division sibling and literal sibling calibrate200→300→200; a context-free registered initial200 calibrates ordinary defaulting. A no-declaration sibling exposes the document initial cache separately.

Root's completed System Firefox158 MCP run already observed a relevant mismatch: provider-first grammar cases had provider200/300/200 but fontWeight400; missing cases had fontWeight555. Length-first cases matched200/300/200. All24 snapshots passed the reported direct/support calibrations; no-declaration initial was800. This is release observation under root's session environment, not local-v4 attribution and not a settled normative contextual-registration verdict. FONT-WEIGHT-RESULT.json and the exact probe are pinned in REFERENCES.

## Research WPT and next comparison

registered-contextual-initial-font-weight.html supplies eight named promise tests, with the exact standalone probe embedded. It collects all eight scenarios and24 snapshots before any assertions. Full JSON remains on window.providerFontWeightObservations and in the hidden observations element; each failure message contains all three snapshots for its scenario. Passing rows establish the explicitly asserted values; the WPT reporter does not automatically retain arbitrary page globals, so a consumer wanting every raw PASS field must separately capture that JSON.

The desired target-context checks are conditional research oracles: first check ordinary support, direct/literal geometry and observed registration, then require the selected provider to equal200/300/200 and the consumer to equal that provider. A cached provider=consumer=800 therefore fails the provider check. Calibration failures are labeled as such; they are not evidence of a provider defect. The fixture is not proposed for immediate unconditional landing. No metadata expectations are changed.

Compare actual v4 with ordinary-restored sources using the same eight cases plus prior775. Retain full changed messages, not just PASS/FAIL. Expected interpretation: restoration may repair four color observations while leaving an early font-weight/provider mismatch. Do not label it a complete repair merely because the original20 readiness tests remain green. Neither the predicted local outcome nor any WPT pass is asserted here.

## Principled completion without a type whitelist

Already-computed inherited values are safe to clone. A document-cached initial is safe only when a sound independence/representation contract applies; registration syntax alone is insufficient. For a context-sensitive or unresolved initial, recursive substitution needs to return a distinct demand/default-computation outcome to the cascade owner, carrying the provider and cycle classification. That outcome must propagate without becoming CSS invalidity or selecting a fallback. The owner can resolve actual required context and compute the target default, then retry from the same selected provider.

compute_value accepts an immutable Context, so replacing the cache lookup with immediate computation is syntactically possible. It is not generally safe: the Context may still lack prioritary values (including writing mode or color scheme), and blindly ensuring every prioritary property creates false dependencies/cycles. The required dependency set must follow the actually selected initial representation, with intrinsic effects and any simplification correspondence accounted for. Actual cycles must remain participant-classified; a demand is neither missing nor cyclic by itself.

Returning raw initial tokens instead of a computed registered value is also not a general repair: it can defer units to the consuming property's semantics and repeat syntax selection. Preserve selected typed representation through any deferred computation. Existing selected-independence and cycle/default models specify useful contracts here, but do not prove this native transport.

This package deliberately stops short of claiming a complete v5 native repair. The minimal ordinary restoration is concrete and transport-checked; the remaining recursive boundary has a runnable observable probe and a specific resolution architecture. No live source/index/epoch mutation, new bug credit or acceptance increment.
