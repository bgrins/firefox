/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import RelativeGenerated.StyloRelativeVerification

open Aeneas Aeneas.Std Relative
set_option maxHeartbeats 1000000

namespace RelativeProofs

abbrev Filter := bloom.CountingBloomFilter bloom.BloomStorageU8
abbrev Kind := relative_filter.TraversalKind

def empty : Filter := ⟨⟨Array.repeat 4096#usize 0#u8⟩⟩

theorem new_eq_empty : bloom.CountingBloomFilter.new
    bloom.BloomStorageU8.Insts.Stylo_relative_verificationBloomBloomStorage = .ok empty := by
  simp [bloom.CountingBloomFilter.new,
    bloom.CountingBloomFilter.Insts.CoreDefaultDefault.default,
    bloom.BloomStorageU8.Insts.CoreDefaultDefault.default, empty]

theorem reuse_filter {E : Type} (ops : tree.Element E) (element : E)
    (kind : Kind) (filter : Filter) :
    relative_filter.Entry.update ops (.HasFilter filter) element kind =
      .ok (.HasFilter filter) := by
  simp [relative_filter.Entry.update]

theorem discard_failed_build {E : Type} (ops : tree.Element E) (element : E)
    (kind : Kind) (incomplete : Filter)
    (hbuild : relative_filter.add_to_filter ops element empty kind = .ok (false, incomplete)) :
    relative_filter.Entry.update ops .Lookup element kind = .ok .Lookup := by
  simp [relative_filter.Entry.update, new_eq_empty, hbuild]

theorem publish_successful_build {E : Type} (ops : tree.Element E) (element : E)
    (kind : Kind) (built : Filter)
    (hbuild : relative_filter.add_to_filter ops element empty kind = .ok (true, built)) :
    relative_filter.Entry.update ops .Lookup element kind = .ok (.HasFilter built) := by
  simp [relative_filter.Entry.update, new_eq_empty, hbuild]

theorem next_children {E : Type} (ops : tree.Element E) (root element : E)
    (next : Option E) (hnext : ops.next_sibling_element element = .ok next) :
    relative_filter.next_after_subtree ops root element .Children = .ok next := by
  unfold relative_filter.next_after_subtree relative_filter.next_after_subtree_loop loop
  cases next <;>
    simp [relative_filter.next_after_subtree_loop.body, hnext,
      relative_filter.TraversalKind.Insts.CoreCmpPartialEqTraversalKind.eq,
      core.option.Option.is_some]

structure PreorderForest (size : Nat) where
  parent : Fin size → Option (Fin size)
  first : Fin size → Option (Fin size)
  next : Fin size → Option (Fin size)
  finish : Fin size → Nat
  bounds : ∀ e, e.val < finish e ∧ finish e ≤ size
  parent_bounds : ∀ e p, parent e = some p → p.val < e.val ∧ e.val < finish p
  parent_inside : ∀ root e, root.val < e.val → e.val < finish root →
    ∃ p, parent e = some p ∧ root.val ≤ p.val ∧ p.val < e.val ∧ finish p ≤ finish root
  next_position : ∀ e s, next e = some s → s.val = finish e
  next_parent : ∀ e s, next e = some s → parent s = parent e
  next_bound : ∀ e p s, parent e = some p → next e = some s → s.val < finish p
  next_none : ∀ e p, parent e = some p → next e = none → finish e = finish p
  first_position : ∀ e c, first e = some c → c.val = e.val + 1
  first_parent : ∀ e c, first e = some c → parent c = some e
  first_bound : ∀ e c, first e = some c → c.val < finish e
  first_none : ∀ e, first e = none → finish e = e.val + 1

structure Navigation {size : Nat} (forest : PreorderForest size)
    (ops : tree.Element (Fin size)) where
  identity : Fin size → Usize
  identity_injective : Function.Injective identity
  opaque_eq : ∀ e, ops.«opaque» e = .ok (identity e)
  first_eq : ∀ e, ops.first_element_child e = .ok (forest.first e)
  next_eq : ∀ e, ops.next_sibling_element e = .ok (forest.next e)
  parent_eq : ∀ e, ops.parent_element e = .ok (forest.parent e)

