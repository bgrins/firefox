# Ordinary typed-parse random rollback WPT proposal

One testharness file,11 named tests, for the same random-counter rollback family as the registered-alternative repair. Intended path: `testing/web-platform/tests/css/css-values/random-typed-parse-rollback.html`. Only `/resources/testharness.js` and `/resources/testharnessreport.js` are required. No registration, external fonts/images, preferences or metadata are added. Random support is asserted; the execution owner must use the intended supported build/preferences.

Six tests compare both specified serialization and computed value against explicit first/second ua cache keys. They cover numeric opacity, length line-height, successful percentage opacity, two filter factors, two border-image-slice numbers, and one conic-gradient angle position. Specified comparisons catch incorrect keys without relying on different keys producing distinct samples. Each pair has the same property, bounds, element styles and document, with no element-scoped key. Successful functions are counted across repeated factors/list members, so restoring zero instead of the entry count fails the two-member controls.

One successful numeric line-height case checks only specified key serialization. Its separate known computed-number zero bug must not be certified by equal0px results. Four additional computed controls cover named sharing and fixed .25 against independent literal results for opacity and length line-height. No assertion encodes the incorrect numeric line-height result; that repair remains independent.

## Source path for the additional cases

- Filter NonNegativeFactor delegates to NonNegativeNumberOrPercentage. The brightness/contrast sequence consumes two successful Number values within one declaration counter scope.
- BorderImageSlice uses Rect::parse_with with NonNegativeNumberOrPercentage. The two nonzero numeric ranges avoid accidental box shorthand collapse. Both successful values must keep successive indexes.
- Conic gradient uses GradientItem::parse_comma_separated with AngleOrPercentage::parse_with_unitless. The first stop parses red, then its random angle once through Percentage-first/Angle-second. No earlier random occurs in the prefix. Later position attempts on exhausted input or blue do not enter random parsing. This bounded input avoids speculating that every gradient retry is fixed.

Searchfox captures of effects.rs, image.rs and border.rs are byte-identical to the exact local sources read. SOURCE-PINS records the join; the prior audit pins NumberOrPercentage/AngleOrPercentage and numeric finalizers.

## Primary oracles

[Values5 key simplification](https://drafts.csswg.org/css-values-5/#random-simplify) counts functions in parsed value order and keeps generated ua keys observable. [Cache semantics](https://drafts.csswg.org/css-values-5/#random-caching) permits ua identifiers and makes identical cache tuples share the base. These tests avoid auto's extra name/element semantics and never require distinct-key inequality.

[Filter effects](https://drafts.csswg.org/filter-effects-1/#funcdef-filter-brightness) accepts number/percentage factors; [border-image-slice](https://drafts.csswg.org/css-backgrounds-3/#border-image-slice) accepts one to four nonnegative numbers/percentages; [Images4 conic color stops](https://drafts.csswg.org/css-images-4/#conic-gradients) accepts angle-percentage stop positions. The same concrete expression with authored ua keys provides the reference rather than duplicating random arithmetic.

## Preparation only

Node syntax check7da1b2/0 and VM enumerationd433ec/0 confirmed11unique registered callbacks; callbacks were not executed. This is not lint, genuine WPT manifest generation, browser validation or acceptance. Root/counter own adapter capture and actual paired execution. Six first assertions may fail before their subsequent computed assertions on the original build; the independent ordinary observer supplies both raw forms for the primary two witnesses. No live source, WPT, index, epoch or ledger changed.
