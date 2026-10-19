import Domain
namespace LiveCount
variable {K V : Type} [DecidableEq K]

structure Store (K V : Type) where
  chain : Chain K V
  stored : Nat

def Ready (ks : List K) (s : Store K V) : Prop :=
  s.stored = count ks s.chain ∧ covers ks s.chain ∧ valid s.chain

def nativeInsert (s : Store K V) (k : K) (v : Option V) : Store K V :=
  ⟨insert s.chain k v, updateCount s.stored (lookup s.chain k).isSome v.isSome⟩

def shouldExpand (c : Chain K V) : Bool :=
  decide (8 < (c.headD []).length ∧ c.length - 1 < 4)

def doInsert (unique : Bool) (compare : Option V → Option V → Bool)
    (s : Store K V) (k : K) (v : Option V) : Store K V :=
  if unique then nativeInsert s k v
  else if compare (lookup s.chain k) v then s
  else if shouldExpand s.chain then nativeInsert ⟨[] :: s.chain, s.stored⟩ k v
  else nativeInsert s k v

def CompareSound (compare : Option V → Option V → Bool) : Prop :=
  ∀ a b, compare a b = true → a = b

theorem native_insert_ready (ks : List K) (s : Store K V) (k : K) (v : Option V)
    (unique : ks.Nodup) (hk : k ∈ ks) (ready : Ready ks s) :
    Ready ks (nativeInsert s k v) := by
  refine ⟨?_, insert_cover _ _ _ _ ready.2.1 hk, insert_valid _ _ _ ready.2.2⟩
  simp only [nativeInsert]
  rw [ready.1, count_transition ks s.chain k v unique hk]

theorem expanded_ready (ks : List K) (s : Store K V) (h : Ready ks s) :
    Ready ks ⟨[] :: s.chain, s.stored⟩ := by
  refine ⟨h.1, ?_, ?_⟩
  · simpa [covers, keysOf] using h.2.1
  · intro n hn
    rcases List.mem_cons.mp hn with rfl | hp
    · simp [nodeUnique]
    · exact h.2.2 n hp

theorem cow_ready (ks : List K) (s : Store K V) (k : K) (v : Option V)
    (isUnique : Bool) (compare : Option V → Option V → Bool)
    (unique : ks.Nodup) (hk : k ∈ ks) (ready : Ready ks s) :
    Ready ks (doInsert isUnique compare s k v) := by
  unfold doInsert
  split
  · exact native_insert_ready _ _ _ _ unique hk ready
  · split
    · exact ready
    · split
      · exact native_insert_ready _ _ _ _ unique hk (expanded_ready _ _ ready)
      · exact native_insert_ready _ _ _ _ unique hk ready

theorem cow_lookup (s : Store K V) (k q : K) (v : Option V)
    (isUnique : Bool) (compare : Option V → Option V → Bool) (sound : CompareSound compare) :
    lookup (doInsert isUnique compare s k v).chain q =
      if q = k then v else lookup s.chain q := by
  unfold doInsert
  split
  · exact lookup_insert _ _ _ _
  · split
    · have eq := sound _ _ ‹compare (lookup s.chain k) v = true›
      by_cases hq : q = k <;> simp_all
    · split
      · simpa [nativeInsert, expand_lookup] using lookup_insert ([] :: s.chain) k q v
      · exact lookup_insert _ _ _ _

structure Op (K V : Type) where
  key : K
  value : Option V
  unique : Bool

def run (compare : Option V → Option V → Bool) (s : Store K V) : List (Op K V) → Store K V
  | [] => s
  | op :: rest => run compare (doInsert op.unique compare s op.key op.value) rest

theorem history_ready (ks : List K) (ops : List (Op K V))
    (compare : Option V → Option V → Bool) (s : Store K V)
    (unique : ks.Nodup) (keys : ∀ op ∈ ops, op.key ∈ ks) (ready : Ready ks s) :
    Ready ks (run compare s ops) := by
  induction ops generalizing s with
  | nil => exact ready
  | cons op rest ih =>
    exact ih _ (fun x hx => keys x (by simp [hx]))
      (cow_ready _ _ _ _ _ _ unique (keys op (by simp)) ready)

def initial : Store K V := ⟨[[]], 0⟩

theorem initial_ready (ks : List K) : Ready ks (initial : Store K V) := by
  refine ⟨(empty_initialization ks).symm, ?_, ?_⟩
  · simp [covers, keysOf, initial]
  · simp [valid, nodeUnique, initial]

theorem finite_history (ops : List (Op K V)) (compare : Option V → Option V → Bool) :
    let ks := dedup (ops.map Op.key)
    Ready ks (run compare initial ops) := by
  apply history_ready
  · exact dedup_unique _
  · intro op hop; apply (dedup_mem _ _).mpr; exact List.mem_map.mpr ⟨op, hop, rfl⟩
  · exact initial_ready _

theorem usize_decrement_defined (ks : List K) (s : Store K V) (k : K)
    (ready : Ready ks s) (hk : k ∈ ks) (old : (lookup s.chain k).isSome = true) :
    0 < s.stored := by
  rw [ready.1]; exact decrement_headroom _ _ _ hk old

theorem usize_increment_bound (n max : Nat) (headroom : n < max) : n + 1 ≤ max := by omega

omit [DecidableEq K] in
theorem expansion_depth_bound (c : Chain K V) (h : shouldExpand c = true) :
    c.length - 1 + 1 ≤ 4 := by
  simp only [shouldExpand, decide_eq_true_eq] at h
  omega

theorem increment_headroom (ks : List K) (s : Store K V) (k : K) (max : Nat)
    (ready : Ready ks s) (hk : k ∈ ks) (old : (lookup s.chain k).isSome = false)
    (domainBound : ks.length ≤ max) : s.stored + 1 ≤ max := by
  have h := tally_missing ks k (fun q => (lookup s.chain q).isSome) hk old
  rw [ready.1]
  change tally ks (fun q => (lookup s.chain q).isSome) + 1 ≤ max
  omega

def referenceRun (f : K → Option V) : List (Op K V) → K → Option V
  | [], q => f q
  | op :: rest, q => referenceRun (fun k => if k = op.key then op.value else f k) rest q

theorem history_lookup (ops : List (Op K V)) (s : Store K V)
    (compare : Option V → Option V → Bool) (sound : CompareSound compare) (q : K) :
    lookup (run compare s ops).chain q = referenceRun (lookup s.chain) ops q := by
  induction ops generalizing s with
  | nil => rfl
  | cons op rest ih =>
    simp only [run, referenceRun]
    rw [ih]
    have functions : lookup (doInsert op.unique compare s op.key op.value).chain =
        (fun k => if k = op.key then op.value else lookup s.chain k) := by
      funext k; exact cow_lookup _ _ _ _ _ _ sound
    rw [functions]

end LiveCount