theorem next_descendants {size : Nat} (forest : PreorderForest size)
    (ops : tree.Element (Fin size)) (nav : Navigation forest ops)
    (root element : Fin size)
    (hinside : root.val < element.val ∧ element.val < forest.finish root) :
    relative_filter.next_after_subtree ops root element .Descendants ⦃ out =>
      match out with
      | none => forest.finish element = forest.finish root
      | some next => next.val = forest.finish element ∧ next.val < forest.finish root ⦄ := by
  unfold relative_filter.next_after_subtree relative_filter.next_after_subtree_loop
  refine loop.spec_decr_nat (fun (e : Fin size) => e.val)
    (fun (e : Fin size) => root.val < e.val ∧ e.val < forest.finish root ∧
      forest.finish e = forest.finish element)
    (fun (out : Option (Fin size)) => match out with
      | none => forest.finish element = forest.finish root
      | some next => next.val = forest.finish element ∧ next.val < forest.finish root)
    (fun e => relative_filter.next_after_subtree_loop.body ops root .Descendants e)
    element ?_ ?_
  · intro current hcurrent
    rcases forest.parent_inside root current hcurrent.1 hcurrent.2.1 with
      ⟨parent, hparent, hroot, hless, hparent_end⟩
    cases hnext : forest.next current with
    | some sibling =>
      have hposition := forest.next_position current sibling hnext
      have hbound := forest.next_bound current parent sibling hparent hnext
      simp [relative_filter.next_after_subtree_loop.body, nav.next_eq, hnext,
        core.option.Option.is_some]
      exact ⟨hposition.trans hcurrent.2.2, Nat.lt_of_lt_of_le hbound hparent_end⟩
    | none =>
      have hfinish := forest.next_none current parent hparent hnext
      by_cases heq : nav.identity parent = nav.identity root
      · simp [relative_filter.next_after_subtree_loop.body, nav.next_eq, hnext,
          core.option.Option.is_some,
          relative_filter.TraversalKind.Insts.CoreCmpPartialEqTraversalKind.eq,
          nav.parent_eq, hparent, nav.opaque_eq, heq]
        have hp := nav.identity_injective heq
        subst parent
        exact hcurrent.2.2.symm.trans hfinish
      · simp [relative_filter.next_after_subtree_loop.body, nav.next_eq, hnext,
          core.option.Option.is_some,
          relative_filter.TraversalKind.Insts.CoreCmpPartialEqTraversalKind.eq,
          nav.parent_eq, hparent, nav.opaque_eq, heq]
        have hp : parent ≠ root := fun h => heq (congrArg nav.identity h)
        have hrank : parent.val ≠ root.val := fun h => hp (Fin.ext h)
        have hb := (forest.bounds parent).1
        have hkind : relative_filter.TraversalKind.Descendants.read_discriminant ≠
            relative_filter.TraversalKind.Children.read_discriminant := by
          simp [relative_filter.TraversalKind.read_discriminant]
        simp only [hkind, ↓reduceIte, WP.spec_ok]
        exact ⟨by omega, by omega, hfinish.symm.trans hcurrent.2.2, hless⟩
  · exact ⟨hinside.1, hinside.2, rfl⟩

theorem finish_inside {size : Nat} (forest : PreorderForest size)
    (root element : Fin size)
    (hinside : root.val < element.val ∧ element.val < forest.finish root) :
    forest.finish element ≤ forest.finish root := by
  rcases forest.parent_inside root element hinside.1 hinside.2 with
    ⟨parent, hparent, _, _, hbound⟩
  cases hnext : forest.next element with
  | none => rw [forest.next_none element parent hparent hnext]; exact hbound
  | some sibling =>
    have hposition := forest.next_position element sibling hnext
    have hsibling := forest.next_bound element parent sibling hparent hnext
    omega

