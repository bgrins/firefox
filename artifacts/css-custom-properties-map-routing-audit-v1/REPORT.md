# Custom-property map routing and metadata audit

## Disposition

Two distinct equality call paths justify a nine-case browser diagnostic. They are source-derived candidates, not reproduced browser defects, security impact findings, or novelty claims. No Lean model discovered these leads. The new count and iterator repairs do not change these comparisons.

The inherited/reset name-domain audit found a coherent static invariant for ordinary full recascades. It did not find a concrete duplicate-name case. Scheduler completeness across all special contexts remains unproved.

## 1. Metadata discarded by shared-map equality

`Value<Component>::PartialEq` compares only `v`, deliberately excluding `attr_tainted` and `url_data`. For universal values, `VariableValue::PartialEq` compares only CSS text. `CustomPropertiesMap::do_insert` first tries `Arc::get_mut`; if shared, it returns immediately when `self.get(name) == value.as_ref()`. In contrast, `Inner::eq` uses `can_deduplicate_values`, which additionally compares taint. This distinction is actual source, not inference from equal serialization.

### A. Reset registration, explicit inherit, equal initial payload

1. Register `<string>`, `inherits:false`, initial string A.
2. Parent computes the same string A using `attr(data-token)` and carries taint. The proposed test first requires parent computed string A and blocked `image-set` use.
3. `Cascade::init_custom_properties` clones the registration's reset initial map, so its Arc is shared with the stylist cache.
4. The child's explicit `inherit` passes `value_may_affect_style` for a nonroot reset property. `cascade_custom_property` copies the parent's actual non-inherited value and marks `INHERITS_RESET_STYLE`.
5. `ComputedSubstitutionFunctions::insert_var` routes through `ComputedCustomProperties::insert` to the reset map. Shared `do_insert` sees equal typed string payload and can retain the untainted initial object instead of the tainted parent object.
6. Subsequent `var()` reads the retained `attr_tainted`; it feeds substitution range taint and `ParserContext::disallow_urls_in_range` / `CssUrl::parse_from_string`. The string is used as a URL through supported `image-set()`.

This is more discriminating than a direct `attr()` override. Ordinary unresolved attr declarations first insert a different universal raw expression, which can make the map unique before final typed insertion. The proposal retains that route as a disconfirming control.

### B. Equal literal override of a tainted inherited value

For inherited `<string>`, the child map starts shared with its parent's map. A literal child string equal to the parent payload is computed and inserted; shared equality may retain the parent's taint. This predicts an incorrectly blocked literal URL, rather than the missing-taint result in A.

For universal/unregistered properties, an earlier independent shortcut exists: `Cascade::value_may_affect_style` compares the existing universal `VariableValue` to the new specified value using CSS-only equality. It may skip the override before the map insertion is reached. A repair solely to `do_insert` cannot be assumed to repair that separate path.

### Normative trace

