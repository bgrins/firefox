import Count
namespace LiveCount
variable {K V : Type} [DecidableEq K]

def keysOf (c : Chain K V) : List K := c.flatten.map Prod.fst

def dedup : List K → List K
  | [] => []
  | k :: ks => if k ∈ dedup ks then dedup ks else k :: dedup ks

theorem dedup_mem (ks : List K) (k : K) : k ∈ dedup ks ↔ k ∈ ks := by
  induction ks generalizing k with
  | nil => simp [dedup]
  | cons a rest ih =>
    simp only [dedup]
    split
    · have ha := (ih a).mp ‹a ∈ dedup rest›
      simp_all
    · simp_all

theorem dedup_unique (ks : List K) : (dedup ks).Nodup := by
  induction ks with
  | nil => simp [dedup]
  | cons k rest ih => simp only [dedup]; split <;> simp_all

def covers (ks : List K) (c : Chain K V) : Prop := ∀ k ∈ keysOf c, k ∈ ks

theorem finite_roster (c : Chain K V) (future : List K) :
    (dedup (keysOf c ++ future)).Nodup ∧
    covers (dedup (keysOf c ++ future)) c ∧
    (∀ k ∈ future, k ∈ dedup (keysOf c ++ future)) := by
  refine ⟨dedup_unique _, ?_, ?_⟩
  · intro k hk; apply (dedup_mem _ _).mpr; simp [hk]
  · intro k hk; apply (dedup_mem _ _).mpr; simp [hk]

theorem own_find_key (n : Node K V) (k : K) (v : Option V)
    (h : ownFind n k = some v) : k ∈ n.map Prod.fst := by
  induction n with
  | nil => simp [ownFind] at h
  | cons e rest ih =>
    rcases e with ⟨key, value⟩
    by_cases eq : key = k
    · subst key; simp
    · simp only [ownFind, eq, ↓reduceIte] at h
      exact List.mem_cons_of_mem key (ih h)

theorem lookup_key (c : Chain K V) (k : K) (v : V)
    (h : lookup c k = some v) : k ∈ keysOf c := by
  induction c with
  | nil => simp [lookup] at h
  | cons n ps ih =>
    cases own : ownFind n k with
    | none =>
      simp only [lookup, own] at h
      have hp := ih h
      simpa [keysOf] using (List.mem_append_right (n.map Prod.fst) hp)
    | some value =>
      have hn := own_find_key n k value own
      simp [keysOf, hn]

theorem projection_member (ks : List K) (c : Chain K V) (k : K) (v : V)
    (cover : covers ks c) : (k, v) ∈ projection ks c ↔ lookup c k = some v := by
  constructor
  · intro h
    rcases List.mem_filterMap.mp h with ⟨q, hq, he⟩
    cases hv : lookup c q with
    | none => simp [hv] at he
    | some w => simp [hv] at he; rcases he with ⟨rfl, rfl⟩; exact hv
  · intro h
    apply List.mem_filterMap.mpr
    exact ⟨k, cover k (lookup_key c k v h), by simp [h]⟩

theorem projection_keys (ks : List K) (c : Chain K V) :
    (projection ks c).map Prod.fst = ks.filter (fun k => (lookup c k).isSome) := by
  induction ks with
  | nil => rfl
  | cons k rest ih => cases h : lookup c k <;> simp_all [projection]

theorem projection_unique (ks : List K) (c : Chain K V) (unique : ks.Nodup) :
    ((projection ks c).map Prod.fst).Nodup := by
  rw [projection_keys]
  exact List.Sublist.nodup (List.filter_sublist) unique

theorem insert_keys (n : Node K V) (k q : K) (v : Option V) :
    q ∈ (ownInsert n k v).map Prod.fst ↔ q = k ∨ q ∈ n.map Prod.fst := by
  induction n with
  | nil => simp [ownInsert]
  | cons e rest ih =>
    rcases e with ⟨key, value⟩
    by_cases h : key = k
    · subst key; simp [ownInsert]
    · simp only [ownInsert, h, ↓reduceIte, List.map_cons, List.mem_cons, ih]
      simp [or_left_comm]

theorem insert_valid_node (n : Node K V) (k : K) (v : Option V)
    (unique : nodeUnique n) : nodeUnique (ownInsert n k v) := by
  induction n with
  | nil => simp [nodeUnique, ownInsert]
  | cons e rest ih =>
    rcases e with ⟨key, value⟩
    have h := List.nodup_cons.mp unique
    by_cases eq : key = k
    · subst key; simpa [nodeUnique, ownInsert] using unique
    · simp only [ownInsert, eq, ↓reduceIte, nodeUnique, List.map_cons, List.nodup_cons]
      refine ⟨?_, ih h.2⟩
      rw [insert_keys]
      simp [eq, h.1]

theorem insert_valid (c : Chain K V) (k : K) (v : Option V) (h : valid c) :
    valid (insert c k v) := by
  cases c with
  | nil => simp [insert, valid, nodeUnique]
  | cons n ps =>
    intro x hx
    simp only [insert, List.mem_cons] at hx
    rcases hx with rfl | hp
    · exact insert_valid_node _ _ _ (h n (by simp))
    · exact h x (by simp [hp])

theorem insert_cover (ks : List K) (c : Chain K V) (k : K) (v : Option V)
    (h : covers ks c) (hk : k ∈ ks) : covers ks (insert c k v) := by
  intro q hq
  cases c with
  | nil =>
    have eq : q = k := by simpa [keysOf, insert] using hq
    simpa [eq] using hk
  | cons n ps =>
    simp only [insert, keysOf, List.flatten_cons, List.map_append, List.mem_append] at hq
    rcases hq with hn | hp
    · rw [insert_keys] at hn
      rcases hn with rfl | hn
      · exact hk
      · exact h q (by simp [keysOf, hn])
    · apply h q
      change q ∈ (n ++ ps.flatten).map Prod.fst
      rw [List.map_append]
      exact List.mem_append_right _ hp

end LiveCount
