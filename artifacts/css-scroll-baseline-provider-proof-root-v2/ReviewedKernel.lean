import Std
namespace ProviderReview
def clamp (outer x : Int) : Int := max 0 (min outer x)
def project (first : Bool) (outer inner border baseline : Int) : Int :=
  let start := clamp outer (border + if first then baseline else inner - baseline)
  if first then start else outer - start
theorem clamp_range (outer x : Int) (h : 0 ≤ outer) :
    0 ≤ clamp outer x ∧ clamp outer x ≤ outer := by
  unfold clamp
  omega
theorem result_range (first : Bool) (outer inner border baseline : Int)
    (h : 0 ≤ outer) :
    0 ≤ project first outer inner border baseline ∧
    project first outer inner border baseline ≤ outer := by
  have hc := clamp_range outer (border + if first then baseline else inner - baseline) h
  cases first <;> simp [project] at * <;> omega
theorem last_orientation (outer inner border baseline : Int) :
    project false outer inner border baseline =
    outer - clamp outer (border + inner - baseline) := by
  have h : border + (inner - baseline) = border + inner - baseline := by omega
  simp [project, h]
theorem first_preservation (outer inner border baseline : Int) :
    project true outer inner border baseline = clamp outer (border + baseline) := by
  simp [project]
theorem inner_conversion_bound (inner baseline : Int)
    (hi : 0 ≤ inner ∧ inner ≤ 2147483647)
    (hb : -2147483648 ≤ baseline ∧ baseline ≤ 2147483647) :
    -2147483647 ≤ inner - baseline ∧ inner - baseline ≤ 4294967295 := by omega
theorem translated_bound (inner border baseline : Int)
    (hi : 0 ≤ inner ∧ inner ≤ 2147483647)
    (hb : -2147483648 ≤ baseline ∧ baseline ≤ 2147483647)
    (hr : -2147483648 ≤ border ∧ border ≤ 2147483647) :
    -4294967295 ≤ border + (inner - baseline) ∧
    border + (inner - baseline) ≤ 6442450942 := by omega
theorem final_subtraction_bound (outer value : Int)
    (ho : 0 ≤ outer ∧ outer ≤ 2147483647)
    (hv : 0 ≤ value ∧ value ≤ outer) :
    0 ≤ outer - value ∧ outer - value ≤ 2147483647 := by omega
theorem equal_box_end_border (inner startBorder endBorder baseline : Int)
    (_ho : 0 ≤ inner + startBorder + endBorder)
    (hinside : 0 ≤ startBorder + inner - baseline ∧
      startBorder + inner - baseline ≤ inner + startBorder + endBorder) :
    project false (inner + startBorder + endBorder) inner startBorder baseline =
    baseline + endBorder := by
  rw [last_orientation]
  unfold clamp
  omega
theorem unequal_box_refutes_end_border :
    project false 100 200 9 12 = 0 ∧ clamp 100 (11 + 12) = 23 := by decide
theorem last_outer_start_clamp : project false 100 200 9 300 = 100 := by decide
theorem last_outer_end_clamp : project false 100 200 9 (-50) = 0 := by decide
theorem signed_min_baseline_safe : project false 2147483647 2147483647 2147483647 (-2147483648) = 0 := by decide
end ProviderReview
#print axioms ProviderReview.clamp_range
#print axioms ProviderReview.result_range
#print axioms ProviderReview.last_orientation
#print axioms ProviderReview.first_preservation
#print axioms ProviderReview.inner_conversion_bound
#print axioms ProviderReview.translated_bound
#print axioms ProviderReview.final_subtraction_bound
#print axioms ProviderReview.equal_box_end_border
#print axioms ProviderReview.unequal_box_refutes_end_border
#print axioms ProviderReview.last_outer_start_clamp
#print axioms ProviderReview.last_outer_end_clamp
#print axioms ProviderReview.signed_min_baseline_safe