Registered properties accept explicit inheritance and strings retain their specified value; the metadata is not made irrelevant by registration. [Properties and Values API](https://drafts.css-houdini.org/css-properties-values-api-1/#specified-value-time)

Attr-derived values and their substitutions retain taint, including the equivalent tokens of registered values. Using that tainted result as a URL is invalid at computed-value time. A replacement authored as an independent literal does not derive from attr. This yields the expected blocked/unblocked distinction while keeping equal text. [CSS Values 5](https://drafts.csswg.org/css-values-5/#attr-security)

Verdict: **REACHED for the proposed normative expectation; runtime implementation outcome remains untested by this audit.**

## 2. URL metadata: no demonstrated defect

The ignored `url_data` field is retained for uncomputation. This audit does not equate different definition origins with different required results. Unregistered URL tokens resolve at their use site, while registered `<url>` computed values already resolve their URL. The selected sources and limited trace do not establish a consumer that observes an incorrectly retained base in the proposed cases. No URL-metadata defect or repair is proposed. [CSS Variables](https://drafts.csswg.org/css-variables/#defining-variables), [registered URL values](https://drafts.css-houdini.org/css-properties-values-api-1/#computed-value-time)

Future work would need an actual uncompute/recascade consumer and two distinct bases, preserving the typed versus universal distinction. The native TODO in `can_deduplicate_values` is a lead, not proof.

## 3. Inherited/reset routing and registration changes

At a coherent registration epoch, the following source chain supports disjoint live name domains:

- `Stylist::get_custom_property_registration` chooses the script registration first, otherwise the origin-selected stylesheet registration, otherwise unregistered descriptors.
- `rebuild_initial_values_for_custom_properties` starts with both maps empty, tracks `seen_names`, and routes each selected registration to exactly one map. Script registrations claim their names before stylesheet registrations, including registrations without a usable initial value.
- `Cascade::init_custom_properties` replaces the builder's maps: inherited values come from the current parent (root uses current registered initial inherited values); reset values come from the current initial reset map. It does not retain the target element's previous two maps.
- All normal custom-property insert/remove/get operations choose their map from the same current registration. Given a fresh parent with that registration epoch, each name remains in its designated live domain.
- `ServoStyleSet::RegisterProperty` posts a root `RecascadeSubtree` after successful registration. `Stylist::register_custom_property` updates the registry and rebuilds initial maps first. Duplicate script registration is rejected.
- For stylesheet changes, `Stylist::flush` rebuilds cascade data and initial maps. `StylesheetInvalidationSet` treats `Property(..)` as full invalidation; `process_style` marks the root subtree for restyle. The existing `at-property-stylesheets.html` checks registration addition/removal and precedence across stylesheet changes.

The relevant spec selects one document-wide registration per name, with script registration precedence. [Registration selection](https://drafts.css-houdini.org/css-properties-values-api-1/#determining-registration)

No concrete violating route was found in these inspected ordinary paths. This is a conditional source argument, not a universal temporal proof: fresh-parent ordering, skipped traversal/subtree contexts, cached styles, animations and adoption are not exhaustively audited. `ComputedCustomProperties` itself does not enforce disjointness if an arbitrary caller changes registration while retaining both old maps. That remains an admission for composed map proofs.

A future focused negative probe could flip one name's stylesheet registration inherited→reset→unregistered, and separately let a script registration override a stylesheet registration, checking named values and exactly one enumerated occurrence after each flush. No need to add a large matrix before the concrete metadata lead is adjudicated.

## 4. Probe and controls

`map-taint-equality.html` contains exactly nine identities listed in `EXPECTED-IDENTITIES.json`. All image URLs are embedded data strings. Each case calibrates literal `image-set`, checks the parent computed custom string, confirms the parent's intended taint behavior, and checks the child's token prerequisite before the final image assertion. Cases cover A, B, different initial/payload controls, universal/unregistered B, direct attr and ordinary inheritance.

The HTML and extracted JS are byte-bound. `node --check` passed. No browser was run and no preexisting test was changed. No `src()`/`string()`/`if()` support assumption is needed. No test silently skips unsupported syntax.

## 5. Coverage and known context

`attr-security.html` already covers direct, registered/unregistered and chained taint, including `image-set`; it does not establish these equal-payload map paths. Metadata files, if present, are retained as configuration context, not current pass claims. `at-property-stylesheets.html` checks registration changes without proving map-domain uniqueness for every lifecycle.

Bug 1997340 is the resolved taint implementation context (Firefox151); its comment 1 identifies additional under-permissiveness work in bug1997583. Bounded search also returned animation-related taint sync issues, which are different paths. No exhaustive duplicate search or novelty claim is made. The project ledger's registered keyframe/defaulting fixes and current count/iterator work remain separate.

## Evidence and limits

Full source snapshots and their hashes are retained. The map snapshot is the parent's exact final combined source, not a temporarily switched live file. Other source snapshots reflect this project's current changes, not Searchfox tip; source hashes distinguish them. Searchfox located the upstream functions, but the installed CLI lacks `--permalink`; no unverified revision URL is fabricated. The current Houdini editor draft was fetched directly after the CSSWG-domain alias failed. No Git operation, native build, browser run or external write was performed.

This capsule authenticates a source/spec audit and a proposed test. It is neither native acceptance nor a proof of C++/Rust, caches, style scheduling or all CSS.
