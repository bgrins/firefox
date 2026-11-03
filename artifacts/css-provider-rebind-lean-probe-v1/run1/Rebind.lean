import Coalesced

namespace ProviderRebind
open CoalescedChain

inductive Parent where
  | a | b
  deriving DecidableEq, Repr

structure World where
  root : Nat
  a : Nat
  b : Nat
  deriving DecidableEq, Repr

structure Consumer where
  parent : Parent
  context : Nat
  node : Node
  deriving DecidableEq, Repr

def expected (w : World) (p : Parent) : Nat :=
  2 * (match p with | .a => w.a | .b => w.b) + w.root

def coherent (w : World) (s : Consumer) : Prop :=
  localValid s.node ∧ (s.node.refresh = false → s.node.endpoint.value = expected w s.parent)

def invalidate (p : Parent) (s : Consumer) : Consumer :=
  { parent := p, context := s.context + 1,
    node := { s.node with endpoint := ⟨s.node.endpoint.generation + 1, s.node.endpoint.value⟩,
                         refresh := true, queued := true } }

def refresh (w : World) (s : Consumer) : Consumer :=
  { s with node := refreshNode (expected w s.parent) s.node }

def select (s : Consumer) : Consumer := { s with node := selectNode s.node }
def complete (s : Consumer) : Consumer := { s with node := completeNode s.node }

theorem invalidate_valid (w : World) (s : Consumer) (p : Parent)
    (h : localValid s.node) : coherent w (invalidate p s) := by
  refine ⟨?_, by simp [invalidate]⟩
  simp only [invalidate, localValid]
  refine ⟨by have hi := h.1; omega, ?_, Or.inr (Or.inl rfl)⟩
  intro job pending
  have bound := (h.2.1 job pending).1
  exact ⟨by omega, by intro impossible; omega⟩

theorem rebind_keeps_numeric_endpoint (s : Consumer) (p : Parent) :
    (invalidate p s).node.endpoint.value = s.node.endpoint.value ∧
    (invalidate p s).context > s.context := by
  simp [invalidate]

theorem old_completion_cannot_publish (s : Consumer) (p : Parent) (job)
    (h : localValid s.node) (pending : s.node.inflight = some job) :
    (complete (invalidate p s)).node.installed = s.node.installed ∧
    (complete (invalidate p s)).node.refresh = true ∧
    (complete (invalidate p s)).node.queued = true := by
  have bound := (h.2.1 job pending).1
  have stale : job.generation ≠ s.node.endpoint.generation + 1 := by omega
  simp [complete, invalidate, completeNode, pending, stale]

theorem refresh_coherent (w : World) (s : Consumer) (h : coherent w s) :
    coherent w (refresh w s) := by
  exact ⟨refresh_valid _ _ h.1, fun _ => (refresh_value _ _).1⟩

theorem select_coherent (w : World) (s : Consumer) (h : coherent w s) :
    coherent w (select s) := by
  exact ⟨select_valid _ h.1, h.2⟩

theorem complete_coherent (w : World) (s : Consumer) (h : coherent w s) :
    coherent w (complete s) := by
  refine ⟨complete_valid _ h.1, ?_⟩
  intro quietRefresh
  have same := complete_endpoint_refresh_unchanged s.node
  simpa [complete, same.1] using h.2 (by simpa [complete, same.2] using quietRefresh)

theorem departed_parent_irrelevant (w : World) (newA : Nat) :
    expected { w with a := newA } .b = expected w .b := by rfl

theorem root_is_direct_dependency (w : World) (root : Nat) (p : Parent) :
    expected { w with root := root } p =
      2 * (match p with | .a => w.a | .b => w.b) + root := by rfl

theorem quiet_ready (w : World) (s : Consumer) (h : coherent w s)
    (done : quiet s.node) : s.node.installed.value = expected w s.parent := by
  have same : s.node.installed = s.node.endpoint := by
    rcases h.1.2.2 with same | queued | active
    · exact same
    · simp [done.2.1] at queued
    · simp [done.2.2] at active
  rw [same]
  exact h.2 done.1

theorem finite_ready_after_last_edit (w : World) (s : Consumer) (h : coherent w s) :
    ∃ count after,
      History 0 (fun _ _ => expected w s.parent) 0 count [s.node] after ∧
      allQuiet after ∧ count ≤ weight [s.node] ∧
      after.map (fun n => n.installed.value) = [expected w s.parent] := by
  have ready := CoalescedChain.finite_ready 0 (fun _ _ => expected w s.parent) 0 [s.node]
    (show CoalescedChain.coherent 0 (fun _ _ => expected w s.parent) 0 [s.node] from ⟨h.1, h.2, trivial⟩)
  simpa [CoalescedChain.expected] using ready

def world : World := ⟨16, 20, 20⟩
def pending : Consumer := ⟨.a, 0, ⟨⟨1, 56⟩, ⟨0, 10⟩, false, false, some ⟨1, 56⟩⟩⟩
def quiet56 : Consumer := ⟨.a, 0, ⟨⟨1, 56⟩, ⟨1, 56⟩, false, false, none⟩⟩
def badRebind : Consumer := { quiet56 with parent := .b }
def changed : World := { world with b := 30 }

theorem equal_value_context_change :
    expected world .a = expected world .b ∧
    (invalidate .b quiet56).context = 1 ∧ (invalidate .b quiet56).node.refresh = true := by
  decide +kernel

theorem missing_rebind_counterexample :
    quiet badRebind.node ∧ badRebind.node.installed.value ≠ expected changed badRebind.parent := by
  decide +kernel

theorem retained_old_job_counterexample :
    (complete (invalidate .b pending)).node.installed.value = 10 ∧
    (complete (invalidate .b pending)).node.queued = true := by
  decide +kernel

end ProviderRebind
