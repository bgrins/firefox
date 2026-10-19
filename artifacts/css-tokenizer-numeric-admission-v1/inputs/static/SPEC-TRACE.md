# Numeric finite-result oracle

Primary sources freshly inspected on 2026-10-19:

- [CSS Syntax consume a number](https://drafts.csswg.org/css-syntax-3/#consume-a-number), ED dated 2026-10-16; complete fetched source retained.
- [CSS Values numeric types](https://drafts.csswg.org/css-values-4/#numeric-types), complete fetched source retained.
- [CSS Color opacity](https://drafts.csswg.org/css-color-4/#transparency), ED dated 2026-10-09, read through the web tool.

Syntax parses the significand and exponent and returns their base-ten combination. Values gives implementations finite range/precision freedom, but specification algorithms assume infinite precision/range; unsupported values are converted to a closest supported value. Opacity computes the specified number clamped to [0,1].

The three challenged complete literals equal exactly 0.5. Ordinary 0.5 and 5e-1 controls establish that this result is supported. The enormous intermediate significand or power is not a separate author-specified CSS value. Therefore final-value range freedom does not justify mapping these complete literals to infinity or NaN. No requirement to support an enormous final finite value or arbitrary correct rounding is needed for this oracle. This last application of the range rule is an explicit specification inference, not a claim that the spec prescribes a particular numeric conversion implementation.

Verdict: REACHED for expected computed opacity 0.5, subject to root's independent adjudication and browser test. The genuinely huge 1e999 control is intentionally different: opacity can clamp it to 1. The zero-with-huge-exponent control has value zero, even though the extracted native payload becomes NaN; later normalization can hide that payload error. No rendering bug is inferred from that control alone.

Exact references are calculated independently using Python Decimal from complete input strings. The retained initial Rust draft's fractional case used exponent400, which denotes5; this was caught by the independent decimal assertion before browser handoff. Final Rust and HTML use exponent399 and denote0.5. Both versions and their execution records remain explicit.
