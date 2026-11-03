# Current CSS fix inventory

**160 committed primary repairs**, through `9afff49c042b06bdfd41bf94858c7ea5e1a899ef`. Research, alternative packaging, held #120 and pending candidates are excluded. Full summaries and hashes are in [INVENTORY.json](INVENTORY.json).

| Area | Repairs |
| --- | ---: |
| Animations, timelines and transitions | 20 |
| Attributes and custom properties | 22 |
| CSSOM geometry and hidden layout | 13 |
| Cascade, layers and shorthands | 7 |
| Colors, images, SVG and shapes | 8 |
| Container queries | 3 |
| Layout, sizing and positioning | 23 |
| Parsing, tokens and CSS math | 33 |
| Selectors, Bloom filters and scoping | 12 |
| Text and fonts | 19 |

Newest repair: typed custom-property reparsing preserves explicit attribute taint. Commit `9afff49c042b` contains only custom_properties.rs and attr-taint-registration-transition.html, directly after research `c5431d8e0bc1`. Configured signing succeeded; root verified the exact parent and both committed/live blobs.

Historical isolated browser comparison: target 3 PASS/1 FAIL → 4 PASS; existing controls 47 PASS unchanged; separate fallback cases 17 PASS/11 FAIL unchanged. Fresh delivery passed WPT lint and manifest checks. No combined font/cancellation/taint build is claimed. Publication bookkeeping still records accepted=false and accepted_fix_increment=0; this inventory counts committed primary repairs.

Review priority: preserve the previous crash-first and taint-review recommendations; include this taint-preservation repair in that review. This is not an assigned security severity or an exfiltration claim.

Pending: selected attr() own-fallback taint and root-self animation context are validated but unpublished; parent font-variation metrics and late/deep queue draining remain investigation work. The provider-rebinding proof/probe is research, with no new native defect established.
