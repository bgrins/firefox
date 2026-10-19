namespace TerminalString

inductive Unit where
  | slash | quote | other (value : Nat)
  deriving DecidableEq, Repr

structure Result where
  text : List Unit
  closed : Bool
  rest : List Unit
  deriving DecidableEq, Repr

def prepend (xs : List Unit) (r : Result) : Result :=
  { r with text := xs ++ r.text }

def consume : List Unit → Result
  | [] => ⟨[], false, []⟩
  | .quote :: xs => ⟨[], true, xs⟩
  | .other n :: xs => prepend [.other n] (consume xs)
  | [.slash] => ⟨[], false, []⟩
  | .slash :: x :: xs => prepend [x] (consume xs)

def slashes (n : Nat) : List Unit := List.replicate n .slash

theorem pairs (n : Nat) (tail : List Unit) :
    consume (slashes (2*n) ++ tail) = prepend (slashes n) (consume tail) := by
  induction n with
  | zero => simp [slashes, prepend]
  | succ n ih =>
    have he : 2 * (n+1) = Nat.succ (Nat.succ (2*n)) := by omega
    simp only [he, slashes, List.replicate_succ,
      List.cons_append]
    simp only [consume]
    change prepend [.slash] (consume (slashes (2*n) ++ tail)) = _
    rw [ih]
    simp [prepend, slashes]

theorem even_eof (n : Nat) : consume (slashes (2*n)) = ⟨slashes n, false, []⟩ := by
  simpa [consume, prepend] using pairs n []

theorem odd_eof (n : Nat) : consume (slashes (2*n+1)) = ⟨slashes n, false, []⟩ := by
  have he : slashes (2*n+1) = slashes (2*n) ++ [.slash] := by
    simp [slashes, List.replicate_succ' ]
  rw [he, pairs]
  simp [consume, prepend]

theorem even_quote (n : Nat) (tail : List Unit) :
    consume (slashes (2*n) ++ .quote :: tail) = ⟨slashes n, true, tail⟩ := by
  rw [pairs]
  simp [consume, prepend]

theorem odd_quote (n : Nat) (tail : List Unit) :
    consume (slashes (2*n+1) ++ .quote :: tail) =
      prepend (slashes n ++ [.quote]) (consume tail) := by
  have he : slashes (2*n+1) = slashes (2*n) ++ [.slash] := by
    simp [slashes, List.replicate_succ' ]
  rw [he, List.append_assoc, pairs]
  simp [consume, prepend, List.append_assoc]

theorem parity_split (n : Nat) : n = 2*(n/2) ∨ n = 2*(n/2)+1 := by omega

theorem decoded_eof (n : Nat) : consume (slashes n) = ⟨slashes (n/2), false, []⟩ := by
  rcases parity_split n with he | ho
  · exact (congrArg (fun k => consume (slashes k)) he).trans (even_eof _)
  · exact (congrArg (fun k => consume (slashes k)) ho).trans (odd_eof _)

def trailing : List Unit → Nat
  | [] => 0
  | .quote :: _ => 0
  | .other _ :: _ => 0
  | .slash :: xs => 1 + trailing xs

theorem trailing_run (n : Nat) (tail : List Unit) (h : trailing tail = 0) :
    trailing (slashes n ++ tail) = n := by
  induction n with
  | zero => simpa [slashes] using h
  | succ n ih =>
    change 1 + trailing (slashes n ++ tail) = n+1
    rw [ih]
    omega

theorem ordinary_prefix (xs : List Nat) (tail : List Unit) :
    consume (xs.map Unit.other ++ tail) = prepend (xs.map Unit.other) (consume tail) := by
  induction xs with
  | nil => simp [prepend]
  | cons n xs ih =>
    simp only [List.map_cons, List.cons_append, consume, ih]
    simp [prepend]

#print axioms ordinary_prefix
#print axioms pairs
#print axioms even_eof
#print axioms odd_eof
#print axioms even_quote
#print axioms odd_quote
#print axioms parity_split
#print axioms decoded_eof
#print axioms trailing_run
end TerminalString
