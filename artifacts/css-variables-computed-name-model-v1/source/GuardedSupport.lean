import CssSemantics.Variables

namespace CssSemantics.GuardedSolver

def remove (entries : List (String × VariableExpr Token)) (name : String) :=
  entries.filter fun entry => decide (entry.1 ≠ name)

theorem remove_length_le (entries : List (String × VariableExpr Token)) (name : String) :
    (remove entries name).length ≤ entries.length := List.length_filter_le _ _

theorem remove_length_lt (entries : List (String × VariableExpr Token))
    (found : entries.lookup name = some expression) :
    (remove entries name).length < entries.length := by
  induction entries with
  | nil => simp at found
  | cons entry rest ih =>
    rcases entry with ⟨key, value⟩
    by_cases same : key = name
    · subst key
      simp only [remove, List.filter_cons, ne_eq, not_true_eq_false, decide_false,
        Bool.false_eq_true, ↓reduceIte, List.length_cons]
      exact Nat.lt_succ_of_le (remove_length_le rest name)
    · have diff : name ≠ key := Ne.symm same
      have unequal : (name == key) = false := beq_eq_false_iff_ne.mpr diff
      simp [List.lookup_cons, unequal] at found
      have smaller := ih found
      simpa [remove, same] using Nat.succ_lt_succ smaller

theorem remove_lookup_other (entries : List (String × VariableExpr Token))
    (different : target ≠ owner) :
    (remove entries owner).lookup target = entries.lookup target := by
  induction entries with
  | nil => rfl
  | cons entry rest ih =>
    rcases entry with ⟨key, value⟩
    by_cases removed : key = owner
    · subst key
      have unequal : (target == owner) = false := beq_eq_false_iff_ne.mpr different
      simpa [remove, List.lookup_cons, unequal] using ih
    · simp [remove] at ih
      simp [remove, removed, List.lookup_cons, ih]

end CssSemantics.GuardedSolver
