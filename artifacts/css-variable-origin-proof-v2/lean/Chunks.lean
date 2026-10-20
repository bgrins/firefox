import Slices

namespace VariableOrigin

def outerSpans : Component → List ReferenceSpan
  | .text _ => []
  | .leafReference s => [⟨0, byteLength s, none⟩]
  | .pair a b => outerSpans a ++ (outerSpans b).map (spanShift (byteLength (render a)))
  | .block a b _ => (outerSpans b).map (spanShift (byteLength a))
  | .reference a b c => [⟨0, byteLength (a ++ render b ++ c), some (byteLength a)⟩]

theorem outer_mem_all (tree : Component) (s : ReferenceSpan)
    (h : s ∈ outerSpans tree) : s ∈ referenceSpans tree := by
  induction tree generalizing s with
  | text _ => simpa [outerSpans] using h
  | leafReference _ => exact h
  | pair a b ia ib =>
      simp only [outerSpans, List.mem_append] at h
      simp only [referenceSpans, List.mem_append]
      rcases h with h | h
      · exact Or.inl (ia s h)
      · obtain ⟨q,hq,rfl⟩ := List.mem_map.mp h
        exact Or.inr (List.mem_map.mpr ⟨q,ib q hq,rfl⟩)
  | block a b c ih =>
      obtain ⟨q,hq,rfl⟩ := List.mem_map.mp h
      exact List.mem_map.mpr ⟨q,ih q hq,rfl⟩
  | reference a b c ih =>
      simp only [outerSpans, List.mem_singleton] at h
      subst s
      exact List.mem_cons_self

def Separated (a b : ReferenceSpan) : Prop := a.stop ≤ b.start

theorem shifted_separated (delta : Nat) (rs : List ReferenceSpan)
    (h : rs.Pairwise Separated) : (rs.map (spanShift delta)).Pairwise Separated := by
  exact h.map (spanShift delta) (by
    intro a b hab
    simp only [Separated,spanShift] at *
    omega)

theorem outer_separated (tree : Component) : (outerSpans tree).Pairwise Separated := by
  induction tree with
  | text _ => simp [outerSpans]
  | leafReference _ => simp [outerSpans]
  | reference _ _ _ _ => simp [outerSpans]
  | block a b c ih => exact shifted_separated _ _ ih
  | pair a b ia ib =>
      apply List.pairwise_append.mpr
      refine ⟨ia, shifted_separated _ _ ib, ?_⟩
      intro x hx y hy
      obtain ⟨q,hq,rfl⟩ := List.mem_map.mp hy
      have hb := boundary_le (span_boundaries a x (outer_mem_all a x hx)).2.1
      simp only [Separated,spanShift]
      omega

def ScanSafe (text : List Char) (cursor limit : Nat) : List ReferenceSpan → Prop
  | [] => SliceWitness text cursor limit
  | r :: rs => SliceWitness text cursor r.start ∧
      SliceWitness text r.start r.stop ∧ ScanSafe text r.stop limit rs

theorem ordered_scan_safe (text : List Char) (rs : List ReferenceSpan)
    (cursor limit : Nat) (hc : Boundary text cursor) (hl : Boundary text limit)
    (cl : cursor ≤ limit)
    (bounds : ∀ r ∈ rs, Boundary text r.start ∧ Boundary text r.stop ∧
      cursor ≤ r.start ∧ r.start ≤ r.stop ∧ r.stop ≤ limit)
    (ordered : rs.Pairwise Separated) : ScanSafe text cursor limit rs := by
  induction rs generalizing cursor with
  | nil => exact boundaries_make_slice _ _ _ hc hl cl
  | cons r rs ih =>
      obtain ⟨hs,he,hcs,hse,hel⟩ := bounds r (by simp)
      obtain ⟨hnext,htail⟩ := List.pairwise_cons.mp ordered
      refine ⟨boundaries_make_slice _ _ _ hc hs hcs,
        boundaries_make_slice _ _ _ hs he hse, ih r.stop he hel ?_ htail⟩
      intro s hmem
      obtain ⟨hs,he,_,hse,hel⟩ := bounds s (by simp [hmem])
      exact ⟨hs,he,hnext s hmem,hse,hel⟩

theorem constructed_chunk_scan (tree : Component) (valid : ValidHeaders tree) :
    ScanSafe (render tree) 0 (byteLength (render tree)) (outerSpans tree) := by
  apply ordered_scan_safe _ _ _ _ (boundary_zero _) (boundary_end _) (Nat.zero_le _)
  · intro r hr
    have mem := outer_mem_all tree r hr
    obtain ⟨hs,he,_⟩ := span_boundaries tree r mem
    exact ⟨hs,he,Nat.zero_le _, Nat.le_of_lt (spans_ordered tree valid r mem).1,
      boundary_le he⟩
  · exact outer_separated tree

end VariableOrigin
