namespace AnimationIdentity
structure Value (ι ν : Type) where
  id : ι
  payload : ν
  deriving Repr, DecidableEq
inductive Composite where
  | replace | add | accumulate
  deriving Repr, DecidableEq
inductive Procedure where
  | add | accumulate (count : Nat) | interpolate (progressBits : Nat)
  deriving Repr, DecidableEq
variable {ι ν : Type}
local notation "V" => Value ι ν
abbrev Arithmetic (ι ν : Type) := Procedure → Value ι ν → Value ι ν → Option (Value ι ν)
def OptId (key : ι) (o : Option V) : Prop := ∀ v, o = some v → v.id = key
def Ready (key : ι) (o : Option V) : Prop := ∃ v, o = some v ∧ v.id = key
def Preserves (arith : Arithmetic ι ν) : Prop :=
  ∀ proc a b out, a.id = b.id → arith proc a b = some out → out.id = a.id

def composite (arith : Arithmetic ι ν) (endpoint : Option V) (mode : Composite)
    (underlying : Option V) : Option (Option V) :=
  match endpoint with
  | none => some underlying
  | some e => match mode with
    | .add => underlying.map (fun u => arith .add u e)
    | .accumulate => underlying.map (fun u => arith (.accumulate 1) u e)
    | _ => some none

def accumulate (arith : Arithmetic ι ν) (endpoint composited : Option V)
    (last : V) (count : Nat) : Option (Option V) :=
  match composited with
  | some c => some ((arith (.accumulate count) last c).or (some c))
  | none => endpoint.map (fun e => arith (.accumulate count) last e)

def EndpointReady (endpoint : Option V) (mode : Composite) (u : Option V) : Prop :=
  (endpoint = none ∨ mode ≠ .replace) → u.isSome = true

variable {key : ι} {arith : Arithmetic ι ν} {a b last : V} {endpoint c u : Option V}

theorem ready_opt (h : Ready key (o : Option V)) : OptId key o := by
  obtain ⟨v,rfl,hv⟩ := h
  intro x hx
  cases hx
  exact hv

theorem ready_some (h : Ready key (o : Option V)) : o.isSome = true := by
  obtain ⟨v,rfl,_⟩ := h
  rfl

theorem opt_none (key : ι) : OptId key (none : Option V) := by
  intro v h; cases h

theorem opt_or (a b : Option V) (ha : OptId key a) (hb : OptId key b) :
    OptId key (a.or b) := by
  cases a <;> simp_all [OptId]

theorem ready_or (a b : Option V) (ha : OptId key a) (hb : Ready key b) :
    Ready key (a.or b) := by
  cases a with
  | none => exact hb
  | some v => exact ⟨v,rfl,ha v rfl⟩

theorem arithmetic_id {a b : Value ι ν} {proc : Procedure} (hp : Preserves arith) (ha : a.id = key) (hb : b.id = key) :
    OptId key (arith proc a b) := by
  intro v hv
  exact (hp proc a b v (ha.trans hb.symm) hv).trans ha

theorem composite_ready {endpoint u : Option (Value ι ν)} {mode : Composite} (hp : Preserves arith) (he : OptId key endpoint)
    (hu : OptId key u) (hr : EndpointReady endpoint mode u) :
    ∃ c, composite arith endpoint mode u = some c ∧ OptId key c ∧ Ready key (c.or endpoint) := by
  cases endpoint with
  | none =>
    have hs := hr (Or.inl rfl)
    cases u with
    | none => cases hs
    | some v => exact ⟨some v,rfl,hu,v,rfl,hu v rfl⟩
  | some e =>
    have hei := he e rfl
    cases mode with
    | replace => exact ⟨none,rfl,opt_none key,e,rfl,hei⟩
    | add =>
      have hs := hr (Or.inr (by decide))
      cases u with
      | none => cases hs
      | some v =>
        have hc := arithmetic_id hp (hu v rfl) hei (proc := .add)
        exact ⟨arith .add v e,rfl,hc,ready_or _ _ hc ⟨e,rfl,hei⟩⟩
    | accumulate =>
      have hs := hr (Or.inr (by decide))
      cases u with
      | none => cases hs
      | some v =>
        have hc := arithmetic_id hp (hu v rfl) hei (proc := .accumulate 1)
        exact ⟨arith (.accumulate 1) v e,rfl,hc,ready_or _ _ hc ⟨e,rfl,hei⟩⟩

theorem accumulate_ready {endpoint c : Option (Value ι ν)} {last : Value ι ν} {count : Nat} (hp : Preserves arith) (he : OptId key endpoint)
    (hc : OptId key c) (hr : Ready key (c.or endpoint)) (hl : last.id = key) :
    ∃ next, accumulate arith endpoint c last count = some next ∧
      OptId key next ∧ Ready key (next.or endpoint) := by
  cases c with
  | some v =>
    have hi := arithmetic_id hp hl (hc v rfl) (proc := .accumulate count)
    have ready := ready_or _ _ hi ⟨v,rfl,hc v rfl⟩
    exact ⟨_,rfl,ready_opt ready,(by
      obtain ⟨v,hv,hid⟩ := ready
      exact ⟨v,by rw [hv];rfl,hid⟩)⟩
  | none =>
    obtain ⟨e,heq,hei⟩ := hr
    change endpoint = some e at heq
    subst endpoint
    have hi := arithmetic_id hp hl hei (proc := .accumulate count)
    exact ⟨_,rfl,hi,ready_or _ _ hi ⟨e,rfl,hei⟩⟩
end AnimationIdentity
