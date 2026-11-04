/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Aeneas
public import Normalized.Types
@[expose] public section
open Aeneas Aeneas.Std Result ControlFlow Error
open Collection
set_option linter.unusedVariables false
set_option linter.dupNamespace false

def core.borrow.Borrow.Blanket.borrow {T : Type _} (x : T) : Result T := ok x

def core.option.Option.Insts.CoreOpsTry_traitTry.branch {T : Type _}
    (x : Option T) : Result (core.ops.control_flow.ControlFlow (Option Never) T) :=
  match x with
  | none => ok (.Break none)
  | some x => ok (.Continue x)

def core.option.Option.Insts.CoreOpsTry_traitFromResidualOptionNever.from_residual
    (T : Type _) (x : Option Never) : Result (Option T) :=
  match x with
  | none => ok none
  | some x => nomatch x

def servo_arc.Arc.Insts.CoreOpsDerefDeref.deref {T : Type _}
    (x : servo_arc.Arc T) : Result T := ok x.value

def servo_arc.HeaderSlice.slice {H T : Type _}
    (x : servo_arc.HeaderSlice H T) : Result (Slice T) := ok x.entries

def parser.SelectorList.slice
  {Impl : Type _} {Clause0_AttrValue : Type _} {Clause0_Identifier : Type _}
  {Clause0_LocalName : Type _} {Clause0_NamespaceUrl : Type _}
  {Clause0_NamespacePrefix : Type _} {Clause0_BorrowedNamespaceUrl : Type _}
  {Clause0_BorrowedLocalName : Type _} {Clause0_NonTSPseudoClass : Type _}
  {Clause0_PseudoElement : Type _} (SelectorImplInst : parser.SelectorImpl Impl
  Clause0_AttrValue Clause0_Identifier Clause0_LocalName Clause0_NamespaceUrl
  Clause0_NamespacePrefix Clause0_BorrowedNamespaceUrl
  Clause0_BorrowedLocalName Clause0_NonTSPseudoClass Clause0_PseudoElement) :
  parser.SelectorList Impl Clause0_AttrValue Clause0_Identifier
    Clause0_LocalName Clause0_NamespaceUrl Clause0_NamespacePrefix
    Clause0_BorrowedNamespaceUrl Clause0_BorrowedLocalName
    Clause0_NonTSPseudoClass Clause0_PseudoElement → Result (Slice
    (parser.Selector Impl Clause0_AttrValue Clause0_Identifier
    Clause0_LocalName Clause0_NamespaceUrl Clause0_NamespacePrefix
    Clause0_BorrowedNamespaceUrl Clause0_BorrowedLocalName
    Clause0_NonTSPseudoClass Clause0_PseudoElement)) := fun self =>
  match self._0 with
  | .first selector => ok (Slice.from [.mk selector] (by simp; scalar_tac))
  | .second selectors => ok selectors.value.entries

def core.option.Option.is_none_or {T T1 : Type _}
    (inst : core.ops.function.FnOnce T1 T Bool) (value : Option T) (f : T1) : Result Bool :=
  match value with
  | none => ok true
  | some x => inst.call_once f x
