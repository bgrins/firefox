import ConstructedCoverage
import DeclarationProvider
namespace ShadowOrder

theorem visible_zip_important_implies_provider_bit
 (declarations : List α) (bits : List Bool) (declaration : α)
 (present : (declaration,true) ∈ rawImportance declarations bits) :
 anyImportantBits bits = true := by
 induction declarations generalizing bits with
 | nil => simp [rawImportance] at present
 | cons first rest ih =>
   cases bits with
   | nil => simp [rawImportance] at present
   | cons bit tail =>
     simp only [rawImportance,List.zip_cons_cons,List.mem_cons] at present
     rcases present with same | later
     · have bitTrue : bit = true := (congrArg Prod.snd same).symm
       simp [anyImportantBits,bitTrue]
     · have tailBit := ih tail later
       cases bit <;> simp_all [anyImportantBits]

def decodeProviderBits (declarations : List Declaration) (bits : List Bool) : List Declaration :=
 (rawImportance declarations bits).map fun pair => {pair.1 with important := pair.2}

theorem decoded_important_event_implies_native_any_important
 (resolve : Declaration → AliasDecision α) (physical : Nat → Nat) (property : Nat)
 (entry : Entry) (declarations : List Declaration) (bits : List Bool)
 (decoded : entry.rule.declarations = decodeProviderBits declarations bits)
 (action : AliasDecision α) (present : action ∈ resolvedImportantHalf resolve physical property entry) :
 anyImportantBits bits = true := by
 have important := resolved_event_has_important_bit resolve physical property entry action present
 rcases List.any_eq_true.mp important with ⟨declaration,member,bit⟩
 rw [decoded] at member
 unfold decodeProviderBits at member
 rcases List.mem_map.mp member with ⟨⟨original,flag⟩,inZip,rfl⟩
 change flag = true at bit
 subst flag
 exact visible_zip_important_implies_provider_bit declarations bits original inZip

#print axioms visible_zip_important_implies_provider_bit
#print axioms decoded_important_event_implies_native_any_important
end ShadowOrder
