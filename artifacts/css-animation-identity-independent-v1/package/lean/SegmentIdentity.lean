import AnimationIdentity
namespace SegmentIdentity
open AnimationIdentity
variable {ι ν : Type}
structure Segment (ι ν : Type) where
  fromValue : Option (Value ι ν)
  toValue : Option (Value ι ν)
  fromMode : Composite
  toMode : Composite
  equalKeys : Bool
  negativeTotal : Bool
  beforeHalf : Bool
  progressBits : Nat
  deriving Repr, DecidableEq

def active (iterationAccumulate : Bool) (count : Nat) : Bool := iterationAccumulate && decide (count > 0)
def need (s : Segment ι ν) (last : Option (Value ι ν)) (iter : Bool) (count : Nat) : Bool :=
  s.fromValue.isNone || s.toValue.isNone || decide (s.fromMode ≠ .replace) ||
  decide (s.toMode ≠ .replace) || (active iter count && last.isNone)

def selected (arith : Arithmetic ι ν) (endpoint composited : Option (Value ι ν))
    (last : Option (Value ι ν)) (iter : Bool) (count : Nat) : Option (Value ι ν) := do
  let c ← if active iter count then do
    let l ← last
    accumulate arith endpoint composited l count
  else some composited
  c.or endpoint

def finish (arith : Arithmetic ι ν) (s : Segment ι ν) (first to : Value ι ν) : Value ι ν :=
  if s.equalKeys then
    if s.negativeTotal then first else to
  else (arith (.interpolate s.progressBits) first to).getD (if s.beforeHalf then first else to)

def compose (arith : Arithmetic ι ν) (s : Segment ι ν) (underlying last : Option (Value ι ν))
    (iter : Bool) (count : Nat) : Option (Value ι ν) := do
  let cf ← composite arith s.fromValue s.fromMode underlying
  let ct ← composite arith s.toValue s.toMode underlying
  let first ← selected arith s.fromValue cf (last.or underlying) iter count
  let to ← selected arith s.toValue ct (last.or underlying) iter count
  some (finish arith s first to)

def SegmentId (key : ι) (s : Segment ι ν) : Prop := OptId key s.fromValue ∧ OptId key s.toValue

variable {key : ι} {arith : Arithmetic ι ν}
theorem guard_endpoints (s : Segment ι ν) (last u : Option (Value ι ν)) (iter : Bool) (count : Nat)
    (guard : need s last iter count = true → u.isSome = true) :
    EndpointReady s.fromValue s.fromMode u ∧ EndpointReady s.toValue s.toMode u := by
  constructor
  · intro h; apply guard
    rcases h with h | h <;> simp [need,h]
  · intro h; apply guard
    rcases h with h | h <;> simp [need,h]

theorem guard_last (s : Segment ι ν) (last u : Option (Value ι ν)) (iter : Bool) (count : Nat)
    (hl : OptId key last) (hu : OptId key u)
    (guard : need s last iter count = true → u.isSome = true) :
    active iter count = true → Ready key (last.or u) := by
  intro ha
  cases last with
  | some v => exact ⟨v,rfl,hl v rfl⟩
  | none =>
    have hs := guard (by simp [need,ha])
    cases u with
    | none => cases hs
    | some v => exact ⟨v,rfl,hu v rfl⟩

theorem selected_ready (endpoint c last : Option (Value ι ν)) (iter : Bool) (count : Nat)
    (hp : Preserves arith) (he : OptId key endpoint) (hc : OptId key c)
    (hr : Ready key (c.or endpoint)) (hl : active iter count = true → Ready key last) :
    Ready key (selected arith endpoint c last iter count) := by
  cases ha : active iter count with
  | false => simpa [selected,ha] using hr
  | true =>
    obtain ⟨l,heq,hid⟩ := hl ha
    obtain ⟨next,hn,_,hs⟩ := accumulate_ready hp he hc hr hid (count := count)
    simpa [selected,ha,heq,hn] using hs

theorem finish_id (s : Segment ι ν) (first to : Value ι ν) (hp : Preserves arith)
    (hf : first.id=key) (ht : to.id=key) : (finish arith s first to).id=key := by
  unfold finish
  split
  · split <;> assumption
  · have hi := arithmetic_id hp hf ht (proc := .interpolate s.progressBits)
    cases h : arith (.interpolate s.progressBits) first to with
    | none => simp only [Option.getD_none];split <;> assumption
    | some v => exact hi v h

theorem compose_ready (s : Segment ι ν) (u last : Option (Value ι ν)) (iter : Bool) (count : Nat)
    (hp : Preserves arith) (hs : SegmentId key s) (hu : OptId key u) (hl : OptId key last)
    (guard : need s last iter count = true → u.isSome = true) :
    Ready key (compose arith s u last iter count) := by
  obtain ⟨hfrom,hto⟩ := guard_endpoints s last u iter count guard
  obtain ⟨cf,hcf,icf,rcf⟩ := composite_ready hp hs.1 hu hfrom
  obtain ⟨ct,hct,ict,rct⟩ := composite_ready hp hs.2 hu hto
  have readyLast := guard_last s last u iter count hl hu guard
  obtain ⟨f,hf,ifrom⟩ := selected_ready s.fromValue cf (last.or u) iter count hp hs.1 icf rcf readyLast
  obtain ⟨t,ht,ito⟩ := selected_ready s.toValue ct (last.or u) iter count hp hs.2 ict rct readyLast
  exact ⟨finish arith s f t,by simp [compose,hcf,hct,hf,ht],finish_id s f t hp ifrom ito⟩
end SegmentIdentity
