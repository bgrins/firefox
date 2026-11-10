import Lean

namespace CssSemantics.CodePointInput

abbrev CodePoint := Fin 0x110000

abbrev Surrogate (p : CodePoint) : Prop := 0xd800 ≤ p.val ∧ p.val ≤ 0xdfff

def ofNat? (n : Nat) : Option CodePoint := if h : n < 0x110000 then some ⟨n, h⟩ else none

def point (p : CodePoint) : Char :=
  if p.val = 0x0d ∨ p.val = 0x0c then '\n'
  else if p.val = 0 ∨ Surrogate p then '�'
  else Char.ofNat p.val

inductive Point : CodePoint → Char → Prop where
  | carriageReturn (p) : p.val = 0x0d → Point p '\n'
  | formFeed (p) : p.val = 0x0c → Point p '\n'
  | null (p) : p.val = 0 → Point p '�'
  | surrogate (p) : Surrogate p → Point p '�'
  | ordinary (p c) : c.toNat = p.val → p.val ≠ 0x0d → p.val ≠ 0x0c → p.val ≠ 0 → Point p c

def NotPair (p : CodePoint) (rest : List CodePoint) : Prop :=
  ∀ q tail, rest = q :: tail → ¬ (p.val = 0x0d ∧ q.val = 0x0a)

inductive Preprocess : List CodePoint → List Char → Prop where
  | empty : Preprocess [] []
  | crlf {p q rest output} : p.val = 0x0d → q.val = 0x0a → Preprocess rest output →
      Preprocess (p :: q :: rest) ('\n' :: output)
  | single {p c rest output} : NotPair p rest → Point p c → Preprocess rest output →
      Preprocess (p :: rest) (c :: output)

def preprocess : List CodePoint → List Char
  | [] => []
  | [p] => [point p]
  | p :: q :: rest =>
      if p.val = 0x0d ∧ q.val = 0x0a then '\n' :: preprocess rest
      else point p :: preprocess (q :: rest)

def filterValues (source : List Nat) : Option (List Char) :=
  (source.mapM ofNat?).map preprocess

def embed (c : Char) : CodePoint :=
  ⟨c.toNat, by
    have valid := c.valid
    change c.toNat < 0xd800 ∨ (0xdfff < c.toNat ∧ c.toNat < 0x110000) at valid
    omega⟩

def Normalized (source : List Char) : Prop :=
  ∀ c ∈ source, c ≠ '\r' ∧ c ≠ '\x0c' ∧ c ≠ '\x00'

end CssSemantics.CodePointInput
