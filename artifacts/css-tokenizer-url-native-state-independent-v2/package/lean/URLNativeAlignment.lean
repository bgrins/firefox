import URLUTF8
set_option maxRecDepth 4096
set_option maxHeartbeats 6000000
namespace URLNativeAlignment
abbrev Byte := CommentScan.Byte

def TailValid (xs : List Byte) : Prop :=
 ∃ pre units, xs=pre++Boundary.bytes units ∧ ∀ b ∈ pre, 128≤b.val ∧ b.val<192

theorem from_valid (xs : List Byte) (h : StringUTF8.Valid xs) : TailValid xs := by
 obtain ⟨units,hu⟩ := h
 exact ⟨[],units,by simpa using hu,by simp⟩

theorem tail (b : Byte) (bs : List Byte) (h : TailValid (b::bs)) : TailValid bs := by
 obtain ⟨pre,units,he,hp⟩ := h
 cases pre with
 | cons c cs =>
   simp only [List.cons_append,List.cons.injEq] at he
   exact ⟨cs,units,he.2,fun d hd => hp d (by simp [hd])⟩
 | nil =>
   cases units with
   | nil => simp [Boundary.bytes] at he
   | cons u us =>
     simp only [List.nil_append,Boundary.bytes,List.flatMap_cons,Boundary.Unit.bytes,List.cons_append,List.cons.injEq] at he
     exact ⟨u.rest,us,he.2,u.continuation⟩

theorem ascii_tail (b : Byte) (bs : List Byte) (h : TailValid (b::bs))
 (hb : b.val<128) : StringUTF8.Valid bs := by
 obtain ⟨pre,units,he,hp⟩ := h
 cases pre with
 | cons c cs =>
   have hc := hp c (by simp)
   simp only [List.cons_append,List.cons.injEq] at he
   rw [← he.1] at hc
   omega
 | nil =>
   obtain ⟨us,hu⟩ := Boundary.ascii_step units b bs (by simpa using he.symm) hb
   exact ⟨us,hu⟩

theorem escape_rest (xs : List Byte) (h : StringUTF8.Valid xs) :
 TailValid (xs.drop (Escape.native xs).count) := by
 obtain ⟨us,rfl⟩ := h
 exact from_valid _ (StringUTF8.escape_valid us).2
end URLNativeAlignment
