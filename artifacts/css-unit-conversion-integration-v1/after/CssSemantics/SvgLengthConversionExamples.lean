import CssSemantics.UnitConversion

namespace CssSemantics.SvgLengthConversionExamples

open UnitConversion

inductive Unit where
  | px
  | percentage
  deriving DecidableEq, Repr

def viewport (width : Rat) : Unit → Rat
  | .px => 1
  | .percentage => width / 100

theorem stale_source_witness :
    convert (viewport 200) ⟨.percentage, 50⟩ .px = some ⟨.px, 100⟩ ∧
    convert (viewport 400) ⟨.percentage, 50⟩ .px = some ⟨.px, 200⟩ ∧
    ¬ Preserves (viewport 400) ⟨.percentage, 50⟩ .px ⟨.px, 100⟩ := by
  unfold Preserves
  decide +kernel

theorem stale_target_witness :
    viewport 200 .px = viewport 400 .px ∧
    convert (viewport 200) ⟨.px, 100⟩ .percentage = some ⟨.percentage, 50⟩ ∧
    convert (viewport 400) ⟨.px, 100⟩ .percentage = some ⟨.percentage, 25⟩ ∧
    ¬ Preserves (viewport 400) ⟨.px, 100⟩ .percentage ⟨.percentage, 50⟩ := by
  unfold Preserves
  decide +kernel

theorem stale_identity_preserves :
    convert (viewport 200) ⟨.percentage, 50⟩ .percentage = some ⟨.percentage, 50⟩ ∧
    Preserves (viewport 400) ⟨.percentage, 50⟩ .percentage ⟨.percentage, 50⟩ ∧
    denote (viewport 400) ⟨.percentage, 50⟩ = 200 := by
  unfold Preserves
  decide +kernel

theorem identity_at_zero_basis :
    convert (viewport 0) ⟨.percentage, 50⟩ .percentage = some ⟨.percentage, 50⟩ ∧
    convert (viewport 0) ⟨.px, 100⟩ .percentage = none := by
  decide +kernel

theorem future_context_not_preserved :
    convert (viewport 400) ⟨.percentage, 50⟩ .px = some ⟨.px, 200⟩ ∧
    ¬ Preserves (viewport 200) ⟨.percentage, 50⟩ .px ⟨.px, 200⟩ := by
  unfold Preserves
  decide +kernel

local instance {U : Type} [DecidableEq U] (basis : U → Rat)
    (input output : Representation U) (target : U) :
    Decidable (Preserves basis input target output) :=
  inferInstanceAs (Decidable (output.unit = target ∧ denote basis output = denote basis input))

def checks : List (String × Bool) := [
  ("SVG unit conversion stale source loses current meaning", decide (
    convert (viewport 200) ⟨.percentage, 50⟩ .px = some ⟨.px, 100⟩ ∧
    convert (viewport 400) ⟨.percentage, 50⟩ .px = some ⟨.px, 200⟩ ∧
    ¬ Preserves (viewport 400) ⟨.percentage, 50⟩ .px ⟨.px, 100⟩)),
  ("SVG unit conversion stale destination loses current meaning", decide (
    viewport 200 .px = viewport 400 .px ∧
    convert (viewport 200) ⟨.px, 100⟩ .percentage = some ⟨.percentage, 50⟩ ∧
    convert (viewport 400) ⟨.px, 100⟩ .percentage = some ⟨.percentage, 25⟩ ∧
    ¬ Preserves (viewport 400) ⟨.px, 100⟩ .percentage ⟨.percentage, 50⟩)),
  ("SVG unit conversion identity preserves current meaning", decide (
    convert (viewport 200) ⟨.percentage, 50⟩ .percentage = some ⟨.percentage, 50⟩ ∧
    Preserves (viewport 400) ⟨.percentage, 50⟩ .percentage ⟨.percentage, 50⟩ ∧
    denote (viewport 400) ⟨.percentage, 50⟩ = 200)),
  ("SVG unit conversion zero basis identity boundary", decide (
    convert (viewport 0) ⟨.percentage, 50⟩ .percentage = some ⟨.percentage, 50⟩ ∧
    convert (viewport 0) ⟨.px, 100⟩ .percentage = none)),
  ("SVG unit conversion future context is not invariant", decide (
    convert (viewport 400) ⟨.percentage, 50⟩ .px = some ⟨.px, 200⟩ ∧
    ¬ Preserves (viewport 200) ⟨.percentage, 50⟩ .px ⟨.px, 200⟩))]

example : checks.all Prod.snd = true := by decide +kernel

end CssSemantics.SvgLengthConversionExamples