inductive Sequence {size : Nat} (finish : Nat) : Nat → List (Fin size) → Prop where
  | nil : Sequence finish finish []
  | cons (element : Fin size) (rest : List (Fin size))
      (tail : Sequence finish (element.val + 1) rest) :
      Sequence finish element.val (element :: rest)

theorem sequence_bound {size finish start : Nat} {nodes : List (Fin size)}
    (h : Sequence finish start nodes) : start ≤ finish := by
  induction h with
  | nil => exact Nat.le_refl _
  | cons element rest tail ih => omega

theorem sequence_head {size finish start : Nat} {nodes : List (Fin size)}
    (h : Sequence finish start nodes) :
    match nodes.head? with
    | none => start = finish
    | some node => node.val = start ∧ start < finish := by
  cases h with
  | nil => simp
  | cons element rest tail =>
    have hb := sequence_bound tail
    simp
    omega

theorem sequence_unique_head {size finish start : Nat} {nodes : List (Fin size)}
    (h : Sequence finish start nodes) (out : Option (Fin size))
    (hout : match out with
      | none => start = finish
      | some node => node.val = start ∧ node.val < finish) : out = nodes.head? := by
  cases h with
  | nil =>
    cases out with
    | none => rfl
    | some node => simp only at hout; omega
  | cons element rest tail =>
    have hb := sequence_bound tail
    cases out with
    | none => simp only at hout; omega
    | some node => exact congrArg some (Fin.ext hout.1)

theorem sequence_members {size finish start : Nat} {nodes : List (Fin size)}
    (h : Sequence finish start nodes) (node : Fin size) :
    node ∈ nodes ↔ start ≤ node.val ∧ node.val < finish := by
  induction h with
  | nil => simp
  | cons element rest tail ih =>
    have hbound := sequence_bound tail
    simp only [List.mem_cons, ih]
    constructor
    · intro h
      rcases h with h | h
      · subst node; omega
      · omega
    · intro h
      by_cases heq : node.val = element.val
      · exact Or.inl (Fin.ext heq)
      · exact Or.inr (by omega)

theorem sequence_nodup {size finish start : Nat} {nodes : List (Fin size)}
    (h : Sequence finish start nodes) : nodes.Nodup := by
  induction h with
  | nil => simp
  | cons element rest tail ih =>
    rw [List.nodup_cons]
    exact ⟨by rw [sequence_members tail element]; omega, ih⟩

theorem sequence_exists {size : Nat} (start length : Nat) (hbound : start + length ≤ size) :
    ∃ nodes : List (Fin size), Sequence (start + length) start nodes := by
  induction length generalizing start with
  | zero => exact ⟨[], Sequence.nil⟩
  | succ length ih =>
    let element : Fin size := ⟨start, by omega⟩
    obtain ⟨rest, hrest⟩ := ih (start + 1) (by omega)
    refine ⟨element :: rest, ?_⟩
    have heq : start + 1 + length = start + (length + 1) := by omega
    rw [heq] at hrest
    exact Sequence.cons element rest hrest

inductive BuildTrace {E : Type} (callback : E → Filter → Bool × Filter → Prop) :
    List E → Filter → Bool × Filter → Prop where
  | nil (filter : Filter) : BuildTrace callback [] filter (true, filter)
  | failed (element : E) (rest : List E) (before after : Filter)
      (call : callback element before (false, after)) :
      BuildTrace callback (element :: rest) before (false, after)
  | step (element : E) (rest : List E) (before after : Filter) (result : Bool × Filter)
      (call : callback element before (true, after))
      (tail : BuildTrace callback rest after result) :
      BuildTrace callback (element :: rest) before result

