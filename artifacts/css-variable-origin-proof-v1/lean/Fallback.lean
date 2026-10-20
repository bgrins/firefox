import ByteSlices

namespace VariableOrigin

def ExactFragment (text body : List Char) (start stop : Nat) : Prop :=
  ∃ before after, text = before ++ body ++ after ∧
    byteLength before = start ∧ byteLength (before ++ body) = stop

theorem fragment_left (text body suffix : List Char) (start stop : Nat)
    (h : ExactFragment text body start stop) : ExactFragment (text ++ suffix) body start stop := by
  obtain ⟨before,after,rfl,rfl,rfl⟩ := h
  exact ⟨before,after ++ suffix,by simp [List.append_assoc],rfl,rfl⟩

theorem fragment_right (prefixText text body : List Char) (start stop : Nat)
    (h : ExactFragment text body start stop) :
    ExactFragment (prefixText ++ text) body (byteLength prefixText + start) (byteLength prefixText + stop) := by
  obtain ⟨before,after,rfl,rfl,rfl⟩ := h
  exact ⟨prefixText ++ before,after,by simp [List.append_assoc],by simp,by simp [Nat.add_assoc]⟩

inductive FallbackAt : Component → Nat → Nat → Component → Prop where
  | here (header : List Char) (body : Component) :
      FallbackAt (.reference header body [')']) (byteLength header)
        (byteLength header + byteLength (render body)) body
  | left (a b body : Component) (start stop : Nat) (h : FallbackAt a start stop body) :
      FallbackAt (.pair a b) start stop body
  | right (a b body : Component) (start stop : Nat) (h : FallbackAt b start stop body) :
      FallbackAt (.pair a b) (byteLength (render a) + start) (byteLength (render a) + stop) body
  | block (a c : List Char) (b body : Component) (start stop : Nat) (h : FallbackAt b start stop body) :
      FallbackAt (.block a b c) (byteLength a + start) (byteLength a + stop) body
  | nested (a c : List Char) (b body : Component) (start stop : Nat) (h : FallbackAt b start stop body) :
      FallbackAt (.reference a b c) (byteLength a + start) (byteLength a + stop) body

theorem fallback_fragment (tree body : Component) (start stop : Nat)
    (h : FallbackAt tree start stop body) : ExactFragment (render tree) (render body) start stop := by
  induction h with
  | here header body => exact ⟨header,[')'],rfl,rfl,by simp⟩
  | left a b body start stop h ih => exact fragment_left _ _ _ _ _ ih
  | right a b body start stop h ih => exact fragment_right _ _ _ _ _ ih
  | block a c b body start stop h ih => exact fragment_left _ _ _ _ _ (fragment_right _ _ _ _ _ ih)
  | nested a c b body start stop h ih => exact fragment_left _ _ _ _ _ (fragment_right _ _ _ _ _ ih)

theorem fallback_slice_content (tree body : Component) (start stop : Nat)
    (h : FallbackAt tree start stop body) : byteSlice (render tree) start stop = render body := by
  obtain ⟨before,after,eq,hs,he⟩ := fallback_fragment _ _ _ _ h
  rw [eq,← hs,← he,slice_exact]

theorem constructed_fallback_occurrence (tree : Component) (valid : ValidHeaders tree)
    (r : ReferenceSpan) (hr : r ∈ referenceSpans tree) (p : Nat) (hp : r.fallback = some p) :
    ∃ body, FallbackAt tree p (r.stop - 1) body ∧ ValidHeaders body := by
  induction tree generalizing r p with
  | text chars => simp [referenceSpans] at hr
  | leafReference chars =>
      simp only [referenceSpans,List.mem_singleton] at hr
      subst r
      contradiction
  | pair a b ia ib =>
      simp only [referenceSpans,List.mem_append] at hr
      rcases hr with hr | hr
      · obtain ⟨body,h,hv⟩ := ia valid.1 r hr p hp
        exact ⟨body,FallbackAt.left _ _ _ _ _ h,hv⟩
      · obtain ⟨q,hq,rfl⟩ := List.mem_map.mp hr
        cases hf : q.fallback with
        | none => simp [spanShift,hf] at hp
        | some k =>
            obtain ⟨body,h,hv⟩ := ib valid.2 q hq k hf
            have positive := (spans_ordered b valid.2 q hq).1
            have peq : p = byteLength (render a) + k := by simpa [spanShift,hf] using hp.symm
            have seq : (spanShift (byteLength (render a)) q).stop - 1 = byteLength (render a) + (q.stop-1) := by simp only [spanShift]; omega
            rw [peq,seq]
            exact ⟨body,FallbackAt.right _ _ _ _ _ h,hv⟩
  | block a b c ih =>
      obtain ⟨q,hq,rfl⟩ := List.mem_map.mp hr
      cases hf : q.fallback with
      | none => simp [spanShift,hf] at hp
      | some k =>
          obtain ⟨body,h,hv⟩ := ih valid q hq k hf
          have positive := (spans_ordered b valid q hq).1
          have peq : p = byteLength a + k := by simpa [spanShift,hf] using hp.symm
          have seq : (spanShift (byteLength a) q).stop - 1 = byteLength a + (q.stop-1) := by simp only [spanShift]; omega
          rw [peq,seq]
          exact ⟨body,FallbackAt.block _ _ _ _ _ _ h,hv⟩
  | reference a b c ih =>
      simp only [referenceSpans,List.mem_cons] at hr
      rcases hr with rfl | hr
      · obtain ⟨_,hc,hv⟩ := valid
        subst c
        simp only [Option.some.injEq] at hp
        subst p
        have hc : ')'.utf8Size = 1 := rfl
        simp only [byteLength_append,byteLength,hc,Nat.add_zero,Nat.add_sub_cancel]
        exact ⟨b,FallbackAt.here _ _,hv⟩
      · obtain ⟨q,hq,rfl⟩ := List.mem_map.mp hr
        cases hf : q.fallback with
        | none => simp [spanShift,hf] at hp
        | some k =>
            obtain ⟨body,h,hv⟩ := ih valid.2.2 q hq k hf
            have positive := (spans_ordered b valid.2.2 q hq).1
            have peq : p = byteLength a + k := by simpa [spanShift,hf] using hp.symm
            have seq : (spanShift (byteLength a) q).stop - 1 = byteLength a + (q.stop-1) := by simp only [spanShift]; omega
            rw [peq,seq]
            exact ⟨body,FallbackAt.nested _ _ _ _ _ _ h,hv⟩

theorem recursive_fallback_scan (tree : Component) (valid : ValidHeaders tree)
    (r : ReferenceSpan) (hr : r ∈ referenceSpans tree) (p : Nat) (hp : r.fallback = some p) :
    ∃ body, byteSlice (render tree) p (r.stop - 1) = render body ∧
      ScanSafe (render body) 0 (byteLength (render body)) (outerSpans body) := by
  obtain ⟨body,occurs,hv⟩ := constructed_fallback_occurrence tree valid r hr p hp
  exact ⟨body,fallback_slice_content _ _ _ _ occurs,constructed_chunk_scan body hv⟩

end VariableOrigin
