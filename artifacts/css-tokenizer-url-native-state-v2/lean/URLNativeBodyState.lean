import URLNativeBody
import URLNativeEscapeCut
set_option maxRecDepth 4096
set_option maxHeartbeats 8000000
namespace URLNativeBodyState
open URLNativeState URLNativeEnd URLNativeAlignment URLNativeBody
abbrev Byte := CommentScan.Byte

def observed (xs : List Byte) (r : CommentObservers.State) :=
 CommentObservers.nativeObserve (URLTrace.run xs).consumed r

theorem nonspace_metadata : ∀ b : Byte, URLScan.nativeClass b≠.space →
 CommentObservers.isNewline b=false ∧
 (URLScan.nativeClass b≠.copy → CommentObservers.nativeWidth b=1) := by decide

theorem no_newline_head (xs : List Byte) (hn : URLScan.newline xs≠true) :
 ∀ b ∈ xs.head?, CommentObservers.isNewline b=false := by
 cases xs with
 | nil => simp
 | cons b bs =>
   simp only [URLScan.newline,List.head?_cons,Option.any_some] at hn
   simpa [CommentObservers.isNewline] using hn

theorem metadata (xs : List Byte) (s : State) (r : CommentObservers.State) (block : Nat)
 (h : Related s r block) (ha : URLNativeBody.Admitted xs s) (hv : TailValid xs) :
 Related (URLNativeBody.run xs s).state (observed xs r) block := by
 induction xs,s using URLNativeBody.run.induct generalizing r with
 | case1 s => simpa [URLNativeBody.run,observed,URLTrace.run,CommentObservers.nativeObserve] using h
 | case2 b bs s hc =>
   obtain ⟨hn,hw⟩ := nonspace_metadata b (by simp [hc])
   have width := hw (by simp [hc])
   simpa [URLNativeBody.run,observed,URLTrace.run,hc,CommentObservers.nativeObserve,hn,
     CommentObservers.ordinary,width,CommentObservers.advance] using advance_related s r block 1 h
 | case3 b bs s hc =>
   obtain ⟨hn,hw⟩ := nonspace_metadata b (by simp [hc])
   have width := hw (by simp [hc])
   have hadm : URLNativeBadState.Admitted bs (advance s 1) := by simpa [URLNativeBody.Admitted,hc] using ha
   have result := bad_metadata bs (advance s 1) (CommentObservers.advance 1 r) block (advance_related s r block 1 h) hadm
   simpa [URLNativeBody.run,observed,URLTrace.run,hc,URLTrace.add,CommentObservers.nativeObserve,hn,
     CommentObservers.ordinary,width,CommentObservers.advance] using result
 | case4 b bs s hc =>
   have hadm : URLNativeEnd.Admitted (b::bs) s := by simpa [URLNativeBody.Admitted,hc] using ha
   simpa [URLNativeBody.run,observed,URLTrace.run,hc,URLNativeEnd.observed] using URLNativeEnd.metadata (b::bs) s r block h hadm
 | case5 b bs s hc ih =>
   obtain ⟨hn,hw⟩ := nonspace_metadata b (by simp [hc])
   have width := hw (by simp [hc])
   have hadm : URLNativeBody.Admitted bs (advance s 1) := by simpa [URLNativeBody.Admitted,hc] using ha
   have result := ih (CommentObservers.advance 1 r) (advance_related s r block 1 h) hadm (tail b bs hv)
   simpa [URLNativeBody.run,observed,URLTrace.run,hc,URLTrace.add,CommentObservers.nativeObserve,hn,
     CommentObservers.ordinary,width,CommentObservers.advance] using result
 | case6 b bs s hc ih =>
   have hn := (nonspace_metadata b (by simp [hc])).1
   have hadm : URLNativeBody.Admitted bs (known s b) := by simpa [URLNativeBody.Admitted,hc] using ha
   have result := ih (CommentObservers.ordinary b r) (known_related s r block b h) hadm (tail b bs hv)
   simpa [URLNativeBody.run,observed,URLTrace.run,hc,URLTrace.add,CommentObservers.nativeObserve,hn] using result
 | case7 b bs s hc hn =>
   obtain ⟨hnb,hw⟩ := nonspace_metadata b (by simp [hc])
   have width := hw (by simp [hc])
   have hadm : URLNativeBadState.Admitted bs (advance s 1) := by simpa [URLNativeBody.Admitted,hc,hn] using ha
   have result := bad_metadata bs (advance s 1) (CommentObservers.advance 1 r) block (advance_related s r block 1 h) hadm
   simpa [URLNativeBody.run,observed,URLTrace.run,hc,hn,URLTrace.add,CommentObservers.nativeObserve,hnb,
     CommentObservers.ordinary,width,CommentObservers.advance] using result
 | case8 b bs s hc hn ih =>
   have hb : b=92 := escape_byte b hc
   have hu := ascii_tail b bs hv (by rw [hb]; decide)
   have hnext := no_newline_head bs hn
   obtain ⟨units,hunits⟩ := hu
   change bs=Boundary.bytes units at hunits
   have hadm : URLNativeEscape.Admitted bs (advance s 1) ∧
     URLNativeBody.Admitted (bs.drop (Escape.native bs).count) (URLNativeEscape.run bs (advance s 1)) := by
     simpa [URLNativeBody.Admitted,hc,hn] using ha
   have he := URLNativeEscape.metadata units (advance s 1) (CommentObservers.advance 1 r) block
     (advance_related s r block 1 h) (by simpa [← hunits] using hadm.1) (by simpa [← hunits] using hnext)
   rw [← hunits] at he
   have result := ih _ he hadm.2 (escape_rest bs ⟨units,hunits⟩)
   have hcut := URLNativeEscapeCut.escape units (by simpa [← hunits] using hnext)
   rw [← hunits] at hcut
   have hcut' := URLNativeEscapeCut.take_right _ _ (URLTrace.run (bs.drop (Escape.native bs).count)).value.count hcut
   rw [← URLTrace.trace_exact] at hcut'
   dsimp only [observed] at result
   rw [← URLDelegation.observe_append _ _ _ hcut'] at result
   have hnb := (nonspace_metadata b (by simp [hc])).1
   have width := (nonspace_metadata b (by simp [hc])).2 (by simp [hc])
   simpa [URLNativeBody.run,observed,URLTrace.run,hc,hn,URLTrace.add,CommentObservers.nativeObserve,hnb,
     CommentObservers.ordinary,width,CommentObservers.advance] using result
end URLNativeBodyState
