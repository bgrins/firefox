import URLNativeState
import Escape
set_option maxRecDepth 4096
set_option maxHeartbeats 4000000
namespace URLNativeWhitespace
open URLNativeState
abbrev Byte := CommentScan.Byte

def consume (xs : List Byte) (s : State) : State :=
 match xs with
 | [] => s
 | b::bs =>
   if b.val=32 ∨ b.val=9 then advance s 1
   else if b.val=10 ∨ b.val=12 ∨ b.val=13 then
     newline s (if b.val=13 ∧ bs.head?=some (Escape.byte 10) then 2 else 1)
   else s

def Admitted (xs : List Byte) (s : State) : Prop :=
 match xs with
 | [] => True
 | b::_ => (b.val=10 ∨ b.val=12 ∨ b.val=13) → s.packedLine+4<modulus

def after (xs : List Byte) (r : CommentObservers.State) : CommentObservers.State :=
 match xs with
 | [] => r
 | b::bs =>
   if b.val=32 ∨ b.val=9 then CommentObservers.advance 1 r
   else if b.val=10 ∨ b.val=12 ∨ b.val=13 then
     CommentObservers.newline (if b.val=13 ∧ bs.head?=some (Escape.byte 10) then 2 else 1) r
   else r

theorem state_relation (xs : List Byte) (s : State) (r : CommentObservers.State) (block : Nat)
 (h : Related s r block) (ha : Admitted xs s) : Related (consume xs s) (after xs r) block := by
 cases xs with
 | nil => exact h
 | cons b bs =>
   simp only [consume,after]
   split
   · exact advance_related s r block 1 h
   · split
     · rename_i hn
       exact newline_related s r block _ h (ha hn)
     · exact h

theorem position (xs : List Byte) (s : State) :
 (consume xs s).position=s.position+Escape.nativeWhitespace xs := by
 cases xs with
 | nil => simp [consume,Escape.nativeWhitespace]
 | cons b bs =>
   simp only [consume,Escape.nativeWhitespace]
   split
   · rfl
   · split
     · split <;> rfl
     · simp

theorem observed (xs : List Byte) (r : CommentObservers.State) :
 after xs r=CommentObservers.nativeObserve (xs.take (Escape.nativeWhitespace xs)) r := by
 have hv9 : (9:Byte).val=9 := rfl
 have hv10 : (10:Byte).val=10 := rfl
 have hv12 : (12:Byte).val=12 := rfl
 have hv13 : (13:Byte).val=13 := rfl
 have hv32 : (32:Byte).val=32 := rfl
 cases xs with
 | nil => simp [hv9,hv10,hv12,hv13,hv32,after,Escape.nativeWhitespace,CommentObservers.nativeObserve]
 | cons b bs =>
   by_cases hs : b.val=32 ∨ b.val=9
   · rcases hs with hb | hb
     · have eq : b=32 := Fin.ext hb
       subst b
       have hw : CommentObservers.nativeWidth (32:Byte)=1 := by decide
       simp [hv9,hv10,hv12,hv13,hv32,after,Escape.nativeWhitespace,CommentObservers.nativeObserve,CommentObservers.isNewline,
        CommentObservers.ordinary,hw,CommentObservers.advance]
     · have eq : b=9 := Fin.ext hb
       subst b
       have hw : CommentObservers.nativeWidth (9:Byte)=1 := by decide
       simp [hv9,hv10,hv12,hv13,hv32,after,Escape.nativeWhitespace,CommentObservers.nativeObserve,CommentObservers.isNewline,
        CommentObservers.ordinary,hw,CommentObservers.advance]
   · by_cases hn : b.val=10 ∨ b.val=12 ∨ b.val=13
     · rcases hn with hb | hb | hb
       · have eq : b=10 := Fin.ext hb
         subst b
         simp [hv9,hv10,hv12,hv13,hv32,after,Escape.nativeWhitespace,CommentObservers.nativeObserve,CommentObservers.isNewline]
       · have eq : b=12 := Fin.ext hb
         subst b
         simp [hv9,hv10,hv12,hv13,hv32,after,Escape.nativeWhitespace,CommentObservers.nativeObserve,CommentObservers.isNewline]
       · have eq : b=13 := Fin.ext hb
         subst b
         cases bs with
         | nil => simp [hv9,hv10,hv12,hv13,hv32,after,Escape.nativeWhitespace,CommentObservers.nativeObserve,CommentObservers.isNewline]
         | cons c cs =>
           by_cases hc : c=10
           · subst c
             simp [hv9,hv10,hv12,hv13,hv32,after,Escape.nativeWhitespace,Escape.byte,CommentObservers.nativeObserve,CommentObservers.isNewline]
           · simp [hv9,hv10,hv12,hv13,hv32,after,Escape.nativeWhitespace,Escape.byte,hc,CommentObservers.nativeObserve,CommentObservers.isNewline]
     · simp [hv9,hv10,hv12,hv13,hv32,after,Escape.nativeWhitespace,hs,hn,CommentObservers.nativeObserve]

theorem metadata (xs : List Byte) (s : State) (r : CommentObservers.State) (block : Nat)
 (h : Related s r block) (ha : Admitted xs s) :
 Related (consume xs s) (CommentObservers.nativeObserve (xs.take (Escape.nativeWhitespace xs)) r) block := by
 rw [← observed]
 exact state_relation xs s r block h ha
end URLNativeWhitespace
