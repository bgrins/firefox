import Coalesced

namespace CoalescedDAG

open EndpointApplication (Version)
open CoalescedChain (Node localValid refreshNode selectNode completeNode localWeight quiet
  refresh_valid refresh_value select_valid complete_valid complete_endpoint_refresh_unchanged
  refresh_weight select_weight complete_weight)

abbrev Values := Nat → Nat

structure Graph where
  reads : Nat → Nat → Bool
  eval : Nat → Values → Nat
  earlier : ∀ target provider, reads target provider = true → provider < target
  depends : ∀ target before after,
    (∀ provider, reads target provider = true → before provider = after provider) →
    eval target before = eval target after

def put (values : Values) (index value : Nat) : Values :=
  fun position => if position = index then value else values position

def Except (index : Nat) (before after : Values) : Prop :=
  ∀ position, position ≠ index → before position = after position

theorem put_except (values : Values) (index old new : Nat) :
    Except index (put values index old) (put values index new) := by
  intro position other
  simp [put, other]

theorem put_preserves_except (source index value : Nat) (before after : Values)
    (h : Except source before after) : Except source (put before index value) (put after index value) := by
  intro position other
  by_cases same : position = index
  · simp [put, same]
  · simpa [put, same] using h position other

theorem unrelated_eval (g : Graph) (source target : Nat) (before after : Values)
    (h : Except source before after) (unread : g.reads target source = false) :
    g.eval target before = g.eval target after := by
  apply g.depends
  intro provider edge
  apply h
  intro same
  subst provider
  simp [unread] at edge

def coherent (g : Graph) (values : Values) (offset : Nat) : List Node → Prop
  | [] => True
  | n :: rest => localValid n ∧
      (n.refresh = false → n.endpoint.value = g.eval offset values) ∧
      coherent g (put values offset n.installed.value) (offset + 1) rest

def markAffected (g : Graph) (source : Nat) (offset : Nat) : List Node → List Node
  | [] => []
  | n :: rest =>
    (if g.reads offset source then { n with refresh := true } else n) ::
      markAffected g source (offset + 1) rest

def downstream (g : Graph) (source offset old new : Nat) (rest : List Node) : List Node :=
  if new = old then rest else markAffected g source offset rest

inductive Step (g : Graph) : Values → Nat → List Node → List Node → Prop
  | refresh {values offset} (n rest) (pending : n.refresh = true) :
      Step g values offset (n :: rest) (refreshNode (g.eval offset values) n :: rest)
  | select {values offset} (n rest) (pending : n.queued = true) (free : n.inflight = none) :
      Step g values offset (n :: rest) (selectNode n :: rest)
  | complete {values offset} (n rest job) (pending : n.inflight = some job) :
      Step g values offset (n :: rest)
        (completeNode n :: downstream g offset (offset + 1)
          n.installed.value (completeNode n).installed.value rest)
  | later {values offset} (n rest next)
      (step : Step g (put values offset n.installed.value) (offset + 1) rest next) :
      Step g values offset (n :: rest) (n :: next)

def capacity : Nat → Nat
  | 0 => 0
  | count + 1 => 3 * (capacity count + 1) + capacity count

def weight : List Node → Nat
  | [] => 0
  | n :: rest => localWeight (capacity rest.length + 1) n + weight rest

def allQuiet : List Node → Prop
  | [] => True
  | n :: rest => quiet n ∧ allQuiet rest

def expected (g : Graph) (values : Values) (offset : Nat) : Nat → List Nat
  | 0 => []
  | count + 1 =>
    let value := g.eval offset values
    value :: expected g (put values offset value) (offset + 1) count

theorem marked_length (g : Graph) (source offset : Nat) (nodes : List Node) :
    (markAffected g source offset nodes).length = nodes.length := by
  induction nodes generalizing offset with
  | nil => rfl
  | cons n rest ih => simp [markAffected, ih]

theorem marked_coherent (g : Graph) (source offset : Nat) (before after : Values)
    (nodes : List Node) (h : coherent g before offset nodes) (outside : Except source before after) :
    coherent g after offset (markAffected g source offset nodes) := by
  induction nodes generalizing before after offset with
  | nil => trivial
  | cons n rest ih =>
    cases edge : g.reads offset source with
    | true =>
      simp only [markAffected, edge, ↓reduceIte, coherent]
      exact ⟨h.1, by simp, ih _ _ _ h.2.2 (put_preserves_except _ _ _ _ _ outside)⟩
    | false =>
      simp only [markAffected, edge, Bool.false_eq_true, ↓reduceIte, coherent]
      refine ⟨h.1, ?_, ih _ _ _ h.2.2 (put_preserves_except _ _ _ _ _ outside)⟩
      intro ready
      exact (h.2.1 ready).trans (unrelated_eval g source offset before after outside edge)

