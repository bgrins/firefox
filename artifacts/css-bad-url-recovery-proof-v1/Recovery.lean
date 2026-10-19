import Std

namespace BadUrl

inductive Kind where
  | close | slash | newline | space | hex | other
  deriving DecidableEq, Repr

def classify (c : Char) : Kind :=
  if c = ')' then .close
  else if c = '\\' then .slash
  else if c = '\n' then .newline
  else if c = ' ' ∨ c = '\t' then .space
  else if ('0' ≤ c ∧ c ≤ '9') ∨ ('a' ≤ c ∧ c ≤ 'f') ∨ ('A' ≤ c ∧ c ≤ 'F') then .hex
  else .other

def optimized : List Char → List Char
  | [] => []
  | c :: cs => if classify c = .close then cs
    else if classify c = .slash then
      match cs with
      | [] => []
      | d :: ds => if classify d = .close ∨ classify d = .slash then optimized ds else optimized (d :: ds)
    else optimized cs

theorem optimized_cons (c : Char) (cs : List Char) : optimized (c :: cs) =
    if classify c = .close then cs else if classify c = .slash then
      match cs with
      | [] => []
      | d :: ds => if classify d = .close ∨ classify d = .slash then optimized ds else optimized (d :: ds)
    else optimized cs := by
  cases cs <;> rfl

def skipHex : Nat → List Char → List Char
  | 0, cs => cs
  | _ + 1, [] => []
  | n + 1, c :: cs => if classify c = .hex then skipHex n cs else c :: cs

def skipWhitespace : List Char → List Char
  | c :: cs => if classify c = .space ∨ classify c = .newline then cs else c :: cs
  | [] => []

def escapeSuffix : List Char → List Char
  | [] => []
  | c :: cs => if classify c = .hex then skipWhitespace (skipHex 5 cs) else cs

theorem skipHex_length (n : Nat) (cs : List Char) : (skipHex n cs).length ≤ cs.length := by
  induction n generalizing cs with
  | zero => simp [skipHex]
  | succ n ih =>
    cases cs with
    | nil => simp [skipHex]
    | cons c cs =>
      simp only [skipHex]
      split
      · exact Nat.le_trans (ih cs) (by simp)
      · exact Nat.le_refl _

theorem skipWhitespace_length (cs : List Char) : (skipWhitespace cs).length ≤ cs.length := by
  cases cs with
  | nil => simp [skipWhitespace]
  | cons c cs => simp [skipWhitespace]; split <;> simp_all

theorem escapeSuffix_length (cs : List Char) : (escapeSuffix cs).length ≤ cs.length := by
  cases cs with
  | nil => simp [escapeSuffix]
  | cons c cs =>
    simp only [escapeSuffix]
    split
    · exact Nat.le_trans (skipWhitespace_length _) (Nat.le_trans (skipHex_length _ _) (by simp))
    · simp

def specification (cs : List Char) : List Char :=
  match cs with
  | [] => []
  | c :: rest => match classify c with
    | .close => rest
    | .slash => match rest with
      | [] => []
      | d :: ds =>
        if classify d = .newline then specification (d :: ds)
        else specification (escapeSuffix (d :: ds))
    | _ => specification rest
termination_by cs.length
decreasing_by
  all_goals simp_wf
  have h := escapeSuffix_length (d :: ds)
  simp only [List.length_cons] at h
  omega

theorem optimized_skipHex (n : Nat) (cs : List Char) : optimized (skipHex n cs) = optimized cs := by
  induction n generalizing cs with
  | zero => rfl
  | succ n ih =>
    cases cs with
    | nil => rfl
    | cons c cs =>
      simp only [skipHex]
      split
      · rename_i hc
        rw [ih]
        simp [optimized_cons, hc]
      · rfl

theorem optimized_inert (c : Char) (cs : List Char)
    (hc : classify c ≠ .close) (hs : classify c ≠ .slash) : optimized (c :: cs) = optimized cs := by
  rw [optimized_cons, ite_eq_right hc, ite_eq_right hs]

