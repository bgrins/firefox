# Escaped EOF: tokenizer versus custom-property serialization

## Verdict

The three existing WPT failures reproduce a specified-value spelling difference. They do not establish a tokenizer error: the decoded identifier, dimension unit and URL contain U+FFFD, while the stored custom-property CSS uses a backslash followed by U+FFFD. Both spellings decode to the same token content. **INCONCLUSIVE** for the claim that current specifications require this WPT's unique unescaped spelling. No native repair is recommended from these failures alone.

The literal author-source requirement in CSS Variables and whole-stylesheet round-trip requirement in CSS Syntax need an explicit EOF-recovery serialization rule to reconcile them. Returning the original terminal backslash unchanged also does not solve the general problem: when embedded before a declaration delimiter it can escape that delimiter. The present report does not declare current Firefox fully conforming to every serialization requirement.

## Observed evidence and exact assertion direction

Root's independently run `css-tokenizer-string-comment-root-v1/browser-result.json` is copied under `evidence/`. It reports stable pins, three escaped-eof failures, passing hash and string controls, and 19 new string/comment plus two known-bad-string controls passing. This scout ran no browser.

`escaped-eof.html` passes the intended constant as the first argument to `assert_equals` and the browser result as the second. Its diagnostic expected/got wording is therefore reversed relative to browser/author expectation. Browser returns `foo\\�`, `1foo\\�`, and `url(foo\\�)`; intended constants omit the backslash. The stored metadata already expects these three failures. Metadata is not execution evidence.

The separate serialize-escape-identifiers failure is a TypeError at its **second** `document.styleSheets[0]` access, after assigning `sheet.innerText = text`. Initial rule access and serialization succeeded. Root subsequently reports 36 constructed-sheet/awaited-import diagnostic checks passing; that report is communication evidence, not an included independently replayed receipt. No rule-specific round-trip defect follows from this TypeError.

## Specification trace

