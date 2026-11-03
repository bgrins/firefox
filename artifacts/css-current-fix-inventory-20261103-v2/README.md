# Current CSS fix inventory

**159 committed primary repairs** through native commit `2409a410a2641c54a42feefd3c998cd58cbf028e`: the historical 147-fix ledger, ten native commits through e86, and the committed font-unit animation and selective cancellation repairs. The prior 157 hashes were verified as ancestors of research commit `2701dc46ac5920adf3505885c67936287e1b037f`; the new native commit has that exact research parent and its exact three changed paths were independently verified read-only (23a988, exit 0). Full per-fix hashes and provenance are in [INVENTORY.json](INVENTORY.json).

Held **#120 (contextual sign)** is excluded. Research/proof/tooling/test-only companions and unaccepted prototypes do not add fixes. This is a committed-repair inventory; it does not rewrite canonical acceptance flags or claim clean-upstream execution.

| Area | Committed repairs |
| --- | ---: |
| Selectors, Bloom filters and scoping | 12 |
| Cascade, layers and shorthands | 7 |
| Parsing, tokens and CSS math | 33 |
| Container queries | 3 |
| Animations, timelines and transitions | 20 |
| Colors, images, SVG and shapes | 8 |
| Attributes and custom properties | 21 |
| Layout, sizing and positioning | 23 |
| Text and fonts | 19 |
| CSSOM geometry and hidden layout | 13 |

## Ten commits added since the 147-fix ledger

| Repair | Primary native commit |
| --- | --- |
| Avoid intermediate overflow and underflow in hypot(). | `36b693fee75e828f87b0c34df156caac903810c8` |
| Handle CSS pow exceptional values consistently in calculation and simplification. | `2d18f8b4a4d7ac7f29b1f8b4b1f3ded57e792e72` |
| Preserve contextual infinity operands when simplifying CSS min and max. | `bc0853a77a445de27e6c5ba1653c60f077a5a7f4` |
| Handle explicit-base log() exceptional values consistently. | `bf9b4d1a12ee559e98cf464689c5c327ac2e4f6d` |
| Derive registered color dependencies from the selected syntax value. | `eb7c6fe8105700d7e1df5e6419c59df64fcdd493` |
| Resolve registered image dependencies before computation. | `bc7defd8eefec531c1e57e1866b77fb04d637724` |
| Honor nowrap suppression when publishing inline line breaks. | `28bbc39fb8fec210ff9ee9880eeedc77be3f6d52` |
| Preserve language context across line-break partitions. | `2435535e6f09be35da5c5cd3d0afac7d0dd60d6d` |
| Apply hyphenation limits from the contributing text. | `8870962db02b006791085b73f9e270942e145365` |
| Preserve prioritary declarations after large unrelated cascades. | `e86b64866cdc5e2260ba9be08c45756fd96e21bb` |

## Newly completed native publication

Font-unit animation rebuild: `334937d9ef8537e95cb80b29295797bc78f44252`, parent research2701. Actual configured signing completed 9262f8/session27895/e46683, exit 0; receipt SHA4104034e49f850156b2030eea1eeb483624d5805bb4c0d5179cd6cf86a55d74f reports a verified signature. The commit contains data.rs, traversal.rs and root-font-unit-invalidation.html only. The receipt still says accepted=false, accepted_fix_increment=0 and app_rebuilt=false; this inventory does not reinterpret those fields.

Cancellation normal handoff: `2409a410a2641c54a42feefd3c998cd58cbf028e`, sole parent research V129 `e795bd155abbcf3bc6d9d861ad4ee22d610b07ad`. Actual 247d8e/session52380/65f560 exited 0; receipt SHA04e71056a08e9180b061cd10e5de1255937b248e315b6e182a4e4e0da83e3df8 records verified signature and exact five native/test paths. Read-only immutable Git verification confirms parent, path set, all five stage blobs and font334 ancestry. Publication acceptance flags remain false/zero as recorded.

This stack repair **semantically depends on font334**: conditional normal-pass propagation needs animated font-unit dependency admission. It is not independently landable by dropping that prerequisite. The separately packaged seven-path alternative includes those native prerequisite hunks and unchanged font14 WPT on research2701. Its signed local alternative is `6d88dc0173d31be32a5522b98e04c914256be391`, parent `2701dc46ac5920adf3505885c67936287e1b037f`, on `refs/heads/css-selective-cancellation-standalone-2701`. It is recorded separately and excluded from159. No new browser/build validation is claimed for packaging equivalence.

## Relative triage recommendations

These are review priorities, not assigned severity or exploitability ratings. Prioritize the crash group and review the taint group in parallel; retain each original evidence limitation.

| Ledger fix | Reason | Primary commit |
| --- | --- | --- |
| #2 | Deep relative-selector Bloom traversal stack overflow | `93a062cded54c974dff03ce2618aaf612a9c8d61` |
| #63 | Quoted EOF fallback endpoint bounds/crash | `2d658a9c5aa4139dc7f196933511abf4a594163f` |
| #83 | Custom-property whitespace/reference-offset bounds panic | `ad608a212bd8d7f77a2f0b9df62df18d33c12b96` |
| #123 | Calculated counter-range export unwrap panic | `0f68c5c1a7a556dd3907fdf7caf2d97110c53c12` |
| #143 | Second linear() stop-position conversion guard | `22f97187e9f062f76211c6c01b07cbc49e71232b` |
| #76 | Attribute-taint conservation: equal custom-property payload replacement | `e04d672a735edcf0e6529c854207b5ee9555ea7c` |
| #78 | Attribute-taint conservation: retained animation endpoint replacement | `4b4a00e707583382f4773039f13a4f335f48f41a` |
| #79 | Attribute-taint conservation: restyle after underlying taint change | `2c09cb2e4ff81bbc4af65d1d069517420b9c1529` |
| #80 | Attribute-taint conservation: both interpolated custom values contribute taint | `ede7ceb101d83f0c4044585a5a687f5286b072c9` |

#123 is explicitly included: calculated counter-range export produced a content-process unwrap panic in local and pinned Firefox158 WPT-profile runs. Exact release callsite, stock-profile exposure and memory-safety impact remain unestablished. The taint rows are scoped repairs, not a new exfiltration claim.

## Pending and held work

| Work | Current status; excluded from159 |
| --- | --- |
| Selected attr() own-fallback taint | validated; separate publication pending |
| Explicit-taint typed reparse | validated; separate publication pending |
| Root-self animation context | validated, including supplemental SMIL; separate publication pending |
| Parent metrics for font-variation-settings | source candidate, native validation pending; orientation scope remains explicit |
| Late/deep animation queue drain | diagnostic/design research; no accepted repair |
| #120 contextual sign | Held; contextual consumer prerequisites remain open |

This is an immutable 159-repair successor to inventory-v1; no prior snapshot was edited. The prior canonical-pin misconception and both failed installations remain preserved in their evidence capsules. Standalone alternative signing completed c7fba5/session41593/719fd0, exit 0; receipt SHA137605577661477ec0fea720dfe2d901743720bfcb0225bb810b3dd32d7d5c8e records signature verification, create-only ref success and preserved main branch state. Independent read-only Git checks confirm its exact research2701 parent, seven changed paths and seven packaged blobs. Root used standalone-commit-execution-v1 after restoring the committed disabled template exactly (73a7e2); an early pre-write guard rejection was resolved by unsetting only process-environment GIT_PAGER. No new browser run or primary-fix increment follows.
