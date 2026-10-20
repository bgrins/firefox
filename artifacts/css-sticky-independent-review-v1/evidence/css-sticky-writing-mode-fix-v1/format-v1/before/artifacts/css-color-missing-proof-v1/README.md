# Missing RGB/XYZ components during color mixing

This bounded artifact covers the missing-component transfer seam in
`AbsoluteColor::carry_forward_analogous_missing_components`, for distinct
RGB/XYZ spaces. It has no color conversion matrix or floating-point model.

`Missing.lean` defines an independent CSS Color 4 category relation across
all 15 native spaces, including residual analogous sets. Its refinement theorem
is explicitly restricted to the nine RGB/XYZ spaces. All eight source masks,
three channels and arbitrary preexisting converted missing flags are quantified.
The patched branch unions the source channel mask with the converted mask.
The union preserves converted flags; it does not prove that flags produced by
conversion are themselves correct. Alpha and other flags are outside this
three-bit model and are unchanged by the authenticated native branch.

The interpolation model compares an explicit native-shaped outcome table against
an independent optional-operand copying specification, for arbitrary values.
A connecting theorem proves that a transferred missing channel copies the
present counterpart. This describes pre-interpolation operands; hue adjustment,
premultiplication, weighted arithmetic, serialization and rendering are excluded.

The full category relation retains the Lab-to-Lch residual-set counterexample as
an outstanding obligation. This patch does not repair that separate omission.
Likewise this artifact does not verify relative-color syntax, parser behavior,
`currentcolor`, same-space conversion, NaN production or powerless components.
The source bridge is manually reviewed and authenticated, not extraction or
mechanized refinement of Rust. Conversion is assumed to supply the inspected
channel flags; the unchanged conversion call preserves alpha separately.

The independent normative source is CSS Color 4, `interpolation-missing`:
https://drafts.csswg.org/css-color-4/#interpolation-missing
The source record identifies the exact archived primary document used for the
category table and residual-set definition. The exact unchanged subsection is retained in `interpolation-missing.html`,
with the W3C copyright and permissive-document-license link in `SPEC-v1.json`.
The complete original snapshot remains in the round-2 color audit.

Run `python3 materialize.py` to reconstruct authenticated old/current native
snapshots from the parent Git revision and the authenticated one-line delta. Then run `python3 check.py NEW_DIRECTORY`
for a clean Lean compilation, axiom audit, four semantic mutations, diagnostic
validator corruptions and native-source shape controls. The checker rejects
input drift and records exact commands and output hashes.

Before applying the native fix, use `check.py NEW_DIRECTORY --snapshots-only`.
That mode verifies the reconstructed candidate, explicitly reports
`live_native_verified: false`, and makes no claim about the working tree.
The default mode additionally authenticates the patched native working files. Unused-variable and unused-simp-argument linters are disabled identically for
positive and mutation compilations; their warnings must not stand in for a
failed semantic theorem. All other warnings are errors. Generated snapshots,
compiler outputs and historical discovery logs are not source files to vendor.
