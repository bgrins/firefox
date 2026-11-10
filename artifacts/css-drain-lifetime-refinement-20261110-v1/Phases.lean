import DAG
import Certified

namespace DescendingPhases
open CertifiedPath (Tree path)
open CoalescedChain (Node localWeight)
open CoalescedDAG (Graph capacity)

def StrictDesc (t : Tree) (ancestor child : Nat) : Prop :=
  0 < child ∧ ancestor ∈ path t (t.parent child)
instance (t : Tree) (ancestor child : Nat) : Decidable (StrictDesc t ancestor child) :=
  inferInstanceAs (Decidable (0 < child ∧ ancestor ∈ path t (t.parent child)))
def normal (node : Nat) := 2 * node
def application (node : Nat) := 2 * node + 1

def routes (t : Tree) (target source : Nat) : Bool :=
  if source % 2 = 0 then decide (target = source + 1)
  else decide (target % 2 = 0 ∧ StrictDesc t (source / 2) (target / 2))

def allowed (t : Tree) (target source : Nat) : Bool :=
  decide (target / 2 ≤ t.size ∧ source / 2 ≤ t.size) && routes t target source

theorem descendant_rank (t : Tree) {ancestor child : Nat} (h : StrictDesc t ancestor child) :
    ancestor < child := by
  cases child with
  | zero => simp [StrictDesc] at h
  | succ k =>
    have hp := CertifiedPath.path_upper t (t.parent (k + 1)) ancestor h.2
    have hl := t.lower k
    omega

theorem allowed_earlier (t : Tree) (target source : Nat)
    (h : allowed t target source = true) : source < target := by
  simp only [allowed, Bool.and_eq_true, decide_eq_true_eq] at h
  have route := h.2
  by_cases hn : source % 2 = 0
  · simp only [routes, hn, ↓reduceIte, decide_eq_true_eq] at route
    omega
  · simp only [routes, hn, ↓reduceIte, decide_eq_true_eq] at route
    have hd := descendant_rank t route.2
    omega

theorem normal_to_same_application (t : Tree) (node : Nat) (hn : node ≤ t.size) :
    allowed t (application node) (normal node) = true := by
  have hd : (2 * node + 1) / 2 = node := by omega
  simp [allowed, routes, application, normal, hd, hn]

theorem application_to_descendant (t : Tree) (ancestor child : Nat)
    (h : StrictDesc t ancestor child) (hc : child ≤ t.size) :
    allowed t (normal child) (application ancestor) = true := by
  have hd : (2 * ancestor + 1) / 2 = ancestor := by omega
  have ha : ancestor ≤ t.size := by have := descendant_rank t h; omega
  simp [allowed, routes, normal, application, hd, ha, hc, h]

theorem no_application_to_self (t : Tree) (node : Nat) :
    allowed t (normal node) (application node) = false := by
  cases he : allowed t (normal node) (application node) with
  | false => rfl
  | true =>
    have h := allowed_earlier t _ _ he
    simp only [normal, application] at h
    omega

def maskedGraph (t : Tree) (choice : Nat → Nat → Bool) : Graph where
  reads := fun target source => allowed t target source && choice target source
  eval := fun _ _ => 0
  earlier := by
    intro target source edge
    simp only [Bool.and_eq_true] at edge
    exact allowed_earlier t target source edge.1
  depends := by intros; rfl

def pendingNode (b : Bool) : Node := ⟨⟨0, 0⟩, ⟨0, 0⟩, b, false, none⟩
def encode (bits : List Bool) : List Node := bits.map pendingNode

def mark (g : Graph) (source : Nat) : Nat → List Bool → List Bool
  | _, [] => []
  | offset, b :: rest => (if g.reads offset source then true else b) :: mark g source (offset + 1) rest

def weight (bits : List Bool) := CoalescedDAG.weight (encode bits)

theorem encode_length (bits : List Bool) : (encode bits).length = bits.length := by
  simp [encode]