theorem downstream_coherent (g : Graph) (values : Values) (source offset old new : Nat)
    (nodes : List Node) (h : coherent g (put values source old) offset nodes) :
    coherent g (put values source new) offset (downstream g source offset old new nodes) := by
  by_cases same : new = old
  · simpa [downstream, same] using h
  · simpa [downstream, same] using marked_coherent g source offset _ _ nodes h (put_except values source old new)

theorem step_coherent {g values offset before after}
    (step : Step g values offset before after)
    (h : coherent g values offset before) : coherent g values offset after := by
  induction step with
  | refresh n rest pending =>
    refine ⟨refresh_valid n _ h.1, fun _ => (refresh_value n _).1, ?_⟩
    simpa only [(refresh_value n _).2] using h.2.2
  | select n rest pending free => exact ⟨select_valid n h.1, h.2.1, h.2.2⟩
  | complete n rest job pending =>
    refine ⟨complete_valid n h.1, ?_, downstream_coherent _ _ _ _ _ _ _ h.2.2⟩
    simpa only [(complete_endpoint_refresh_unchanged n).1,
      (complete_endpoint_refresh_unchanged n).2] using h.2.1
  | later n rest next step ih => exact ⟨h.1, h.2.1, ih h.2.2⟩

theorem downstream_length (g : Graph) (source offset old new : Nat) (nodes : List Node) :
    (downstream g source offset old new nodes).length = nodes.length := by
  by_cases same : new = old <;> simp [downstream, same, marked_length]

theorem step_length {g values offset before after}
    (step : Step g values offset before after) : after.length = before.length := by
  induction step with
  | refresh => rfl
  | select => rfl
  | complete n rest job pending => simp [downstream_length]
  | later n rest next step ih => simp [ih]

theorem marked_weight (g : Graph) (source offset : Nat) (nodes : List Node) :
    weight (markAffected g source offset nodes) ≤ weight nodes + capacity nodes.length := by
  induction nodes generalizing offset with
  | nil => simp [markAffected, weight, capacity]
  | cons n rest ih =>
    have bound := ih (offset + 1)
    simp only [markAffected, weight, marked_length, List.length_cons, capacity]
    cases edge : g.reads offset source <;> cases pending : n.refresh <;>
      simp only [localWeight, pending, Bool.false_eq_true, ↓reduceIte] <;> omega

theorem downstream_weight (g : Graph) (source offset old new : Nat) (nodes : List Node) :
    weight (downstream g source offset old new nodes) ≤ weight nodes + capacity nodes.length := by
  by_cases same : new = old
  · simp [downstream, same]
  · simpa [downstream, same] using marked_weight g source offset nodes

theorem step_decreases {g values offset before after}
    (step : Step g values offset before after) : weight after < weight before := by
  induction step with
  | refresh n rest pending =>
    exact Nat.add_lt_add_right (refresh_weight _ (by omega) n _ pending) _
  | select n rest pending free =>
    exact Nat.add_lt_add_right (select_weight _ (by omega) n pending free) _
  | @complete values offset n rest job pending =>
    have spent := complete_weight (capacity rest.length + 1) n job pending
    have added := downstream_weight g offset (offset + 1) n.installed.value (completeNode n).installed.value rest
    simp only [weight, downstream_length]
    omega
  | later n rest next step ih =>
    have same := step_length step
    simp only [weight, same]
    exact Nat.add_lt_add_left ih _

theorem quiet_dependency_values (g : Graph) (values : Values) (offset : Nat)
    (nodes : List Node) (h : coherent g values offset nodes) (done : allQuiet nodes) :
    nodes.map (fun n => n.installed.value) = expected g values offset nodes.length := by
  induction nodes generalizing values offset with
  | nil => rfl
  | cons n rest ih =>
    have installed : n.installed = n.endpoint := by
      rcases h.1.2.2 with same | queued | active
      · exact same
      · simp [done.1.2.1] at queued
      · simp [done.1.2.2] at active
    have value : n.installed.value = g.eval offset values := by
      rw [installed]
      exact h.2.1 done.1.1
    simp only [List.map_cons, List.length_cons, expected]
    rw [←value]
    exact congrArg (List.cons n.installed.value) (ih _ _ h.2.2 done.2)

theorem progress (g : Graph) (values : Values) (offset : Nat) (nodes : List Node) :
    allQuiet nodes ∨ ∃ next, Step g values offset nodes next := by
  induction nodes generalizing values offset with
  | nil => exact Or.inl trivial
  | cons n rest ih =>
    cases refresh : n.refresh with
    | true => exact Or.inr ⟨_, Step.refresh n rest refresh⟩
    | false =>
      cases active : n.inflight with
      | some job => exact Or.inr ⟨_, Step.complete n rest job active⟩
      | none =>
        cases queued : n.queued with
        | true => exact Or.inr ⟨_, Step.select n rest queued active⟩
        | false =>
          rcases ih (put values offset n.installed.value) (offset + 1) with done | ⟨next, step⟩
          · exact Or.inl ⟨⟨refresh, queued, active⟩, done⟩
          · exact Or.inr ⟨_, Step.later n rest next step⟩

