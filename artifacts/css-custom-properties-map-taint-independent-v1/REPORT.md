# Independent review: custom-property taint equality

## Disposition

The root browser baseline reproduces four taint-sensitive computed-value errors and passes five controls. I independently read the raw observations, source and oracle. The failures occur at the final child image assertion after the literal-image, parent value/taint and child-token prerequisites succeeded. The diagnostic is byte-identical to the sealed routing scout proposal.

The two source shortcuts need one metadata-preserving no-op repair. `proposed.patch` is an exact two-file, two-site artifact-only candidate. Its originals matched the live source when prepared; no production files were modified. It has not been compiled or browser-tested by this review. Root owns integration and candidate gates.

## Normative oracle

1. Registered properties accept CSS-wide keywords even with string syntax. Universal registrations use ordinary custom-property computed values. [Properties and Values API: specified/computed values](https://drafts.css-houdini.org/css-properties-values-api-1/#specified-value-time).
2. Explicit inherit takes the parent's computed value, including for a non-inherited property. A child's authored literal replaces the inherited value rather than deriving from it. [Cascade: explicit inheritance](https://drafts.csswg.org/css-cascade-4/#inherit).
3. Attribute-derived values and substitutions carry taint, including registered values' equivalent token sequences. Using that result as a URL is invalid at computed-value time. An independent literal does not acquire taint merely by matching an ancestor's text. [Values 5: attr security](https://drafts.csswg.org/css-values-5/#attr-security).
4. An image-set string represents a URL. This makes image-set a direct observable consumer without depending on src()/string() support or a network request. [Images 4: image-set](https://drafts.csswg.org/css-images-4/#image-set-notation).

Verdict: **REACHED** for the nine-case oracle. No claim about exfiltration, external requests or severity follows from these computed-style observations.

Current primary documents were read with the web tool. `spec/primary-web-capture.txt` retains the deciding sections. `webspec-index` was unavailable and direct curl failed DNS resolution; `spec/RECEIPTS.json` preserves that failure. Thus full HTML-id authentication was unavailable; links are the primary section links used by the documents and prior source audit, not a claim of successful CLI anchor validation. No bootstrap or shared-tool change was attempted under this artifact-only task.

## Path A: shared map retains the wrong taint

`CustomPropertiesMap::do_insert` has only two direct callers in the complete file: public insert and remove. Unique maps insert immediately; shared maps skip before cloning or expanding when their existing value compares equal to the proposed value. `Value<Component>::PartialEq` intentionally compares only the payload `v`, omitting both taint and URL data.

All normal custom-property insertions pass through `ComputedSubstitutionFunctions::insert_var` and `ComputedCustomProperties::insert`, selecting the inherited/reset map by the current registration. `Cascade::init_custom_properties` shares the parent inherited map and stylist initial reset map. Explicit nonroot reset-property inherit clones the parent's reset value, which can be tainted despite matching the untainted initial payload. Conversely, a typed literal child override can match a tainted inherited payload while carrying false taint. The early return drops the new metadata in either direction.

The existing `can_deduplicate_values` already compares payload and outer taint and is used by `Inner::eq`. Reusing it for the shared early return is the smallest local fix. None/None, actual unequal values, unique mutation, count arithmetic, COW threshold and ordering retain their original branch behavior. The proposal does not add URL-data equality or change global PartialEq.

## Path B: universal cascade skips the override before insertion

`value_may_affect_style` has one actual direct caller, `cascade_custom_property`; an early false marks the declaration seen and returns before applying it. For unregistered/universal values, the shortcut extracts `as_universal()` and compares two `VariableValue`s. Their PartialEq compares CSS text only.

The taint comparison must use the OUTER computed wrapper. `Substitution::into_value` builds a new resolved inner VariableValue and separately ORs substitution taint into the computed wrapper. Consequently, checking only the existing inner value's explicit flag or `is_attr_tainted()` is insufficient. The proposal renames the extracted inner binding and compares `existing_value.attr_tainted` with incoming `value.is_attr_tainted()`, then performs the existing CSS comparison. The incoming query is exactly the taint initialization used by `ComputedRegisteredValue::universal`.

This is a second required site, not automatically a second independently landable bug. With only B fixed, application can still reach A and discard the override. With only A fixed, universal cases can still stop before insertion. The typed probes directly exercise A; the unregistered/universal probes exercise the earlier B path. A separate unique-map control could isolate B, but is unnecessary to justify the small combined repair and is not claimed as executed.

## Equality quotient and scope

Do not globally modify Value or VariableValue PartialEq for this repair. Their payload-only behavior is explicit, and other inspected consumers include `StyleFeaturePlain::substitute_and_compare`/`matches` and derived CustomAnimatedValue/AnimationValue equality. Altering those would change style-query and animation comparison behavior and require separate normative analysis. The proposed two sites decide whether to replace a stored value, for which preserving the new metadata is necessary.

The decisive downstream chain is `substitute_one_reference` reading the computed wrapper's taint, `do_substitute_chunk` adding tainted source ranges, `ParserContext::disallow_urls_in_range`, and `CssUrl::parse_from_string` rejecting tainted URL ranges. `ImageSetItem::parse` sends its string's actual token span to that URL parser. Complete relevant definitions are pinned in `SOURCE-BINDINGS.json`.

The recent count/iterator composition's readiness/index guarantees remain applicable without CompareSound. Its separate requested-value history theorem deliberately needed sound equality on the chosen payload semantics. These examples show why the original native PartialEq cannot discharge that premise when semantic values include taint. Even after this repair, URL-data equality and arbitrary payload semantics are not silently proved.

## Runtime and WPT review

Copied `root-baseline-RUN.json` and raw JSONL record root-owned execution on the final combined map baseline: four failures, five passes, harness OK and stable recorded inputs. The failures are exactly:

- Reset registered explicit inherit with equal initial text: untainted image-set retained instead of none.
- Inherited typed literal overriding equal tainted parent: none retained instead of literal image-set.
- Unregistered equal literal override: same incorrect none.
- Universal registered equal literal override: same incorrect none.

Controls distinguish unequal initial values, literal parent, unequal override, direct attr computation and ordinary inheritance. Embedded data URLs avoid external resources. The comparison is against a calibrated equivalent literal image-set and tests computed style, not image loading. Every registration name is unique and cleanup removes the fixture nodes.

The existing attr-security WPT covers direct/chained/registered/unregistered taint but does not substitute for these shared equal-payload paths. `METADATA.json` records local expectation files as configuration only; absence never proves a current pass. Suggested root regression gate: this nine-case test, existing attr-security, and current registered-property/defaulting/animation taint tests already maintained in the project. Candidate compilation, formatting/lint and exact paired browser execution remain open.

## Known context and inspected surface

Bug 1997340 introduced taint tracking; bug 1997583 implemented partial URL-use taint handling and is now resolved. Their bounded fetched histories are retained. These equality shortcuts fit that feature area, but the reviewed descriptions do not establish an existing exact duplicate. No novelty claim or exhaustive duplicate search is made. Existing project animation/defaulting fixes are separate paths, not credited to this candidate.

Inspected: complete map, both equality implementations, cascade seeding/custom declaration admission/application, substitution/wrapper taint conversion, URL rejection, image-set string provider, direct insert/remove routing, and selected style-query/animation equality consumers. Not exhaustively inspected: all implicit derived PartialEq callsites, all animation equality semantics, URL-base metadata, scheduler/lifecycle/registration epochs, resource fetching, or every custom-property consumer. The exact local two-site proposal does not need those broader equivalence claims.