theorem mark_length (g : Graph) (source offset : Nat) (bits : List Bool) :
    (mark g source offset bits).length = bits.length := by
  induction bits generalizing offset with
  | nil => rfl
  | cons b rest ih => simp [mark, ih]

theorem encode_mark (g : Graph) (source offset : Nat) (bits : List Bool) :
    encode (mark g source offset bits) = CoalescedDAG.markAffected g source offset (encode bits) := by
  induction bits generalizing offset with
  | nil => rfl
  | cons b rest ih =>
    cases h : g.reads offset source <;>
      simp [encode, mark, CoalescedDAG.markAffected, h, pendingNode] <;>
      simpa only [encode] using ih (offset + 1)

theorem mark_weight (g : Graph) (source offset : Nat) (bits : List Bool) :
    weight (mark g source offset bits) ≤ weight bits + capacity bits.length := by
  simpa only [weight, encode_mark, encode_length] using
    CoalescedDAG.marked_weight g source offset (encode bits)

theorem weight_cons (b : Bool) (rest : List Bool) :
    weight (b :: rest) = (if b then 3 * (capacity rest.length + 1) else 0) + weight rest := by
  simp [weight, encode, CoalescedDAG.weight, pendingNode, localWeight]

inductive Step (t : Tree) : Nat → List Bool → List Bool → Prop
  | fire (offset : Nat) (rest : List Bool) (choice : Nat → Nat → Bool) :
      Step t offset (true :: rest)
        (false :: mark (maskedGraph t choice) offset (offset + 1) rest)
  | later {offset : Nat} (b : Bool) {rest next : List Bool} :
      Step t (offset + 1) rest next → Step t offset (b :: rest) (b :: next)

theorem step_length {t offset before after} (h : Step t offset before after) :
    after.length = before.length := by
  induction h with
  | fire => simp [mark_length]
  | later b h ih => simp [ih]

theorem step_decreases {t offset before after} (h : Step t offset before after) :
    weight after < weight before := by
  induction h with
  | fire offset rest choice =>
    have hm := mark_weight (maskedGraph t choice) offset (offset + 1) rest
    simp only [weight_cons, Bool.false_eq_true, ↓reduceIte, Nat.zero_add]
    omega
  | later b h ih =>
    have hl := step_length h
    simp only [weight_cons, hl]
    omega

def quiet (bits : List Bool) : Prop := ∀ b ∈ bits, b = false

theorem progress (t : Tree) (offset : Nat) (bits : List Bool) :
    quiet bits ∨ ∃ next, Step t offset bits next := by
  induction bits generalizing offset with
  | nil => left; simp [quiet]
  | cons b rest ih =>
    cases b with
    | true => exact Or.inr ⟨_, Step.fire offset rest (fun _ _ => true)⟩
    | false =>
      rcases ih (offset + 1) with done | ⟨next, h⟩
      · left; simpa [quiet] using done
      · exact Or.inr ⟨false :: next, Step.later false h⟩

inductive History (t : Tree) (offset : Nat) : Nat → List Bool → List Bool → Prop
  | zero (bits) : History t offset 0 bits bits
  | next {count before middle after} : Step t offset before middle →
      History t offset count middle after → History t offset (count + 1) before after

theorem history_budget {t offset count before after} (h : History t offset count before after) :
    weight after + count ≤ weight before := by
  induction h with
  | zero => omega
  | next step rest ih => have hd := step_decreases step; omega

theorem finite_empty_work (t : Tree) (offset : Nat) (bits : List Bool) :
    ∃ count after, History t offset count bits after ∧ quiet after ∧ count ≤ weight bits := by
  have finish : ∀ budget, ∀ before : List Bool, weight before = budget →
      ∃ count after, History t offset count before after ∧ quiet after ∧ count ≤ weight before := by
    intro budget
    induction budget using Nat.strongRecOn with
    | ind budget ih =>
      intro before hb
      rcases progress t offset before with done | ⟨next, step⟩
      · exact ⟨0, before, History.zero before, done, Nat.zero_le _⟩
      · have less : weight next < budget := by have := step_decreases step; omega
        obtain ⟨count, after, history, done, _⟩ := ih (weight next) less next rfl
        have combined := History.next step history
        have bound := history_budget combined
        exact ⟨count + 1, after, combined, done, by omega⟩
  exact finish (weight bits) bits rfl

