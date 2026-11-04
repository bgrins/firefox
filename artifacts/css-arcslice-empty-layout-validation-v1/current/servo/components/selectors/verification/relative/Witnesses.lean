/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import RelativeProofs

open Aeneas Aeneas.Std Relative RelativeProofs

namespace RelativeWitnesses

def sampleForest : PreorderForest 4 where
  parent := fun e => match e.val with
    | 0 => none
    | 2 => some ⟨1, by decide⟩
    | _ => some ⟨0, by decide⟩
  first := fun e => match e.val with
    | 0 => some ⟨1, by decide⟩
    | 1 => some ⟨2, by decide⟩
    | _ => none
  next := fun e => if e.val = 1 then some ⟨3, by decide⟩ else none
  finish := fun e => if e.val = 1 ∨ e.val = 2 then 3 else 4
  bounds := by decide
  parent_bounds := by decide
  parent_inside := by decide
  next_position := by decide
  next_parent := by decide
  next_bound := by decide
  next_none := by decide
  first_position := by decide
  first_parent := by decide
  first_bound := by decide
  first_none := by decide

theorem branch_and_chain :
    sampleForest.parent ⟨1, by decide⟩ = some ⟨0, by decide⟩ ∧
    sampleForest.parent ⟨2, by decide⟩ = some ⟨1, by decide⟩ ∧
    sampleForest.parent ⟨3, by decide⟩ = some ⟨0, by decide⟩ := by decide

def sampleIdentity (element : Fin 4) : Usize :=
  Usize.ofNat element.val (by have h := element.isLt; scalar_tac)

def sampleOps : tree.Element (Fin 4) where
  coremarkerCopyInst := { cloneInst := { clone := fun e => .ok e } }
  «opaque» := fun e => .ok (sampleIdentity e)
  first_element_child := fun e => .ok (sampleForest.first e)
  next_sibling_element := fun e => .ok (sampleForest.next e)
  parent_element := fun e => .ok (sampleForest.parent e)
  add_element_unique_hashes := fun _ filter => .ok (true, filter)

def sampleNavigation : Navigation sampleForest sampleOps where
  identity := sampleIdentity
  identity_injective := by
    intro first second heq
    have hval := congrArg UScalar.val heq
    simp [sampleIdentity, Usize.ofNat] at hval
    exact Fin.ext hval
  opaque_eq := fun _ => rfl
  first_eq := fun _ => rfl
  next_eq := fun _ => rfl
  parent_eq := fun _ => rfl

#print axioms branch_and_chain
#print axioms sampleForest
#print axioms sampleNavigation

end RelativeWitnesses
