# Signed flex-line collection

This isolated model implements the reviewed first-failure collection interpretation from CSS Flexbox1 §9.3, with already resolved fixed inter-item gutters from CSS Gaps1. It preserves arbitrary full item values and their supplied signed rational outer hypothetical main sizes.

`FlexCollect.collect size threshold gap input` produces occupied lines. `FlexCollect.NextLine` independently describes a nonempty exact prefix/residual: either the first item is oversized and alone, or every nonempty prefix fits and the next extension fails (unless input ends). `FlexCollect.Collected` composes that relation. `FlexCollect.universal` proves the exact frozen target: executable correspondence, full flatten/order/multiplicity preservation, nonempty lines, count bound, deterministic relation and nowrap flatten preservation.

All generic laws permit arbitrary Rat parameters. CSS interpretation requires the separate Domain predicate (nonnegative inner threshold and fixed used gap); signed item sizes remain unrestricted. No theorem bans a later individually large item: [−50,150] at100 fits. Collection stops at first failure: [80,30,−50] gives [[80],[30,−50]], regardless of its smaller total. An oversized first item is immediately sealed: [150,−50] gives [[150],[−50]]. Exact fits use ≤. Gap is counted only between items; span_sum_count proves the executable fold equals item sum plus gap×(length−1).

The16 frozen design examples are source-authenticated against the corresponding checked case declarations. Additional cases cover exact fractions, full identity/repeated values, a third item and nowrap. Six compiled negated false claims and six refused positive versions test absorption, lookahead, strict fit, prefix flooring, duplicate dropping and edge-gap charging. These are semantic false-postcondition controls, not mutated native binaries.

Run the complete fresh source replay from the Firefox workspace root:

```
python3 -I -B artifacts/css-flex-line-collection-20261111-v1/check.py --out /absolute/new/replay
```

The checker uses pinned Lean4.35.0-rc4/Std, one worker,4GiB Lean memory and180seconds per command. It authenticates inputs before/after, checks all64 exact audit names, requires exactly exit1/one false-proposition diagnostic for each refusal, and removes owned compiled scratch only after observed process-group absence. `--modules` is an explicitly labeled development mode, not the full gate. Sources/logs/receipts remain for review.

DOM/CSS order, relevant-item selection, collapse/struts, forced breaks, fragmentation, size/margin acquisition, gap percentage/cyclic resolution, rounding, positioning and native source/binary correspondence remain outside this proof. Empty output denotes no occupied lines, not absence of an internal empty native FlexLine. No canonical library or native/WPT changes are made here. Browser data from the predecessor are supporting evidence, never proof premises.
