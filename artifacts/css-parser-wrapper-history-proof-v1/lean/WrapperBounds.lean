import WrapperEntry
set_option autoImplicit false
namespace WrapperBounds
open PublicCache WrapperWhitespace

theorem unit_bound (xs : List Byte) (u : WrapperWhitespace.Unit) (h : nativeUnit xs=some u) : u.count≤xs.length := by
 rw [unit_refines] at h
 unfold referenceUnit at h
 split at h
 · cases h; simp
 · cases h; simp
 · cases h; simp
 · cases h; simp
 · cases h; simp
 · cases h; simp
 · rename_i tail
   cases h
   have hb := CommentScan.consumed_bound tail
   rw [CommentScan.scan_reference] at hb
   simp only [List.length_cons]
   omega
 · contradiction

theorem run_bounds (bytes : List Byte) (fuel : Nat) (s : State)
 (hs : s.cursor.position≤bytes.length) :
 s.cursor.position≤(run bytes fuel s).cursor.position ∧
 (run bytes fuel s).cursor.position≤bytes.length := by
 induction fuel generalizing s with
 | zero => exact ⟨Nat.le_refl _,hs⟩
 | succ fuel ih =>
   simp only [run]
   split
   · exact ⟨Nat.le_refl _,hs⟩
   · rename_i u hu
     have bound := unit_bound _ _ hu
     simp only [List.length_drop] at bound
     have next : (advance u s).cursor.position≤bytes.length := by simp only [advance]; omega
     have rest := ih _ next
     have first : s.cursor.position≤(advance u s).cursor.position := by simp [advance]
     exact ⟨Nat.le_trans first rest.1,rest.2⟩

theorem pending_cursor_bound (length : Nat) (read : Nat → Lexeme) (names : List (List Byte))
 (fuel : Nat) (stack : List Block) (s : State) (hs : s.cursor.position≤length)
 (hb : ∀ p, p<length → (read p).cursor.position≤length) :
 (PublicCleanup.run length read names fuel stack s).state.cursor.position≤length := by
 induction fuel generalizing stack s with
 | zero => exact hs
 | succ fuel ih =>
   simp only [PublicCleanup.run]
   split
   · exact hs
   · rename_i hd
     apply ih
     change (read s.cursor.position).cursor.position ≤ length
     apply hb
     simp [PublicCleanup.done] at hd
     omega

theorem skip_bound (bytes : List Byte) (read : Nat → Lexeme) (names : List (List Byte))
 (s : State) (hs : s.cursor.position≤bytes.length)
 (hb : ∀ p, p<bytes.length → (read p).cursor.position≤bytes.length) :
 (WrapperSkip.native bytes read names s).state.cursor.position≤bytes.length := by
 apply (run_bounds _ _ _ _).2
 unfold PublicCleanup.pending
 split
 · exact hs
 · exact pending_cursor_bound _ _ _ _ _ _ hs hb

end WrapperBounds
