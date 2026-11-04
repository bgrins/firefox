/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Normalized.AncestorLoopProofs
public import Normalized.RecursiveCollectorProofs
@[expose] public section
open Aeneas Aeneas.Std Result Collection
open CollectionStepProofs CollectionInvariantProofs RecursiveCollectionProofs
open AncestorIteratorProofs AncestorProgressProofs AncestorLoopProofs
namespace AncestorContracts
variable {I A D L N P BN BL C E : Type}
local notation "Component" => parser.Component I A D L N P BN BL C E
local notation "Inst" => parser.SelectorImpl I A D L N P BN BL C E
local notation "Iter" => parser.SelectorIter I A D L N P BN BL C E

inductive Phase where
  | subject
  | ancestor

def afterBoundary : parser.Combinator → Phase
  | .PseudoElement | .SlotAssignment | .Part => .subject
  | _ => .ancestor

def boundaryIndex (slice : Slice Component) (index : Nat) (c : parser.Combinator) : Nat :=
  match c with
  | .NextSibling | .LaterSibling => skipIndex slice (index + 1)
  | _ => index + 1

inductive PhaseReach (slice : Slice Component) (origin : Nat) : Phase → Nat → Prop
  | initial : PhaseReach slice origin .subject origin
  | subjectStep (cursor : Nat) (h : cursor < slice.len)
      (before : PhaseReach slice origin .subject cursor)
      (ordinary : ∀ c, slice[cursor] ≠ parser.Component.Combinator c) :
      PhaseReach slice origin .subject (cursor + 1)
  | boundary (cursor : Nat) (h : cursor < slice.len) (c : parser.Combinator)
      (before : PhaseReach slice origin .subject cursor)
      (at_boundary : slice[cursor] = parser.Component.Combinator c) :
      PhaseReach slice origin (afterBoundary c) (boundaryIndex slice cursor c)
  | ancestorStep (cursor picked : Nat)
      (before : PhaseReach slice origin .ancestor cursor)
      (emitted : Yield slice cursor picked) :
      PhaseReach slice origin .ancestor (picked + 1)

def FullRegion (subjectGood ancestorGood : Component → Prop)
    (slice : Slice Component) (origin : Nat) : Prop :=
  (∀ cursor, PhaseReach slice origin .subject cursor →
    ∀ h : cursor < slice.len, subjectGood slice[cursor]) ∧
  (∀ cursor picked, PhaseReach slice origin .ancestor cursor →
    Yield slice cursor picked → ∀ h : picked < slice.len, ancestorGood slice[picked])

def policies (allowed : U32 → Prop) (inst : Inst) (quirks : context.QuirksMode) :
    Nat → (Component → Prop) × (Component → Prop)
  | 0 => (fun component => nested component = false,
      fun component => nested component = false ∧
        (parser.simple_selector_hash inst component quirks
          ⦃ result => ∀ raw ∈ result, allowed (masked raw) ⦄))
  | depth + 1 =>
    let child := policies allowed inst quirks depth
    (fun component => match component with
      | .Is list | .Where list =>
        (selectorsOf list).val.length = 1 → ∀ selector ∈ (selectorsOf list).val,
          FullRegion child.1 child.2 selector._0.value.entries 0
      | _ => True,
     fun component => match component with
      | .Is list | .Where list =>
        (selectorsOf list).val.length = 1 → ∀ selector ∈ (selectorsOf list).val,
          GoodRegion child.2 selector._0.value.entries 0
      | component => nested component = false ∧
        (parser.simple_selector_hash inst component quirks
          ⦃ result => ∀ raw ∈ result, allowed (masked raw) ⦄))

def FullGood (allowed : U32 → Prop) (inst : Inst) (quirks : context.QuirksMode)
    (depth : Nat) (slice : Slice Component) (origin : Nat) : Prop :=
  FullRegion (policies allowed inst quirks depth).1 (policies allowed inst quirks depth).2
    slice origin

end AncestorContracts
