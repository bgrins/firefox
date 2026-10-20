import BadURL
import Escape
import Boundary
set_option maxRecDepth 4096
set_option maxHeartbeats 4000000
namespace BadURLEscape
open BadURL
abbrev Unit := Boundary.Unit
abbrev bytes := Boundary.bytes

def Safe (b : Byte) : Prop := b ≠ 41 ∧ b ≠ 92

theorem safe_prefix (pre tail : List Byte) (safe : ∀ b ∈ pre, Safe b) :
 native (pre++tail) = add pre.length (native tail) := by
 induction pre with
 | nil => simp [add]
 | cons b bs ih =>
   have hb := safe b (by simp)
   have ih := ih (fun c hc => safe c (by simp [hc]))
   have h41 : (b == 41) = false := by simpa using hb.1
   have h92 : (b == 92) = false := by simpa using hb.2
   simp [native,h41,h92,ih,add,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]

theorem escape_chunk (first : Byte) (rest tail : List Byte) (safe : ∀ b ∈ rest, Safe b) :
 native (92::first::(rest++tail)) = add (2+rest.length) (native tail) := by
 by_cases special : first = 41 ∨ first = 92
 · rcases special with rfl | rfl <;> simp [native,safe_prefix rest tail safe,add,← Nat.add_assoc]
 · have h41 : (first == 41) = false := by simp_all
   have h92 : (first == 92) = false := by simp_all
   simp [native,h41,h92,safe_prefix rest tail safe,add,← Nat.add_assoc]

theorem classified_safe : ∀ (b : Byte), (HexPrefix.nativeDigit b).isSome → Safe b := by unfold Safe; decide

theorem digit_safe (b : Byte) (d : Nat) (h : HexPrefix.nativeDigit b = some d) : Safe b := by
 apply classified_safe b
 simp [h]

theorem hex_safe (fuel : Nat) (xs : List Byte) (initial) :
 ∀ b ∈ xs.take (HexPrefix.run fuel xs initial).count, Safe b := by
 induction fuel generalizing xs initial with
 | zero => simp [HexPrefix.run]
 | succ fuel ih =>
   cases xs with
   | nil => simp
   | cons c cs =>
     cases hd : HexPrefix.nativeDigit c with
     | none => simp [HexPrefix.run,hd]
     | some d =>
       have hc := digit_safe c d hd
       have ht := ih cs (initial*16+d)
       simpa [HexPrefix.run,hd,Nat.add_comm 1] using (show ∀ b ∈ c::cs.take (HexPrefix.run fuel cs (initial*16+d)).count, Safe b from by
         intro b hb; rcases List.mem_cons.mp hb with rfl | hb; exact hc; exact ht b hb)

theorem whitespace_byte_safe (b : Byte)
 (h : b.val = 9 ∨ b.val = 10 ∨ b.val = 12 ∨ b.val = 13 ∨ b.val = 32) : Safe b := by
 constructor
 · intro he; have hv := congrArg Fin.val he; change b.val = 41 at hv; omega
 · intro he; have hv := congrArg Fin.val he; change b.val = 92 at hv; omega

theorem whitespace_safe (xs : List Byte) :
 ∀ b ∈ xs.take (Escape.nativeWhitespace xs), Safe b := by
 cases xs with
 | nil => simp
 | cons c cs =>
   simp only [Escape.nativeWhitespace]
   split
   · rename_i h
     simp only [List.take_succ_cons,List.take_zero,List.mem_cons,List.not_mem_nil,or_false]
     intro b hb; subst b
     exact whitespace_byte_safe c (by omega)
   · split
     · rename_i h
       split
       · rename_i pair
         cases cs with
         | nil => simp at pair
         | cons d ds =>
           have he : d = Escape.byte 10 := by simpa using pair.2
           subst d
           simp only [List.take_succ_cons,List.take_zero,List.mem_cons,List.not_mem_nil,or_false]
           intro b hb; rcases hb with rfl | rfl
           · exact whitespace_byte_safe _ (by omega)
           · exact whitespace_byte_safe _ (by decide)
       · simp only [List.take_succ_cons,List.take_zero,List.mem_cons,List.not_mem_nil,or_false]
         intro b hb; subst b
         exact whitespace_byte_safe c (by omega)
     · simp

