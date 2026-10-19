import URLNativeBadState
import URLTrace
set_option maxRecDepth 4096
set_option maxHeartbeats 6000000
namespace URLNativeEnd
open URLNativeState
abbrev Byte := CommentScan.Byte
structure Result where
 state : State
 rawEnd : Option Nat
 deriving DecidableEq, Repr

def bad (xs : List Byte) (s : State) : Result :=
 let r := URLNativeBad.run xs s
 ⟨r.state,some r.rawEnd⟩

def run : List Byte → State → Result
 | [], s => ⟨s,none⟩
 | b::bs, s =>
   if b==41 then ⟨advance s 1,none⟩
   else if b==32 || b==9 then run bs (advance s 1)
   else if b==13 && bs.head?==some 10 then run bs.tail (newline s 2)
   else if CommentObservers.isNewline b then run bs (newline s 1)
   else bad (b::bs) s
termination_by xs => xs.length

def Admitted : List Byte → State → Prop
 | [], _ => True
 | b::bs, s =>
   if b==41 then True
   else if b==32 || b==9 then Admitted bs (advance s 1)
   else if b==13 && bs.head?==some 10 then s.packedLine+4<modulus ∧ Admitted bs.tail (newline s 2)
   else if CommentObservers.isNewline b then s.packedLine+4<modulus ∧ Admitted bs (newline s 1)
   else URLNativeBadState.Admitted (b::bs) s
termination_by xs => xs.length

def observed (xs : List Byte) (r : CommentObservers.State) :=
 CommentObservers.nativeObserve (URLTrace.ending xs).consumed r

theorem bad_metadata (xs : List Byte) (s : State) (r : CommentObservers.State) (block : Nat)
 (h : Related s r block) (ha : URLNativeBadState.Admitted xs s) :
 Related (bad xs s).state
 (CommentObservers.nativeObserve (URLTrace.bad xs).consumed r) block :=
 URLNativeBadState.metadata xs s r block h ha

theorem white_class : ∀ b : Byte,
 URLScan.nativeWhitespace b = ((b==32 || b==9) || CommentObservers.isNewline b) := by decide

theorem metadata (xs : List Byte) (s : State) (r : CommentObservers.State) (block : Nat)
 (h : Related s r block) (ha : Admitted xs s) :
 Related (run xs s).state (observed xs r) block := by
 have widths : CommentObservers.nativeWidth (41:Byte)=1 ∧ CommentObservers.nativeWidth (32:Byte)=1 ∧ CommentObservers.nativeWidth (9:Byte)=1 := by decide
 induction xs,s using run.induct generalizing r with
 | case1 s => simpa [run,observed,URLTrace.ending,CommentObservers.nativeObserve] using h
 | case2 b bs s hc =>
   have hb : b=41 := by simpa using hc
   subst b
   simpa [run,observed,URLTrace.ending,CommentObservers.nativeObserve,CommentObservers.isNewline,
    CommentObservers.ordinary,widths.1,widths.2.1,widths.2.2,CommentObservers.advance] using advance_related s r block 1 h
 | case3 b bs s hc hw ih =>
   have hadm : Admitted bs (advance s 1) := by simpa [Admitted,hc,hw] using ha
   have result := ih (CommentObservers.advance 1 r) (advance_related s r block 1 h) hadm
   have hb : b=32 ∨ b=9 := by simpa using hw
   rcases hb with rfl | rfl
   all_goals simpa [run,observed,URLTrace.ending,URLTrace.add,URLScan.nativeWhitespace,
     CommentObservers.nativeObserve,CommentObservers.isNewline,CommentObservers.ordinary,
     widths.1,widths.2.1,widths.2.2,CommentObservers.advance] using result
 | case4 b bs s hc hw hp ih =>
   cases bs with
   | nil => simp at hp
   | cons c cs =>
     have pair : b=13 ∧ c=10 := by simpa using hp
     obtain ⟨rfl,rfl⟩ := pair
     have hadm : s.packedLine+4<modulus ∧ Admitted cs (newline s 2) := by simpa [Admitted] using ha
     have result := ih (CommentObservers.newline 2 r) (newline_related s r block 2 h hadm.1) hadm.2
     simpa [run,observed,URLTrace.ending,URLTrace.add,URLScan.nativeWhitespace,
       CommentObservers.nativeObserve,CommentObservers.isNewline] using result
 | case5 b bs s hc hw hp hn ih =>
   have hadm : s.packedLine+4<modulus ∧ Admitted bs (newline s 1) := by simpa [Admitted,hc,hw,hp,hn] using ha
   have result := ih (CommentObservers.newline 1 r) (newline_related s r block 1 h hadm.1) hadm.2
   have ht : ¬(b==13 && (URLTrace.ending bs).consumed.head?==some 10)=true := by
     rw [URLTrace.ending_trace]
     by_cases hb : b=13
     · have hh : bs.head?≠some 10 := by simpa [hb] using hp
       simpa [hb] using CommentExecution.head_take_not bs (URLTrace.ending bs).value.count 10 hh
     · simp [hb]
   simpa [run,hc,hw,hp,hn,observed,URLTrace.ending,URLTrace.add,white_class,
     CommentObservers.nativeObserve,ht] using result
 | case6 b bs s hc hw hp hn =>
   have hadm : URLNativeBadState.Admitted (b::bs) s := by simpa [Admitted,hc,hw,hp,hn] using ha
   simpa [run,hc,hw,hp,hn,observed,URLTrace.ending,white_class] using bad_metadata (b::bs) s r block h hadm

