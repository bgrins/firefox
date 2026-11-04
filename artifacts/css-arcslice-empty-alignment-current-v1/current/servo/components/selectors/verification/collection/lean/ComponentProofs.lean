/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Normalized.Funs
@[expose] public section
open Aeneas Aeneas.Std Collection
set_option linter.unusedSimpArgs false

namespace CollectionProofs

theorem eq_ok_of_spec {α : Type} (m : Result α) (x : α)
    (h : m ⦃ v => v = x ⦄) : m = .ok x := by
  cases m with
  | ret v => simpa using h
  | vis e k => simp at h
  | div => simp at h

theorem quirks_ne (a b : context.QuirksMode) :
    core.cmp.PartialEq.ne.default context.QuirksMode.Insts.CoreCmpPartialEqQuirksMode.eq a b =
      .ok (match a, b with
        | .Quirks, .Quirks | .LimitedQuirks, .LimitedQuirks | .NoQuirks, .NoQuirks => false
        | _, _ => true) := by
  apply eq_ok_of_spec
  have hEq : context.QuirksMode.Insts.CoreCmpPartialEqQuirksMode.eq a b ⦃ v => v ↔ a = b ⦄ := by
    cases a <;> cases b <;> simp [context.QuirksMode.Insts.CoreCmpPartialEqQuirksMode.eq,
      context.QuirksMode.read_discriminant]
  apply WP.spec_mono (core.cmp.PartialEq.ne.default.spec _ a b hEq)
  intro v hv
  cases a <;> cases b <;> cases v <;> simp_all

variable {Impl Attr Id Name Ns Prefix BorrowNs BorrowName NonTS Pseudo : Type}
  [DecidableEq Name]

def componentHash (hashName : Name → U32) (hashId : Id → U32) (hashNs : Ns → U32)
    (collectAttr : Name → Bool)
    (component : parser.Component Impl Attr Id Name Ns Prefix BorrowNs BorrowName NonTS Pseudo)
    (quirks : context.QuirksMode) : Option U32 :=
  match component with
  | .LocalName ln => if ln.name = ln.lower_name then some (hashName ln.name) else none
  | .ID atom | .Class atom =>
    match quirks with
    | .Quirks => none
    | _ => some (hashId atom)
  | .DefaultNamespace atom | .Namespace _ atom => some (hashNs atom)
  | .AttributeInNoNamespaceExists atom lower =>
    if atom = lower ∧ collectAttr atom then some (hashName atom) else none
  | .AttributeInNoNamespace atom _ _ _ =>
    if collectAttr atom then some (hashName atom) else none
  | .AttributeOther attr =>
    if attr.local_name = attr.local_name_lower ∧ collectAttr attr.local_name
    then some (hashName attr.local_name) else none
  | _ => none

theorem simple_component_policy
    (inst : parser.SelectorImpl Impl Attr Id Name Ns Prefix BorrowNs BorrowName NonTS Pseudo)
    (hashName : Name → U32) (hashId : Id → U32) (hashNs : Ns → U32)
    (collectAttr : Name → Bool)
    (name_hash : ∀ n, inst.precomputed_hashPrecomputedHashInst1.precomputed_hash n = .ok (hashName n))
    (id_hash : ∀ n, inst.precomputed_hashPrecomputedHashInst.precomputed_hash n = .ok (hashId n))
    (ns_hash : ∀ n, inst.precomputed_hashPrecomputedHashInst2.precomputed_hash n = .ok (hashNs n))
    (name_ne : ∀ a b, inst.corecmpEqInst2.partialEqInst.ne a b = .ok (decide (a ≠ b)))
    (attr_policy : ∀ n, inst.should_collect_attr_hash n = .ok (collectAttr n))
    (component : parser.Component Impl Attr Id Name Ns Prefix BorrowNs BorrowName NonTS Pseudo)
    (quirks : context.QuirksMode) :
    parser.simple_selector_hash inst component quirks =
      .ok (componentHash hashName hashId hashNs collectAttr component quirks) := by
  cases component <;> cases quirks <;>
    simp [componentHash, parser.simple_selector_hash,
      name_hash, id_hash, ns_hash, name_ne, attr_policy,
      core.cmp.impls.PartialEqShared.ne, core.cmp.PartialEq.ne.trait_default,
      context.QuirksMode.Insts.CoreCmpPartialEqQuirksMode, quirks_ne] <;>
    split_ifs <;> simp_all <;> grind

#print axioms simple_component_policy

end CollectionProofs
