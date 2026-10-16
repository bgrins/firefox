/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Normalized.Funs
@[expose] public section
open Aeneas Aeneas.Std Result
open Collection
set_option linter.unusedVariables false
set_option linter.unusedSimpArgs false
namespace CollectionStepProofs
variable {I A D L N P BN BL C E Walk : Type}
local notation "Component" => parser.Component I A D L N P BN BL C E
local notation "Instance" => parser.SelectorHashIterator Walk I A D L N P BN BL C E

def nested (component : Component) : Bool :=
  match component with
  | .Is _ | .Where _ => true
  | _ => false

def storeHash (hash : Option U32) (hashes : Array U32 4#usize) (len : Usize) :
    Result (Bool × Array U32 4#usize × Usize) := do
  match hash with
  | none => ok (true, hashes, len)
  | some hash =>
    let masked ← lift (hash &&& bloom.BLOOM_HASH_MASK)
    let hashes ← Array.update hashes len masked
    let len ← len + 1#usize
    let slice ← lift (Array.to_slice hashes)
    ok (len != Slice.len slice, hashes, len)

theorem simple_component_step (inst : Instance) (component : Component)
    (h : nested component = false) (quirks : context.QuirksMode)
    (hashes : Array U32 4#usize) (len : Usize) :
    parser.collect_component_hashes inst component quirks hashes len = (do
      let hash ← parser.simple_selector_hash inst.SelectorImplInst component quirks
      storeHash hash hashes len) := by
  cases component <;>
    simp_all [nested, parser.collect_component_hashes, storeHash] <;>
    with_unfolding_all rfl

#print axioms simple_component_step
end CollectionStepProofs
