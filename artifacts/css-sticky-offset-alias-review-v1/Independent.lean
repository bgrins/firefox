import ModelMutants
namespace AliasIndependent
open OffsetEncoding OffsetSource

theorem integer_machine_no_alias (v : Int) (lo : -2147483648 ≤ v) :
    -2147483648 ≤ reserve v ∧ reserve v ≤ 2147483647 ∧ reserve v ≠ autoCode := by
  unfold reserve autoCode
  omega

theorem source_endpoint_exact (side : Nat) (basis : Int) :
    observe ⟨side,false,autoCode,basis⟩ = ⟨1073741822,side,1,1,basis⟩ := by
  simp [observe,autoCode]
  omega

theorem actual_auto_trace (side : Nat) (value basis : Int) :
    observe ⟨side,true,value,basis⟩ = ⟨autoCode,side,1,0,-1⟩ := rfl

theorem below_endpoint_full_trace (side : Nat) (v basis : Int) (h : v < autoCode) :
    observe ⟨side,false,v,basis⟩ = observeOld ⟨side,false,v,basis⟩ := by
  unfold observe observeOld autoCode at *
  simp only [Bool.false_eq_true,↓reduceIte]
  congr 1
  omega

theorem intended_resolution_loss (v : Int) (hi : v ≤ autoCode) :
    v-reserve v = (if v=autoCode then 1 else 0) := by
  unfold reserve autoCode at *
  split <;> omega

theorem clamping_is_idempotent (v : Int) : reserve (reserve v) = reserve v := by
  unfold reserve
  omega

theorem zero_and_negative_remain_numeric :
    decode (observe ⟨3,false,0,1073741823⟩).value = some 0 ∧
    decode (observe ⟨2,false,minimum,0⟩).value = some minimum := by decide +kernel

theorem explicit_vs_auto_are_distinct :
    observe ⟨0,false,autoCode,0⟩ ≠ observe ⟨0,true,autoCode,0⟩ := by decide +kernel

theorem negative_outside_range_preserved :
    reserve (-2147483648) = -2147483648 := by decide +kernel

theorem upper_bound_is_required :
    (autoCode+1)-reserve (autoCode+1) = 2 := by decide +kernel

end AliasIndependent
