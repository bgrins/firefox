import Intervals

namespace VariableOrigin

theorem bytes_zero_empty (text : List Char) (h : byteLength text = 0) : text = [] := by
  cases text with
  | nil => rfl
  | cons c cs =>
      have hc := Char.utf8Size_pos c
      simp only [byteLength] at h
      omega

def SliceWitness (text : List Char) (start stop : Nat) : Prop :=
  ∃ before inside after, text = before ++ inside ++ after ∧
    byteLength before = start ∧ byteLength (before ++ inside) = stop

theorem boundaries_make_slice (text : List Char) (start stop : Nat)
    (hs : Boundary text start) (he : Boundary text stop) (order : start ≤ stop) :
    SliceWitness text start stop := by
  obtain ⟨a,b,hab,ha⟩ := hs
  obtain ⟨c,d,hcd,hc⟩ := he
  have eq : a ++ b = c ++ d := hab.symm.trans hcd
  rcases List.append_eq_append_iff.mp eq with ⟨m,hc',hb'⟩ | ⟨m,ha',hd'⟩
  · refine ⟨a,m,d,?_,ha,?_⟩
    · simpa [hb', List.append_assoc] using hab
    · simpa [hc'] using hc
  · have hm : byteLength m = 0 := by
      rw [ha',byteLength_append] at ha
      omega
    have empty := bytes_zero_empty m hm
    subst m
    simp only [List.append_nil] at ha'
    subst a
    exact ⟨c,[],d,by simpa using hcd,ha,by simpa using hc⟩

theorem constructed_reference_slice (tree : Component) (valid : ValidHeaders tree)
    (r : ReferenceSpan) (hr : r ∈ referenceSpans tree) :
    SliceWitness (render tree) r.start r.stop := by
  obtain ⟨hs,he,_⟩ := span_boundaries tree r hr
  exact boundaries_make_slice _ _ _ hs he (Nat.le_of_lt (spans_ordered tree valid r hr).1)

theorem fallback_end_boundary (tree : Component) (valid : ValidHeaders tree)
    (r : ReferenceSpan) (hr : r ∈ referenceSpans tree) (p : Nat)
    (hp : r.fallback = some p) : Boundary (render tree) (r.stop - 1) := by
  induction tree generalizing r p with
  | text chars => simp [referenceSpans] at hr
  | leafReference chars =>
      simp only [referenceSpans, List.mem_singleton] at hr
      subst r
      contradiction
  | pair a b ia ib =>
      simp only [referenceSpans, List.mem_append] at hr
      rcases hr with hr | hr
      · exact boundary_left _ (ia valid.1 r hr p hp)
      · obtain ⟨q,hq,rfl⟩ := List.mem_map.mp hr
        cases hf : q.fallback with
        | none => simp [spanShift,hf] at hp
        | some k =>
          have hb := boundary_right (render a) (ib valid.2 q hq k hf)
          have ho := (spans_ordered b valid.2 q hq).1
          have eq : byteLength (render a) + (q.stop - 1) =
              (spanShift (byteLength (render a)) q).stop - 1 := by
            simp only [spanShift]
            omega
          simpa only [render,eq] using hb
  | block a b c ih =>
      obtain ⟨q,hq,rfl⟩ := List.mem_map.mp hr
      cases hf : q.fallback with
      | none => simp [spanShift,hf] at hp
      | some k =>
          have hb := boundary_left c (boundary_right a (ih valid q hq k hf))
          have ho := (spans_ordered b valid q hq).1
          have eq : byteLength a + (q.stop - 1) =
              (spanShift (byteLength a) q).stop - 1 := by
            simp only [spanShift]
            omega
          simpa only [render,eq] using hb
  | reference a b c ih =>
      simp only [referenceSpans, List.mem_cons] at hr
      rcases hr with rfl | hr
      · obtain ⟨_,hc,_⟩ := valid
        subst c
        have hb := boundary_left [')'] (boundary_end (a ++ render b))
        have hc : ')'.utf8Size = 1 := rfl
        simpa [render,byteLength,hc] using hb
      · obtain ⟨q,hq,rfl⟩ := List.mem_map.mp hr
        cases hf : q.fallback with
        | none => simp [spanShift,hf] at hp
        | some k =>
            have hb := boundary_left c (boundary_right a (ih valid.2.2 q hq k hf))
            have ho := (spans_ordered b valid.2.2 q hq).1
            have eq : byteLength a + (q.stop - 1) =
                (spanShift (byteLength a) q).stop - 1 := by
              simp only [spanShift]
              omega
            simpa only [render,eq] using hb

theorem constructed_fallback_slice (tree : Component) (valid : ValidHeaders tree)
    (r : ReferenceSpan) (hr : r ∈ referenceSpans tree) (p : Nat)
    (hp : r.fallback = some p) : SliceWitness (render tree) p (r.stop - 1) := by
  obtain ⟨_,_,hf⟩ := span_boundaries tree r hr
  have ho := ((spans_ordered tree valid r hr).2 p hp).2
  exact boundaries_make_slice _ _ _ (hf p hp)
    (fallback_end_boundary tree valid r hr p hp) (by omega)

end VariableOrigin
