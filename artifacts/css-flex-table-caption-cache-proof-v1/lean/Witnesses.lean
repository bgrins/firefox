import Pipeline
namespace CaptionCache

def tableInput (basis : Int) : Input Unit := ⟨(),⟨240,basis⟩⟩
def tableOutput (a : Input Unit) : Int := a.containingBlock.blockSize / 2 + 20

theorem original_aliases_growing_and_shrinking_basis :
    original (tableInput 200) (tableInput 300) = true ∧
    original (tableInput 300) (tableInput 200) = true ∧
    candidate (tableInput 200) (tableInput 300) = false ∧
    candidate (tableInput 300) (tableInput 200) = false := by decide +kernel

theorem old_two_stage_failure :
    observe (reusableFinal 120)
      (measure true false (original (tableInput 200) (tableInput 300)) 120 170) 120 170 = 120 ∧
    observe (reusableFinal 170)
      (measure true false (original (tableInput 300) (tableInput 200)) 170 120) 170 120 = 170 ∧
    tableOutput (tableInput 300) = 170 ∧ tableOutput (tableInput 200) = 120 := by decide +kernel

theorem repaired_two_stage_witness :
    observe (reusableFinal 120)
      (measure true false (candidate (tableInput 200) (tableInput 300)) 120 170) 120 170 = 170 ∧
    observe (reusableFinal 170)
      (measure true false (candidate (tableInput 300) (tableInput 200)) 170 120) 170 120 = 120 := by decide +kernel

def inlineOnly [DecidableEq P] (a b : Input P) : Bool :=
  original a b && decide (a.containingBlock.inlineSize = b.containingBlock.inlineSize)
def blockOnly [DecidableEq P] (a b : Input P) : Bool :=
  original a b && decide (a.containingBlock.blockSize = b.containingBlock.blockSize)

theorem each_basis_component_matters :
    inlineOnly (tableInput 200) (tableInput 300) = true ∧
    candidate (tableInput 200) (tableInput 300) = false ∧
    blockOnly (tableInput 200) ⟨(),⟨300,200⟩⟩ = true ∧
    candidate (tableInput 200) ⟨(),⟨300,200⟩⟩ = false := by decide +kernel

theorem same_key_does_not_constrain_fresh_external_provider :
    candidate (tableInput 200) (tableInput 200) = true ∧
    observe (reusableFinal 120) (measure true false true 120 130) 120 130 ≠ 130 := by decide +kernel

end CaptionCache