theorem hex_whitespace_safe (xs : List Byte) :
 ∀ b ∈ xs.take ((HexPrefix.run 6 xs 0).count + Escape.nativeWhitespace (HexPrefix.run 6 xs 0).rest), Safe b := by
 rw [List.take_add, ← HexPrefix.exact_remainder]
 intro b hb
 rcases List.mem_append.mp hb with h | h
 · exact hex_safe 6 xs 0 b h
 · exact whitespace_safe _ b h

theorem escape_positive (b : Byte) (bs : List Byte) : 0 < (Escape.native (b::bs)).count := by
 simp only [Escape.native]
 cases hd : HexPrefix.nativeDigit b with
 | some d => simp only [hd,HexPrefix.run]; omega
 | none =>
   simp only [hd]
   split
   · decide
   · simp only [List.length_take,List.length_cons]
     have hw : 0 < Escape.width b := by
       unfold Escape.width
       split
       · omega
       · split
         · omega
         · split <;> omega
     omega

theorem consumed_tail_safe (u : Unit) (us : List Unit) :
 ∀ b ∈ ((bytes (u::us)).take (Escape.native (bytes (u::us))).count).tail, Safe b := by
 have form : bytes (u::us) = u.first :: (u.rest ++ bytes us) := rfl
 cases hd : HexPrefix.nativeDigit u.first with
 | some d =>
   have hs := hex_whitespace_safe (bytes (u::us))
   simp only [form,Escape.native,hd] at hs ⊢
   intro b hb
   exact hs b (List.mem_of_mem_tail hb)
 | none =>
   simp only [form,Escape.native,hd]
   split
   · simp
   · have widthEq : Escape.width u.first = u.bytes.length := by
       simpa [Boundary.Unit.bytes,Nat.add_comm] using u.lengthWidth.symm
     have taken : List.take (Escape.width u.first) (bytes (u::us)) = u.bytes := by
       rw [widthEq]
       change (u.bytes ++ bytes us).take u.bytes.length = u.bytes
       simp
     rw [← form,taken]
     have re : (bytes (u::us)).take u.bytes.length = u.bytes := by
       change (u.bytes ++ bytes us).take u.bytes.length = u.bytes
       simp
     rw [re]
     intro b hb
     have hc := u.continuation b hb
     constructor
     · intro he; have hv := congrArg Fin.val he; change b.val = 41 at hv; omega
     · intro he; have hv := congrArg Fin.val he; change b.val = 92 at hv; omega

theorem escape_grouping (u : Unit) (us : List Unit) :
 native (92::bytes (u::us)) =
 add (1+(Escape.native (bytes (u::us))).count)
   (native ((bytes (u::us)).drop (Escape.native (bytes (u::us))).count)) := by
 let xs := bytes (u::us)
 let n := (Escape.native xs).count
 have positive : 0 < n := escape_positive u.first (u.rest ++ bytes us)
 have bound : n ≤ xs.length := Escape.consumption_bound xs
 have part := List.take_append_drop n xs
 have safe := consumed_tail_safe u us
 cases hp : xs.take n with
 | nil =>
   have hn := (List.take_eq_nil_iff.mp hp)
   have length : 0 < xs.length := by simp [xs,Boundary.bytes,Boundary.Unit.bytes]
   rcases hn with hn | hn
   · omega
   · simp [hn] at length
 | cons first rest =>
   have hs : ∀ b ∈ rest, Safe b := by simpa [xs,n,hp] using safe
   have len : 1+rest.length = n := by
     have hl := congrArg List.length hp
     simp only [List.length_take,List.length_cons] at hl
     omega
   have ex : xs = first::(rest ++ xs.drop n) := by rw [hp] at part; exact part.symm
   calc native (92::xs) = native (92::first::(rest ++ xs.drop n)) := congrArg (fun tail => native (92::tail)) ex
        _ = add (2+rest.length) (native (xs.drop n)) := escape_chunk _ _ _ hs
        _ = add (1+n) (native (xs.drop n)) := by rw [show 2+rest.length=1+n by omega]

end BadURLEscape
