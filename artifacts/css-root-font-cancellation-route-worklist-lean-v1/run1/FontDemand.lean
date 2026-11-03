import Std

namespace FontConsumerDemand

inductive Demand where
  | none | size | metrics | oriented
  deriving DecidableEq, Repr

def rank : Demand → Nat
  | .none => 0
  | .size => 1
  | .metrics => 2
  | .oriented => 3

def Covers (available need : Demand) : Prop := rank need ≤ rank available

instance (available need : Demand) : Decidable (Covers available need) :=
  inferInstanceAs (Decidable (rank need ≤ rank available))

def join : Demand → Demand → Demand
  | .none, b => b
  | a, .none => a
  | .oriented, _ => .oriented
  | _, .oriented => .oriented
  | .metrics, _ => .metrics
  | _, .metrics => .metrics
  | .size, .size => .size

structure FontState where
  size : Nat
  font : Nat
  vertical : Bool
  deriving DecidableEq, Repr

def Ready (demand : Demand) (actual final : FontState) : Prop :=
  match demand with
  | .none => True
  | .size => actual.size = final.size
  | .metrics => actual.size = final.size ∧ actual.font = final.font
  | .oriented => actual.size = final.size ∧ actual.font = final.font ∧
      actual.vertical = final.vertical

instance (d : Demand) (actual final : FontState) : Decidable (Ready d actual final) := by
  cases d <;> unfold Ready <;> infer_instance

inductive Unit where
  | em | ex | ch | cap | ic
  deriving DecidableEq, Repr

def demand : Unit → Demand
  | .em => .size
  | .ex | .cap => .metrics
  | .ch | .ic => .oriented

inductive SemanticNode where
  | fontSize
  deriving DecidableEq, Repr

def semanticNode (_ : Unit) : SemanticNode := .fontSize
def coarseDemand (_ : Unit) : Demand := .size

inductive Inputs where
  | size (value : Nat)
  | metrics (size font : Nat)
  | oriented (size font : Nat) (vertical : Bool)
  deriving DecidableEq, Repr

def reads (state : FontState) : Unit → Inputs
  | .em => .size state.size
  | .ex | .cap => .metrics state.size state.font
  | .ch | .ic => .oriented state.size state.font state.vertical

def summary : List Unit → Demand
  | [] => .none
  | unit :: rest => join (demand unit) (summary rest)

def observations (state : FontState) (units : List Unit) : List Inputs :=
  units.map (reads state)

theorem join_assoc (a b c : Demand) : join (join a b) c = join a (join b c) := by
  cases a <;> cases b <;> cases c <;> rfl

theorem join_comm (a b : Demand) : join a b = join b a := by
  cases a <;> cases b <;> rfl

theorem join_covers_both (a b : Demand) : Covers (join a b) a ∧ Covers (join a b) b := by
  cases a <;> cases b <;> decide

theorem ready_weaken (available need : Demand) (actual final : FontState)
    (covered : Covers available need) (ready : Ready available actual final) :
    Ready need actual final := by
  cases available <;> cases need <;> simp_all [Covers, rank, Ready]

theorem ready_join (a b : Demand) (actual final : FontState) :
    Ready (join a b) actual final ↔ Ready a actual final ∧ Ready b actual final := by
  cases a <;> cases b <;> simp [join, Ready, and_left_comm, and_comm]

theorem ready_single_iff (unit : Unit) (actual final : FontState) :
    Ready (demand unit) actual final ↔ reads actual unit = reads final unit := by
  cases unit <;> simp [demand, Ready, reads]

theorem ready_summary_iff (units : List Unit) (actual final : FontState) :
    Ready (summary units) actual final ↔ observations actual units = observations final units := by
  induction units with
  | nil => simp [summary, Ready, observations]
  | cons unit rest ih =>
      simpa [summary, observations, ready_join, ready_single_iff] using
        and_congr (ready_single_iff unit actual final) ih

def zero : FontState := ⟨0, 0, false⟩
def sizeChanged : FontState := ⟨1, 0, false⟩
def fontChanged : FontState := ⟨0, 1, false⟩
def modeChanged : FontState := ⟨0, 0, true⟩

