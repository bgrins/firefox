import TerminalString
namespace ParityRepair
open TerminalString

def remove (n : Nat) : Bool := n % 2 == 1
def repaired (n : Nat) : List TerminalString.Unit := slashes (n - if remove n then 1 else 0) ++ [.quote]

theorem retained_even (n : Nat) : n - (if remove n then 1 else 0) = 2*(n/2) := by
  unfold remove
  split <;> simp_all <;> omega

theorem recovered (n : Nat) : consume (repaired n) = ⟨slashes (n/2), true, []⟩ := by
  simp only [repaired, retained_even]
  exact even_quote _ []

theorem decoded_preserved (n : Nat) : (consume (repaired n)).text = (consume (slashes n)).text := by
  rw [recovered, decoded_eof]

theorem closes_before_suffix (n : Nat) (suffix : List TerminalString.Unit) :
    consume (repaired n ++ suffix) = ⟨slashes (n/2), true, suffix⟩ := by
  simp only [repaired, retained_even, List.append_assoc, List.cons_append, List.nil_append]
  exact even_quote _ _

theorem even_never_deleted (n : Nat) : remove (2*n) = false := by simp [remove]
theorem odd_deleted (n : Nat) : remove (2*n+1) = true := by simp [remove, Nat.add_mod]

theorem original_even_counterexample :
    consume (slashes (2-1) ++ [.quote]) ≠ consume (repaired 2) := by decide

theorem never_delete_counterexample :
    consume (slashes 1 ++ [.quote]) ≠ consume (repaired 1) := by decide

theorem framed_recovery (pre : List Nat) (n : Nat) (suffix : List TerminalString.Unit) :
    consume (pre.map TerminalString.Unit.other ++ repaired n ++ suffix) =
      ⟨pre.map TerminalString.Unit.other ++ slashes (n/2), true, suffix⟩ := by
  rw [List.append_assoc, ordinary_prefix, closes_before_suffix]
  rfl

theorem deletion_bounded (n : Nat) : (if remove n then 1 else 0) ≤ n := by
  unfold remove
  split <;> simp_all <;> omega

theorem offset_alignment (pre n closing : Nat) :
    pre + n + closing - (if remove n then 1 else 0) = pre + 2*(n/2) + closing := by
  have h := retained_even n
  have hb := deletion_bounded n
  omega

#print axioms deletion_bounded
#print axioms offset_alignment
#print axioms framed_recovery
#print axioms retained_even
#print axioms recovered
#print axioms decoded_preserved
#print axioms closes_before_suffix
#print axioms even_never_deleted
#print axioms odd_deleted
#print axioms original_even_counterexample
#print axioms never_delete_counterexample
end ParityRepair
