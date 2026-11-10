import CssSemantics.CssCodePointInputLaws

namespace CssSemantics.DomString

open CodePointInput

abbrev CodeUnit := Fin 0x10000

abbrev Leading (u : CodeUnit) : Prop := 0xd800 ≤ u.val ∧ u.val ≤ 0xdbff
abbrev Trailing (u : CodeUnit) : Prop := 0xdc00 ≤ u.val ∧ u.val ≤ 0xdfff

def unitOfNat? (n : Nat) : Option CodeUnit := if h : n < 0x10000 then some ⟨n, h⟩ else none

def unitPoint (u : CodeUnit) : CodePoint := ⟨u.val, by have := u.isLt; omega⟩

def pairPoint (u v : CodeUnit) (lead : Leading u) (trail : Trailing v) : CodePoint :=
  ⟨(u.val - 0xd800) * 0x400 + (v.val - 0xdc00) + 0x10000, by
    obtain ⟨_, _⟩ := lead
    obtain ⟨_, _⟩ := trail
    omega⟩

def NoPair (u : CodeUnit) (rest : List CodeUnit) : Prop :=
  ∀ v tail, rest = v :: tail → ¬ (Leading u ∧ Trailing v)

inductive Step : List CodeUnit → CodePoint → List CodeUnit → Prop where
  | pair (u v p rest) : Leading u → Trailing v →
      p.val = (u.val - 0xd800) * 0x400 + (v.val - 0xdc00) + 0x10000 →
      Step (u :: v :: rest) p rest
  | single (u p rest) : NoPair u rest → p.val = u.val → Step (u :: rest) p rest

def next : List CodeUnit → Option (CodePoint × List CodeUnit)
  | [] => none
  | [u] => some (unitPoint u, [])
  | u :: v :: rest =>
      if h : Leading u ∧ Trailing v then some (pairPoint u v h.1 h.2, rest)
      else some (unitPoint u, v :: rest)

def decode : List CodeUnit → List CodePoint
  | [] => []
  | [u] => [unitPoint u]
  | u :: v :: rest =>
      if h : Leading u ∧ Trailing v then pairPoint u v h.1 h.2 :: decode rest
      else unitPoint u :: decode (v :: rest)

inductive Decoded : List CodeUnit → List CodePoint → Prop where
  | empty : Decoded [] []
  | cons {source p rest output} : Step source p rest → Decoded rest output →
      Decoded source (p :: output)

def preprocess (source : List CodeUnit) : List Char := CodePointInput.preprocess (decode source)

def Prepared (source : List CodeUnit) (output : List Char) : Prop :=
  ∃ points, Decoded source points ∧ CodePointInput.Preprocess points output

def decodeValues (source : List Nat) : Option (List Nat) :=
  (source.mapM unitOfNat?).map fun units => (decode units).map Fin.val

def prepareValues (source : List Nat) : Option (List Char) :=
  (source.mapM unitOfNat?).map preprocess

def nextValues (source : List Nat) : Option (Option (Nat × List Nat)) :=
  (source.mapM unitOfNat?).map fun units => (next units).map fun (p, rest) => (p.val, rest.map Fin.val)

def JavaScriptLength (source : List CodeUnit) : Prop := source.length ≤ 2 ^ 53 - 1

end CssSemantics.DomString
