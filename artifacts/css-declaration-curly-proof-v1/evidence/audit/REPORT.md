# Declaration fallback/reparse audit

Date: 2026-10-19. Status: one browser-reproduced syntax defect; proposed repair
passes the bounded parser/helper witness. No live code changes were made here.
This audit establishes neither a universal native proof nor novelty.

## Ranked finding

**1. Property-parser cleanup hides a forbidden top-level curly block from
declaration fallback validation.**

`font-family: serif {var(--x)}` is accepted and replaces a prior valid
`font-family: monospace`. It should be discarded at parse time. The same
mechanism accepts a comma before the block, a leading block followed by an
identifier, an empty block followed by `var()`, and `env()`/`attr()` inside the
block. This is ordinary-size input, independent of the repaired nesting limit.

The decisive normative rule is CSS Syntax's [consume a declaration, step
8](https://drafts.csswg.org/css-syntax/#consume-declaration): noncustom values
cannot combine a top-level curly block with another significant component.
The [CSSWG resolution in issue 9317](https://github.com/w3c/csswg-drafts/issues/9317)
explicitly applies that restriction even when a variable function is present.
Whole-value curly blocks and custom properties are different cases. The
ordinary [substitution grammar deferral](https://drafts.csswg.org/css-values-5/#arbitrary-substitution)
does not waive this declaration-level restriction. Retrieved primary evidence
and resolution text are retained in `evidence/spec-*.json`.

### Actual source chain

1. `parse_one_declaration_into` constructs a fresh parser and calls
   `PropertyDeclaration::parse_into` inside `parse_entirely`. Declaration-list
   callers instead enter through `DeclarationParserState::parse_value`; nested
   style rules forward there from `NestedRuleParser::parse_value`.
2. `PropertyDeclaration::parse_into` skips initial whitespace, saves `start`,
   and selects the noncustom helper. Its longhand callback invokes the actual
   longhand value parser and requires exhaustion before publishing.
3. `FontFamily::parse` calls `Parser::parse_comma_separated` with
   `SingleFontFamily::parse`. The `serif` branch is a valid generic family;
   the unexpected remaining curly block makes that comma item fail.
4. `parse_comma_separated_internal` calls `parse_until_before(Comma, ...)`.
   Its consume-on-error cleanup traverses the remaining item, including the
   curly block and its substitution function, before returning failure.
5. `parse_non_custom_property_declaration_value_into` originally scans only
   the suffix after that failure. The suffix is empty, so it misses the curly
   block. The function observer has recorded the nested substitution.
6. Reset and `VariableValue::parse` accept the arbitrary declaration value;
   that parser intentionally permits curly blocks. It does not know whether
   the property is custom. The normal property is published as WithVariables.

Complete source snapshots are in `evidence/source/`. The exact helper matches
Searchfox's retrieved helper; whole-file equality is intentionally not claimed
because unrelated local changes exist. `evidence/searchfox-properties.json`
retains successful discovery; batch CLI attempts failed DNS and are retained
separately. The installed CLI lacks `--permalink`. No revision URL was invented.

### Browser evidence, produced by root

The artifact WPT tests 12 values through setProperty, cssText, stylesheet and
CSS.supports: **24 failures and 24 passing controls**, with an OK harness.
All six malformed substitution values fail through all four APIs. Prior valid
declarations remain the expected CSSOM value; the actual value is the malformed
declaration. A following opacity declaration is also checked. Controls include
the non-substitution malformed value, whole-value curly, plain var, square
blocks, the color path, and a custom property.

This proves observable parsing/CSSOM behavior. There is no rendered-font or
computed-style claim in this audit. Root's raw output, input and before/after
pins are copied under `evidence/root-browser/`; the checker derives the 24/24
split by subtest identity and verifies the source/test binding and stable pins.
No browser was launched by this worker.

### Existing coverage and known issues

The existing `css/css-syntax/var-with-blocks.html` covers the general rule,
including leading/trailing blocks, but its ordinary property is `color`.
There is no local expectation metadata for that file. Color's failure leaves
the relevant block visible to the helper; it does not exercise the consuming
comma-item path. That explains this test gap without suggesting the syntax
rule lacked tests entirely.

The 66-fix ledger was inspected and is pinned. This is separate from the
accepted depth recovery repair `55d251b7a90003546994f6576e5ee78e8fa07cb2`,
quoted EOF repairs, typed attr fixes and rollback-cache work. Bounded Bugzilla
and Stylo issue searches did not identify a matching implementation report;
search results were sparse/noisy. That is not evidence of novelty. CSSWG 9317
is prior normative discussion, not an implementation bug report for this path.

## Native witness and proposed repair

`replay.py` builds the complete pinned current cssparser crate and its four
dependency crates. All 128 retained vendor inputs match the inspected local
tree, including the accepted depth repair/checksum. It compiles the **byte-exact
complete noncustom helper**, with small declared type/provider adapters.

The two callback modes are a single identifier parser and an identifier comma
list. The latter uses the real cssparser comma-item cleanup. These are provider
projections, not the complete Stylo FontFamily parser. The `serif` branch and
actual FontFamily caller are inspected source, and the browser run supplies
the end-to-end connection. `VariableValue::parse` is deliberately an accepting
boundary adapter: a `gateway` result means the helper reached fallback parsing,
not that arbitrary native custom-property syntax was proved valid. The cases
contain simple independently understood var/env/attr bodies. CSS-wide keyword
and namespace/URL storage adapters are likewise not full providers.

The independent syntax oracle counts complete top-level components and asks
whether any is curly and whether there is another component. It does not use
the property parser's failure cursor or the helper's starts-with flag. It
shares the real tokenizer/block-skipping provider, so lexical correctness is
not independently verified here.

**26 observations per variant:** original has seven forbidden fallback
gateways, all on the comma-list path; candidate has zero. Exactly seven rows
change. Single-parser controls and legal fallback gateways are unchanged.
The candidate is root's retained one-line semantic addition: reset to saved
start before the existing curly validation scan. It also updates the existing
comment. `evidence/proposed-native.patch` is the proposal, not a live edit.

State reasoning:

- Ordinary successful parses with no observed substitution return before the
  new reset: the common successful path has no added scan.
- Failed parsing leaves the observation epoch enabled. Reset restores parser
  state, not observation state; replay continues the same epoch.
- Successful parsing with an observed substitution stores true before the
  query disables tracking. The later OR retains that true value during the
  reset scan. The scan's curly validation does not depend on tracking.
- Saved start is after initial whitespace/comments. Empty values, one curly
  block, repeated curly blocks and mixed values have a direct full-list
  classification; custom properties never enter this helper.

The repair adds a rescan of the consumed prefix on fallback/error paths, with
linear additional work in that prefix. It preserves the cheap ordinary
success path. No benchmark or universal complexity/compiler theorem is claimed.
Full Gecko candidate build, paired WPT and independent review remain root gates.

## Other inspected surfaces and negative findings

| Surface | Result / limit |
| --- | --- |
| `expect_exhausted` consuming an offending block | Disconfirmed: it saves and resets parser state. `color` is a passing browser control. |
| `!important` publication after invalid suffix | `DeclarationParserState::parse_value` requires outer exhaustion before draining to the output block; `did_error` clears scratch declarations. No new defect established. |
| Top-level bang/semicolon vs nested punctuation | `parse_declaration_value` establishes the top-level stops; recursive block parser accepts nested punctuation. No flattening defect found in the inspected path. |
| Invalid var name, extra arguments without comma | Custom scanner parses the name; no-comma branch resets before enclosing exhaustion, retaining invalid trailing input. No new defect established. |
| Malformed attr type / fallback | Transactional attr-type parse and enclosing exhaustion inspected; existing typed-attr ledger repairs excluded. Not a new general attr-conformance claim. |
| `env()` reserved identifiers | Source explicitly records CSSWG issue 3262 interoperability policy. Not promoted as a new bug. |
| Observer cache entry | Separate worker's admission audit covers fresh/colon entries and the observation epoch; no duplicated proof or browser defect claim here. |
| Custom properties with mixed curly blocks | Exempt by Syntax; root browser control passes. |
| Depth/error cleanup | Accepted repair retained in native crate; this finding needs no excessive nesting. |
| Stylesheet fallback from declaration to qualified rule | Source reset path inspected; the new probe shows the declaration wrongly wins before that fallback. Full arbitrary nesting grammar remains unproved. |

Uninspected: exhaustive generated longhand/shorthand parsers, descriptor grammars,
new Values 5 functions and spread syntax, all registration grammars, complete
substitution/cascade evaluation, URL observer publication, allocation failures,
and compiler correctness. This bounded audit reports one mechanism, not a
claim that the remaining declaration machinery is bug-free.

## Next meaningful formal target

See `FORMAL-PLAN.md`: full-component validation must be independent of where a
failed property parser leaves the cursor. This is a compositional parser
invariant, with observer and publication contracts kept explicit. No Lean
theorem was produced in this static audit.

## Replay and integrity

Authenticate the checker and MANIFEST against the external FREEZE digest, then:

```
python3 -I -S check.py --output /tmp/declaration-reparse-fresh
```

The output directory must be new and outside this artifact. The checker verifies
the complete file roster before spawning the isolated source-only replay.
`MANIFEST.json` lists the commit roster; add MANIFEST and FREEZE. Replay binaries,
rlibs and temporary copied sources are outside the artifact and excluded.
