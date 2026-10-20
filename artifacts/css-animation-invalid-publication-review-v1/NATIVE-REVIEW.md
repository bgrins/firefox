# Native and fixture review

## Source-first verdict

The observed behavior is specified: an animation effect selecting a computed guaranteed-invalid custom value must preserve that value through publication. Replacing it with CSS-wide `initial` changes the result when a universal registration supplies a valid explicit initial value. The original 16 fixture demonstrates this with empty expected custom serialization and 61px fallback becoming 20px. SOURCE-FIRST.md was written before reading the root design or candidate. SPEC-EXTRACTS.json retains the deciding primary-source sections and source pins.

## Candidate path

- `CustomAnimatedValue::value` already represents present semantic GIV as inner `None`; the outer animation value still exists. The original `to_declaration` replaced that inner state with `CSSWideKeyword::Initial`, causing subsequent cascade to use registered initial 20px.
- `to_declaration` now emits internal `CustomDeclarationValue::GuaranteedInvalid`. Author parsing still creates only CSS-wide or Unparsed forms; this is not new author syntax.
- `from_declaration` converts the new variant to inner `None`, then returns `Some(Self { name, value })`. It preserves outer presence instead of treating the property/effect as absent.
- `cascade_custom_property` first enforces the existing cascade/revert/seen guards. The new variant has no references; it inserts the seen entry before removing the variable. A lower-priority declaration therefore remains suppressed.
- `value_may_affect_style` gives GIV no Initial/Inherit/Unset shortcut. With an existing value it falls through to true; without one it also returns true. Repeated removal may be unnecessary, but preserves semantics and seen bookkeeping.
- `remove_var` selects the registration's inherited or non-inherited map. The map removal stores a local `None` tombstone; lookup checks local entries before parent maps. Removing the computed value therefore does not expose a parent map value. This differs from omitting the winning declaration.
- The existing ToCss derive's `css(skip)` arm returns `Ok(())` without emitting bytes. The ToTyped derive's corresponding arm returns `Err(())`. Thus the internal marker is not serialized as a new author keyword or reified as an invented typed keyword. Empty serialization alone is not proof of semantic invalidity; substitution-map behavior establishes that distinction.
- Existing Parsed, Unparsed and CSS-wide branches remain unchanged. Ordinary `initial` still requests the registered initial. Existing valid-empty Unparsed values remain present token lists, which must not trigger var fallback.

The source audit covers the retained enum/conversion/cascade code, custom-property and map adapters, animation uncompute/keyframe conversion, declaration parsing, and both derive implementations. Searchfox discovery failed with DNS resolution; the failure is retained. It is not an exhaustive whole-repository proof of every wildcard consumer. The successful native build checks the concrete changed enum against compiled consumers; browser regression results provide additional bounded evidence.

## Standalone fixture independence

The revised fixture establishes parent, target and reference GIV using an ordinary unresolved universal declaration. It does not use a direct `inherit` declaration to prepare the reset target, avoiding the earlier registered-inherit-invalid repair. Only animation endpoints use literal `inherit`; their existing `CustomAnimatedValue::from_declaration` path reads the parent's computed map directly.

The registered-keyframe-substitution repair diverts only non-universal Unparsed values to the computed keyframe map. This fixture always registers syntax `*`, so its literal-inherit endpoints, implicit underlying endpoints and unresolved-declaration control do not require that typed-provider diversion. The retained upstream conversion source has the same universal branch and CSS-wide inheritance lookup. This is static independence evidence, not an isolated upstream browser execution.

The16 tests verify registration initial 20px, parent provider, a direct GIV/valid reference, effect identity/presence, exact sampled progress, custom serialization, fallback alias and width. Ten failures reach the final observation with 20px; six initial/valid-parent/unresolved-declaration controls pass. After the candidate, all 16 pass.

## Additional test requirement and authorship

The initial failing rows also had a GIV underlying declaration. An incorrect implementation that dropped the winning animation declaration could therefore accidentally satisfy them. I authored six additive cases, preserving the original 16 HTML bytes as an exact prefix:

- Both inheritance modes with valid 44px underlying declaration overridden by a GIV animation; cancellation restores 44px.
- Both modes with 55px lower animation overridden by a later GIV animation; cancellation successively restores 55px then 44px.
- Both modes with valid empty-token animation: empty custom serialization and empty alias, but width resolves as auto to the fixed 200px container, while a GIV reference selects 61px fallback. Keyframe property retention is explicitly checked.

The lower-effect ordering follows Web Animations' effect-stack composite order and replace operation: the later script animation replaces the earlier effect. Cancellation checks expose accidental destructive state changes. These additions are reviewer-authored tests, not independently authored production fixtures. Their separate candidate receipt now confirms all six pass (FINAL-REVIEW.json); no baseline result for them is inferred from the original 16 tests.

## Landing source transfer and limitations

The native-only landing patch contains exactly three files and excludes the unrelated formatter change to `UnparsedValue::substitution_property_id`. The compiled-to-landing transfer was checked by exact known-signature substitution: line wrapping and an optional trailing parameter comma only. No identifier, type or body changes. The other two native files are byte-identical between compiled and landing snapshots.

Runtime reconciliation independently reads raw WPT rows and verifies the exact original 16 pairing. The wider 343-row candidate run compares with 308 prior fix81 rows, 19 historical animation calibration rows and 16 new baseline rows; 333 status/message pairs are unchanged. The two remaining failures are unchanged parent-mutation animation calibration failures. They are not repaired by this change.

The baseline runtime pin dictionary omits properties/mod.rs; its original bytes are separately authenticated by native_original and source snapshots. Candidate runtime pins include all three changed files. No complete scheduling/cache proof, dynamic registration proof, performance claim, release-browser impact estimate or isolated upstream build is supplied by this review.
