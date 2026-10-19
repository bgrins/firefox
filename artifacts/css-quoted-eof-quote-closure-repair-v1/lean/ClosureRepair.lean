import TerminalString
namespace ClosureRepair
open TerminalString

def genuine (n : Nat) : Bool := n % 2 == 0
def raw (n : Nat) : List TerminalString.Unit := slashes n ++ [.quote]
def repaired (n : Nat) : List TerminalString.Unit := raw n ++ if genuine n then [] else [.quote]
def decoded (n : Nat) : List TerminalString.Unit := slashes (n/2) ++ if genuine n then [] else [.quote]

theorem even_genuine (n : Nat) : genuine (2*n) = true := by simp [genuine]
theorem odd_not_genuine (n : Nat) : genuine (2*n+1) = false := by simp [genuine, Nat.add_mod]

theorem classification (n : Nat) : (consume (raw n)).closed = genuine n := by
  rcases parity_split n with he | ho
  · rw [he]
    simp [raw, even_quote, even_genuine]
  · rw [ho]
    simp [raw, odd_quote, odd_not_genuine, prepend, consume]

theorem decoded_raw (n : Nat) : (consume (raw n)).text = decoded n := by
  rcases parity_split n with he | ho
  · rw [he]
    simp [raw, decoded, even_quote, even_genuine]
  · rw [ho]
    simp [raw, decoded, odd_quote, odd_not_genuine, prepend, consume]
    congr 2 <;> omega

theorem repaired_with_suffix (n : Nat) (suffix : List TerminalString.Unit) :
    consume (repaired n ++ suffix) = ⟨decoded n, true, suffix⟩ := by
  rcases parity_split n with he | ho
  · rw [he]
    simp [repaired, raw, decoded, even_genuine, even_quote, List.append_assoc]
  · rw [ho]
    simp [repaired, raw, decoded, odd_not_genuine, List.append_assoc,
      odd_quote, consume, prepend]
    congr 2 <;> omega

theorem decoded_preserved (n : Nat) : (consume (repaired n)).text = (consume (raw n)).text := by
  have h := repaired_with_suffix n []
  simp only [List.append_nil] at h
  rw [h, decoded_raw]

theorem no_quote_eof_open : (consume []).closed = false := rfl

theorem old_closure_counterexample :
    consume (raw 1 ++ [.other 1]) ≠ consume (repaired 1 ++ [.other 1]) := by decide

theorem always_append_counterexample :
    consume (raw 0 ++ [.quote] ++ [.other 1]) ≠ consume (repaired 0 ++ [.other 1]) := by decide

theorem framed_recovery (pre : List Nat) (n : Nat) (suffix : List TerminalString.Unit) :
    consume (pre.map TerminalString.Unit.other ++ repaired n ++ suffix) =
      ⟨pre.map TerminalString.Unit.other ++ decoded n, true, suffix⟩ := by
  rw [List.append_assoc, ordinary_prefix, repaired_with_suffix]
  rfl

#print axioms framed_recovery
#print axioms even_genuine
#print axioms odd_not_genuine
#print axioms classification
#print axioms decoded_raw
#print axioms repaired_with_suffix
#print axioms decoded_preserved
#print axioms no_quote_eof_open
#print axioms old_closure_counterexample
#print axioms always_append_counterexample
end ClosureRepair
