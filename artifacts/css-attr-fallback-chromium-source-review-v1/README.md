# Chromium cross-check: attr() own fallback taint

**Chromium's implementation explicitly taints a selected literal fallback returned by `attr()`.** This supports the current-text verdict and the standalone Firefox candidate; it is source evidence, not a Chromium browser observation or proof that our candidate passes.

## Exact implementation path

The fetched `main` source was independently re-fetched at commit `4984943c549958db678bf91c76252d38e9f684fd` (2026-10-28) and matches exactly, Git blob `98a7a926daa0481e7a584e7bfd6d761e26cc6dba`.

In [StyleCascade::ResolveAttrInto](https://github.com/chromium/chromium/blob/4984943c549958db678bf91c76252d38e9f684fd/third_party/blink/renderer/core/css/resolver/style_cascade.cc#L2423), a missing attribute leaves the substitution value null. An attribute that fails its requested syntax also has no substitution value. Both reach the fallback branch. With an explicit comma, that branch substitutes fallback tokens using `ResolveTokensInto`; failure returns false. On success, the final call is:

```
out.AppendFallback(fallback, /*is_attr_tainted=*/true, ...)
```

The boolean is unconditional for this selected fallback: it is not derived from whether the fallback itself contained another `attr()`. A literal quoted string therefore gets true. A successful primary also uses true. This directly covers our missing raw literal, invalid typed literal and missing typed literal fallback cases.

[TokenSequence::AppendFallback](https://github.com/chromium/chromium/blob/4984943c549958db678bf91c76252d38e9f684fd/third_party/blink/renderer/core/css/resolver/style_cascade.cc#L1070) appends the fallback text, inserts a token separator if necessary, and records the appended interval in `attr_taint_ranges_` when that argument is true. This is an actual range write, not a conclusion inferred from a function name. Its empty-token early return is a separate boundary: this review concerns tokenful quoted literal fallbacks and does not claim an aggregate empty-value preservation result.

`SOURCE.json` retains exact function excerpts. Source retrieval and pin confirmation were f549b9/17ed21/165781, all exit 0. The initial sandbox curl could not resolve the host (ab18cb/6); subsequent read-only public GitHub API fetches succeeded. The web renderer also failed to open the pinned page; the saved API response and decoded source are the successful authority.

## Tests and issue search

Bounded inspection of Chromium's primary test sources found no exact own-literal-fallback URL-taint regression test in the files below. This is not a repository-wide absence claim.

| Source | What it establishes |
| --- | --- |
| `style_cascade_test.cc` | Attr-cycle and argument tests, but no attr-taint-named case or direct fallback taint check in the inspected tests. |
| [attr-security.html](https://github.com/chromium/chromium/blob/main/third_party/blink/web_tests/external/wpt/css/css-values/attr-security.html) | Primary attr URL rejection, registered propagation and `var(--y, attr(...))` fallback tests. That fallback belongs to `var()`, not to `attr()`. |
| [attr-notype-fallback.html](https://github.com/chromium/chromium/blob/main/third_party/blink/web_tests/external/wpt/css/css-values/attr-notype-fallback.html) | Own literal fallbacks used for content; no URL sink, hence no taint oracle. |
| `attr-all-types.html` | Invalid typed primary with literal identifier fallback in animation-name; no URL-taint distinction for that fallback. |
| `attr-parse-url.html` | Direct typed URL rejection, a different boundary. |

The fetched API objects pin each test by its Git blob and decoded bytes. No test was run or modified. The directory listing and source searches are retained.

A primary GitHub issue search `repo:w3c/csswg-drafts attr fallback taint` returned four results: [5092](https://github.com/w3c/csswg-drafts/issues/5092), [13946](https://github.com/w3c/csswg-drafts/issues/13946), 10372 and 11144. It did not identify a specifically titled own-literal-fallback exception or regression. The earlier sealed spec review already examines the relevant security and URL-type discussions. The web search also surfaced [Chromium 517746687](https://issues.chromium.org/issues/517746687), a fixed interpolated-custom-property transition taint issue; that concerns loss during interpolation, not an intentional exclusion of `attr()`'s literal fallback. No duplicate or exhaustive issue-absence claim is made.

## Consequence and limits

The actual implementation agrees with marking a successful legacy Firefox fallback tainted iff its reference is Attr, while preserving existing nested taint. The sealed standalone fix remains unchanged. System Firefox's nine mismatches / 15 matching controls are independently observed runtime evidence; this report adds only Chromium source compatibility. No other engine was run, no live source/fixture/index was changed, and no bug or fix count changes follow from this review.
