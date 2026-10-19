import URLUTF8
import URLDelegation
set_option maxRecDepth 4096
set_option maxHeartbeats 5000000
namespace URLLeading
open URLScan
abbrev Byte := CommentScan.Byte
inductive Result where
 | function
 | token (value : Value)
 deriving DecidableEq, Repr

def quote (b : Byte) : Bool := b == 34 || b == 39

def native : List Byte → Nat → Result
 | [], skipped => .token ⟨.url,[],skipped⟩
 | b::bs, skipped =>
   if nativeWhitespace b then native bs (skipped+1)
   else if quote b then .function
   else .token (extend [] skipped (borrowed (b::bs) []).value)

def reference (xs : List Byte) (skipped : Nat) : Result :=
 let rest := xs.dropWhile referenceWhitespace
 let count := skipped+xs.length-rest.length
 match rest with
 | [] => .token ⟨.url,[],count⟩
 | b::bs => if quote b then .function
   else .token (extend [] count (URLScan.reference (b::bs)))

theorem native_reference (xs : List Byte) (skipped : Nat) : native xs skipped = reference xs skipped := by
 induction xs generalizing skipped with
 | nil => simp [native,reference]
 | cons b bs ih =>
   by_cases ws : nativeWhitespace b = true
   · have wr : referenceWhitespace b = true := by rwa [← whitespace_equivalence]
     have bound := drop_bound bs
     simp only [native,ws,↓reduceIte,ih,reference,List.dropWhile_cons,wr,↓reduceIte,List.length_cons]
     have arithmetic : skipped+1+bs.length-(bs.dropWhile referenceWhitespace).length = skipped+(bs.length+1)-(bs.dropWhile referenceWhitespace).length := by omega
     rw [arithmetic]
   · have wf : referenceWhitespace b = false := by simpa [← whitespace_equivalence] using ws
     simp [native,ws,reference,List.dropWhile_cons,wf,borrowed_reference,extend_identity]

theorem whitespace_prefix (ws tail : List Byte) (h : ∀ b ∈ ws, nativeWhitespace b = true) (skipped : Nat) :
 native (ws++tail) skipped = native tail (skipped+ws.length) := by
 induction ws generalizing skipped with
 | nil => simp
 | cons b bs ih =>
   have hb := h b (by simp)
   have ht := ih (fun c hc => h c (by simp [hc])) (skipped+1)
   simpa [native,hb,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] using ht

theorem quote_after_whitespace (ws body : List Byte) (b : Byte)
 (h : ∀ c ∈ ws, nativeWhitespace c = true) (hq : quote b = true) :
 native (ws++b::body) 0 = .function := by
 rw [whitespace_prefix ws (b::body) h]
 have hn : nativeWhitespace b = false := by
   have disjoint : ∀ b, quote b=true → nativeWhitespace b=false := by decide
   exact disjoint b hq
 simp [native,hn,hq]

structure Observed where
 result : Result
 state : CommentObservers.State
 urls : CommentDirectives.URLs
 deriving DecidableEq, Repr

def observed (xs : List Byte) (s : CommentObservers.State) (urls : CommentDirectives.URLs) : Observed :=
 let result := native xs 0
 let state := match result with
 | .function => s
 | .token value => CommentObservers.nativeObserve (xs.take value.count) s
 ⟨result,state,urls⟩

theorem quoted_rollback (ws body : List Byte) (b : Byte)
 (h : ∀ c ∈ ws, nativeWhitespace c = true) (hq : quote b=true)
 (s : CommentObservers.State) (urls : CommentDirectives.URLs) :
 observed (ws++b::body) s urls = ⟨.function,s,urls⟩ := by
 simp [observed,quote_after_whitespace ws body b h hq]

theorem bounds (xs : List Byte) (skipped : Nat) (v : Value) (h : native xs skipped = .token v) :
 v.count ≤ skipped+xs.length := by
 induction xs generalizing skipped with
 | nil => cases h; simp
 | cons b bs ih =>
   simp only [native] at h
   split at h
   · have bound := ih _ h
     simpa [Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] using bound
   · split at h
     · contradiction
     · cases h
       have bound := borrowed_bound (b::bs) []
       simp only [extend]
       omega

theorem whitespace_suffix_valid (units : List Boundary.Unit) :
 StringUTF8.Valid ((Boundary.bytes units).dropWhile URLScan.referenceWhitespace) := by
 induction units with
 | nil => exact StringUTF8.valid_nil
 | cons u us ih =>
   by_cases ws : URLScan.nativeWhitespace u.first=true
   · have empty := Boundary.unit_ascii_singleton u (URLUTF8.whitespace_ascii u.first ws)
     have form : Boundary.bytes (u::us)=u.first::Boundary.bytes us := by simp [Boundary.bytes,Boundary.Unit.bytes,empty]
     simpa [form,← URLScan.whitespace_equivalence,ws] using ih
   · have form : Boundary.bytes (u::us)=u.first::(u.rest++Boundary.bytes us) := rfl
     simpa [form,← URLScan.whitespace_equivalence,ws] using (show StringUTF8.Valid (Boundary.bytes (u::us)) from ⟨u::us,rfl⟩)

theorem token_output_valid (units : List Boundary.Unit) (v : Value)
 (h : native (Boundary.bytes units) 0=.token v) : StringUTF8.Valid v.output := by
 rw [native_reference] at h
 obtain ⟨remaining,hr⟩ := whitespace_suffix_valid units
 change (Boundary.bytes units).dropWhile URLScan.referenceWhitespace=Boundary.bytes remaining at hr
 have valid := (URLUTF8.reference_valid remaining).1
 unfold reference at h
 rw [hr] at h
 cases hc : Boundary.bytes remaining with
 | nil => simp only [hc] at h; cases h; exact StringUTF8.valid_nil
 | cons b bs =>
   simp only [hc] at h
   split at h
   · contradiction
   · cases h
     change StringUTF8.Valid (URLScan.reference (Boundary.bytes remaining)).output at valid
     rw [hc] at valid
     exact URLUTF8.extend_valid _ _ _ StringUTF8.valid_nil valid

theorem quote_decomposition (xs : List Byte) (skipped : Nat)
 (h : native xs skipped=.function) :
 ∃ ws q body, xs=ws++q::body ∧
   (∀ b ∈ ws, nativeWhitespace b=true) ∧ quote q=true := by
 induction xs generalizing skipped with
 | nil => simp [native] at h
 | cons b bs ih =>
   simp only [native] at h
   split at h
   · rename_i hw
     obtain ⟨ws,q,body,he,hws,hq⟩ := ih _ h
     refine ⟨b::ws,q,body,?_,?_,hq⟩
     · simp [he]
     · intro c hc
       rcases List.mem_cons.mp hc with rfl | hc
       · exact hw
       · exact hws c hc
   · split at h
     · rename_i hq
       exact ⟨[],b,bs,rfl,by simp,hq⟩
     · contradiction

theorem admitted_quoted_completion (xs : List Byte)
 (h : native xs 0=.function) (s : CommentObservers.State)
 (urls : CommentDirectives.URLs) :
 ∃ ws q body, xs=ws++q::body ∧
   (∀ b ∈ ws, nativeWhitespace b=true) ∧ quote q=true ∧
   URLDelegation.nativeCombined (q==39) ws body s urls =
     URLDelegation.specCombined (q==39) ws body s urls := by
 obtain ⟨ws,q,body,he,hws,hq⟩ := quote_decomposition xs 0 h
 exact ⟨ws,q,body,he,hws,hq,URLDelegation.combined_string _ _ _ _ _⟩

end URLLeading
