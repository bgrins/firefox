import CssDerivation.Codec.Document.Profile

namespace CssDerivation.DocumentSchema
open Lean FirstOrder TypedCodec JsonSchema

theorem field_spec (j : Json) (name : String) (value : Json) :
    field j name = some value ↔ Field j name value := by
  unfold field Field
  cases j.getObjVal? name <;> simp [Except.toOption]

theorem permutation_of_counts (names keys : List String) (unique : names.Nodup)
    (lengths : keys.length = names.length)
    (counts : ∀ name ∈ names, keys.count name = 1) : keys.Perm names := by
  induction names generalizing keys with
  | nil => simpa using lengths
  | cons name rest ih =>
    obtain ⟨absent, unique⟩ := List.nodup_cons.mp unique
    have member : name ∈ keys := List.count_pos_iff.mp (by rw [counts name (by simp)]; decide)
    have split := List.perm_cons_erase member
    have lengthTail : (keys.erase name).length = rest.length := by
      have h := split.length_eq
      simp only [List.length_cons] at h lengths
      omega
    have countsTail : ∀ x ∈ rest, (keys.erase name).count x = 1 := by
      intro x hx
      have ne : x ≠ name := by intro equal; subst x; exact absent hx
      rw [List.count_erase_of_ne ne]
      exact counts x (by simp [hx])
    exact split.trans ((ih (keys.erase name) unique lengthTail countsTail).cons name)

theorem exactFields_spec {α : Type} (names : List String) (fields : List (String × α))
    (unique : names.Nodup) :
    exactFields names fields = true ↔ (fields.map Prod.fst).Perm names := by
  simp only [exactFields, Bool.and_eq_true, beq_iff_eq, List.all_eq_true]
  constructor
  · rintro ⟨lengths, counts⟩
    apply permutation_of_counts names _ unique
    · simpa using lengths
    · intro name member
      simpa [List.count_eq_countP, List.countP_map, Function.comp_def] using counts name member
  · intro permutation
    refine ⟨?_, ?_⟩
    · simpa using permutation.length_eq
    · intro name member
      have count := permutation.count_eq name
      have one := unique.count (a := name)
      simpa [List.count_eq_countP, List.countP_map, Function.comp_def, member] using count.trans one

theorem exact_keys_spec (j : Json) (names : List String) (unique : names.Nodup) :
    fieldsExactly j names = true ↔ ExactKeys j names := by
  cases j <;> simp [fieldsExactly, ExactKeys, exactFields_spec, unique]

end CssDerivation.DocumentSchema
