/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import Generated.StyloBloomVerification

open Aeneas Aeneas.Std Result Bloom

namespace RecoveryProofs

variable {capacity : Nat}

structure StackView (S E : Type) where
  chain : S → List E
  pending : S → List E
  valid : S → Prop

structure StackContract {S E : Type} (ops : style_bloom_recovery.RecoveryState S E)
    (view : StackView S E) (capacity : Nat) where
  len_spec : ∀ s, view.valid s → ops.len s ⦃ n => n.val = (view.chain s).length ⦄
  current_parent_spec : ∀ s, view.valid s → ops.current_parent s ⦃ o => o = (view.chain s).head? ⦄
  pop_spec : ∀ s, view.valid s → ops.pop s ⦃ p =>
    view.valid p.2 ∧ view.chain p.2 = (view.chain s).tail ∧
    view.pending p.2 = view.pending s ∧ p.1 = (view.chain s).head? ⦄
  push_spec : ∀ s e, view.valid s → (view.chain s).length < capacity →
    ops.parent e = ok (view.chain s).head? → ops.push s e ⦃ s' =>
    view.valid s' ∧ view.chain s' = e :: view.chain s ∧ view.pending s' = view.pending s ⦄
  pending_pop_spec : ∀ s, view.valid s → ops.pending_pop s ⦃ p =>
    view.valid p.2 ∧ view.chain p.2 = view.chain s ∧
    view.pending p.2 = (view.pending s).tail ∧ p.1 = (view.pending s).head? ⦄
  pending_push_spec : ∀ s e, view.valid s → (view.pending s).length < capacity → ops.pending_push s e ⦃ s' =>
    view.valid s' ∧ view.chain s' = view.chain s ∧ view.pending s' = e :: view.pending s ⦄
  clear_spec : ∀ s, view.valid s → ops.clear s ⦃ s' =>
    view.valid s' ∧ view.chain s' = [] ∧ view.pending s' = view.pending s ⦄

structure Forest (E : Type) where
  parent : E → Option E
  ancestors : E → List E
  ancestors_eq : ∀ e, ancestors e = match parent e with
    | none => []
    | some p => p :: ancestors p

def Chain {E : Type} (forest : Forest E) (chain : List E) : Prop :=
  chain = [] ∨ ∃ e, chain = e :: forest.ancestors e

theorem ancestors_chain {E : Type} (forest : Forest E) (e : E) :
    Chain forest (forest.ancestors e) := by
  rw [forest.ancestors_eq e]
  cases forest.parent e with
  | none => exact Or.inl rfl
  | some p => exact Or.inr ⟨p, rfl⟩

theorem chain_tail {E : Type} (forest : Forest E) {chain : List E} (h : Chain forest chain) :
    Chain forest chain.tail := by
  rcases h with rfl | ⟨e, rfl⟩
  · exact Or.inl rfl
  · exact ancestors_chain forest e

theorem chain_head {E : Type} (forest : Forest E) {chain : List E} {head : E}
    (hc : Chain forest chain) (hh : chain.head? = some head) :
    chain = head :: forest.ancestors head := by
  rcases hc with rfl | ⟨e, rfl⟩
  · simp at hh
  · simp only [List.head?_cons, Option.some.injEq] at hh
    rw [hh]

theorem chain_suffix {E : Type} (forest : Forest E) (xs suffix : List E)
    (hc : Chain forest (xs ++ suffix)) : Chain forest suffix := by
  induction xs with
  | nil => exact hc
  | cons head rest ih =>
    apply ih
    exact chain_tail forest hc

theorem chain_cons_parent {E : Type} (forest : Forest E) (head : E) (rest : List E)
    (hc : Chain forest (head :: rest)) : forest.parent head = rest.head? := by
  have hh := chain_head forest hc (show (head :: rest).head? = some head from rfl)
  have hr : rest = forest.ancestors head := by simpa only [List.cons.injEq, true_and] using hh
  rw [hr, forest.ancestors_eq head]
  cases forest.parent head <;> rfl

