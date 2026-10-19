import URLNativeEscape
set_option maxRecDepth 4096
set_option maxHeartbeats 8000000
namespace URLNativeEscapeCut
abbrev Byte := CommentScan.Byte
open URLDelegation

theorem whitespace (xs : List Byte) :
 NoSplit (xs.take (Escape.nativeWhitespace xs)) (xs.drop (Escape.nativeWhitespace xs)) := by
 cases xs with
 | nil => simp [NoSplit]
 | cons b bs =>
   simp only [Escape.nativeWhitespace]
   split
   · rename_i h
     left
     simp only [List.take_succ_cons,List.take_zero,List.getLast?_singleton,ne_eq,Option.some.injEq]
     intro hb
     subst b
     change (13=32 ∨ 13=9) at h
     omega
   · split
     · split
       · rename_i h
         cases bs with
         | nil => simp at h
         | cons c cs =>
           have hb : b=13 := Fin.ext h.1
           have hc : c=10 := by simpa [Escape.byte] using h.2
           simp [hb,hc,NoSplit]
       · rename_i hn hp
         by_cases hb : b=13
         · right
           simp only [List.drop_succ_cons,List.drop_zero]
           have hv : b.val=13 := by rw [hb]; rfl
           have he : Escape.byte 10=(10:Byte) := rfl
           simpa only [hv,true_and,he] using hp
         · left
           simpa using hb
     · simp [NoSplit]

theorem prepend_noncr (a b c : List Byte) (ha : a.getLast?≠some 13)
 (h : NoSplit b c) : NoSplit (a++b) c := by
 rcases h with h | h
 · left
   rw [List.getLast?_append]
   cases hb : b.getLast? with
   | none => simpa [hb] using ha
   | some v => simpa [hb] using h
 · exact Or.inr h

theorem hex (xs : List Byte) :
 let n := (HexPrefix.run 6 xs 0).count
 let m := Escape.nativeWhitespace (HexPrefix.run 6 xs 0).rest
 NoSplit (xs.take (n+m)) (xs.drop (n+m)) := by
 dsimp
 rw [← StringTrace.take_split _ _ _ (HexPrefix.count_bound 6 xs 0).1,← List.drop_drop]
 rw [← HexPrefix.exact_remainder]
 exact prepend_noncr _ _ _ (URLNativeEscape.hex_not_cr 6 xs 0)
   (whitespace (HexPrefix.run 6 xs 0).rest)

theorem unit_noncr (u : Boundary.Unit) (hn : CommentObservers.isNewline u.first=false) :
 u.bytes.getLast?≠some 13 := by
 intro h
 obtain ⟨pre,hpre⟩ := List.getLast?_eq_some_iff.mp h
 have hm : (13:Byte)∈u.bytes := by simp [hpre]
 rcases List.mem_cons.mp hm with hb | hb
 · rw [← hb] at hn
   contradiction
 · have hc := u.continuation 13 hb
   change 128≤13 ∧ 13<192 at hc
   omega

theorem escape (units : List Boundary.Unit)
 (hn : ∀ b ∈ (Boundary.bytes units).head?, CommentObservers.isNewline b=false) :
 NoSplit ((Boundary.bytes units).take (Escape.native (Boundary.bytes units)).count)
   ((Boundary.bytes units).drop (Escape.native (Boundary.bytes units)).count) := by
 cases units with
 | nil => simp [Boundary.bytes,Escape.native,NoSplit]
 | cons u us =>
   cases hd : HexPrefix.nativeDigit u.first with
   | some d =>
     simpa only [Boundary.bytes,List.flatMap_cons,Boundary.Unit.bytes,List.cons_append,Escape.native,hd] using hex (Boundary.bytes (u::us))
   | none =>
     by_cases hz : u.first.val=0
     · have hu : u.first=0 := Fin.ext hz
       simp [Boundary.bytes,Boundary.Unit.bytes,Escape.native,hd,hz,NoSplit,hu,HexPrefix.nativeDigit]
     · have hw := URLNativeCharacter.byte_length u
       have ht : (u.bytes++Boundary.bytes us).take (Escape.width u.first)=u.bytes := by rw [← hw,List.take_left]
       have hn' : CommentObservers.isNewline u.first=false := hn u.first (by simp [Boundary.bytes,Boundary.Unit.bytes])
       left
       change ((u.bytes++Boundary.bytes us).take (Escape.native (u.bytes++Boundary.bytes us)).count).getLast?≠some 13
       have he : Escape.native (u.bytes++Boundary.bytes us)=⟨u.bytes,u.bytes.length⟩ := by
         change Escape.native (u.first::(u.rest++Boundary.bytes us))=_
         simp only [Escape.native,hd,hz,↓reduceIte]
         change ({output := (u.bytes++Boundary.bytes us).take (Escape.width u.first), count := ((u.bytes++Boundary.bytes us).take (Escape.width u.first)).length} : Escape.Result)=_
         rw [ht]
       rw [he,List.take_left]
       exact unit_noncr u hn'

theorem take_right (a b : List Byte) (n : Nat) (h : NoSplit a b) : NoSplit a (b.take n) := by
 rcases h with h | h
 · exact Or.inl h
 · exact Or.inr (CommentExecution.head_take_not b n 10 h)
end URLNativeEscapeCut
