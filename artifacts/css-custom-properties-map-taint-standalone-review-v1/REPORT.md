# Standalone test dependency addendum

This addendum preserves the sealed independent review unchanged. It checks source dependency of its exact nine-case WPT, not an upstream browser execution or a general substitution-provider theorem. Root separately owns patch application and runtime verification.

## Earlier repairs

- **72, registered invalid inheritance:** `fix72.patch` and complete `pre72-cascade.rs` show that the old non-inherited explicit-inherit shortcut returned early only when the parent's named reset value was absent. All three reset fixtures first establish a present parent `<string>` value, check its serialization and URL taint, and then inherit that value. The old absence condition is false. The old `Some(inherited_value)` insertion is the same relevant path; the repair's new missing-parent removal is unreachable. These are non-root children.
- **73, substituted inheritance restyling:** `fix73.patch` adds the reset-inheritance dependency flag in substituted CSS-wide keyword handling. These tests use direct `inherit`, ordinary literal strings, `attr(data-token)`, or no child declaration. They never substitute a CSS-wide inherit keyword and do not mutate ancestor values after a style flush. Direct inheritance already records its dependency. Thus these fixtures do not require the added substituted-inherit invalidation.
- **74, nearest-owner iterator:** the tests perform named `getPropertyValue` and `backgroundImage` reads, not CSSOM indexed enumeration. The standalone document registers eight names in total across the nine fixtures, with a maximum of five inherited registrations and three reset registrations; its one unregistered name exists only in its own removed fixture. No map exceeds the original own-entry threshold of eight for chain expansion. The retained original `do_insert` therefore uses ordinary copy-on-write, not a duplicate-ancestor flattening path. This reasoning assumes the exact isolated WPT document, with no injected ambient custom declarations or registrations.
- **75, live enumeration/count:** no fixture creates a custom-property tombstone, removes a declaration, or resurrects an invalid entry. All stored custom values in question are valid strings; the invalid-at-computed-value-time result is the consuming `background-image`. Replacing a present value by another present value leaves both old and corrected count updates unchanged. Tests do not call indexed CSSOM access or assert style length. The complete pre-repair map is retained as `pre74-75-map.rs`.

Accordingly, source analysis finds no dependency on repairs 72–75 for these nine cases. This is weaker than observing the same failures and fixes on upstream. The exact source patch's upstream applicability and any upstream runtime outcome are separate root gates.

## Universal shortcut admission

The complete reviewed `cascade_custom_property` calls `value_may_affect_style` before calculating `has_references`. Its universal-value comparison has no reference-free guard. The proposed repair compares existing **outer** taint with the incoming declaration's `is_attr_tainted()` and retains the existing CSS-text comparison. It repairs metadata-sensitive no-op decisions; it does not prove that equality implies interchangeable providers for every declaration containing references, relative units, or arbitrary context dependencies.

The two universal failing fixtures use a reference-free literal child string. The existing parent value is a completed `attr()` substitution with equal text and outer taint. That is the discriminating admitted domain here. No universal declaration-provider refinement is claimed; adding a reference guard without a separate counterexample would broaden this patch and is not recommended by this review.

## Replay evidence

`REPLAY.json` records a clean copied-source execution of the sealed review checker (42 inputs, 26 full source bindings, exact two-site patch, retained root four failures/five controls). Appending one LF to the copied patch is rejected. The temporary copied capsule was removed after retaining stdout/stderr and identities. No native compiler, browser, Git or WPT command was run. The sealed review's hashes are retained in `reviewed-source-pins.json`.
