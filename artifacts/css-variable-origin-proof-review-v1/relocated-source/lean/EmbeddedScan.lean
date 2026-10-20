import Fallback

namespace VariableOrigin

theorem embedded_slice (text body : List Char) (base endOffset start stop : Nat)
    (fragment : ExactFragment text body base endOffset)
    (slice : SliceWitness body start stop) :
    SliceWitness text (base + start) (base + stop) := by
  obtain ⟨outerLeft,outerRight,rfl,rfl,rfl⟩ := fragment
  obtain ⟨innerLeft,inside,innerRight,rfl,rfl,rfl⟩ := slice
  exact ⟨outerLeft ++ innerLeft,inside,innerRight ++ outerRight,
    by simp [List.append_assoc],by simp,by simp [Nat.add_assoc]⟩

theorem scan_embedding (text body : List Char) (base endOffset cursor limit : Nat)
    (fragment : ExactFragment text body base endOffset) (rs : List ReferenceSpan)
    (safe : ScanSafe body cursor limit rs) :
    ScanSafe text (base+cursor) (base+limit) (rs.map (spanShift base)) := by
  induction rs generalizing cursor with
  | nil => exact embedded_slice _ _ _ _ _ _ fragment safe
  | cons r rs ih =>
      obtain ⟨prefixSafe,removedSafe,tailSafe⟩ := safe
      exact ⟨embedded_slice _ _ _ _ _ _ fragment prefixSafe,
        embedded_slice _ _ _ _ _ _ fragment removedSafe,ih _ tailSafe⟩

theorem constructed_global_fallback_scan (tree : Component) (valid : ValidHeaders tree)
    (r : ReferenceSpan) (hr : r ∈ referenceSpans tree) (p : Nat) (hp : r.fallback = some p) :
    ∃ body, byteSlice (render tree) p (r.stop - 1) = render body ∧
      ScanSafe (render tree) p (r.stop - 1) ((outerSpans body).map (spanShift p)) := by
  obtain ⟨body,occurs,hv⟩ := constructed_fallback_occurrence tree valid r hr p hp
  have fragment := fallback_fragment _ _ _ _ occurs
  have length : p + byteLength (render body) = r.stop - 1 := by
    obtain ⟨before,after,_,hs,he⟩ := fragment
    rw [byteLength_append,hs] at he
    exact he
  refine ⟨body,fallback_slice_content _ _ _ _ occurs,?_⟩
  have result := scan_embedding _ _ _ _ 0 (byteLength (render body)) fragment
    (outerSpans body) (constructed_chunk_scan body hv)
  simpa only [Nat.add_zero,length] using result

end VariableOrigin