theorem descendant_suffix {size : Nat} (forest : PreorderForest size)
    (ops : tree.Element (Fin size)) (nav : Navigation forest ops)
    (callback : Fin size → Filter → Bool × Filter → Prop)
    (hcallback : ∀ element filter, ops.add_element_unique_hashes element filter ⦃ result =>
      callback element filter result ⦄)
    (root : Fin size) (start : Nat) (nodes : List (Fin size))
    (sequence : Sequence (forest.finish root) start nodes)
    (hstart : root.val < start) (initial : Filter) :
    relative_filter.add_to_filter_loop ops nodes.head? root initial .Descendants ⦃ result =>
      BuildTrace callback nodes initial result ⦄ := by
  induction sequence generalizing initial with
  | nil =>
    unfold relative_filter.add_to_filter_loop loop
    simpa [relative_filter.add_to_filter_loop.body] using BuildTrace.nil (callback := callback) initial
  | cons element rest tail ih =>
    have hbound := sequence_bound tail
    have hinside : root.val < element.val ∧ element.val < forest.finish root := ⟨hstart, by omega⟩
    unfold relative_filter.add_to_filter_loop loop
    simp only [List.head?_cons, relative_filter.add_to_filter_loop.body]
    step with hcallback element initial as ⟨result, hcall⟩
    rcases result with ⟨success, updated⟩
    cases success with
    | false =>
      simpa using BuildTrace.failed element rest initial updated hcall
    | true =>
      cases hfirst : forest.first element with
      | none =>
        have hf := (nav.first_eq element).trans (congrArg Result.ok hfirst)
        simp [relative_filter.TraversalKind.Insts.CoreCmpPartialEqTraversalKind.eq, hf]
        step with next_descendants forest ops nav root element hinside as ⟨next, hnext⟩
        have hend := forest.first_none element hfirst
        have hn : next = rest.head? := sequence_unique_head tail next (by simpa [hend] using hnext)
        subst next
        have hi := ih (by omega) updated
        simpa [relative_filter.add_to_filter_loop, relative_filter.add_to_filter_loop.body,
          relative_filter.TraversalKind.Insts.CoreCmpPartialEqTraversalKind.eq] using
          (WP.spec_mono hi (fun result htrace =>
            BuildTrace.step element rest initial updated result hcall htrace))
      | some child =>
        have hf := (nav.first_eq element).trans (congrArg Result.ok hfirst)
        simp [relative_filter.TraversalKind.Insts.CoreCmpPartialEqTraversalKind.eq, hf]
        have hpos := forest.first_position element child hfirst
        have hb := forest.first_bound element child hfirst
        have he := finish_inside forest root element hinside
        have hn : some child = rest.head? := sequence_unique_head tail (some child) ⟨hpos, by omega⟩
        rw [← hn] at ih
        have hi := ih (by omega) updated
        simpa [relative_filter.add_to_filter_loop, relative_filter.add_to_filter_loop.body,
          relative_filter.TraversalKind.Insts.CoreCmpPartialEqTraversalKind.eq] using
          (WP.spec_mono hi (fun result htrace =>
            BuildTrace.step element rest initial updated result hcall htrace))

theorem descendants_trace {size : Nat} (forest : PreorderForest size)
    (ops : tree.Element (Fin size)) (nav : Navigation forest ops)
    (callback : Fin size → Filter → Bool × Filter → Prop)
    (hcallback : ∀ element filter, ops.add_element_unique_hashes element filter ⦃ result =>
      callback element filter result ⦄)
    (root : Fin size) (nodes : List (Fin size))
    (sequence : Sequence (forest.finish root) (root.val + 1) nodes) (initial : Filter) :
    relative_filter.add_to_filter ops root initial .Descendants ⦃ result =>
      BuildTrace callback nodes initial result ⦄ := by
  have hf : forest.first root = nodes.head? := by
    apply sequence_unique_head sequence
    cases hfirst : forest.first root with
    | none => exact (forest.first_none root hfirst).symm
    | some child => exact ⟨forest.first_position root child hfirst,
        forest.first_bound root child hfirst⟩
  unfold relative_filter.add_to_filter
  rw [nav.first_eq, hf]
  simpa using descendant_suffix forest ops nav callback hcallback root (root.val + 1)
    nodes sequence (by omega) initial

inductive Descendant {size : Nat} (forest : PreorderForest size) (root : Fin size) :
    Fin size → Prop where
  | child {element : Fin size} (parent : forest.parent element = some root) :
      Descendant forest root element
  | step {parent element : Fin size} (above : Descendant forest root parent)
      (link : forest.parent element = some parent) : Descendant forest root element