theorem flush_pending {S E : Type} (ops : style_bloom_recovery.RecoveryState S E)
    (view : StackView S E) (laws : StackContract ops view capacity) (forest : Forest E)
    (parent_spec : ∀ e, ops.parent e = ok (forest.parent e))
    (s : S) (hv : view.valid s)
    (hchain : Chain forest ((view.pending s).reverse ++ view.chain s))
    (hbudget : (view.chain s).length + (view.pending s).length ≤ capacity) :
    style_bloom_recovery.rebuild_loop1 ops s ⦃ s' => view.valid s' ∧ view.pending s' = [] ∧
      view.chain s' = (view.pending s).reverse ++ view.chain s ⦄ := by
  unfold style_bloom_recovery.rebuild_loop1
  refine loop.spec_decr_nat (fun state => (view.pending state).length)
    (fun state => view.valid state ∧
      (view.pending state).reverse ++ view.chain state = (view.pending s).reverse ++ view.chain s)
    (fun state => view.valid state ∧ view.pending state = [] ∧
      view.chain state = (view.pending s).reverse ++ view.chain s)
    (fun state => style_bloom_recovery.rebuild_loop1.body ops state) s ?_ ⟨hv, rfl⟩
  intro state hs
  rcases hs with ⟨hvalid, hpres⟩
  unfold style_bloom_recovery.rebuild_loop1.body
  step with laws.pending_pop_spec state hvalid as ⟨o, p, hpvalid, hpchain, hppending, hpop⟩
  cases hpend : view.pending state with
  | nil =>
    simp_all
  | cons head rest =>
    simp only [hpend, List.head?_cons] at hpop
    simp only [hpop]
    have hsum := congrArg List.length hpres
    simp only [List.length_append, List.length_reverse, hpend, List.length_cons] at hsum
    have hroom : (view.chain p).length < capacity := by rw [hpchain]; omega
    have hcombined : Chain forest ((view.pending state).reverse ++ view.chain state) := by
      rw [hpres]
      exact hchain
    have hsuffix : Chain forest (head :: view.chain state) := by
      apply chain_suffix forest rest.reverse
      simpa only [hpend, List.reverse_cons, List.append_assoc, List.singleton_append] using hcombined
    have hadmissible : ops.parent head = ok (view.chain p).head? := by
      rw [parent_spec, hpchain, chain_cons_parent forest head (view.chain state) hsuffix]
    step with laws.push_spec p head hpvalid hroom hadmissible as ⟨next, hnvalid, hnchain, hnpending⟩
    simp_all [List.reverse_cons, List.append_assoc]

