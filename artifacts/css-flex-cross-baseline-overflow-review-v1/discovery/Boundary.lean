import Std
namespace FlexCrossBoundary

def L : Int := 1073741823
def signed32 (x : Int) : Prop := -2147483648 ≤ x ∧ x ≤ 2147483647
instance (x : Int) : Decidable (signed32 x) := inferInstanceAs (Decidable (_ ∧ _))

theorem providers_and_each_subtraction_fit :
    signed32 L ∧ signed32 (-L) ∧ signed32 (L - (-L)) ∧ signed32 (L - L) := by
  decide +kernel

theorem cross_group_sum_overflows :
    ¬ signed32 (max (-L) L + max (L - (-L)) (L - L)) := by
  decide +kernel

theorem smaller_provider_control :
    signed32 (max (-700000000) 700000000 +
      max (700000000 - (-700000000)) (700000000 - 700000000)) := by
  decide +kernel

theorem paired_component_bounds_suffice (a b : Int)
    (ha : -L ≤ a ∧ a ≤ L) (hb : -L ≤ b ∧ b ≤ L) : signed32 (a + b) := by
  unfold signed32 L at *
  omega

#print axioms providers_and_each_subtraction_fit
#print axioms cross_group_sum_overflows
#print axioms smaller_provider_control
#print axioms paired_component_bounds_suffice
end FlexCrossBoundary