theorem descendant_interval {size : Nat} (forest : PreorderForest size)
    (root element : Fin size) :
    Descendant forest root element ↔ root.val < element.val ∧ element.val < forest.finish root := by
  constructor
  · intro h
    induction h with
    | child parent => exact forest.parent_bounds _ root parent
    | @step parent element above link ih =>
      have hb := forest.parent_bounds element parent link
      have he := finish_inside forest root parent ih
      omega
  · intro h
    generalize hi : element.val = index
    induction index using Nat.strong_induction_on generalizing element with
    | h index ih =>
      rcases forest.parent_inside root element h.1 h.2 with
        ⟨parent, hparent, hroot, hless, hfinish⟩
      by_cases hp : parent = root
      · subst parent; exact Descendant.child hparent
      · have hne : parent.val ≠ root.val := fun heq => hp (Fin.ext heq)
        have hb := (forest.bounds parent).1
        have hdesc := ih parent.val (by omega) parent ⟨by omega, by omega⟩ rfl
        exact Descendant.step hdesc hparent

inductive ChildrenSequence {size : Nat} (forest : PreorderForest size) (root : Fin size) :
    Nat → List (Fin size) → Prop where
  | nil : ChildrenSequence forest root (forest.finish root) []
  | cons (element : Fin size) (rest : List (Fin size))
      (parent : forest.parent element = some root)
      (tail : ChildrenSequence forest root (forest.finish element) rest) :
      ChildrenSequence forest root element.val (element :: rest)

theorem children_bound {size start : Nat} {forest : PreorderForest size} {root : Fin size}
    {nodes : List (Fin size)} (h : ChildrenSequence forest root start nodes) :
    start ≤ forest.finish root := by
  cases h with
  | nil => exact Nat.le_refl _
  | cons element rest parent tail => exact Nat.le_of_lt (forest.parent_bounds element root parent).2

theorem children_head {size start : Nat} {forest : PreorderForest size} {root : Fin size}
    {nodes : List (Fin size)} (h : ChildrenSequence forest root start nodes)
    (out : Option (Fin size))
    (hout : match out with
      | none => start = forest.finish root
      | some node => node.val = start ∧ node.val < forest.finish root) : out = nodes.head? := by
  cases h with
  | nil =>
    cases out with
    | none => rfl
    | some node => simp only at hout; omega
  | cons element rest parent tail =>
    have hb := forest.parent_bounds element root parent
    cases out with
    | none => simp only at hout; omega
    | some node => exact congrArg some (Fin.ext hout.1)

theorem children_members {size start : Nat} {forest : PreorderForest size} {root : Fin size}
    {nodes : List (Fin size)} (h : ChildrenSequence forest root start nodes) (node : Fin size) :
    node ∈ nodes ↔ forest.parent node = some root ∧ start ≤ node.val := by
  induction h with
  | nil =>
    simp only [List.not_mem_nil, false_iff, not_and]
    intro hp
    have hb := forest.parent_bounds node root hp
    omega
  | cons element rest parent tail ih =>
    have hb := forest.parent_bounds element root parent
    have he := (forest.bounds element).1
    simp only [List.mem_cons, ih]
    constructor
    · intro h
      rcases h with h | h
      · subst node; exact ⟨parent, Nat.le_refl _⟩
      · exact ⟨h.1, by omega⟩
    · intro h
      by_cases heq : node.val = element.val
      · exact Or.inl (Fin.ext heq)
      · right
        refine ⟨h.1, ?_⟩
        by_contra hn
        have hinside : element.val < node.val ∧ node.val < forest.finish element := by omega
        rcases forest.parent_inside element node hinside.1 hinside.2 with
          ⟨p, hp, hpos, _, _⟩
        rw [h.1] at hp
        have hpr : p = root := (Option.some.inj hp).symm
        subst p
        omega

