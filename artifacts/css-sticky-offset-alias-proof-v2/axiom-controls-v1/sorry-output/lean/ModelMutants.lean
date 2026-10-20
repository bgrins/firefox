import OffsetSource

namespace ModelMutants
open OffsetSource OffsetEncoding

def observe (mode : Nat) (input : Input) : Observation :=
  let original := OffsetSource.observe input
  match mode with
  | 1 => if input.automatic then { original with value := autoCode - 1 } else original
  | 2 => if input.automatic then original else { original with value := max (autoCode - 1) input.resolved }
  | 3 => if input.automatic then original else { original with value := min (autoCode - 2) input.resolved }
  | 4 => if input.automatic then original else { original with value := max 0 original.value }
  | 5 => ⟨7 + Int.ofNat ((input.side + 1) % 4), (input.side + 1) % 4, 1, 1, input.basis⟩
  | _ => original

theorem auto_branch_witness :
    observe 1 ⟨0, true, 0, 0⟩ ≠ OffsetSource.observe ⟨0, true, 0, 0⟩ := by decide +kernel

theorem maximum_witness :
    observe 2 ⟨0, false, 0, 0⟩ ≠ OffsetSource.observe ⟨0, false, 0, 0⟩ := by decide +kernel

theorem two_units_witness :
    observe 3 ⟨0, false, autoCode - 1, 0⟩ ≠ OffsetSource.observe ⟨0, false, autoCode - 1, 0⟩ := by decide +kernel

theorem negative_witness :
    observe 4 ⟨0, false, -1, 0⟩ ≠ OffsetSource.observe ⟨0, false, -1, 0⟩ := by decide +kernel

theorem side_witness :
    observe 5 ⟨0, false, 0, 0⟩ ≠ OffsetSource.observe ⟨0, false, 0, 0⟩ := by decide +kernel

end ModelMutants
