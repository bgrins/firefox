import PublicCache
set_option autoImplicit false
namespace FunctionMatching
open PublicCache

def pair (a b : Byte) : Bool := decide
 (a.val=b.val ∨ (65≤a.val ∧ a.val≤90 ∧ b.val=a.val+32) ∨
   (65≤b.val ∧ b.val≤90 ∧ a.val=b.val+32))

def referenceName : List Byte → List Byte → Bool
 | [],[] => true
 | a::as,b::bs => pair a b && referenceName as bs
 | _,_ => false

theorem lower_pair (a b : Byte) : (lower a == lower b)=pair a b := by
 apply Bool.eq_iff_iff.mpr
 by_cases ha : 65≤a.val ∧ a.val≤90 <;> by_cases hb : 65≤b.val ∧ b.val≤90 <;>
   simp [lower,ha,hb,pair] <;> omega

theorem name_matching (as bs : List Byte) :
 (as.map lower == bs.map lower)=referenceName as bs := by
 induction as generalizing bs with
 | nil => cases bs <;> rfl
 | cons a as ih =>
   cases bs with
   | nil => rfl
   | cons b bs => simpa [referenceName,lower_pair] using congrArg (fun v => pair a b && v) (ih bs)

def referenceRelevant (names : List (List Byte)) : Token → Bool
 | .function name => names.any (referenceName name)
 | _ => false

theorem relevance (names : List (List Byte)) (token : Token) :
 relevant names token=referenceRelevant names token := by
 cases token <;> simp [relevant,referenceRelevant,name_matching]

end FunctionMatching
