# Independent declaration publication audit

Date: 2026-10-19. Recommendation: accept the narrow native/WPT repair. The
original discovery run is six FAIL / 19 PASS; the final pair repairs twelve
cases with 135 unchanged outcome keys. This worker ran an isolated extracted
Rust replay, no Gecko build or browser, and changed no production source.
The separate universal publication companion is not reviewed or accepted here.

## Normative oracle

For an enabled ordinary property, setProperty parses the value and sets the
declaration. The resulting list must contain exactly one declaration of that
property and preserve unrelated properties. `length` counts declarations and
`item()` exposes their names. `removeProperty()` removes the matching declaration
and returns its former value. Thus setting one valid longhand on an empty block
requires length one, and subsequently removing it requires length zero.
[CSSOM setProperty and declaration constraints](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-setproperty),
[length/item](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-length),
[removeProperty](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-removeproperty).

The linked-parameter grammar accepts `none` or a comma-separated param list.
A dashed parameter name with a declaration-value, including an explicitly empty
value, is supported; substitution inside the value is meaningful. This test
uses no typed parameter or external resource loading.
[Linked Parameters](https://drafts.csswg.org/css-link-params-1/#propdef-link-parameters).
Current primary drafts were read on 2026-10-19. The CSSOM structural consequence
is independent of parameter resolution or computed serialization.

Verdict: REACHED for the length oracle, conditional on the feature being enabled;
the browser's first passing calibration establishes that condition for this run.

## Source chain

1. `nsDOMCSSDeclaration::SetProperty` recognizes the ordinary property and calls
   `ParsePropertyValue`. `ModifyDeclaration` obtains an empty or existing block,
   makes it mutable, and invokes `Servo_DeclarationBlock_SetPropertyById`.
2. Rust `set_property` creates an empty SourcePropertyDeclaration, then
   `parse_property_into` and `parse_one_declaration_into` reach
   `PropertyDeclaration::parse_into`. That function asserts the scratch source
   is empty. Its longhand callback pushes the ordinary parsed declaration only
   after the actual value parser and exhaustion succeed.
3. `LinkParameters::parse` accepts the param function, dashed name, and comma.
   It calls actual `VariableValue::parse` for the remaining declaration-value.
   This accepts the valid var/env/attr examples while the shared tokenizer
   records the substitution. The result becomes a LinkParamValue and the
   ordinary LinkParameters declaration is pushed.
4. The noncustom helper queries and disables the observer, obtaining true. It
   abandons ordinary success, validates the whole value, resets, reparses the
   arbitrary value, and invokes `parsed_custom`. That callback pushes a
   WithVariables declaration with the same longhand ID. It never clears the
   already pushed ordinary value. SourcePropertyDeclaration::push does not
   deduplicate; the scratch buffer now has two same-ID entries.
5. `set_property_to_declarations` calls `prepare_for_update` against the original
   destination. If the property is absent, both entries independently plan
   Append. `update` executes both plans; inserting the ID in a set does not
   prevent either vector append. Existing-destination updates instead target
   the same slot, so they need not duplicate.
6. `SetCSSDeclaration` reaches `nsStyledElement::SetInlineStyleDeclaration`,
   which wraps the block directly in nsAttrValue and passes it to
   `Element::SetAttrAndNotify` without AfterSetAttr reparsing. Style access does
   not reparse an existing eCSSDeclaration attribute. There is no automatic
   deduplication on the tested ordinary div path.
7. Length and IndexedGetter call Servo Count/GetAt, which inspect the vector.
   Rust removal finds the first matching longhand, removes it and its presence
   bit, then returns. One vector entry remains. `get()` first checks the presence
   bit, so source reasoning predicts a possible masked leftover value; this
   getter outcome was not measured by the original failing probe branch. The
   expanded final probe subsequently measured this exact disagreement.

Declaration-list parsing is a useful contrast: `DeclarationParserState` drains
through `PropertyDeclarationBlock::extend`, whose sequential `push` deduplicates.
The same source scratch defect can therefore remain invisible to cssText input.
On errors, `set_property` does not publish, and declaration-list `did_error`
clears scratch storage. These negative paths agree with the passing controls.

Complete named source snapshots are retained under `source/`. They include the
C++ entry/storage path and Rust publication providers. Six snapshots also match
the browser's explicit fixed-input pins; other snapshots are independently
hashed static evidence, not retrospectively added runtime pins. Source identities
and that distinction are executable in the checker.

## Exact observed scope

The probe has six values through new, existing, cssText and remove operations,
plus an enabled-feature calibration: 25 subtests. Root's raw result is exactly
six FAIL, 19 PASS and one OK harness. The six failures are the three valid
var/env/attr values through new and remove. New reports length two rather than
one; removal reports length one rather than zero. Existing and cssText controls,
`none`, explicit empty parameter, and invalid var-name inputs pass.

The failed assertions occur before the later Array.from/item-count or
getPropertyValue checks in those branches. Accordingly this audit does not
claim measured duplicate item names, cssText duplication, returned removal
values, or hidden getPropertyValue results. Those are separate proposed
observations; only the two length discrepancies are runtime confirmed here.

The raw/console hashes match the result receipt, all 75 fixed pins and two
binary pins remain stable, and the installed HTML matches the retained proposal.
The helper source is `6754d46e612a369fa6b3853151dc6179a60a92beb25a0a2dc1b8827b80669f92`;
param provider is `104a50a4c9945c3f36417ca006b92f71aba190279a44e58d53a4d8b15ad3dd24`;
WPT is `02a1010d78826b5e8923178f1f359759821d84b36cfc421e24adf3a57085a5f1`.
This is a shared project build with earlier repairs, not an isolated upstream run.

`layout.css.link-parameters.enabled` defaults according to IS_NIGHTLY_BUILD.
The WPT directory explicitly enables it. Release-default exposure is therefore
not established; the bug is not described as affecting an unmodified release
configuration. This is still a valid supported-property CSSOM invariant.

## Repair boundary and next checks

The exact candidate clears source scratch immediately after the successful
ordinary callback's no-observation early return. This is the point where that
ordinary result is abandoned. `SourcePropertyDeclaration::clear` resets both
its vector and all_shorthand. It runs before fallback structural validation and
VariableValue parsing, so later errors also leave no abandoned ordinary output.
The original empty-entry assertion makes this scratch private to the attempt.

Longhand callbacks push only after parse_entirely succeeds. The complete
helpers.mako.rs shorthand wrapper likewise places pushes inside the successful
map of parse_entirely; properties.mako.rs dispatches to those wrappers. Special
parse_all always errors without modifying scratch. These actual wrapper paths
establish empty scratch on ordinary callback failure; clearing that separate
error branch is not needed. Generated value grammar semantics remain external.
The selected clear leaves CSS-wide success, no-substitution ordinary success,
observer disable/query order, reset and validation order unchanged. It adds no
input scan. Its destruction cost is bounded by the abandoned scratch expansion;
no performance benchmark or universal allocator claim is made.

Changing only update deduplication or removal would hide the invalid source
publication contract from some consumers. It would not establish that the
scratch result contains one coherent representation. General-purpose update
changes also affect logical property ordering and importance, unnecessary for
this lead.

Useful regression coverage is one entry after valid substitution parsing,
removal to empty, existing value replacement, cssText normalization, invalid
fallback preserving prior value, ordinary/no-substitution and CSS-wide controls,
and unrelated-property order/importance preservation. Record length/items/
cssText/getPropertyValue separately before and after removal so an early failure
does not hide later state. The final pair below covers the chosen minimal test matrix. Unrelated-property
ordering, all shorthand grammar, allocation semantics and exhaustive ordinary
parser behavior are not proved by these cases.

The preceding curly proof's synthetic success callback now has a concrete
production analogue, but this does not retroactively prove its native source
admission. Its fallback gateway theorem did not model scratch multiplicity.
A useful next formal contract is transactional publication: successful fallback
replaces all scratch output from the abandoned attempt; successful ordinary
parsing remains unchanged; errors never publish. Composition with the update
planner must require unique source IDs and derive destination uniqueness and
presence-bit/vector agreement, rather than assume them after two Appends.

## Coverage and novelty

Existing linked-parameter parsing tests cover plain values and invalid grammar;
the dynamic var test checks computed substitution but not declaration count or
removal. This explains the coverage gap without claiming all prior tests pass.
Typed parameters and external SVG/resource semantics are outside this audit.

Bounded searches for link-parameters with duplicate/removeProperty found the
feature meta bug 1812163 and WPT sync bug 2072473. Their duplicate parameter-name
discussion concerns entries inside one property value, not duplicate CSSOM
property declarations. No exact duplicate was identified; novelty remains
unestablished. No external message or bug submission was made.

Searchfox CLI discovery failed DNS in this review; producer-supplied exact paths
and retained source were used. Layout instructions and overview/review docs were
read from retained artifacts; this session has no Read tool. No Mach bootstrap
was run because root explicitly prohibits Mach work for this task.

## Final exact-byte source and browser gate

The native candidate is
`2ef96482f50b06dcf87a18abc4d1a9aa0109a9063aa71cadc53e7737022c094d`.
It differs from retained original only by `declarations.clear()` at the boundary
above. The two-file patch is
`e9c2db7b54f48220053b76f02b5377b9ab78fa039eb461e828db3e38a48e7fae`.
This reviewer applied and reversed it on an artifact copy and verified complete
native/WPT bytes. Root's separate PATCH-CHECK records applicability/reversal at
upstream 976279105b2e78b8666a959eb3f25c9176cefaf8. That Git-based upstream result
is retained evidence, not independently repeated here; isolated upstream runtime
was not run. Whole-file rustfmt has a pre-existing wrapping difference; the
one-line delta is stable under formatting, as the retained FORMAT-CHECK records.

Final WPT has 49 subtests: one feature calibration, six values, two priorities,
four operations. The oracle counts declared properties, not parameter entries
or computed substituted values. Both normal and important declarations must
publish one property; removal snapshots all five observers before assertion.
Invalid updates preserve an existing value; fresh invalid input remains empty.
No font, asynchronous task or external resource is needed. Attribute syntax is
untyped here. These expectations follow CSSOM and valid declaration-value
parsing; they do not assert that unresolved param values compute successfully.

Independent raw-key reconstruction yields 147 unique outcomes: baseline
128 PASS / 13 FAIL / 6 OK; candidate 140 PASS / 1 FAIL / 6 OK. Exactly twelve
var/env/attr new/removal cases change FAIL to PASS, with both priorities.
The other 135 normalized outcomes are identical. All 49 new subtests pass.
The six baseline removal snapshots expose length one, stale item and cssText,
but empty getter and priority. The sole remaining failure is the existing
computed `param(ident("--a"), orange)` case, explicitly expected in metadata.
The original 25-case probe's more limited observations are retained above.

Each phase's input/before/after pins match. Only properties/mod.rs changes among
fixed pins; test/config/other source inputs are identical. The two binary hashes
change, and candidate build-after binaries match the browser inputs. Forced
Rust build and binaries link both exit zero. The link log contains four
build-monitor `KeyError: export` traces, preserved rather than hidden; XUL link
and final browser success are recorded. WPT lint reports zero problems. These
are project-build results, not an isolated upstream build or release-default
exposure claim.

## Extracted source replay and boundaries

Both producer capsules were authenticated before any producer code executed.
A fresh relocated source-only replay in /private/tmp compiled the complete
retained cssparser, actual VariableValue recursive parser, namespace helper,
LinkParameters parser and noncustom helper. All thirteen rows per source
variant match: four ordinary-plus-fallback scratch duplicates become exactly
one fallback value, with nine controls unchanged. Actual invalid VariableValue
inputs reject; the witness does not substitute an always-accepting provider.

I read native/build.py, the complete facade/driver/extractor, eighteen source
bindings and the retained complete provider functions. The candidate is generated
by the same one-line edit and checked against root's full candidate. The facade
uses Vec labels instead of the actual declaration enum/ArrayVec; it does not
execute CSSOM prepare/update/removal or C++ publication. DashedIdent admits the
ASCII fixture names, typed attr is rejected by an explicit guard, CSS-wide
support covers initial, atom/URL/Arc ownership is supplied. The handwritten
SubstitutionFunctionKind::from_ident mapping implements var/env/attr; the actual
derive expansion is not proved or compiled. cssparser is compiled directly
without its fast_match_byte default feature. Actual browser results exercise the
project configuration; this extracted gate is not an all-configuration theorem.
The binding extractor is a supported Rust lexer, not a general compiler parser;
its retained target bodies and boundaries were read, and the complete generated
functions compile. The replay's per-row assertions are finite fixture oracles,
not a universal independent parser specification.

No substantive blocker was found for the narrow two-file repair. The original
whole-tokenizer, property grammar, native memory and full publication proof
obligations remain open. A forthcoming model must state its unique-source-ID,
callback atomicity and publication-provider assumptions explicitly.

## Recheck and exact packaging

Authenticate this review's FREEZE/MANIFEST externally, then run
`python3 -I -S artifacts/css-declaration-publication-independent-v1/check.py`.
It authenticates both sibling source/browser capsules before using evidence,
reconstructs raw identities, binds source/build/test inputs and applies/reverses
the patch only in a fresh temporary directory. No live Git or browser is used.
For a fresh native extraction replay, authenticate the static sibling first,
then run its `python3 -I -S check.py --output /absolute/new/output`.
The retained TOOLCHAIN pins rustc; its toolchain runtime remains external.

COMMIT-INVENTORY.json lists exact source-only paths for static companion,
final browser evidence, this independent review, and the two native/WPT paths.
It includes every authenticated dependency and excludes all temporary binaries.
The root patch and formatting/applicability receipts are copied into this
review. No mutable root staging directory is a replay dependency. Root owns
final acceptance, signing and the separate formal companion review.