theorem allowed_finite (t : Tree) (target source : Nat) (h : allowed t target source = true) :
    target < 2 * (t.size + 1) ∧ source < 2 * (t.size + 1) := by
  simp only [allowed, Bool.and_eq_true, decide_eq_true_eq] at h
  omega

theorem consumed_only_present {t offset before after} (h : Step t offset before after) :
    true ∈ before := by
  induction h with
  | fire => simp
  | later b h ih => exact List.mem_cons_of_mem b ih

theorem quiet_no_step (t : Tree) (offset : Nat) (before : List Bool) (hq : quiet before) :
    ¬ ∃ after, Step t offset before after := by
  rintro ⟨after, h⟩
  have impossible := hq true (consumed_only_present h)
  contradiction

theorem no_stutter {t offset bits} : ¬ Step t offset bits bits := by
  intro h
  have hd := step_decreases h
  omega

theorem history_length {t offset count before after} (h : History t offset count before after) :
    after.length = before.length := by
  induction h with
  | zero => rfl
  | next step rest ih => exact ih.trans (step_length step)

theorem finite_tree_shape (t : Tree) {count before after}
    (shape : before.length = 2 * (t.size + 1)) (h : History t 0 count before after) :
    after.length = 2 * (t.size + 1) := by
  exact (history_length h).trans shape

theorem no_infinite_productive_run (t : Tree) (offset : Nat) (stream : Nat → List Bool)
    (steps : ∀ n, Step t offset (stream n) (stream (n + 1))) : False := by
  have bound : ∀ n, weight (stream n) + n ≤ weight (stream 0) := by
    intro n
    induction n with
    | zero => omega
    | succ n ih => have hd := step_decreases (steps n); omega
  have impossible := bound (weight (stream 0) + 1)
  omega

inductive BroadStep : List Bool → List Bool → Prop
  | normal : BroadStep [true, false] [false, true]
  | selfSeed : BroadStep [false, true] [true, false]

inductive BroadHistory : Nat → List Bool → List Bool → Prop
  | zero (bits) : BroadHistory 0 bits bits
  | next {count before middle after} : BroadStep before middle →
      BroadHistory count middle after → BroadHistory (count + 1) before after

theorem broad_repeatable_cycle (n : Nat) :
    BroadHistory (2 * n) [true, false] [true, false] := by
  induction n with
  | zero => exact BroadHistory.zero _
  | succ n ih =>
    have two := BroadHistory.next BroadStep.normal (BroadHistory.next BroadStep.selfSeed ih)
    simpa [Nat.mul_add, Nat.add_assoc] using two

theorem broad_no_decreasing_rank (rank : List Bool → Nat)
    (decreases : ∀ before after, BroadStep before after → rank after < rank before) : False := by
  have hn := decreases _ _ BroadStep.normal
  have ha := decreases _ _ BroadStep.selfSeed
  omega

theorem broad_application_increases_rank :
    weight [false, true] < weight [true, false] := by decide +kernel

theorem ranked_root_edges :
    allowed CertifiedPath.chain 1 0 = true ∧
    allowed CertifiedPath.chain 2 1 = true ∧
    allowed CertifiedPath.chain 0 1 = false ∧
    allowed CertifiedPath.chain 3 1 = false := by decide +kernel

theorem exact_normal_mask :
    mark (maskedGraph CertifiedPath.chain (fun _ _ => true)) 0 1
      [false, false, false, false] = [true, false, false, false] := by decide +kernel

