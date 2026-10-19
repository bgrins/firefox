import URLNativeState
import HexPrefix
import Escape
set_option maxRecDepth 4096
set_option maxHeartbeats 4000000
namespace URLNativeHex
open URLNativeState
abbrev Byte := CommentScan.Byte

def run : Nat → List Byte → Nat → State → State
 | 0, _, _, s => s
 | _+1, [], _, s => s
 | fuel+1, b::bs, value, s =>
   match HexPrefix.nativeDigit b with
   | none => s
   | some digit => run fuel bs (value*16+digit) (advance s 1)

theorem advance_compose (s : State) (a b : Nat) :
 advance (advance s a) b=advance s (a+b) := by
 simp [advance,Nat.add_assoc]

theorem state_exact (fuel : Nat) (xs : List Byte) (value : Nat) (s : State) :
 run fuel xs value s=advance s (HexPrefix.run fuel xs value).count := by
 induction fuel generalizing xs value s with
 | zero => simp [run,HexPrefix.run,advance]
 | succ fuel ih =>
   cases xs with
   | nil => simp [run,HexPrefix.run,advance]
   | cons b bs =>
     cases hd : HexPrefix.nativeDigit b with
     | none => simp [run,HexPrefix.run,hd,advance]
     | some digit => simp [run,HexPrefix.run,hd,ih,advance_compose,Nat.add_comm 1]

theorem digit_metadata : ∀ b : Byte, (HexPrefix.nativeDigit b).isSome=true →
 CommentObservers.nativeWidth b=1 ∧ CommentObservers.isNewline b=false := by decide

theorem observed (fuel : Nat) (xs : List Byte) (value : Nat) (r : CommentObservers.State) :
 CommentObservers.nativeObserve (xs.take (HexPrefix.run fuel xs value).count) r =
 CommentObservers.advance (HexPrefix.run fuel xs value).count r := by
 induction fuel generalizing xs value r with
 | zero => simp [HexPrefix.run,CommentObservers.nativeObserve,CommentObservers.advance]
 | succ fuel ih =>
   cases xs with
   | nil => simp [HexPrefix.run,CommentObservers.nativeObserve,CommentObservers.advance]
   | cons b bs =>
     cases hd : HexPrefix.nativeDigit b with
     | none => simp [HexPrefix.run,hd,CommentObservers.nativeObserve,CommentObservers.advance]
     | some digit =>
       obtain ⟨hw,hn⟩ := digit_metadata b (by simp [hd])
       simp only [HexPrefix.run,hd]
       simp only [List.take_succ_cons,CommentObservers.nativeObserve,hn,↓reduceIte,ih]
       simp [CommentObservers.ordinary,hw,CommentObservers.advance,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]

theorem related (fuel : Nat) (xs : List Byte) (value : Nat) (s : State)
 (r : CommentObservers.State) (block : Nat) (h : Related s r block) :
 Related (run fuel xs value s)
  (CommentObservers.nativeObserve (xs.take (HexPrefix.run fuel xs value).count) r) block := by
 rw [state_exact,observed]
 exact advance_related s r block _ h
theorem consumed_digits (fuel : Nat) (xs : List Byte) (value : Nat) :
 ∀ b ∈ xs.take (HexPrefix.run fuel xs value).count,
  (HexPrefix.nativeDigit b).isSome=true := by
 induction fuel generalizing xs value with
 | zero => simp [HexPrefix.run]
 | succ fuel ih =>
   cases xs with
   | nil => simp [HexPrefix.run]
   | cons c cs =>
     cases hd : HexPrefix.nativeDigit c with
     | none => simp [HexPrefix.run,hd]
     | some digit =>
       intro b hb
       simp only [HexPrefix.run,hd,List.take_succ_cons,List.mem_cons] at hb
       rcases hb with rfl | hb
       · simp [hd]
       · exact ih cs (value*16+digit) b hb

end URLNativeHex
