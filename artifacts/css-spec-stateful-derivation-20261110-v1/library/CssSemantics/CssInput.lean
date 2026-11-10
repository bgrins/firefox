import Lean

namespace CssSemantics.CssInput

inductive Point : Char → Char → Prop where
  | carriageReturn : Point '\r' '\n'
  | formFeed : Point '\x0c' '\n'
  | null : Point '\x00' '\uFFFD'
  | ordinary (c) : c ≠ '\r' → c ≠ '\x0c' → c ≠ '\x00' → Point c c

def point (c : Char) : Char :=
  if c = '\r' ∨ c = '\x0c' then '\n' else if c = '\x00' then '\uFFFD' else c

theorem point_iff (c d : Char) : point c = d ↔ Point c d := by
  constructor
  · intro equal
    subst d
    by_cases cr : c = '\r'
    · subst c; simpa [point] using Point.carriageReturn
    by_cases ff : c = '\x0c'
    · subst c; simpa [point] using Point.formFeed
    by_cases nul : c = '\x00'
    · subst c; simpa [point] using Point.null
    · simpa [point, cr, ff, nul] using Point.ordinary c cr ff nul
  · intro converted; cases converted <;> simp_all [point]

def NotPair (c : Char) (rest : List Char) : Prop :=
  ∀ tail, ¬ (c = '\r' ∧ rest = '\n' :: tail)

inductive Preprocess : List Char → List Char → Prop where
  | empty : Preprocess [] []
  | crlf {rest output} : Preprocess rest output → Preprocess ('\r' :: '\n' :: rest) ('\n' :: output)
  | single {c d rest output} : NotPair c rest → Point c d → Preprocess rest output →
      Preprocess (c :: rest) (d :: output)

def preprocess : List Char → List Char
  | [] => []
  | '\r' :: '\n' :: rest => '\n' :: preprocess rest
  | c :: rest => point c :: preprocess rest

theorem preprocess_cons {c rest} (noPair : NotPair c rest) :
    preprocess (c :: rest) = point c :: preprocess rest := by
  cases rest with
  | nil => by_cases cr : c = '\r' <;> simp [preprocess, cr]
  | cons d tail =>
      by_cases cr : c = '\r'
      · by_cases lf : d = '\n'
        · exact False.elim (noPair tail ⟨cr, by simp [lf]⟩)
        · simp [preprocess, cr, lf]
      · simp [preprocess, cr]

theorem Preprocess.result {input output} (parsed : Preprocess input output) : preprocess input = output := by
  induction parsed with
  | empty => rfl
  | crlf _ ih => simpa [preprocess] using ih
  | single noPair converted _ ih =>
      rw [preprocess_cons noPair, (point_iff _ _).mpr converted, ih]

theorem preprocess_sound (input : List Char) : Preprocess input (preprocess input) := by
  cases input with
  | nil => exact .empty
  | cons c rest =>
      cases rest with
      | nil =>
          have noPair : NotPair c [] := by simp [NotPair]
          rw [preprocess_cons noPair]
          exact .single noPair ((point_iff _ _).mp rfl) .empty
      | cons d tail =>
          by_cases cr : c = '\r'
          · by_cases lf : d = '\n'
            · subst c; subst d; exact .crlf (preprocess_sound tail)
            · have noPair : NotPair c (d :: tail) := by simp [NotPair, lf]
              rw [preprocess_cons noPair]
              exact .single noPair ((point_iff _ _).mp rfl) (preprocess_sound (d :: tail))
          · have noPair : NotPair c (d :: tail) := by simp [NotPair, cr]
            rw [preprocess_cons noPair]
            exact .single noPair ((point_iff _ _).mp rfl) (preprocess_sound (d :: tail))
termination_by input.length

theorem preprocess_iff (input output : List Char) : preprocess input = output ↔ Preprocess input output := by
  constructor
  · intro equal; simpa [← equal] using preprocess_sound input
  · exact Preprocess.result

theorem Preprocess.unique {input left right} (hl : Preprocess input left) (hr : Preprocess input right) :
    left = right := hl.result.symm.trans hr.result

def Normalized (input : List Char) : Prop :=
  ∀ c ∈ input, c ≠ '\r' ∧ c ≠ '\x0c' ∧ c ≠ '\x00'

theorem point_normalized (c : Char) : point c ≠ '\r' ∧ point c ≠ '\x0c' ∧ point c ≠ '\x00' := by
  unfold point
  split
  · decide
  · split
    · decide
    · simp_all

theorem Preprocess.normalized {input output} (parsed : Preprocess input output) : Normalized output := by
  induction parsed with
  | empty => simp [Normalized]
  | crlf _ ih => simpa [Normalized] using ih
  | @single c d rest output _ converted _ ih =>
      have valid := point_normalized c
      rw [(point_iff _ _).mpr converted] at valid
      simpa [Normalized] using And.intro valid ih

theorem preprocess_normalized (input : List Char) : Normalized (preprocess input) :=
  (preprocess_sound input).normalized

theorem normalized_fixed {input} (normal : Normalized input) : preprocess input = input := by
  induction input with
  | nil => rfl
  | cons c rest ih =>
      obtain ⟨valid, tail⟩ : (c ≠ '\r' ∧ c ≠ '\x0c' ∧ c ≠ '\x00') ∧ Normalized rest := by
        simpa [Normalized] using normal
      have converted : point c = c := by simp [point, valid.1, valid.2.1, valid.2.2]
      simpa [preprocess, valid.1, converted] using ih tail

theorem fixed_iff (input : List Char) : preprocess input = input ↔ Normalized input := by
  constructor
  · intro fixed; simpa [fixed] using preprocess_normalized input
  · exact normalized_fixed

theorem preprocess_idempotent (input : List Char) : preprocess (preprocess input) = preprocess input :=
  normalized_fixed (preprocess_normalized input)

theorem Preprocess.length_le {input output} (parsed : Preprocess input output) : output.length ≤ input.length := by
  induction parsed with
  | empty => simp
  | crlf _ ih => simp_all; omega
  | single _ _ _ ih => simpa using ih

theorem preprocess_length_le (input : List Char) : (preprocess input).length ≤ input.length :=
  (preprocess_sound input).length_le

end CssSemantics.CssInput
