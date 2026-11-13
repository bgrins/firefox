import Std

namespace FlexCollect

variable {α : Type}

def span (size : α → Rat) (gap : Rat) : List α → Rat
  | [] => 0
  | x :: xs => xs.foldl (fun used y => used + gap + size y) (size x)

def takeMore (size : α → Rat) (threshold gap used : Rat) : List α → List α × List α
  | [] => ([], [])
  | x :: xs =>
    if used + gap + size x ≤ threshold then
      let p := takeMore size threshold gap (used + gap + size x) xs
      (x :: p.1, p.2)
    else ([], x :: xs)

private theorem takeMore_rest_le (size : α → Rat) (threshold gap used : Rat)
    (xs : List α) : (takeMore size threshold gap used xs).2.length ≤ xs.length := by
  induction xs generalizing used with
  | nil => simp [takeMore]
  | cons x xs ih =>
    simp only [takeMore]
    split
    · exact Nat.le_trans (ih _) (Nat.le_succ _)
    · exact Nat.le_refl _

def collect (size : α → Rat) (threshold gap : Rat) (input : List α) : List (List α) :=
  match input with
  | [] => []
  | x :: xs =>
    if threshold < size x then [x] :: collect size threshold gap xs
    else
      let p := takeMore size threshold gap (size x) xs
      (x :: p.1) :: collect size threshold gap p.2
termination_by input.length
decreasing_by
  · simp_wf
  · have h := takeMore_rest_le size threshold gap (size x) xs
    simp_wf
    omega

def nowrap (input : List α) : List (List α) :=
  if input.isEmpty then [] else [input]

def PrefixesFit (size : α → Rat) (threshold gap : Rat) (line : List α) : Prop :=
  ∀ pre suffix, line = pre ++ suffix → pre ≠ [] → span size gap pre ≤ threshold

def NextLine (size : α → Rat) (threshold gap : Rat)
    (input line rest : List α) : Prop :=
  input = line ++ rest ∧ line ≠ [] ∧
    ((∃ x, line = [x] ∧ threshold < size x) ∨
      (PrefixesFit size threshold gap line ∧
        match rest with
        | [] => True
        | x :: _ => threshold < span size gap (line ++ [x])))

inductive Collected (size : α → Rat) (threshold gap : Rat) :
    List α → List (List α) → Prop
  | nil : Collected size threshold gap [] []
  | cons {input line rest lines} :
      NextLine size threshold gap input line rest →
      Collected size threshold gap rest lines →
      Collected size threshold gap input (line :: lines)

def Domain (threshold gap : Rat) : Prop := 0 ≤ threshold ∧ 0 ≤ gap

end FlexCollect