theorem exact_application_mask :
    mark (maskedGraph CertifiedPath.chain (fun _ _ => true)) 1 2
      [false, false, false, false] = [true, false, true, false] := by decide +kernel

theorem coalesced_mask :
    mark (maskedGraph CertifiedPath.chain (fun _ _ => true)) 1 2
      [true, false, true, false] = [true, false, true, false] := by decide +kernel

theorem no_new_work_choice :
    mark (maskedGraph CertifiedPath.chain (fun _ _ => false)) 1 2
      [false, true, false, true] = [false, true, false, true] := by decide +kernel

theorem weight_capacity (bits : List Bool) : weight bits ≤ capacity bits.length := by
  induction bits with
  | nil => simp [weight, encode, CoalescedDAG.weight, capacity]
  | cons b rest ih =>
    simp only [weight_cons, List.length_cons, capacity]
    cases b <;> simp only [Bool.false_eq_true, ↓reduceIte] <;> omega

theorem finite_tree_dispatch_bound (t : Tree) {count before after}
    (shape : before.length = 2 * (t.size + 1)) (h : History t 0 count before after) :
    count ≤ capacity (2 * (t.size + 1)) := by
  have budget := history_budget h
  have cap := weight_capacity before
  rw [shape] at cap
  omega

theorem graph_not_backward (g : Graph) (target source : Nat) (h : target ≤ source) :
    g.reads target source = false := by
  cases he : g.reads target source with
  | false => rfl
  | true => have earlier := g.earlier target source he; omega

theorem mark_keeps_prefix (g : Graph) (source offset : Nat) (front tail : List Bool)
    (bound : offset + front.length ≤ source + 1) :
    mark g source offset (front ++ tail) =
      front ++ mark g source (offset + front.length) tail := by
  induction front generalizing offset with
  | nil => simp
  | cons b front ih =>
    have unread := graph_not_backward g offset source (by simp only [List.length_cons] at bound; omega)
    have rest := ih (offset + 1) (by simp only [List.length_cons] at bound; omega)
    simp only [List.cons_append, mark, unread, Bool.false_eq_true, ↓reduceIte]
    rw [rest]
    simp [Nat.add_comm, Nat.add_left_comm]

theorem full_mark_equals_suffix (g : Graph) (offset : Nat) (front rest : List Bool) :
    mark g (offset + front.length) offset (front ++ false :: rest) =
      front ++ false :: mark g (offset + front.length) (offset + front.length + 1) rest := by
  have h := mark_keeps_prefix g (offset + front.length) offset (front ++ [false]) rest (by simp [Nat.add_assoc])
  simpa [List.append_assoc, Nat.add_assoc] using h

theorem lift_step (t : Tree) (offset : Nat) (front before after : List Bool)
    (h : Step t (offset + front.length) before after) :
    Step t offset (front ++ before) (front ++ after) := by
  induction front generalizing offset with
  | nil => simpa using h
  | cons b front ih =>
    apply Step.later b
    apply ih (offset + 1)
    simpa [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using h

def dispatch (t : Tree) (offset : Nat) (front rest : List Bool) (choice : Nat → Nat → Bool) : List Bool :=
  mark (maskedGraph t choice) (offset + front.length) offset (front ++ false :: rest)

theorem full_dispatch_step (t : Tree) (offset : Nat) (front rest : List Bool)
    (choice : Nat → Nat → Bool) :
    Step t offset (front ++ true :: rest) (dispatch t offset front rest choice) := by
  rw [dispatch, full_mark_equals_suffix]
  exact lift_step t offset front _ _ (Step.fire (offset + front.length) rest choice)

theorem full_dispatch_decreases (t : Tree) (offset : Nat) (front rest : List Bool)
    (choice : Nat → Nat → Bool) :
    weight (dispatch t offset front rest choice) < weight (front ++ true :: rest) := by
  exact step_decreases (full_dispatch_step t offset front rest choice)

end DescendingPhases
