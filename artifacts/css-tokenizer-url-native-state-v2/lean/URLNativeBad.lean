import URLNativeState
import BadURL
import URLDelegation
set_option maxRecDepth 4096
set_option maxHeartbeats 4000000
namespace URLNativeBad
open URLNativeState
abbrev Byte := CommentScan.Byte
structure Result where
 state : State
 rawEnd : Nat
 closed : Bool
 count : Nat
 deriving DecidableEq, Repr

def add (n : Nat) (r : Result) : Result := {r with count:=n+r.count}

def run : List Byte → State → Result
 | [], s => ⟨s,s.position,false,0⟩
 | b::bs, s =>
   if b==41 then ⟨advance s 1,s.position,true,1⟩
   else if b==92 && (bs.head?==some 41 || bs.head?==some 92) then
     add 2 (run bs.tail (advance s 2))
   else if b==13 && bs.head?==some 10 then
     add 2 (run bs.tail (newline s 2))
   else if CommentObservers.isNewline b then
     add 1 (run bs (newline s 1))
   else add 1 (run bs (known s b))
termination_by xs => xs.length

theorem known_position (s : State) (b : Byte) : (known s b).position=s.position+1 := by
 unfold known
 split
 · rfl
 · split <;> rfl

theorem positions (xs : List Byte) (s : State) :
 (run xs s).state.position=s.position+(run xs s).count ∧
 (run xs s).rawEnd+(if (run xs s).closed then 1 else 0)=(run xs s).state.position ∧
 s.position≤(run xs s).rawEnd := by
 induction xs,s using run.induct with
 | case1 s => simp [run]
 | case2 b bs s hc => simp [run,hc,advance]
 | case3 b bs s hc hp ih =>
   simp [run,hc,hp,add]
   dsimp only [advance] at ih ⊢
   obtain ⟨hpos,hend,hbound⟩ := ih
   exact ⟨by omega,hend,by omega⟩
 | case4 b bs s hc hp hn ih =>
   simp [run,hc,hp,hn,add]
   dsimp only [newline,advanceLine] at ih ⊢
   obtain ⟨hpos,hend,hbound⟩ := ih
   exact ⟨by omega,hend,by omega⟩
 | case5 b bs s hc hp hn hnl ih =>
   simp [run,hc,hp,hn,hnl,add]
   dsimp only [newline,advanceLine] at ih ⊢
   obtain ⟨hpos,hend,hbound⟩ := ih
   exact ⟨by omega,hend,by omega⟩
 | case6 b bs s hc hp hn hnl ih =>
   simp [run,hc,hp,hn,hnl,add]
   rw [known_position] at ih
   obtain ⟨hpos,hend,hbound⟩ := ih
   exact ⟨by omega,hend,by omega⟩

theorem boundary (xs : List Byte) (s : State) :
 (run xs s).count=(BadURL.native xs).count ∧
 (run xs s).closed=(BadURL.native xs).closed := by
 induction xs,s using run.induct with
 | case1 s => simp [run,BadURL.native]
 | case2 b bs s hc => simp [run,hc,BadURL.native]
 | case3 b bs s hc hp ih =>
   simpa [run,hc,hp,BadURL.native,add,BadURL.add] using ih
 | case4 b bs s hc hp hn ih =>
   cases bs with
   | nil => simp at hn
   | cons c cs =>
     simp at hn
     obtain ⟨rfl,rfl⟩ := hn
     simpa [run,BadURL.native,add,BadURL.add,← Nat.add_assoc] using ih
 | case5 b bs s hc hp hn hnl ih =>
   simpa [run,hc,hp,hn,hnl,BadURL.native,add,BadURL.add] using ih
 | case6 b bs s hc hp hn hnl ih =>
   simpa [run,hc,hp,hn,hnl,BadURL.native,add,BadURL.add] using ih

theorem raw_endpoint (xs : List Byte) (s : State) :
 (run xs s).rawEnd=s.position+(BadURL.native xs).count-
   (if (BadURL.native xs).closed then 1 else 0) := by
 obtain ⟨hp,he,_⟩ := positions xs s
 obtain ⟨hc,hclose⟩ := boundary xs s
 rw [hc] at hp
 rw [hclose,hp] at he
 omega

theorem consumed_bound (xs : List Byte) (s : State) :
 (run xs s).state.position≤s.position+xs.length := by
 obtain ⟨hp,_,_⟩ := positions xs s
 rw [hp,(boundary xs s).1]
 have h := BadURL.bounded xs
 omega
end URLNativeBad