inductive History (g : Graph) (values : Values) (offset : Nat) : Nat → List Node → List Node → Prop
  | zero (nodes) : History g values offset 0 nodes nodes
  | next {count before middle after} (step : Step g values offset before middle)
      (rest : History g values offset count middle after) :
      History g values offset (count + 1) before after

theorem history_budget {g : Graph} {values : Values} {offset count : Nat}
    {before after : List Node} (history : History g values offset count before after) :
    weight after + count ≤ weight before := by
  induction history with
  | zero => omega
  | next step rest ih => have decreases := step_decreases step; omega

theorem history_coherent {g : Graph} {values : Values} {offset count : Nat}
    {before after : List Node} (history : History g values offset count before after)
    (h : coherent g values offset before) : coherent g values offset after := by
  induction history with
  | zero => exact h
  | next step rest ih => exact ih (step_coherent step h)

theorem history_length {g values offset count before after}
    (history : History g values offset count before after) : after.length = before.length := by
  induction history with
  | zero => rfl
  | next step rest ih => exact ih.trans (step_length step)

theorem stopped_values {g : Graph} {values : Values} {offset count : Nat}
    {before after : List Node} (history : History g values offset count before after)
    (h : coherent g values offset before)
    (stopped : ¬∃ next, Step g values offset after next) :
    after.map (fun n => n.installed.value) = expected g values offset after.length := by
  have done : allQuiet after := (progress g values offset after).resolve_right stopped
  exact quiet_dependency_values _ _ _ _ (history_coherent history h) done

theorem finite_settlement (g : Graph) (values : Values) (offset : Nat)
    (nodes : List Node) :
    ∃ count after, History g values offset count nodes after ∧
      allQuiet after ∧ count ≤ weight nodes := by
  have terminate : ∀ budget, ∀ before : List Node, weight before = budget →
      ∃ count after, History g values offset count before after ∧
        allQuiet after ∧ count ≤ weight before := by
    intro budget
    induction budget using Nat.strongRecOn with
    | ind budget ih =>
      intro before bound
      rcases progress g values offset before with done | ⟨next, step⟩
      · exact ⟨0, before, History.zero before, done, Nat.zero_le _⟩
      · have lower : weight next < budget := by
          have decrease := step_decreases step
          omega
        rcases ih (weight next) lower next rfl with ⟨count, after, history, done, _⟩
        have combined := History.next step history
        have limit := history_budget combined
        exact ⟨count + 1, after, combined, done, by omega⟩
  exact terminate (weight nodes) nodes rfl

theorem finite_ready (g : Graph) (values : Values) (offset : Nat)
    (nodes : List Node) (h : coherent g values offset nodes) :
    ∃ count after, History g values offset count nodes after ∧
      allQuiet after ∧ count ≤ weight nodes ∧
      after.map (fun n => n.installed.value) = expected g values offset nodes.length := by
  rcases finite_settlement g values offset nodes with ⟨count, after, history, done, bound⟩
  have result := quiet_dependency_values g values offset after (history_coherent history h) done
  rw [history_length history] at result
  exact ⟨count, after, history, done, bound, result⟩


def AgreeBefore (offset : Nat) (before after : Values) : Prop :=
  ∀ provider, provider < offset → before provider = after provider

theorem earlier_values_suffice (g : Graph) (offset : Nat) (before after : Values)
    (h : AgreeBefore offset before after) : g.eval offset before = g.eval offset after := by
  exact g.depends offset before after (fun provider edge => h provider (g.earlier offset provider edge))

theorem put_agrees (offset value : Nat) (before after : Values)
    (h : AgreeBefore offset before after) :
    AgreeBefore (offset + 1) (put before offset value) (put after offset value) := by
  intro provider less
  by_cases same : provider = offset
  · simp [put, same]
  · simpa [put, same] using h provider (by omega)

theorem expected_ignores_future (g : Graph) (offset count : Nat) (before after : Values)
    (h : AgreeBefore offset before after) :
    expected g before offset count = expected g after offset count := by
  induction count generalizing offset before after with
  | zero => rfl
  | succ count ih =>
    have same := earlier_values_suffice g offset before after h
    simp only [expected, same]
    exact congrArg (List.cons (g.eval offset after)) (ih _ _ _ (put_agrees _ _ _ _ h))