theorem children_nodup {size start : Nat} {forest : PreorderForest size} {root : Fin size}
    {nodes : List (Fin size)} (h : ChildrenSequence forest root start nodes) : nodes.Nodup := by
  induction h with
  | nil => simp
  | cons element rest parent tail ih =>
    rw [List.nodup_cons]
    have hb := (forest.bounds element).1
    exact ⟨by rw [children_members tail element]; omega, ih⟩

theorem children_exists_from {size : Nat} (forest : PreorderForest size)
    (root element : Fin size) (parent : forest.parent element = some root) :
    ∃ nodes, ChildrenSequence forest root element.val nodes := by
  generalize hd : forest.finish root - element.val = distance
  induction distance using Nat.strong_induction_on generalizing element with
  | h distance ih =>
    have hb := forest.parent_bounds element root parent
    have he := (forest.bounds element).1
    cases hnext : forest.next element with
    | none =>
      have hend := forest.next_none element root parent hnext
      refine ⟨[element], ChildrenSequence.cons element [] parent ?_⟩
      rw [hend]
      exact ChildrenSequence.nil
    | some sibling =>
      have hspos := forest.next_position element sibling hnext
      have hsbound := forest.next_bound element root sibling parent hnext
      have hsparent := (forest.next_parent element sibling hnext).trans parent
      obtain ⟨rest, hrest⟩ := ih (forest.finish root - sibling.val) (by omega)
        sibling hsparent rfl
      rw [hspos] at hrest
      exact ⟨element :: rest, ChildrenSequence.cons element rest parent hrest⟩

theorem children_exists {size : Nat} (forest : PreorderForest size) (root : Fin size) :
    ∃ nodes, ChildrenSequence forest root (root.val + 1) nodes := by
  cases hfirst : forest.first root with
  | none =>
    refine ⟨[], ?_⟩
    rw [← forest.first_none root hfirst]
    exact ChildrenSequence.nil
  | some child =>
    obtain ⟨nodes, hn⟩ := children_exists_from forest root child (forest.first_parent root child hfirst)
    rw [forest.first_position root child hfirst] at hn
    exact ⟨nodes, hn⟩

theorem children_suffix {size : Nat} (forest : PreorderForest size)
    (ops : tree.Element (Fin size)) (nav : Navigation forest ops)
    (callback : Fin size → Filter → Bool × Filter → Prop)
    (hcallback : ∀ element filter, ops.add_element_unique_hashes element filter ⦃ result =>
      callback element filter result ⦄)
    (root : Fin size) (start : Nat) (nodes : List (Fin size))
    (sequence : ChildrenSequence forest root start nodes) (initial : Filter) :
    relative_filter.add_to_filter_loop ops nodes.head? root initial .Children ⦃ result =>
      BuildTrace callback nodes initial result ⦄ := by
  induction sequence generalizing initial with
  | nil =>
    unfold relative_filter.add_to_filter_loop loop
    simpa [relative_filter.add_to_filter_loop.body] using BuildTrace.nil (callback := callback) initial
  | cons element rest parent tail ih =>
    unfold relative_filter.add_to_filter_loop loop
    simp only [List.head?_cons, relative_filter.add_to_filter_loop.body]
    step with hcallback element initial as ⟨result, hcall⟩
    rcases result with ⟨success, updated⟩
    cases success with
    | false => simpa using BuildTrace.failed element rest initial updated hcall
    | true =>
      have hn : forest.next element = rest.head? := by
        apply children_head tail
        cases hnext : forest.next element with
        | none => exact forest.next_none element root parent hnext
        | some sibling => exact ⟨forest.next_position element sibling hnext,
            forest.next_bound element root sibling parent hnext⟩
      have hnext := next_children ops root element (forest.next element) (nav.next_eq element)
      have hkind : relative_filter.TraversalKind.Children.read_discriminant ≠
          relative_filter.TraversalKind.Descendants.read_discriminant := by
        simp [relative_filter.TraversalKind.read_discriminant]
      simp [relative_filter.TraversalKind.Insts.CoreCmpPartialEqTraversalKind.eq,
        hkind, hnext, hn]
      simpa [relative_filter.add_to_filter_loop, relative_filter.add_to_filter_loop.body,
        relative_filter.TraversalKind.Insts.CoreCmpPartialEqTraversalKind.eq, hkind] using
        (WP.spec_mono (ih updated) (fun result htrace =>
          BuildTrace.step element rest initial updated result hcall htrace))