theorem optimized_skipWhitespace (cs : List Char) : optimized (skipWhitespace cs) = optimized cs := by
  cases cs with
  | nil => rfl
  | cons c cs =>
    cases h : classify c <;> simp [skipWhitespace, h]
    all_goals exact (optimized_inert c cs (by simp [h]) (by simp [h])).symm

theorem optimized_escape (c : Char) (cs : List Char) :
    optimized (escapeSuffix (c :: cs)) =
      if classify c = .close ∨ classify c = .slash then optimized cs else optimized (c :: cs) := by
  cases h : classify c <;> simp [escapeSuffix, h, optimized_skipWhitespace, optimized_skipHex]
  all_goals exact (optimized_inert c cs (by simp [h]) (by simp [h])).symm

theorem suffix_equivalence (cs : List Char) : specification cs = optimized cs := by
  induction cs using (measure List.length).wf.induction with
  | h cs ih =>
    cases cs with
    | nil => simp [specification, optimized]
    | cons c rest =>
      rw [specification.eq_def, optimized_cons]
      cases hc : classify c <;> simp only [hc, reduceCtorEq, ite_true, ite_false]
      · cases rest with
        | nil => rfl
        | cons d ds =>
          dsimp only
          split
          · rename_i hd
            rw [ih (d :: ds) (by change (d :: ds).length < (c :: d :: ds).length; simp)]
            simp [hd]
          · rw [ih (escapeSuffix (d :: ds)) (by change (escapeSuffix (d :: ds)).length < (c :: d :: ds).length; have h := escapeSuffix_length (d :: ds); simp only [List.length_cons] at *; omega)]
            exact optimized_escape d ds
      all_goals exact ih rest (by change rest.length < (c :: rest).length; simp)


def trimWhitespace : List Char → List Char
  | [] => []
  | c :: cs => if classify c = .space ∨ classify c = .newline then trimWhitespace cs else c :: cs

def specificationHandoff (cs : List Char) : List Char :=
  match trimWhitespace cs with
  | [] => []
  | c :: rest => if classify c = .close then rest else specification (c :: rest)

def candidateHandoff (cs : List Char) : List Char :=
  match trimWhitespace cs with
  | [] => []
  | c :: rest => if classify c = .close then rest else optimized (c :: rest)

def originalHandoff (cs : List Char) : List Char :=
  match trimWhitespace cs with
  | [] => []
  | c :: rest => if classify c = .close then rest else optimized rest

theorem handoff_equivalence (cs : List Char) : candidateHandoff cs = specificationHandoff cs := by
  unfold candidateHandoff specificationHandoff
  cases trimWhitespace cs with
  | nil => rfl
  | cons c cs => dsimp only; rw [suffix_equivalence]

def slashPairs : Nat → List Char
  | 0 => []
  | n + 1 => '\\' :: '\\' :: slashPairs n

theorem pairs_preserve (n : Nat) (cs : List Char) : optimized (slashPairs n ++ cs) = optimized cs := by
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [slashPairs, List.cons_append]
    rw [optimized_cons]
    simpa [classify] using ih

theorem even_slashes_close (n : Nat) (cs : List Char) :
    optimized (slashPairs n ++ ')' :: cs) = cs := by
  rw [pairs_preserve, optimized_cons]
  simp [classify]

theorem odd_slashes_escape (n : Nat) (cs : List Char) :
    optimized ('\\' :: slashPairs n ++ ')' :: cs) = optimized cs := by
  induction n with
  | zero => rw [show slashPairs 0 = [] from rfl]; simp only [List.cons_append, List.nil_append]; rw [optimized_cons]; simp [classify]
  | succ n ih =>
    simp only [slashPairs, List.cons_append]
    rw [optimized_cons]
    simpa [classify] using ih

