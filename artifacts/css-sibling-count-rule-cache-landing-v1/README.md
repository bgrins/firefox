# Sibling-count reset-cache landing proposal

The two-path patch adds the existing uncacheable condition to `query_sibling_count` and a self-contained two-test WPT for width and opacity. The source change is byte-identical to the sealed source proposal. Its base also matches signed HEAD 19b09cce1a9b03ab19c46addc6fa46242f1544f9.

Each test uses equal-style parents with different child counts, then prepends to one and appends to the other before restoring both. All three snapshots and literal, topology, parent-style, and repeat-read calibrations are collected before the value assertions. Width additionally checks geometry. The iframe is visible and cleanup is registered before setup.

This is a rewritten landing fixture, not a byte projection or replay of the original six-test diagnostic. The original six tests retain the three index controls and inherited font-weight count control as broader validation. Their original browser result was two reset-count failures and four passing controls. This new two-test body has not run in a browser; it must be validated separately before acceptance. No failed gate is removed or relabelled.

No contextual easing, experimental animation representation, or accepted Round arithmetic repair is needed by these test expressions or the one-line cache condition. A clean upstream cherry-pick/build has not been performed. The conservative change disables reset-cache reuse for sibling-count computations; it does not claim measured performance impact or native equivalence of the accompanying abstract model.

Static verification used the actual WPT manifest parser and lint in a private temporary root, plus HTML parsing and inert callback enumeration. Final receipt 3a25b0/0: one testharness page, two callbacks, lint zero, scratch removed. Earlier d060f2 stopped on a missing vendored PyYAML import before validation; the checker now supplies that path. No browser, native source, main index, or canonical epoch changes were made.

Independent setup/oracle review by typed_demand_review: 771fba/0, clear. The review confirms the visible iframe, equal parent styles, exact counts 2/3 → 3/4 → 2/3 and calibration ordering; it does not establish the browser cache path.