theorem children_trace {size : Nat} (forest : PreorderForest size)
    (ops : tree.Element (Fin size)) (nav : Navigation forest ops)
    (callback : Fin size → Filter → Bool × Filter → Prop)
    (hcallback : ∀ element filter, ops.add_element_unique_hashes element filter ⦃ result =>
      callback element filter result ⦄)
    (root : Fin size) (nodes : List (Fin size))
    (sequence : ChildrenSequence forest root (root.val + 1) nodes) (initial : Filter) :
    relative_filter.add_to_filter ops root initial .Children ⦃ result =>
      BuildTrace callback nodes initial result ⦄ := by
  have hf : forest.first root = nodes.head? := by
    apply children_head sequence
    cases hfirst : forest.first root with
    | none => exact (forest.first_none root hfirst).symm
    | some child => exact ⟨forest.first_position root child hfirst,
        forest.first_bound root child hfirst⟩
  unfold relative_filter.add_to_filter
  rw [nav.first_eq, hf]
  simpa using children_suffix forest ops nav callback hcallback root (root.val + 1)
    nodes sequence initial

theorem target_mapping {E : Type} (ops : tree.Element E) (element : E)
    (parent : Option E) (hparent : ops.parent_element element = .ok parent)
    (hint : parser.RelativeSelectorMatchHint) :
    relative_filter.filter_target ops element hint = .ok (match hint with
      | .InNextSibling => none
      | .InChild => some (element, .Children)
      | .InSubtree => some (element, .Descendants)
      | .InSibling => parent.map (fun e => (e, .Children))
      | .InNextSiblingSubtree | .InSiblingSubtree => parent.map (fun e => (e, .Descendants))) := by
  cases hint <;> cases parent <;> simp [relative_filter.filter_target, hparent]

theorem key_separation (first second : Usize) (first_descendants second_descendants : Bool) :
    relative_filter.same_key first first_descendants second second_descendants =
      .ok (decide (first = second ∧ first_descendants = second_descendants)) := by
  cases first_descendants <;> cases second_descendants <;>
    by_cases h : first = second <;>
    simp [relative_filter.same_key, relative_filter.Key.Insts.CoreCmpPartialEqKey.eq,
      relative_filter.TraversalKind.Insts.CoreCmpPartialEqTraversalKind.eq,
      relative_filter.TraversalKind.read_discriminant, h]

theorem successful_trace_coverage {E Hash : Type}
    (callback : E → Filter → Bool × Filter → Prop)
    (hashes : E → Hash → Prop) (present : Filter → Hash → Prop)
    (hcallback : ∀ element before after, callback element before (true, after) →
      (∀ hash, present before hash → present after hash) ∧
      (∀ hash, hashes element hash → present after hash))
    (nodes : List E) (initial final : Filter)
    (trace : BuildTrace callback nodes initial (true, final)) :
    (∀ hash, present initial hash → present final hash) ∧
    (∀ element ∈ nodes, ∀ hash, hashes element hash → present final hash) := by
  generalize heq : (true, final) = result at trace
  induction trace with
  | nil filter =>
    cases heq
    exact ⟨fun _ h => h, by simp⟩
  | failed element rest before after call => cases heq
  | step element rest before after result call tail ih =>
    obtain ⟨preserve, insert⟩ := hcallback element before after call
    obtain ⟨preserve_tail, cover_tail⟩ := ih heq
    refine ⟨fun hash h => preserve_tail hash (preserve hash h), ?_⟩
    intro node hnode hash hhash
    rcases List.mem_cons.mp hnode with hnode | hnode
    · subst node
      exact preserve_tail hash (insert hash hhash)
    · exact cover_tail node hnode hash hhash

