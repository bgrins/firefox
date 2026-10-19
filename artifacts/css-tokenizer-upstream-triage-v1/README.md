# cssparser upstream issue check

Read public GitHub API issue/search records on 19 October 2026; exact responses and request receipts are retained here.

The identifier-start escaped-newline repair overlaps open [issue440](https://github.com/servo/rust-cssparser/issues/440). That report includes numeric-dimension, identifier and hash witnesses for the same hyphen/backslash predicate. Our browser WPT and formal model supply additional local evidence; this is not a novelty claim.

Searches scoped to servo/rust-cssparser for overflow and exponent returned historical [issue35](https://github.com/servo/rust-cssparser/issues/35), [issue72](https://github.com/servo/rust-cssparser/issues/72), [PR73](https://github.com/servo/rust-cssparser/pull/73) and [PR132](https://github.com/servo/rust-cssparser/pull/132). They discuss intermediate f64 precision, overflow panic/clamping and numeric parser performance. Their returned descriptions do not report the exact finite compensated-exponent discrepancy. This limited title/body search is not an exhaustive novelty check, and it does not establish absence of an existing fix or report.

Web retrieval of the specific GitHub issue page failed; the public API request succeeded. A cached raw tokenizer search result was older than the current checkout, so it is not used as evidence of latest upstream source.