theorem collect_parents {S E : Type} (ops : style_bloom_recovery.RecoveryState S E)
    (view : StackView S E) (laws : StackContract ops view capacity) (forest : Forest E)
    (parent_spec : ∀ e, ops.parent e = ok (forest.parent e))
    (s : S) (element : E) (hv : view.valid s)
    (hbudget : (view.pending s).length + (forest.ancestors element).length ≤ capacity) :
    style_bloom_recovery.rebuild_loop0 ops element s ⦃ s' => view.valid s' ∧
      view.chain s' = view.chain s ∧
      (view.pending s').reverse = (view.pending s).reverse ++ forest.ancestors element ⦄ := by
  unfold style_bloom_recovery.rebuild_loop0
  refine loop.spec_decr_nat (fun (p : E × S) => (forest.ancestors p.1).length)
    (fun p => view.valid p.2 ∧ view.chain p.2 = view.chain s ∧
      (view.pending p.2).reverse ++ forest.ancestors p.1 =
        (view.pending s).reverse ++ forest.ancestors element)
    (fun state => view.valid state ∧ view.chain state = view.chain s ∧
      (view.pending state).reverse = (view.pending s).reverse ++ forest.ancestors element)
    (fun (e, state) => style_bloom_recovery.rebuild_loop0.body ops e state) (element, s) ?_
    ⟨hv, rfl, rfl⟩
  intro p hp
  rcases p with ⟨e, state⟩
  rcases hp with ⟨hvalid, hchain, hpres⟩
  dsimp only at hvalid hchain hpres ⊢
  unfold style_bloom_recovery.rebuild_loop0.body
  rw [parent_spec]
  simp only [bind_ok]
  have ha := forest.ancestors_eq e
  cases hparent : forest.parent e with
  | none =>
    simp only [hparent] at ha
    simp_all
  | some parent =>
    simp only [hparent] at ha
    have hsum := congrArg List.length hpres
    simp only [List.length_append, List.length_reverse, ha, List.length_cons] at hsum
    have hroom : (view.pending state).length < capacity := by omega
    step with laws.pending_push_spec state parent hvalid hroom as ⟨next, hnvalid, hnchain, hnpending⟩
    simp_all [List.reverse_cons, List.append_assoc]

theorem rebuild_ancestors {S E : Type} (ops : style_bloom_recovery.RecoveryState S E)
    (view : StackView S E) (laws : StackContract ops view capacity) (forest : Forest E)
    (parent_spec : ∀ e, ops.parent e = ok (forest.parent e))
    (s : S) (element : E) (hv : view.valid s) (hp : view.pending s = [])
    (hbudget : (forest.ancestors element).length ≤ capacity) :
    style_bloom_recovery.rebuild ops s element ⦃ s' => view.valid s' ∧
      view.pending s' = [] ∧ view.chain s' = forest.ancestors element ⦄ := by
  unfold style_bloom_recovery.rebuild
  step with laws.clear_spec s hv as ⟨s1, hv1, hc1, hp1⟩
  have hb1 : (view.pending s1).length + (forest.ancestors element).length ≤ capacity := by
    simpa only [hp1, hp, List.length_nil, Nat.zero_add] using hbudget
  step with collect_parents ops view laws forest parent_spec s1 element hv1 hb1 as ⟨s2, hv2, hc2, hp2⟩
  have hb2 : (view.chain s2).length + (view.pending s2).length ≤ capacity := by
    have hsum := congrArg List.length hp2
    simp only [List.length_reverse, List.length_append, hp1, hp, List.length_nil, Nat.zero_add] at hsum
    simpa only [hc2, hc1, List.length_nil, Nat.zero_add, hsum] using hbudget
  have hcflush : Chain forest ((view.pending s2).reverse ++ view.chain s2) := by
    simp only [hp2, hp1, hp, List.reverse_nil, List.nil_append, hc2, hc1, List.append_nil]
    exact ancestors_chain forest element
  step with flush_pending ops view laws forest parent_spec s2 hv2 hcflush hb2 as ⟨s3, hv3, hp3, hc3⟩
  simp_all

theorem trim_depth {S E : Type} (ops : style_bloom_recovery.RecoveryState S E)
    (view : StackView S E) (laws : StackContract ops view capacity) (forest : Forest E)
    (s : S) (depth current : Usize) (hv : view.valid s) (hc : Chain forest (view.chain s))
    (hlen : current.val + 1 = (view.chain s).length) (hd : 0 < depth.val) :
    style_bloom_recovery.recover_loop0 ops s depth current ⦃ p =>
      view.valid p.1 ∧ Chain forest (view.chain p.1) ∧ view.pending p.1 = view.pending s ∧
      p.2.val + 1 = (view.chain p.1).length ∧
      (view.chain p.1).getLast? = (view.chain s).getLast? ∧ p.2.val ≤ depth.val - 1 ⦄ := by
  unfold style_bloom_recovery.recover_loop0
  refine loop.spec_decr_nat (fun (p : S × Usize) => p.2.val)
    (fun p => view.valid p.1 ∧ Chain forest (view.chain p.1) ∧
      view.pending p.1 = view.pending s ∧ p.2.val + 1 = (view.chain p.1).length ∧
      (view.chain p.1).getLast? = (view.chain s).getLast?)
    (fun p => view.valid p.1 ∧ Chain forest (view.chain p.1) ∧ view.pending p.1 = view.pending s ∧
      p.2.val + 1 = (view.chain p.1).length ∧
      (view.chain p.1).getLast? = (view.chain s).getLast? ∧ p.2.val ≤ depth.val - 1)
    (fun (state, curr) => style_bloom_recovery.recover_loop0.body ops depth state curr)
    (s, current) ?_ ⟨hv, hc, rfl, hlen, rfl⟩
  intro p hp
  rcases p with ⟨state, curr⟩
  rcases hp with ⟨hvalid, hchain, hpend, hlength, hroot⟩
  dsimp only at hvalid hchain hpend hlength hroot ⊢
  unfold style_bloom_recovery.recover_loop0.body
  step as ⟨limit, hlimit⟩
  split
  · rename_i hmore
    have hpositive : 0 < curr.val := by scalar_tac
    step with laws.pop_spec state hvalid as ⟨o, state1, hv1, hc1, hp1, ho⟩
    have hnonempty : view.chain state ≠ [] := by intro he; simp [he] at hlength
    cases hlist : view.chain state with
    | nil => exact False.elim (hnonempty hlist)
    | cons head rest =>
      simp only [hlist, List.head?_cons] at ho
      simp only [ho]
      step
      step as ⟨curr1, hcurr1⟩
      have htail := chain_tail forest hchain
      simp only [hlist, List.tail_cons] at hc1 htail
      refine ⟨hv1, ?_, ?_, ?_, ?_, ?_⟩
      · simpa only [hc1] using htail
      · exact hp1.trans hpend
      · simp only [hc1]
        simp only [hlist, List.length_cons] at hlength
        omega
      · have hrest : rest ≠ [] := by
          intro hn
          simp only [hlist, hn, List.length_cons, List.length_nil] at hlength
          omega
        simpa only [hc1, hlist, List.getLast?_cons_of_ne_nil hrest] using hroot
      · omega
  · rename_i hdone
    simp only [WP.spec_ok]
    refine ⟨hvalid, hchain, hpend, hlength, hroot, ?_⟩
    scalar_tac

theorem ascend_target {S E : Type} (ops : style_bloom_recovery.RecoveryState S E)
    (view : StackView S E) (laws : StackContract ops view capacity) (forest : Forest E)
    (parent_spec : ∀ e, ops.parent e = ok (forest.parent e))
    (s : S) (element : E) (current depth : Usize) (desired : List E)
    (hv : view.valid s) (hd : depth.val = (forest.ancestors element).length)
    (hle : current.val ≤ depth.val)
    (hpath : (view.pending s).reverse ++ element :: forest.ancestors element = desired)
    (hbudget : desired.length ≤ capacity) :
    style_bloom_recovery.recover_loop1 ops s current element depth ⦃ p =>
      view.valid p.1 ∧ view.chain p.1 = view.chain s ∧
      p.2.2.val = (forest.ancestors p.2.1).length ∧
      (view.pending p.1).reverse ++ p.2.1 :: forest.ancestors p.2.1 = desired ∧
      p.2.2.val = current.val ⦄ := by
  unfold style_bloom_recovery.recover_loop1
  refine loop.spec_decr_nat (fun (p : S × E × Usize) => p.2.2.val)
    (fun p => view.valid p.1 ∧ view.chain p.1 = view.chain s ∧
      p.2.2.val = (forest.ancestors p.2.1).length ∧
      (view.pending p.1).reverse ++ p.2.1 :: forest.ancestors p.2.1 = desired ∧
      current.val ≤ p.2.2.val)
    (fun p => view.valid p.1 ∧ view.chain p.1 = view.chain s ∧
      p.2.2.val = (forest.ancestors p.2.1).length ∧
      (view.pending p.1).reverse ++ p.2.1 :: forest.ancestors p.2.1 = desired ∧
      p.2.2.val = current.val)
    (fun (state, e, d) => style_bloom_recovery.recover_loop1.body ops current state e d)
    (s, element, depth) ?_ ⟨hv, rfl, hd, hpath, hle⟩
  intro p hp
  rcases p with ⟨state, e, d⟩
  rcases hp with ⟨hvalid, hchain, hdepth, hdesired, htarget⟩
  dsimp only at hvalid hchain hdepth hdesired htarget ⊢
  unfold style_bloom_recovery.recover_loop1.body
  split
  · rename_i hmore
    have hg : current.val < d.val := by scalar_tac
    have ha := forest.ancestors_eq e
    cases hparent : forest.parent e with
    | none => simp only [hparent] at ha; simp only [ha, List.length_nil] at hdepth; omega
    | some parent =>
      simp only [hparent] at ha
      have hsum := congrArg List.length hdesired
      simp only [List.length_append, List.length_reverse, List.length_cons] at hsum
      have hroom : (view.pending state).length < capacity := by omega
      step with laws.pending_push_spec state e hvalid hroom as ⟨state1, hv1, hc1, hp1⟩
      rw [parent_spec, hparent]
      simp only [bind_ok]
      step as ⟨d1, hd1⟩
      refine ⟨hv1, hc1.trans hchain, ?_, ?_, ?_, ?_⟩
      · simp only [ha, List.length_cons] at hdepth
        omega
      · simp only [hp1, List.reverse_cons, List.append_assoc, List.singleton_append]
        simpa only [ha] using hdesired
      · omega
      · omega
  · rename_i hdone
    simp only [WP.spec_ok]
    refine ⟨hvalid, hchain, hdepth, hdesired, ?_⟩
    scalar_tac

theorem find_common_parent {S E : Type} [DecidableEq E]
    (ops : style_bloom_recovery.RecoveryState S E)
    (view : StackView S E) (laws : StackContract ops view capacity) (forest : Forest E)
    (parent_spec : ∀ e, ops.parent e = ok (forest.parent e))
    (ne_spec : ∀ a b, ops.corecmpEqInst.partialEqInst.ne a b = ok (decide (a ≠ b)))
    (s : S) (element : E) (allow : Bool) (desired : List E) (hv : view.valid s)
    (hc : Chain forest (view.chain s))
    (hlen : (view.chain s).length = (forest.ancestors element).length + 1)
    (hpath : (view.pending s).reverse ++ element :: forest.ancestors element = desired)
    (hbudget : desired.length ≤ capacity)
    (hroots : allow = true ∨ (view.chain s).getLast? = (element :: forest.ancestors element).getLast?) :
    style_bloom_recovery.recover_loop2 ops s allow element ⦃ s' => view.valid s' ∧
      (view.pending s').reverse ++ view.chain s' = desired ⦄ := by
  unfold style_bloom_recovery.recover_loop2
  refine loop.spec_decr_nat (fun (p : S × E) => (view.chain p.1).length)
    (fun p => view.valid p.1 ∧ Chain forest (view.chain p.1) ∧
      (view.chain p.1).length = (forest.ancestors p.2).length + 1 ∧
      (view.pending p.1).reverse ++ p.2 :: forest.ancestors p.2 = desired ∧
      (allow = true ∨ (view.chain p.1).getLast? = (p.2 :: forest.ancestors p.2).getLast?))
    (fun state => view.valid state ∧ (view.pending state).reverse ++ view.chain state = desired)
    (fun (state, e) => style_bloom_recovery.recover_loop2.body ops allow state e)
    (s, element) ?_ ⟨hv, hc, hlen, hpath, hroots⟩
  intro p hp
  rcases p with ⟨state, e⟩
  rcases hp with ⟨hvalid, hchain, hlength, hdesired, hsame⟩
  dsimp only at hvalid hchain hlength hdesired hsame ⊢
  unfold style_bloom_recovery.recover_loop2.body
  step with laws.current_parent_spec state hvalid as ⟨o, ho⟩
  have hnonempty : view.chain state ≠ [] := by intro he; simp [he] at hlength
  cases hlist : view.chain state with
  | nil => exact False.elim (hnonempty hlist)
  | cons head rest =>
    simp only [hlist, List.head?_cons] at ho
    simp only [ho, core.option.Option.unwrap, Result.ofOption, bind_ok]
    rw [ne_spec]
    simp only [bind_ok]
    split
    · rename_i hneq
      have hsum := congrArg List.length hdesired
      simp only [List.length_append, List.length_reverse, List.length_cons] at hsum
      have hroom : (view.pending state).length < capacity := by omega
      step with laws.pending_push_spec state e hvalid hroom as ⟨state1, hv1, hc1, hp1⟩
      step with laws.pop_spec state1 hv1 as ⟨o2, state2, hv2, hc2, hp2, ho2⟩
      simp only [hc1, hlist, List.head?_cons] at ho2
      simp only [ho2, bind_ok]
      rw [parent_spec]
      simp only [bind_ok]
      have ha := forest.ancestors_eq e
      have htail := chain_tail forest hchain
      simp only [hc1, hlist, List.tail_cons] at hc2
      cases hparent : forest.parent e with
      | none =>
        simp only [hparent] at ha
        have hrest : rest = [] := by
          simp only [hlist, List.length_cons, ha, List.length_nil] at hlength
          exact List.eq_nil_of_length_eq_zero (by omega)
        step with laws.len_spec state2 hv2 as ⟨len, hlen2⟩
        have hz : len = 0#usize := by simp only [hc2, hrest, List.length_nil] at hlen2; scalar_tac
        have hallow : allow = true := by
          rcases hsame with h | h
          · exact h
          · have he : head = e := by simpa only [hlist, hrest, ha, List.getLast?_singleton, Option.some.injEq] using h
            simp only [he, ne_eq, not_true_eq_false, decide_false, Bool.false_eq_true] at hneq
        simp only [hz, hallow]
        step*
      | some parent =>
        simp only [hparent] at ha
        simp only [WP.spec_ok]
        refine ⟨hv2, ?_, ?_, ?_, ?_, ?_⟩
        · simpa only [hlist, List.tail_cons, hc2] using htail
        · simp only [hc2]
          simp only [hlist, List.length_cons, ha, List.length_cons] at hlength
          omega
        · simp only [hp2, hp1, List.reverse_cons, List.append_assoc, List.singleton_append]
          simpa only [ha] using hdesired
        · rcases hsame with h | h
          · exact Or.inl h
          · right
            have hrest : rest ≠ [] := by
              intro hn
              simp only [hlist, hn, List.length_cons, List.length_nil, ha] at hlength
              simp at hlength
            simpa only [hc2, hlist, ha, List.getLast?_cons_of_ne_nil hrest,
              List.getLast?_cons_cons] using h
        · simp only [hc2, List.length_cons]
          omega
    · rename_i heq
      have he : head = e := by simpa using heq
      have hc : view.chain state = e :: forest.ancestors e := by
        apply chain_head forest hchain
        simp only [hlist, List.head?_cons, he]
      simpa only [WP.spec_ok, hc] using And.intro hvalid hdesired

theorem trim_loop_same {S E : Type} (ops : style_bloom_recovery.RecoveryState S E) :
    style_bloom_recovery.recover_loop4 ops = style_bloom_recovery.recover_loop0 ops := rfl

theorem ascend_loop_same {S E : Type} (ops : style_bloom_recovery.RecoveryState S E) :
    style_bloom_recovery.recover_loop5 ops = style_bloom_recovery.recover_loop1 ops := rfl

theorem common_loop_same {S E : Type} (ops : style_bloom_recovery.RecoveryState S E) :
    style_bloom_recovery.recover_loop6 ops = style_bloom_recovery.recover_loop2 ops := rfl

theorem flush_loop_same {S E : Type} (ops : style_bloom_recovery.RecoveryState S E) :
    style_bloom_recovery.recover_loop7 ops = style_bloom_recovery.rebuild_loop1 ops := rfl

theorem recover_ancestors {S E : Type} [DecidableEq E]
    (ops : style_bloom_recovery.RecoveryState S E)
    (view : StackView S E) (laws : StackContract ops view capacity) (forest : Forest E)
    (parent_spec : ∀ e, ops.parent e = ok (forest.parent e))
    (eq_spec : ∀ a b, ops.corecmpEqInst.partialEqInst.eq a b = ok (decide (a = b)))
    (ne_spec : ∀ a b, ops.corecmpEqInst.partialEqInst.ne a b = ok (decide (a ≠ b)))
    (s : S) (element : E) (depth : Usize) (allow : Bool) (hv : view.valid s)
    (hc : Chain forest (view.chain s)) (hp : view.pending s = [])
    (hd : depth.val = (forest.ancestors element).length)
    (hbudget : (forest.ancestors element).length ≤ capacity)
    (hroots : allow = true ∨ view.chain s = [] ∨ forest.parent element = none ∨
      (view.chain s).getLast? = (forest.ancestors element).getLast?) :
    style_bloom_recovery.recover ops s element depth allow ⦃ s' => view.valid s' ∧
      view.pending s' = [] ∧ view.chain s' = forest.ancestors element ⦄ := by
  unfold style_bloom_recovery.recover
  step with laws.len_spec s hv as ⟨len, hlen⟩
  split
  · exact rebuild_ancestors ops view laws forest parent_spec s element hv hp hbudget
  · rename_i hnonzero
    rw [parent_spec]
    simp only [bind_ok]
    have ha := forest.ancestors_eq element
    cases hparent : forest.parent element with
    | none =>
      simp only [hparent] at ha
      step with laws.clear_spec s hv as ⟨s1, hv1, hc1, hp1⟩
      simp_all
    | some parent =>
      simp only [hparent] at ha
      step with laws.current_parent_spec s hv as ⟨o, ho⟩
      cases hlist : view.chain s with
      | nil => simp only [hlist, List.length_nil] at hlen; scalar_tac
      | cons head rest =>
        simp only [hlist, List.head?_cons] at ho
        simp only [ho]
        rw [eq_spec]
        simp only [bind_ok]
        have hdepth : 0 < depth.val := by simp only [ha, List.length_cons] at hd; omega
        have hdz : depth ≠ 0#usize := by scalar_tac
        by_cases heq : head = parent
        · simp only [heq, decide_true, Bool.true_or]
          step*
          have hcfull := chain_head forest hc (show (view.chain s).head? = some parent by
            simp only [hlist, List.head?_cons, heq])
          simp_all
        · simp only [heq, decide_false, Bool.false_or, hdz]
          step
          step
          simp only [Bool.false_eq_true, ↓reduceIte, trim_loop_same, ascend_loop_same, common_loop_same, flush_loop_same]
          step as ⟨current, hcurrent⟩
          have hl : current.val + 1 = (view.chain s).length := by scalar_tac
          step with trim_depth ops view laws forest s depth current hv hc hl hdepth as
            ⟨s1, current1, hv1, hc1, hp1, hl1, hroot1, hd1⟩
          step as ⟨common_depth, hcommon_depth⟩
          have hcd : common_depth.val = (forest.ancestors parent).length := by
            simp only [ha, List.length_cons] at hd
            omega
          have hle : current1.val ≤ common_depth.val := by omega
          have hpath1 : (view.pending s1).reverse ++ parent :: forest.ancestors parent =
              forest.ancestors element := by simp only [hp1, hp, List.reverse_nil, List.nil_append, ha]
          step with ascend_target ops view laws forest parent_spec s1 parent current1 common_depth
            (forest.ancestors element) hv1 hcd hle hpath1 hbudget as
            ⟨s2, common, common_depth1, hv2, hc2, hcd2, hp2, heq2⟩
          step
          have hchain2 : Chain forest (view.chain s2) := by simpa only [hc2] using hc1
          have hlength2 : (view.chain s2).length = (forest.ancestors common).length + 1 := by
            rw [hc2]
            omega
          have hroot2 : allow = true ∨ (view.chain s2).getLast? =
              (common :: forest.ancestors common).getLast? := by
            rcases hroots with hallow | hempty | hnone | hroot
            · exact Or.inl hallow
            · simp only [hlist, List.cons_ne_nil] at hempty
            · simp only [hparent, Option.some_ne_none] at hnone
            · right
              have hdesired := congrArg List.getLast? hp2
              simp only [List.getLast?_append] at hdesired
              cases ht : forest.ancestors common with
              | nil => simpa only [ht, List.getLast?_singleton, Option.some_or, hc2,
                  hroot1, hroot] using hdesired.symm
              | cons x xs => simpa only [ht, List.getLast?_cons_cons, List.getLast?_cons,
                  Option.some_or, hc2, hroot1, hroot] using hdesired.symm
          step with find_common_parent ops view laws forest parent_spec ne_spec s2 common allow
            (forest.ancestors element) hv2 hchain2 hlength2 hp2 hbudget hroot2 as ⟨s3, hv3, hp3⟩
          have hb3 : (view.chain s3).length + (view.pending s3).length ≤ capacity := by
            have hs := congrArg List.length hp3
            simp only [List.length_append, List.length_reverse] at hs
            omega
          have hcflush : Chain forest ((view.pending s3).reverse ++ view.chain s3) := by
            rw [hp3]
            exact ancestors_chain forest element
          step with flush_pending ops view laws forest parent_spec s3 hv3 hcflush hb3 as ⟨s4, hv4, hp4, hc4⟩
          step with laws.len_spec s4 hv4 as ⟨len4, hlen4⟩
          have heq4 : len4 = depth := by
            rw [hc4, hp3] at hlen4
            exact UScalar.eq_of_val_eq (hlen4.trans hd.symm)
          simp only [heq4]
          step*

end RecoveryProofs

#print axioms RecoveryProofs.ancestors_chain
#print axioms RecoveryProofs.chain_tail
#print axioms RecoveryProofs.chain_head
#print axioms RecoveryProofs.chain_suffix
#print axioms RecoveryProofs.chain_cons_parent
#print axioms RecoveryProofs.flush_pending
#print axioms RecoveryProofs.collect_parents
#print axioms RecoveryProofs.rebuild_ancestors
#print axioms RecoveryProofs.trim_depth
#print axioms RecoveryProofs.ascend_target
#print axioms RecoveryProofs.find_common_parent
#print axioms RecoveryProofs.recover_ancestors