theorem universal_readiness_iff_covers (available need : Demand) :
    (∀ actual final, Ready available actual final → Ready need actual final) ↔ Covers available need := by
  constructor
  · intro h
    have hs := h zero sizeChanged
    have hf := h zero fontChanged
    have hm := h zero modeChanged
    cases available <;> cases need <;>
      simp_all [Covers, rank, Ready, zero, sizeChanged, fontChanged, modeChanged]
  · intro h actual final ready
    exact ready_weaken available need actual final h ready

theorem least_sufficient_projection (units : List Unit) (available : Demand) :
    (∀ actual final, Ready available actual final →
      observations actual units = observations final units) ↔ Covers available (summary units) := by
  rw [← universal_readiness_iff_covers]
  constructor
  · intro h actual final ready
    exact (ready_summary_iff units actual final).mpr (h actual final ready)
  · intro h actual final ready
    exact (ready_summary_iff units actual final).mp (h actual final ready)

theorem summary_append (left right : List Unit) :
    summary (left ++ right) = join (summary left) (summary right) := by
  induction left with
  | nil => rfl
  | cons unit rest ih => simp [summary, ih, join_assoc]

inductive Use (Name : Type) where
  | direct (unit : Unit)
  | alias (name : Name)

def expansion (resolve : Name → List Unit) : Use Name → List Unit
  | .direct unit => [unit]
  | .alias name => resolve name

def useDemand (resolve : Name → List Unit) : Use Name → Demand
  | .direct unit => demand unit
  | .alias name => summary (resolve name)

def unionDemands : List Demand → Demand
  | [] => .none
  | first :: rest => join first (unionDemands rest)

theorem alias_projection_composes (resolve : Name → List Unit) (uses : List (Use Name)) :
    summary (uses.flatMap (expansion resolve)) = unionDemands (uses.map (useDemand resolve)) := by
  induction uses with
  | nil => rfl
  | cons use rest ih =>
      simp only [List.flatMap_cons, List.map_cons, summary_append, unionDemands, ih]
      cases use with
      | direct unit => cases unit <;> rfl
      | alias name => rfl

def accumulate (held : Demand) : List (List Unit) → Demand
  | [] => held
  | batch :: rest => accumulate (join held (summary batch)) rest

theorem accumulated_demand_exact (held : Demand) (batches : List (List Unit)) :
    accumulate held batches = join held (summary batches.flatten) := by
  induction batches generalizing held with
  | nil => cases held <;> rfl
  | cons batch rest ih =>
      simp only [accumulate, List.flatten_cons, summary_append]
      rw [ih, join_assoc]

theorem later_demands_preserved (held : Demand) (batches : List (List Unit)) :
    Covers (accumulate held batches) held ∧
      Covers (accumulate held batches) (summary batches.flatten) := by
  rw [accumulated_demand_exact]
  exact join_covers_both held (summary batches.flatten)

theorem ready_after_escalation (held : Demand) (batches : List (List Unit))
    (actual final : FontState) :
    Ready (accumulate held batches) actual final ↔
      Ready held actual final ∧
      observations actual batches.flatten = observations final batches.flatten := by
  rw [accumulated_demand_exact, ready_join, ready_summary_iff]

def oldFamily : FontState := ⟨20, 1, false⟩
def finalFamily : FontState := ⟨20, 2, false⟩
def finalVertical : FontState := ⟨20, 2, true⟩

theorem coarse_projection_loses_metric_information :
    semanticNode .em = semanticNode .ch ∧
    coarseDemand .em = coarseDemand .ch ∧
    Ready (coarseDemand .ch) oldFamily finalFamily ∧
    reads oldFamily .ch ≠ reads finalFamily .ch := by decide

theorem metrics_without_orientation_is_insufficient :
    Ready .metrics finalFamily finalVertical ∧
    reads finalFamily .ch ≠ reads finalVertical .ch := by decide

theorem later_alias_requires_upgrade :
    let resolve : Nat → List Unit := fun _ => [.ch]
    let requested := summary ([Use.alias 0].flatMap (expansion resolve))
    join .size requested = .oriented ∧
    Ready .size oldFamily finalFamily ∧
    ¬ Ready (join .size requested) oldFamily finalFamily := by decide

end FontConsumerDemand
