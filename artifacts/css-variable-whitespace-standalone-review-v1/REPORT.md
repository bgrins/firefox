# Independent whitespace standalone packaging review

**Verdict: all three upstream packages contain only the respective repair and its WPT. No concrete source or test dependency on another repair was found.** Exact applicability is established; isolated upstream compilation and browser execution remain **NOT RUN**. The existing stacked runtime must not be described as isolated standalone runtime.

## Exact inventories

All use upstream `976279105b2e78b8666a959eb3f25c9176cefaf8`. Read-only Git blob comparison plus independent pure-text application/reversal reproduces each retained candidate tree. Each patch changes only `servo/components/style/custom_properties.rs` and the named WPT. AUDIT.json contains complete hashes/tree IDs. Tests are byte-identical to their committed integration versions; integration parent/candidate native hashes exactly match accepted review pairs (INTEGRATION-SOURCE-CHECK.json).

| Fix | Upstream patch SHA-256 | WPT | Independence |
| --- | --- | --- | --- |
| 83 origin normalization | a864fb3ce93c599bdff14f31601f5cdc5dbcaf11498a27f9de659cdf7d7a1ba1 | css-values/attr-substitution-leading-whitespace.html | Prefix token step and removal of post-scan leading trim only. No trailing repair. |
| 84 final metadata | 1bc7ddfbff4dce59820c102f37633e21a201634f61a54c1f6b6511b21628668a | css-variables/trailing-whitespace-token-boundary.html | Adds last-non-whitespace summary and conditional metadata update. Retains old leading and trailing byte trimming. |
| 85 escaped whitespace | a65f809c215f32f8483ef30620ef69ee6066fa7f4cd63002db5cfb1bd7678e68 | css-variables/trailing-escaped-whitespace.html | Adds terminal WhiteSpace raw length and saturating subtraction. Retains old leading trim and final metadata. |

Tuple return/caller/fallback changes are necessary plumbing for each respective summary. No unrelated EOF repair, source-aware cache, namespace, taint, registered-value or graph repair is smuggled into these patches. Each preserves upstream's existing EOF-repair code. The integration commits ad608a212bd8, bccea9c1fffc and fff2d758ef6b instead apply sequentially to the accumulated local source. Use the authenticated upstream alternatives for upstream standalone refs; do not equate the integration patches with those alternatives.

## Test dependency assessment

**83 (26 cases):** uses raw default-namespace typed attributes, acyclic var/attr chains and absolute px values. Inspection of upstream `update_attributes_map`, `visit_value_references`, `traverse`, `get_attr_value_for_cycle_resolution` and substitution shows existing eager root loading, lazy chained loading and used var fallbacks cover these paths. Tests do not require qualified namespace separation, repeated tombstone invalidation, nested attr inside a used fallback, invalid typed primary selection, registered relative-unit cycles or font-size/line-height dependency fixes. The missing attr fallback contains var(), whose value already exists. Comments/UTF-8/reference ranges are the actual repaired origin concern. Trailing control is whole-value substitution, with no following token to require fix84. No escaped terminal identifier requires fix85.

**84 (40 cases):** nonempty values begin with plain number/dimension/identifier bytes; no leading reference origin shift occurs. Only the all-whitespace empty control has a leading prefix, and existing empty substitution handling skips it. No attr or registered values are used. The fallback control retains its source whitespace; the literal comment and multiplication controls do not require another repair. The tokens contain no escaped terminal whitespace. Thus neither83 nor85 is a source prerequisite.

**85 (20 cases):** each value begins with x, a quote, or an ordinary identifier, never removable leading whitespace. Whole-value `animation-name:var(--token)` substitution does not concatenate a following token, so stale old last-token metadata is not exposed. Literal CSS.supports/computed-name and CSS.escape calibration plus clean→set→restore→set phases remain intact. There are no @keyframes or actual animation effects, so animation endpoint/equality repairs are not prerequisites. Escaped SP/HT are identifier content; the separate backslash-delimiter/newline repair is not exercised.

These are source-derived independence assessments, not exhaustive executions of upstream. Normal prerequisites are the existing upstream typed-attr/var parser and CSSOM support, standard testharness resources, and the ordinary build/test configuration. No new helper/resource files or preferences are added by these WPTs. A later isolated run could expose an unrelated upstream issue; the present evidence cannot exclude all such behavior.

## Prior acceptance and helper

Authenticated every file of the three prior native reviews against their accepted manifests (REVIEW-AUTH.json); their source/spec/runtime conclusions are retained without rerunning unrelated gates. Tests remain calibrated and expectations unchanged. No broader mathematical/native closure is inferred from prior conditional proofs.

Reviewed the pinned `create-standalone.py` without execution. It reads committed evidence, uses a temporary GIT_INDEX_FILE for mutations, verifies exact source/test/roster and patch reversal, creates signed trees/commits without checkout, then creates a new ref with an expected nonexistent old value. No source-level blocker found. It checks signature presence rather than independent cryptographic verification and pins affected worktree paths, not every file. Commit this review/helper evidence before invoking it; its own committed-evidence requirement should then be satisfied.

No native/WPT/index/ref/worktree edits, commits, build or browser execution by this audit. Only read-only Git and owned artifact writes were performed; no generated compiler outputs exist to clean.
