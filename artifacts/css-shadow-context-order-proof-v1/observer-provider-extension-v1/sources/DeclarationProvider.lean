import Base
namespace ShadowOrder

def rawImportance (declarations : List α) (bits : List Bool) : List (α × Bool) :=
 declarations.zip bits

def anyImportantBits (bits : List Bool) : Bool := !(bits.all (! ·))

theorem any_bits (bits : List Bool) : anyImportantBits bits = bits.any id := by
 induction bits with
 | nil => rfl
 | cons bit bits ih =>
   cases bit <;> simp [anyImportantBits,List.all_cons,List.any_cons] at * <;> exact ih

theorem provider_importance_consistent (declarations : List α) (bits : List Bool)
 (h : declarations.length = bits.length) :
 anyImportantBits bits = (rawImportance declarations bits).any Prod.snd := by
 rw [any_bits]
 have hm := List.map_snd_zip (l₁ := declarations) (l₂ := bits) (Nat.le_of_eq h.symm)
 calc
  bits.any id = ((declarations.zip bits).map Prod.snd).any id := congrArg (fun xs => xs.any id) hm.symm
  _ = (rawImportance declarations bits).any Prod.snd := by simp [rawImportance,List.any_map]

#print axioms provider_importance_consistent
end ShadowOrder
