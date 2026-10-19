import Model
namespace EndpointTaint

theorem pairs_length (cmp : A → B → Bool) (as : List A) (bs : List B)
    (h : pairs cmp as bs = true) : as.length = bs.length := by
  induction as generalizing bs with
  | nil => cases bs <;> simp_all [pairs]
  | cons a as ih =>
    cases bs with
    | nil => simp [pairs] at h
    | cons b bs =>
      simp only [pairs, Bool.and_eq_true] at h
      simp [ih bs h.2]

theorem pairs_index (cmp : A → B → Bool) (as : List A) (bs : List B)
    (h : pairs cmp as bs = true) (i : Nat) (bound : i < bs.length) :
    ∃ a b, as[i]? = some a ∧ bs[i]? = some b ∧ cmp a b = true := by
  induction as generalizing bs i with
  | nil => cases bs <;> simp_all [pairs]
  | cons a as ih =>
    cases bs with
    | nil => simp at bound
    | cons b bs =>
      simp only [pairs, Bool.and_eq_true] at h
      cases i with
      | zero => exact ⟨a,b,rfl,rfl,h.1⟩
      | succ i =>
        obtain ⟨x,y,hx,hy,hxy⟩ := ih bs h.2 i (by simpa using bound)
        exact ⟨x,y,hx,hy,hxy⟩

theorem property_ready (key : K → K → Bool) (payload : P → P → Bool)
    (core : C → C → Bool) (a b : Property K P C)
    (h : propertySame key payload core a b = true) :
    a.custom = b.custom ∧ pairs (segmentSame payload core) a.segments b.segments = true ∧
      a.segments.length = b.segments.length := by
  simp only [propertySame, Bool.and_eq_true, beq_iff_eq] at h
  exact ⟨h.1.2,h.2,pairs_length _ _ _ h.2⟩

theorem array_ready (key : K → K → Bool) (payload : P → P → Bool)
    (core : C → C → Bool) (as bs : List (Property K P C))
    (h : ordinarySame key payload core as bs = true) : as.length = bs.length :=
  pairs_length _ _ _ h

theorem indexed_reads_ready (key : K → K → Bool) (payload : P → P → Bool)
    (core : C → C → Bool) (as bs : List (Property K P C))
    (h : ordinarySame key payload core as bs = true) (i : Nat) (bound : i < bs.length) :
    ∃ a b, as[i]? = some a ∧ bs[i]? = some b ∧ a.custom = b.custom ∧
      ∀ j, j < b.segments.length → ∃ x y,
        a.segments[j]? = some x ∧ b.segments[j]? = some y ∧ segmentSame payload core x y = true := by
  obtain ⟨a,b,ha,hb,he⟩ := pairs_index _ as bs h i bound
  have ready := property_ready key payload core a b he
  exact ⟨a,b,ha,hb,ready.1,fun j hj => pairs_index _ _ _ ready.2.1 j hj⟩

theorem endpoint_presence (cmp : P → P → Bool) (a b : Endpoint P)
    (h : endpointSame cmp a b = true) :
    a.isSome = b.isSome ∧ a.join.isSome = b.join.isSome := by
  cases a with
  | none => cases b <;> simp_all [endpointSame]
  | some a =>
    cases b with
    | none => simp [endpointSame] at h
    | some b => cases a <;> cases b <;> simp_all [endpointSame,TaintShortcut.payloadSame]
theorem counter_headroom (index length maximum : Nat)
    (beforeEnd : index < length) (representable : length ≤ maximum) : index + 1 ≤ maximum := by
  omega
end EndpointTaint
