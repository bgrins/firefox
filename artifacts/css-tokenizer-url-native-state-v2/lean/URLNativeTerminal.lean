import URLNativeLeading
set_option maxRecDepth 4096
set_option maxHeartbeats 8000000
namespace URLNativeTerminal
open URLNativeState
abbrev Byte := CommentScan.Byte

def AtBoundary (xs : List Byte) (start finish : Nat) : Prop :=
 ∃ consumed rest, xs=consumed++rest ∧ finish=start+consumed.length ∧
   (rest=[] ∨ rest.head?=some 41)

theorem prepend (pre xs : List Byte) (start finish : Nat)
 (h : AtBoundary xs (start+pre.length) finish) : AtBoundary (pre++xs) start finish := by
 obtain ⟨used,rest,he,hp,hr⟩ := h
 exact ⟨pre++used,rest,by simp [he,List.append_assoc],by simpa [List.length_append,Nat.add_assoc] using hp,hr⟩

theorem bad (xs : List Byte) (s : State) :
 AtBoundary xs s.position (URLNativeBad.run xs s).rawEnd := by
 induction xs,s using URLNativeBad.run.induct with
 | case1 s => exact ⟨[],[],rfl,by simp [URLNativeBad.run],Or.inl rfl⟩
 | case2 b bs s hc =>
   have hb : b=41 := by simpa using hc
   exact ⟨[],b::bs,rfl,by simp [URLNativeBad.run,hc],Or.inr (by simp [hb])⟩
 | case3 b bs s hc hp ih =>
   cases bs with
   | nil => simp at hp
   | cons c cs =>
     have pair : b=92 ∧ (c=41 ∨ c=92) := by simpa using hp
     obtain ⟨rfl,cpair⟩ := pair
     have he := prepend [92,c] cs s.position _ ih
     simpa [URLNativeBad.run,cpair,URLNativeBad.add,advance] using he
 | case4 b bs s hc hp hn ih =>
   cases bs with
   | nil => simp at hn
   | cons c cs =>
     have pair : b=13 ∧ c=10 := by simpa using hn
     obtain ⟨rfl,rfl⟩ := pair
     have he := prepend [13,10] cs s.position _ ih
     simpa [URLNativeBad.run,URLNativeBad.add,newline,advanceLine] using he
 | case5 b bs s hc hp hn hnl ih =>
   have he := prepend [b] bs s.position _ ih
   simpa [URLNativeBad.run,hc,hp,hn,hnl,URLNativeBad.add,newline,advanceLine] using he
 | case6 b bs s hc hp hn hnl ih =>
   rw [URLNativeBad.known_position] at ih
   have he := prepend [b] bs s.position _ ih
   simpa [URLNativeBad.run,hc,hp,hn,hnl,URLNativeBad.add] using he

theorem ending (xs : List Byte) (s : State) (finish : Nat)
 (h : (URLNativeEnd.run xs s).rawEnd=some finish) : AtBoundary xs s.position finish := by
 induction xs,s using URLNativeEnd.run.induct with
 | case1 s => simp [URLNativeEnd.run] at h
 | case2 b bs s hc => simp [URLNativeEnd.run,hc] at h
 | case3 b bs s hc hw ih =>
   have he := ih (by simpa [URLNativeEnd.run,hc,hw] using h)
   exact prepend [b] bs s.position finish he
 | case4 b bs s hc hw hp ih =>
   cases bs with
   | nil => simp at hp
   | cons c cs =>
     have pair : b=13 ∧ c=10 := by simpa using hp
     obtain ⟨rfl,rfl⟩ := pair
     have he := ih (by simpa [URLNativeEnd.run] using h)
     exact prepend [13,10] cs s.position finish he
 | case5 b bs s hc hw hp hn ih =>
   have he := ih (by simpa [URLNativeEnd.run,hc,hw,hp,hn] using h)
   exact prepend [b] bs s.position finish he
 | case6 b bs s hc hw hp hn =>
   have he : (URLNativeBad.run (b::bs) s).rawEnd=finish := by simpa [URLNativeEnd.run,hc,hw,hp,hn,URLNativeEnd.bad] using h
   rw [← he]
   exact bad (b::bs) s