1. A style rule's declaration value is tokenized and parsed even at EOF. [CSS Syntax escaped code point](https://drafts.csswg.org/css-syntax-3/#consume-escaped-code-point) returns replacement character for an escape ending at EOF. Ident-sequence consumption appends it; numeric token consumption uses the ident sequence for the dimension unit; unquoted URL consumption appends it to URL content. Quoted-string backslash followed by EOF is ignored instead. This is a token-content contract, not a raw spelling contract.
2. [CSSOM getPropertyValue](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-getpropertyvalue) finds the case-sensitive custom declaration and invokes CSS value serialization. It does not apply the non-custom shorthand path.
3. [CSSOM value serialization](https://drafts.csswg.org/cssom/#serialize-a-css-value) gives general component serialization rules. Applying ordinary identifier serialization would yield a literal replacement character, but this does not supersede the custom-property-specific preservation requirement.
4. [CSS Variables §4.1](https://drafts.csswg.org/css-variables-1/#serializing-custom-props) requires author spelling for specified values, and for computed values apart from substitutions; its stated exception concerns empty values. That requirement precludes general identifier canonicalization of raw custom-property contents.
5. [CSS Syntax §9](https://drafts.csswg.org/css-syntax-3/#serialization) delegates general serialization to CSSOM and feature specs, while requiring parse/serialize/reparse structural preservation. It does not select one spelling of replacement characters for unregistered custom properties.

Thus replacement-token content is REACHED; necessity of the exact three WPT strings is INCONCLUSIVE. The missing edge is a normative serialization rule for EOF-recovered raw custom-property tokens, not a missing escape-decoder call.

Primary documents were read on 2026-10-19 (Variables draft October 9; CSSOM October 13; Syntax current draft). `spec/` preserves parsed web-tool responses and retrieval identity; these are not raw HTML snapshots. `webspec-index` was unavailable; shell HTTPS retrieval failed DNS. No bootstrap/shared tool mutation was attempted for this bounded artifact task. Fragment URLs were read through the web tool, which strips fragments; independent HTML-id validation remains unavailable. Searchfox initially had intermittent DNS failures, then discovery succeeded for the named local paths.

## Native source chain

Complete files are pinned in `source/` and `SOURCE-PINS.json`.

- `PropertyDeclaration::parse_into` in properties/mod.rs handles custom property IDs, attempts a CSS-wide keyword, then calls `VariableValue::parse` for raw specified values.
- `VariableValue::parse` obtains source bytes through `Parser::slice_from`, trims boundary whitespace, calls declaration-value parsing, and appends accumulated missing closing characters. Only quoted-string EOF repair pops the terminal backslash.
- Complete `parse_declaration_value` and `parse_declaration_value_block` traverse nested blocks. The shared Ident/AtKeyword/Hash/IDHash/UnquotedUrl/Dimension arm detects a decoded value ending in U+FFFD and a raw token slice ending in backslash, then appends U+FFFD to the repair suffix. The source comment explicitly chooses escaped replacement character as a convenient equivalent spelling. URLs also get a closing parenthesis.
- cssparser `consume_escape_and_write` supplies replacement UTF-8 at EOF; complete `consume_name`, `consume_numeric`, and `consume_unquoted_url` route through it for the relevant tokens. The current numeric repair does not change this unit/suffix route.
- `nsDOMCSSDeclaration::GetPropertyValue` calls `Servo_DeclarationBlock_GetPropertyValue`, then `get_property_value`, `PropertyDeclarationBlock::property_value_to_css`, exact-name `get`, and `PropertyDeclaration::to_css`. The properties.mako.rs serializer dispatches to CustomDeclaration's derived ToCss; its name is skipped and its unparsed value reaches `SpecifiedValue::to_css`, which writes `self.css` unchanged. No late canonicalizer removes this repair backslash.
- Derived ToCss expansion and the full HTML/style-loader route were inspected only at their declaration/template interfaces, not freshly generated or compiled. This is source review, not executable whole-caller refinement.

## Smallest repair boundary, conditional on resolving the oracle

Do not change cssparser's escape decoder: its replacement content already agrees. Do not canonicalize every custom-property token. A future choice to use literal U+FFFD belongs to the raw EOF-repair boundary and its serialization contract.

A one-line `css.pop()` in VariableValue::parse is unsafe without more work. Substitution-function `reference.end` is already calculated using original source end plus the repair suffix's byte length. For `var(--missing, foo\\` at EOF, dropping one original byte afterward leaves the enclosing end one byte too large. Nested references and fallback slicing need a common offset transformation. Keeping internal storage unchanged and recording an explicit EOF-repair site for external serialization is another design, but requires carrying that provenance through substitution and concatenation. Neither design is implemented or approved here.

If the desired change is solely a tokenization test, an independently landable WPT correction could test token semantics/round-trip rather than a raw custom-property spelling. That still needs WPT/spec agreement; no metadata or WPT edit is proposed for landing now.

## Known overlap and controls

Bounded web searches for escaped-eof and custom-property EOF serialization found historical reports of exactly these three failures in bug 1611178, and recent WPT-sync listings in bugs 2050643 and 2082681. These are synchronization/reporting records, not identified root-cause fixes. No novelty claim and no claim that a dedicated bug does not exist. Search URLs are listed in SEARCH.md.

`probe.html` is explicitly **UNEXECUTED**, standalone, and diagnostic: three EOF token spellings, quoted-string EOF, escaped backslash, explicit hex replacement escape, and nested var fallback cases. It records code points and rule round-trip stability without asserting the disputed spelling. Existing missing-closing-nested-fallback and crash tests are pinned as relevant offset controls; they were not run by this scout.

## Proof obligations and coverage

Useful narrow targets: (1) decoded token equivalence for EOF repair, preserving even/odd backslash distinction; (2) closure suffix ordering under arbitrary nested blocks; (3) all substitution/fallback intervals remain UTF-8 boundaries within the repaired buffer, including every enclosing reference; (4) standalone token preservation when serialized within declaration/rule delimiters; (5) raw author-spelling preservation outside precisely admitted recovery sites.

Inspected: complete custom raw parser/repair, relevant tokenizer bodies, complete CSSOM getter/property-value dispatcher/get, serializer template and derived-wrapper declarations, exact WPT and metadata, root's browser result. Not proved or executed: arbitrary substitution histories, generated derives, HTML loader/DOM binding, allocation/usize arithmetic, whole parser/tokenizer soundness, CSSWG interpretation of recovery serialization, cross-browser results. No whole-tokenizer or formal acceptance claim.