theorem bad_position (xs : List Byte) (s : State) :
 (bad xs s).state.position=s.position+(URLTrace.bad xs).value.count := by
 exact (URLNativeBad.positions xs s).1.trans (congrArg (s.position+·) (URLNativeBad.boundary xs s).1)

theorem bad_capture (xs : List Byte) (s : State) :
 (bad xs s).rawEnd=some (s.position+(URLTrace.bad xs).value.count-if (URLTrace.bad xs).closed then 1 else 0) := by
 exact congrArg some (URLNativeBad.raw_endpoint xs s)

theorem position (xs : List Byte) (s : State) :
 (run xs s).state.position=s.position+(URLTrace.ending xs).value.count := by
 induction xs,s using run.induct with
 | case1 s => simp [run,URLTrace.ending]
 | case2 b bs s hc => simp [run,URLTrace.ending,hc,advance]
 | case3 b bs s hc hw ih =>
   simpa [run,hc,hw,URLTrace.ending,white_class,URLTrace.add,URLScan.extend,advance,Nat.add_assoc] using ih
 | case4 b bs s hc hw hp ih =>
   cases bs with
   | nil => simp at hp
   | cons c cs =>
     have pair : b=13 ∧ c=10 := by simpa using hp
     obtain ⟨rfl,rfl⟩ := pair
     simpa [run,URLTrace.ending,URLScan.nativeWhitespace,URLTrace.add,URLScan.extend,newline,advanceLine,← Nat.add_assoc] using ih
 | case5 b bs s hc hw hp hn ih =>
   simpa [run,hc,hw,hp,hn,URLTrace.ending,white_class,URLTrace.add,URLScan.extend,newline,advanceLine,← Nat.add_assoc] using ih
 | case6 b bs s hc hw hp hn =>
   simpa [run,hc,hw,hp,hn,URLTrace.ending,white_class] using bad_position (b::bs) s

theorem capture (xs : List Byte) (s : State) :
 (run xs s).rawEnd = if (URLTrace.ending xs).value.kind=.bad then
  some (s.position+(URLTrace.ending xs).value.count-if (URLTrace.ending xs).closed then 1 else 0) else none := by
 induction xs,s using run.induct with
 | case1 s => simp [run,URLTrace.ending]
 | case2 b bs s hc => simp [run,hc,URLTrace.ending,advance]
 | case3 b bs s hc hw ih =>
   simpa [run,hc,hw,URLTrace.ending,white_class,URLTrace.add,URLScan.extend,advance,Nat.add_assoc] using ih
 | case4 b bs s hc hw hp ih =>
   cases bs with
   | nil => simp at hp
   | cons c cs =>
     have pair : b=13 ∧ c=10 := by simpa using hp
     obtain ⟨rfl,rfl⟩ := pair
     simp [run,URLTrace.ending,URLScan.nativeWhitespace,URLTrace.add,URLScan.extend,newline,advanceLine,← Nat.add_assoc] at ih ⊢
     exact ih
 | case5 b bs s hc hw hp hn ih =>
   simpa [run,hc,hw,hp,hn,URLTrace.ending,white_class,URLTrace.add,URLScan.extend,newline,advanceLine,← Nat.add_assoc] using ih
 | case6 b bs s hc hw hp hn =>
   simp only [run,hc,hw,hp,hn,↓reduceIte,URLTrace.ending,white_class,Bool.false_or,URLTrace.bad]
   exact bad_capture (b::bs) s
end URLNativeEnd
