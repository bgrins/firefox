import URLNativeBad
set_option maxRecDepth 4096
set_option maxHeartbeats 4000000
namespace URLNativeBadState
open URLNativeState URLNativeBad
abbrev Byte := CommentScan.Byte

def Admitted : List Byte → State → Prop
 | [], _ => True
 | b::bs, s =>
   if b==41 then True
   else if b==92 && (bs.head?==some 41 || bs.head?==some 92) then
     Admitted bs.tail (advance s 2)
   else if b==13 && bs.head?==some 10 then
     s.packedLine+4<modulus ∧ Admitted bs.tail (newline s 2)
   else if CommentObservers.isNewline b then
     s.packedLine+4<modulus ∧ Admitted bs (newline s 1)
   else Admitted bs (known s b)
termination_by xs => xs.length

def observed (xs : List Byte) (r : CommentObservers.State) : CommentObservers.State :=
 CommentObservers.nativeObserve (xs.take (BadURL.native xs).count) r

theorem observed_close (bs : List Byte) (r : CommentObservers.State) :
 observed (41::bs) r=CommentObservers.advance 1 r := by
 have hw : CommentObservers.nativeWidth (41:Byte)=1 := by decide
 simp [observed,BadURL.native,CommentObservers.nativeObserve,CommentObservers.isNewline,
  CommentObservers.ordinary,hw,CommentObservers.advance]

theorem observed_pair (c : Byte) (cs : List Byte) (r : CommentObservers.State)
 (hc : c=41 ∨ c=92) : observed (92::c::cs) r=observed cs (CommentObservers.advance 2 r) := by
 have hw41 : CommentObservers.nativeWidth (41:Byte)=1 := by decide
 have hw92 : CommentObservers.nativeWidth (92:Byte)=1 := by decide
 rcases hc with rfl | rfl
 all_goals simp [observed,BadURL.native,BadURL.add,Nat.add_comm 2,
  CommentObservers.nativeObserve,CommentObservers.isNewline,CommentObservers.ordinary,
  hw41,hw92,CommentObservers.advance,Nat.add_assoc]

theorem observed_crlf (cs : List Byte) (r : CommentObservers.State) :
 observed (13::10::cs) r=observed cs (CommentObservers.newline 2 r) := by
 simp [observed,BadURL.native,BadURL.add,← Nat.add_assoc,Nat.add_comm 2,
  CommentObservers.nativeObserve,CommentObservers.isNewline]

theorem observed_newline (b : Byte) (bs : List Byte) (r : CommentObservers.State)
 (hn : CommentObservers.isNewline b=true)
 (hp : ¬(b==13 && bs.head?==some 10)=true) :
 observed (b::bs) r=observed bs (CommentObservers.newline 1 r) := by
 have ht : ¬(b==13 && (bs.take (BadURL.native bs).count).head?==some 10)=true := by
  by_cases hb : b=13
  · have hhead : bs.head?≠some 10 := by simpa [hb] using hp
    have htake := CommentExecution.head_take_not bs (BadURL.native bs).count 10 hhead
    simpa [hb] using htake
  · simp [hb]
 have hclose : b≠41 := by
  intro hb; subst b; simp [CommentObservers.isNewline] at hn
 have hslash : b≠92 := by
  intro hb; subst b; simp [CommentObservers.isNewline] at hn
 simp [observed,BadURL.native,hclose,hslash,BadURL.add,Nat.add_comm 1,
  CommentObservers.nativeObserve,hn,ht]

theorem observed_known (b : Byte) (bs : List Byte) (r : CommentObservers.State)
 (hc : b≠41)
 (hp : ¬(b==92 && (bs.head?==some 41 || bs.head?==some 92))=true)
 (hn : CommentObservers.isNewline b≠true) :
 observed (b::bs) r=observed bs (CommentObservers.ordinary b r) := by
 simp [observed,BadURL.native,hc,hp,BadURL.add,Nat.add_comm 1,
  CommentObservers.nativeObserve,hn]

theorem metadata (xs : List Byte) (s : State) (r : CommentObservers.State) (block : Nat)
 (h : Related s r block) (admitted : Admitted xs s) :
 Related (run xs s).state (observed xs r) block := by
 induction xs,s using run.induct generalizing r with
 | case1 s => simpa [run,observed,BadURL.native,CommentObservers.nativeObserve] using h
 | case2 b bs s hc =>
   have hb : b=41 := by simpa using hc
   subst b
   simpa [run,observed_close] using advance_related s r block 1 h
 | case3 b bs s hc hp ih =>
   have hadm : Admitted bs.tail (advance s 2) := by simpa [Admitted,hc,hp] using admitted
   have result := ih (CommentObservers.advance 2 r) (advance_related s r block 2 h) hadm
   cases bs with
   | nil => simp at hp
   | cons c cs =>
     have pair : b=92 ∧ (c=41 ∨ c=92) := by simpa using hp
     obtain ⟨rfl,pairClose⟩ := pair
     simpa [run,pairClose,add,CommentObservers.isNewline,observed_pair c cs r pairClose] using result
 | case4 b bs s hc hp hn ih =>
   cases bs with
   | nil => simp at hn
   | cons c cs =>
     have pair : b=13 ∧ c=10 := by simpa using hn
     obtain ⟨rfl,rfl⟩ := pair
     have hadm : s.packedLine+4<modulus ∧ Admitted cs (newline s 2) := by simpa [Admitted] using admitted
     have result := ih (CommentObservers.newline 2 r) (newline_related s r block 2 h hadm.1) hadm.2
     simpa [run,add,observed_crlf] using result
 | case5 b bs s hc hp hn hnl ih =>
   have hadm : s.packedLine+4<modulus ∧ Admitted bs (newline s 1) := by simpa [Admitted,hc,hp,hn,hnl] using admitted
   have result := ih (CommentObservers.newline 1 r) (newline_related s r block 1 h hadm.1) hadm.2
   simpa [run,hc,hp,hn,hnl,add,observed_newline b bs r hnl hn] using result
 | case6 b bs s hc hp hn hnl ih =>
   have hadm : Admitted bs (known s b) := by simpa [Admitted,hc,hp,hn,hnl] using admitted
   have result := ih (CommentObservers.ordinary b r) (known_related s r block b h) hadm
   have hclose : b≠41 := by simpa using hc
   simpa [run,hc,hp,hn,hnl,add,observed_known b bs r hclose hp hnl] using result
end URLNativeBadState