theorem one_slash_counterexample :
    originalHandoff [' ', '\\', ')', 'x', ')', 't'] ≠
      specificationHandoff [' ', '\\', ')', 'x', ')', 't'] := by rw [← handoff_equivalence]; decide

theorem two_slash_counterexample :
    originalHandoff [' ', '\\', '\\', ')', 'x', ')', 't'] ≠
      specificationHandoff [' ', '\\', '\\', ')', 'x', ')', 't'] := by rw [← handoff_equivalence]; decide

theorem six_hex_limit : escapeSuffix ['1', '2', '3', '4', '5', '6', '7', ')', 't', 'a', 'i', 'l'] = ['7', ')', 't', 'a', 'i', 'l'] := by decide

theorem hex_whitespace : escapeSuffix ['2', '9', ' ', ')', 't', 'a', 'i', 'l'] = [')', 't', 'a', 'i', 'l'] := by decide

theorem escaped_eof : specification ['\\'] = [] := by rw [suffix_equivalence]; decide

theorem invalid_newline_escape : specification ['\\', '\n', ')', 't', 'a', 'i', 'l'] = ['t', 'a', 'i', 'l'] := by rw [suffix_equivalence]; decide

theorem decoded_closer_is_data : specification ['\\', '2', '9', ' ', 'x', ')', 't', 'a', 'i', 'l'] = ['t', 'a', 'i', 'l'] := by rw [suffix_equivalence]; decide

theorem decoded_slash_is_data : specification ['\\', '5', 'c', ' ', ')', 't', 'a', 'i', 'l'] = ['t', 'a', 'i', 'l'] := by rw [suffix_equivalence]; decide

def normalize : List Char → List Char
  | [] => []
  | '\r' :: '\n' :: cs => '\n' :: normalize cs
  | '\r' :: cs => '\n' :: normalize cs
  | '\x0c' :: cs => '\n' :: normalize cs
  | '\x00' :: cs => '�' :: normalize cs
  | c :: cs => c :: normalize cs

theorem normalized_suffix_equivalence (raw : List Char) :
    specification (normalize raw) = optimized (normalize raw) := suffix_equivalence _

theorem raw_suffix_transfer (raw : List UInt8) (filtered : List Char)
    (decodeSuffix : List UInt8 → List Char)
    (correspondence : decodeSuffix raw = optimized filtered) :
    decodeSuffix raw = specification filtered := by
  rw [correspondence, suffix_equivalence]

theorem classification_boundaries :
    classify ')' = .close ∧ classify '\\' = .slash ∧ classify '\n' = .newline ∧
    classify ' ' = .space ∧ classify '\t' = .space ∧ classify '0' = .hex ∧
    classify 'F' = .hex ∧ classify 'g' = .other ∧ classify 'é' = .other := by decide

theorem normalization_boundaries :
    normalize ['\r', '\n', '\r', '\x0c', '\x00', 'é', '😀'] =
      ['\n', '\n', '\n', '�', 'é', '😀'] := by decide

#print axioms optimized_cons
#print axioms skipHex_length
#print axioms skipWhitespace_length
#print axioms escapeSuffix_length
#print axioms optimized_skipHex
#print axioms optimized_inert
#print axioms optimized_skipWhitespace
#print axioms optimized_escape
#print axioms suffix_equivalence
#print axioms handoff_equivalence
#print axioms pairs_preserve
#print axioms even_slashes_close
#print axioms odd_slashes_escape
#print axioms one_slash_counterexample
#print axioms two_slash_counterexample
#print axioms six_hex_limit
#print axioms hex_whitespace
#print axioms escaped_eof
#print axioms invalid_newline_escape
#print axioms decoded_closer_is_data
#print axioms decoded_slash_is_data
#print axioms normalized_suffix_equivalence
#print axioms raw_suffix_transfer
#print axioms classification_boundaries
#print axioms normalization_boundaries

end BadUrl
