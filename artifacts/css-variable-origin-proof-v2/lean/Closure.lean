import Normalization
import Repair
import EmbeddedScan
import FastPaths

namespace VariableOrigin

theorem constructor_consumer_safety (base : Nat) (padding : List Char) (tree : Component)
    (valid : ValidHeaders tree) (provider : ReferenceSpan → Except Unit Piece)
    (separator : Nat → Bool) (collectTaint : Bool) (result : Output)
    (success : nativeDispatch (normalizedConstructor base padding tree).1 provider separator
      0 (byteLength (render tree)) (outerSpans tree) collectTaint = .ok result) :
    (normalizedConstructor base padding tree).2 = layout tree ∧
    ScanSafe (normalizedConstructor base padding tree).1 0 (byteLength (render tree)) (outerSpans tree) ∧
    (∀ r ∈ referenceSpans tree, ∀ p, r.fallback = some p →
      ∃ body, byteSlice (render tree) p (r.stop - 1) = render body ∧
        ScanSafe (render body) 0 (byteLength (render body)) (outerSpans body) ∧
        ScanSafe (render tree) p (r.stop - 1) ((outerSpans body).map (spanShift p))) ∧
    OutputSafe result := by
  refine ⟨by simp [normalizedConstructor,collected_common_origin],constructed_chunk_scan tree valid,?_,?_⟩
  · intro r hr p hp
    obtain ⟨body,occurs,hv⟩ := constructed_fallback_occurrence tree valid r hr p hp
    have fragment := fallback_fragment _ _ _ _ occurs
    have length : p + byteLength (render body) = r.stop - 1 := by
      obtain ⟨before,after,_,hs,he⟩ := fragment
      rw [byteLength_append,hs] at he
      exact he
    refine ⟨body,fallback_slice_content _ _ _ _ occurs,constructed_chunk_scan body hv,?_⟩
    have globalScan := scan_embedding _ _ _ _ 0 (byteLength (render body)) fragment
      (outerSpans body) (constructed_chunk_scan body hv)
    simpa only [Nat.add_zero,length] using globalScan
  · exact native_dispatch_safe _ _ _ _ _ _ _ _ success

theorem byte_not_character_offset : byteLength "/*é中𐐀*/".toList = 13 ∧
    "/*é中𐐀*/".toList.length = 7 := by decide

theorem skipped_comment_changes_source :
    stripLeading " /*é中𐐀*/var(--v)".toList ≠ "var(--v)".toList := by decide

theorem omitted_reset_changes_first_token :
    "var(--v)".toList.drop 4 = "--v)".toList ∧
    "--v)".toList ≠ render (.leafReference "var(--v)".toList) := by decide

theorem empty_fallback_nonvacuous :
    ∃ body, byteSlice (render (.reference "var(--missing,".toList (.text []) [')']))
      14 14 = render body ∧
      ScanSafe (render body) 0 (byteLength (render body)) (outerSpans body) := by
  exact ⟨.text [],rfl,constructed_chunk_scan (.text []) trivial⟩

theorem lookahead_same_epoch (seen first later : Bool) :
    ((seen || first) || first) || later = (seen || first) || later := by
  cases seen <;> cases first <;> cases later <;> rfl

end VariableOrigin