theorem body (xs : List Byte) (s : State) (finish : Nat)
 (valid : URLNativeAlignment.TailValid xs)
 (h : (URLNativeBody.run xs s).rawEnd=some finish) : AtBoundary xs s.position finish := by
 induction xs,s using URLNativeBody.run.induct with
 | case1 s => simp [URLNativeBody.run] at h
 | case2 b bs s hc => simp [URLNativeBody.run,hc] at h
 | case3 b bs s hc =>
   have he : (URLNativeBad.run bs (advance s 1)).rawEnd=finish := by simpa [URLNativeBody.run,hc,URLNativeEnd.bad] using h
   rw [← he]
   exact prepend [b] bs s.position _ (bad bs (advance s 1))
 | case4 b bs s hc => exact ending (b::bs) s finish (by simpa [URLNativeBody.run,hc] using h)
 | case5 b bs s hc ih =>
   exact prepend [b] bs s.position finish (ih (URLNativeAlignment.tail b bs valid) (by simpa [URLNativeBody.run,hc] using h))
 | case6 b bs s hc ih =>
   have he := ih (URLNativeAlignment.tail b bs valid) (by simpa [URLNativeBody.run,hc] using h)
   rw [URLNativeBad.known_position] at he
   exact prepend [b] bs s.position finish he
 | case7 b bs s hc hn =>
   have he : (URLNativeBad.run bs (advance s 1)).rawEnd=finish := by simpa [URLNativeBody.run,hc,hn,URLNativeEnd.bad] using h
   rw [← he]
   exact prepend [b] bs s.position _ (bad bs (advance s 1))
 | case8 b bs s hc hn ih =>
   have hb := URLNativeBody.escape_byte b hc
   have hv := URLNativeAlignment.ascii_tail b bs valid (by rw [hb]; decide)
   have he := ih (URLNativeAlignment.escape_rest bs hv) (by simpa [URLNativeBody.run,hc,hn] using h)
   rw [URLNativeBody.escape_position bs s hv] at he
   have count := Escape.consumption_bound bs
   have he' : AtBoundary (bs.drop (Escape.native bs).count)
     (s.position+(b::bs.take (Escape.native bs).count).length) finish := by
     simpa [List.length_take,Nat.min_eq_left count,Nat.add_assoc,Nat.add_comm 1] using he
   have result := prepend (b::bs.take (Escape.native bs).count) (bs.drop (Escape.native bs).count) s.position finish he'
   simpa using result

theorem marker (xs : List Byte) (start finish : Nat) (h : AtBoundary xs start finish) :
 Boundary.marker xs (finish-start) := by
 obtain ⟨used,rest,rfl,rfl,hr⟩ := h
 simp only [Nat.add_sub_cancel_left]
 constructor
 · simp
 · rw [← List.head?_drop,List.drop_left]
   rcases hr with rfl | hr
   · trivial
   · rw [hr]
     exact Or.inl (by decide)

theorem captured_marker (before xs : List Byte) (s : State) (finish : Nat)
 (hp : s.position=before.length) (valid : StringUTF8.Valid xs)
 (h : (URLNativeBorrowed.entry xs s).result.rawEnd=some finish) :
 Boundary.marker (before++xs) finish := by
 have he := body xs s finish (URLNativeAlignment.from_valid xs valid)
   (by simpa [URLNativeBorrowed.entry,URLNativeBorrowed.state_handoff] using h)
 rw [hp] at he
 have full := prepend before xs 0 finish (by simpa using he)
 simpa using marker (before++xs) 0 finish full
end URLNativeTerminal
