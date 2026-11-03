import Application

namespace EndpointWaves

abbrev Chain := Nat → EndpointApplication.State
abbrev Compute := Nat → Nat → Nat

def valid (depth : Nat) (nodes : Chain) : Prop :=
  ∀ i, i < depth → EndpointApplication.valid (nodes i)

def parentValue (root : Nat) (nodes : Chain) : Nat → Nat
  | 0 => root
  | i + 1 => (nodes i).installed.value

def expected (root : Nat) (compute : Compute) : Nat → Nat
  | 0 => compute 0 root
  | i + 1 => compute (i + 1) (expected root compute i)

def wave (depth root : Nat) (compute : Compute) (nodes : Chain) : Chain :=
  fun i => if i < depth then
    EndpointApplication.drain (EndpointApplication.refresh
      (compute i (parentValue root nodes i)) (nodes i))
  else nodes i

def waves (depth root : Nat) (compute : Compute) : Nat → Chain → Chain
  | 0, nodes => nodes
  | budget + 1, nodes => wave depth root compute (waves depth root compute budget nodes)

def ready (depth root : Nat) (compute : Compute) (nodes : Chain) : Prop :=
  ∀ i, i < depth → EndpointApplication.ready (nodes i) ∧
    (nodes i).installed.value = expected root compute i

theorem refresh_endpoint_value (s : EndpointApplication.State) (value : Nat) :
    (EndpointApplication.refresh value s).endpoint.value = value := by
  by_cases same : value = s.endpoint.value
  · simp [EndpointApplication.refresh, same]
  · simp [EndpointApplication.refresh, same]

theorem refresh_then_drain_value (s : EndpointApplication.State) (value : Nat)
    (h : EndpointApplication.valid s) :
    (EndpointApplication.drain (EndpointApplication.refresh value s)).installed.value = value := by
  have current := (EndpointApplication.stable_drain_ready _
    (EndpointApplication.refresh_valid s value h)).2
  rw [current]
  exact refresh_endpoint_value s value

theorem wave_valid (depth root : Nat) (compute : Compute) (nodes : Chain)
    (h : valid depth nodes) : valid depth (wave depth root compute nodes) := by
  intro i within
  simp only [wave, within, ↓reduceIte]
  exact EndpointApplication.drain_valid _
    (EndpointApplication.refresh_valid _ _ (h i within))

theorem waves_valid (depth root : Nat) (compute : Compute) (nodes : Chain)
    (budget : Nat) (h : valid depth nodes) :
    valid depth (waves depth root compute budget nodes) := by
  induction budget with
  | zero => exact h
  | succ budget ih => exact wave_valid _ _ _ _ ih

theorem wave_uses_previous_parent (depth root : Nat) (compute : Compute)
    (nodes : Chain) (i : Nat) (within : i < depth) (h : valid depth nodes) :
    (wave depth root compute nodes i).installed.value = compute i (parentValue root nodes i) := by
  simp only [wave, within, ↓reduceIte]
  exact refresh_then_drain_value _ _ (h i within)

theorem wave_locally_ready (depth root : Nat) (compute : Compute)
    (nodes : Chain) (i : Nat) (within : i < depth) (h : valid depth nodes) :
    EndpointApplication.ready (wave depth root compute nodes i) := by
  simp only [wave, within, ↓reduceIte]
  exact EndpointApplication.stable_drain_ready _
    (EndpointApplication.refresh_valid _ _ (h i within))

theorem outside_chain_unchanged (depth root : Nat) (compute : Compute)
    (nodes : Chain) (i : Nat) (outside : depth ≤ i) :
    wave depth root compute nodes i = nodes i := by
  simp [wave, Nat.not_lt_of_ge outside]

theorem rank_bound (depth root : Nat) (compute : Compute) (nodes : Chain)
    (h : valid depth nodes) (i budget : Nat) (within : i < depth)
    (enough : i + 1 ≤ budget) :
    (waves depth root compute budget nodes i).installed.value = expected root compute i := by
  induction i generalizing budget with
  | zero =>
    cases budget with
    | zero => omega
    | succ budget =>
      rw [waves, wave_uses_previous_parent _ _ _ _ _ within (waves_valid _ _ _ _ budget h)]
      rfl
  | succ i ih =>
    cases budget with
    | zero => omega
    | succ budget =>
      rw [waves, wave_uses_previous_parent _ _ _ _ _ within (waves_valid _ _ _ _ budget h)]
      simp only [parentValue, expected]
      rw [ih budget (by omega) (by omega)]

theorem depth_waves_ready (depth root : Nat) (compute : Compute) (nodes : Chain)
    (h : valid depth nodes) (budget : Nat) (enough : depth ≤ budget) :
    ready depth root compute (waves depth root compute budget nodes) := by
  intro i within
  refine ⟨?_, rank_bound depth root compute nodes h i budget within (by omega)⟩
  cases budget with
  | zero => omega
  | succ budget =>
    exact wave_locally_ready _ _ _ _ i within (waves_valid _ _ _ _ budget h)

def zeroNodes : Chain := fun _ => EndpointApplication.initial 0
def double (_ : Nat) (parent : Nat) : Nat := 2 * parent

theorem zero_nodes_valid (depth : Nat) : valid depth zeroNodes := by
  intro i _
  exact EndpointApplication.initial_valid 0

theorem beyond_frontier_zero (depth budget i : Nat) (within : i < depth)
    (beyond : budget ≤ i) :
    (waves depth 1 double budget zeroNodes i).installed.value = 0 := by
  induction budget generalizing i with
  | zero => rfl
  | succ budget ih =>
    rw [waves, wave_uses_previous_parent _ _ _ _ _ within
      (waves_valid _ _ _ _ budget (zero_nodes_valid depth))]
    cases i with
    | zero => omega
    | succ i =>
      simp only [parentValue, double]
      rw [ih i (by omega) (by omega)]

theorem double_expected_positive (i : Nat) : 0 < expected 1 double i := by
  induction i with
  | zero => decide +kernel
  | succ i ih =>
    exact Nat.mul_pos (by decide) ih

theorem no_depth_independent_budget (budget : Nat) :
    ¬ready (budget + 1) 1 double (waves (budget + 1) 1 double budget zeroNodes) := by
  intro done
  have leaf := (done budget (by omega)).2
  have zero := beyond_frontier_zero (budget + 1) budget budget (by omega) (by omega)
  have positive := double_expected_positive budget
  omega

theorem local_application_is_not_chain_readiness :
    EndpointApplication.ready (waves 3 1 double 2 zeroNodes 2) ∧
    (waves 3 1 double 2 zeroNodes 2).installed.value = 0 ∧
    expected 1 double 2 = 8 := by
  decide +kernel

theorem finite_depth_control :
    (waves 3 1 double 3 zeroNodes 2).installed.value = 8 ∧
    (waves 4 32 double 4 zeroNodes 3).installed.value = 512 := by
  decide +kernel

end EndpointWaves
