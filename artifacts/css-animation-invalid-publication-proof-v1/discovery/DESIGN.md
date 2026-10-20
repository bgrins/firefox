# Minimal native design

Root owns implementation. This document is a source review of the proposed three-file boundary.

## Representation

Add an internal `CustomDeclarationValue::GuaranteedInvalid` unit variant marked `#[css(skip)]`. Only uncomputing an inner-None custom animation value produces it. No parser syntax exposes it. `CustomAnimatedValue::from_declaration` maps it to inner `None` while still returning outer `Some` and preserving the declaration name. `to_declaration` maps inner `None` to this variant; its Some arm stays unchanged.

`style_derive/to_css.rs::derive_variant_arm` returns `Ok(())` without writing for a skipped variant. `style_derive/to_typed.rs::derive_variant_arm` returns `Err(())` for that variant in this mixed enum. Consequently GIV is not accidentally exported as a fabricated CSS keyword or a valid empty unparsed token stream. The serialization is intentionally lossy: an empty serialized string cannot be reparsed to recover GIV. `Servo_AnimationValue_Serialize` uncomputes and serializes a single declaration; `Servo_AnimationValue_Uncompute` retains the internal declaration itself. Current source uses internal declarations for recascade, not a serialize/reparse bridge. Typed OM's complete externally observable behavior is outside this bounded review; it should not be described as a new proven API contract.

## Cascade

The new variant has no references. After normal priority/revert/seen guards, mark it seen and call `substitution_functions.remove_var(registration,name)`. This must not run the Initial or Unset shortcuts and must suppress lower-priority declarations, just as a winning computed value would.

`value_may_affect_style` may conservatively return true for GuaranteedInvalid. In its final exhaustive match add an arm that does no early return; the existing final true is sufficient. If optimized later, returning false is valid only when the selected map already lacks a value; that optimization is unnecessary for the repair.

`remove_var` dispatches to `ComputedCustomProperties::remove`, selecting inherited/noninherited by the current registration, then `CustomPropertiesMap::remove`. Removal inserts None as an override; it does not expose an ancestor value. `Inner::insert` decrements live count only for Some→None; `get` observes the tombstone before any parent. Shared-map dedup permits None/None and otherwise performs the removal. It neither reinserts the registration initial nor alters the other inheritance map.

Searchfox's complete `CustomDeclarationValue` text search found exhaustive production matches in the three edited files only. Current source snapshots include the derive providers and map implementation. Generated match/derive compilation still needs the root build; this source inventory is not a compiler guarantee.

## Rejected alternatives

| Alternative | Why insufficient |
|---|---|
| Continue using Initial | Registered initial can be non-GIV, as reproduced. |
| Use Inherit or Unset | Depends on parent/inheritance flag; cannot represent arbitrary selected underlying GIV. |
| Drop the declaration | Exposes the prior cascade/underlying/initial value rather than publishing GIV. |
| Empty Unparsed/Universal value | Valid empty tokens differ from GIV; var fallback would not be selected. |
| Artificial unresolved variable | Introduces a dependency and name-resolution/registration behavior into a computed-value representation. |
| Fix only endpoint construction | Neutral endpoints can supply the same legitimate GIV independently. |

## Expected control impact and boundaries

Some computed values, ordinary CSS-wide Initial/Inherit/Unset, parser-produced declarations and unresolved-variable computation remain on existing branches. Outer absence remains unchanged. Universal values with non-GIV initial exercise the new behavior; unregistered/initial-GIV cases should remain observationally unchanged. No global payload equality, map dedup, arithmetic, sampling or scheduling change is needed.

A stable registration is sufficient for this defect and design. A stale typed value under a changed registration requires separate constructor/scheduling evidence; the new variant alone does not prove registration-epoch coherence. Root will prepare a dedicated patch and WPT, with discovery/proof evidence preceding the native commit.