theorem no_two_cycle (g : Graph) (first second : Nat)
    (forward : g.reads second first = true) (backward : g.reads first second = true) : False := by
  have left := g.earlier second first forward
  have right := g.earlier first second backward
  omega

def sharedReads (target provider : Nat) : Bool :=
  decide ((target = 1 ∧ provider = 0) ∨ (target = 2 ∧ (provider = 0 ∨ provider = 1)))

def sharedEval (target : Nat) (values : Values) : Nat :=
  if target = 0 then 2 else if target = 1 then 2 * values 0 else
  if target = 2 then values 0 + values 1 else 7

def shared : Graph where
  reads := sharedReads
  eval := sharedEval
  earlier := by
    intro target provider edge
    simp only [sharedReads, decide_eq_true_eq] at edge
    omega
  depends := by
    intro target before after h
    by_cases zero : target = 0
    · simp [sharedEval, zero]
    by_cases one : target = 1
    · have same := h 0 (by simp [sharedReads, one])
      simp [sharedEval, one, same]
    by_cases two : target = 2
    · have root := h 0 (by simp [sharedReads, two])
      have parent := h 1 (by simp [sharedReads, two])
      simp [sharedEval, two, root, parent]
    · simp [sharedEval, zero, one, two]

def zeroValues : Values := fun _ => 0

def rootJob : Node := ⟨⟨1, 2⟩, ⟨0, 0⟩, false, false, some ⟨1, 2⟩⟩
def oldConsumer : Node := ⟨⟨0, 0⟩, ⟨0, 0⟩, false, false, none⟩
def unrelated : Node := ⟨⟨0, 7⟩, ⟨0, 7⟩, false, false, none⟩
def sharedBefore : List Node := [rootJob, oldConsumer, oldConsumer, unrelated]
def sharedAfter : List Node := completeNode rootJob ::
  downstream shared 0 1 0 2 [oldConsumer, oldConsumer, unrelated]
def dropped : List Node := [completeNode rootJob, oldConsumer, oldConsumer, unrelated]

theorem shared_initial_coherent : coherent shared zeroValues 0 sharedBefore := by
  simp [coherent, sharedBefore, rootJob, oldConsumer, unrelated, localValid,
    shared, sharedEval, put]

theorem shared_completion : Step shared zeroValues 0 sharedBefore sharedAfter := by
  exact Step.complete rootJob [oldConsumer, oldConsumer, unrelated] ⟨1, 2⟩ rfl

theorem exact_shared_invalidation :
    sharedAfter.map (fun n => n.refresh) = [false, true, true, false] ∧
    (markAffected shared 1 2 [oldConsumer, unrelated]).map (fun n => n.refresh) = [true, false] := by
  decide +kernel

theorem independent_shared_values : expected shared zeroValues 0 4 = [2, 4, 6, 7] := by
  decide +kernel

theorem shared_ready_exists :
    ∃ count after, History shared zeroValues 0 count sharedBefore after ∧ allQuiet after ∧
      count ≤ weight sharedBefore ∧ after.map (fun n => n.installed.value) = [2, 4, 6, 7] := by
  have size : sharedBefore.length = 4 := rfl
  simpa only [size, independent_shared_values]
    using finite_ready shared zeroValues 0 sharedBefore shared_initial_coherent

theorem dropped_shared_work :
    allQuiet dropped ∧ dropped.map (fun n => n.installed.value) ≠ expected shared zeroValues 0 4 := by
  constructor
  · simp [allQuiet, quiet, dropped, rootJob, oldConsumer, unrelated, completeNode]
  · decide +kernel

def staleSelected : List Node := [CoalescedChain.newer80]
def staleCompleted : List Node := [CoalescedChain.afterStale]

theorem stale_graph_completion : Step shared zeroValues 0 staleSelected staleCompleted := by
  simpa [staleSelected, staleCompleted, downstream, markAffected,
    CoalescedChain.afterStale, CoalescedChain.newer80, CoalescedChain.selected64,
    CoalescedChain.pending64, selectNode, refreshNode, completeNode]
    using (Step.complete (g := shared) (values := zeroValues) (offset := 0)
      CoalescedChain.newer80 [] ⟨1, 64⟩ rfl)

def orderedWithin (reads : Nat → Nat → Bool) (count : Nat) : Bool :=
  (List.range count).all (fun target =>
    (List.range count).all (fun provider => !reads target provider || decide (provider < target)))

def cycleReads (target provider : Nat) : Bool :=
  decide ((target = 0 ∧ provider = 1) ∨ (target = 1 ∧ provider = 0))

theorem finite_edge_order_controls :
    orderedWithin shared.reads 4 = true ∧ orderedWithin cycleReads 2 = false := by
  decide +kernel

end CoalescedDAG