theorem descendants_coverage {size : Nat} {Hash : Type} (forest : PreorderForest size)
    (ops : tree.Element (Fin size)) (nav : Navigation forest ops)
    (callback : Fin size → Filter → Bool × Filter → Prop)
    (hashes : Fin size → Hash → Prop) (present : Filter → Hash → Prop)
    (hcalls : ∀ element filter, ops.add_element_unique_hashes element filter ⦃ result =>
      callback element filter result ⦄)
    (hhashes : ∀ element before after, callback element before (true, after) →
      (∀ hash, present before hash → present after hash) ∧
      (∀ hash, hashes element hash → present after hash))
    (root : Fin size) (initial : Filter) :
    relative_filter.add_to_filter ops root initial .Descendants ⦃ result =>
      result.1 = true → ∀ element, Descendant forest root element →
        ∀ hash, hashes element hash → present result.2 hash ⦄ := by
  have hb := forest.bounds root
  obtain ⟨nodes, hn⟩ := sequence_exists (root.val + 1)
    (forest.finish root - (root.val + 1)) (by omega :
      root.val + 1 + (forest.finish root - (root.val + 1)) ≤ size)
  have he : root.val + 1 + (forest.finish root - (root.val + 1)) = forest.finish root := by omega
  rw [he] at hn
  apply WP.spec_mono (descendants_trace forest ops nav callback hcalls root nodes hn initial)
  intro result htrace hsuccess element hdesc hash hhash
  rcases result with ⟨success, final⟩
  simp only at hsuccess
  subst success
  have hcover := (successful_trace_coverage callback hashes present hhashes nodes initial final htrace).2
  have hrange := (descendant_interval forest root element).mp hdesc
  apply hcover element ((sequence_members hn element).mpr (by omega)) hash hhash

theorem children_coverage {size : Nat} {Hash : Type} (forest : PreorderForest size)
    (ops : tree.Element (Fin size)) (nav : Navigation forest ops)
    (callback : Fin size → Filter → Bool × Filter → Prop)
    (hashes : Fin size → Hash → Prop) (present : Filter → Hash → Prop)
    (hcalls : ∀ element filter, ops.add_element_unique_hashes element filter ⦃ result =>
      callback element filter result ⦄)
    (hhashes : ∀ element before after, callback element before (true, after) →
      (∀ hash, present before hash → present after hash) ∧
      (∀ hash, hashes element hash → present after hash))
    (root : Fin size) (initial : Filter) :
    relative_filter.add_to_filter ops root initial .Children ⦃ result =>
      result.1 = true → ∀ element, forest.parent element = some root →
        ∀ hash, hashes element hash → present result.2 hash ⦄ := by
  obtain ⟨nodes, hn⟩ := children_exists forest root
  apply WP.spec_mono (children_trace forest ops nav callback hcalls root nodes hn initial)
  intro result htrace hsuccess element hparent hash hhash
  rcases result with ⟨success, final⟩
  simp only at hsuccess
  subst success
  have hcover := (successful_trace_coverage callback hashes present hhashes nodes initial final htrace).2
  have hb := forest.parent_bounds element root hparent
  apply hcover element ((children_members hn element).mpr ⟨hparent, by omega⟩) hash hhash

#print axioms next_children
#print axioms new_eq_empty
#print axioms reuse_filter
#print axioms discard_failed_build
#print axioms publish_successful_build
#print axioms next_descendants
#print axioms finish_inside
#print axioms sequence_bound
#print axioms sequence_head
#print axioms sequence_unique_head
#print axioms sequence_members
#print axioms sequence_nodup
#print axioms sequence_exists
#print axioms descendant_suffix
#print axioms descendants_trace
#print axioms descendant_interval
#print axioms children_bound
#print axioms children_head
#print axioms children_members
#print axioms children_nodup
#print axioms children_exists_from
#print axioms children_exists
#print axioms children_suffix
#print axioms children_trace
#print axioms target_mapping
#print axioms key_separation
#print axioms successful_trace_coverage
#print axioms descendants_coverage
#print axioms children_coverage

end RelativeProofs
