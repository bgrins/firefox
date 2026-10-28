# Focused page-selector repair review

No concrete source or test-oracle blocker found in this bounded review. This is source/spec review, not acceptance or independent build/browser validation.

## Normative trace: REACHED

For a named alpha page, a nonempty @page rule applies through a matching list member ([Page §4.1](https://drafts.csswg.org/css-page-3/#at-page-rule)). The current Page draft, dated 21 October 2026, states: “A page selector is said to match a given page if and only if all of its components match the page.” Names are case-sensitive ([§4.2](https://drafts.csswg.org/css-page-3/#page-selectors)). Page cascading compares the (f,g,h) tuple, with the name component first ([§4.4](https://drafts.csswg.org/css-page-3/#cascading-and-page-context)). Selectors defines effective list specificity using “the most specific selector in the list that matches” ([Selectors §15](https://drafts.csswg.org/selectors-4/#specificity-rules)). Thus an unmatched beta member cannot supply either applicability or specificity on alpha.

The existing nameless-bucket pass is necessary: absence of a page type selector does not restrict a selector to unnamed pages. Filtering that bucket by its empty atom preserves this behavior.

## Native correspondence

Reviewed captured ExtraStyleData::add_page, PageRuleMap::match_and_append_rules, match_and_add_rules, PageRule::match_specificity, PageSelector::match_specificity, and selector_specificity. The focused change passes the bucket name and filters before pseudo testing and maximum calculation. Empty selector lists remain universal and are inserted only into the empty-name bucket.

Taking a maximum within each visited bucket and appending both is sufficient here. A named match has f=1 and every nameless match f=0, so named/nameless results cannot tie. The existing stable sort preserves source-order ties within each bucket; a rule present in both buckets retains its stronger matching instance. Duplicate same-name insertions repeat the same declaration block/layer at the same bucket maximum, without introducing a different winner. The repair changes neither layer ordering nor importance handling. Broader duplicate elimination is unnecessary for this fix.

## Six landable files

There are three print tests and three references, not six independent test cases. Exact patch-added bytes match their historical captured test/reference bodies (check 46a71f/0).

| Test suffix | Required result | Independent reference |
|---|---|---|
| applicability-print | alpha:first matches only page 1; beta never matches alpha; page 2 has zero margin | nameless :first margin, explicit page break |
| specificity-print | alpha and the later alpha rule tie at (1,0,0); later zero margin wins; beta:first is irrelevant | single zero-margin page |
| control-unnamed-mixed-print | beta is irrelevant; two :first matches tie at (0,1,0), later zero margin wins; page 2 zero margin | two zero-margin pages |

The 20px green boxes and explicit page breaks avoid text/font metrics; 96px margin changes are visible in both selected page ranges. Named-page assignment itself is intentionally not shared by the references. The broader paired roster covers reversed/split selectors, duplicates, named/unnamed overlap, names/case, layers, and importance, but is not required to expand the six-file landing scope.

## Evidence and limits

This review does not independently certify screenshots, native compilation, current runtime results, lint, or all cascade/revert behavior. Root's fresh baseline and ongoing candidate experiment remain separate evidence. No live source, index, epoch, build, browser, or ledger was changed.

Tools: read locally changed/captured source and exact patch; opened both current official drafts via web tool (references turn2600view0/turn2600view1), inspected captured HTML section IDs (46a71f/0). `command -v webspec-index` returned exit 1 with no path (8c5ead); no CLI trace/exists result is claimed. Bootstrap was not run concurrently with root's active native build. Anchors were checked directly in pinned official HTML instead. Firefox frontend and spec-trace skills were read. This is a direct prose-rule trace, not an automated reference-graph enumeration.
