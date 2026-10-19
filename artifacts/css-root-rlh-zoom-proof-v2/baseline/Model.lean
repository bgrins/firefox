import Std
namespace Rlh
structure DocumentId where
  value : Nat
  deriving DecidableEq, Repr
structure ElementId where
  value : Nat
  deriving DecidableEq, Repr
structure StyleVersion where
  value : Nat
  deriving DecidableEq, Repr
instance (n : Nat) : OfNat DocumentId n := ⟨⟨n⟩⟩
instance (n : Nat) : OfNat ElementId n := ⟨⟨n⟩⟩
instance (n : Nat) : OfNat StyleVersion n := ⟨⟨n⟩⟩
structure Owner where
  document : DocumentId
  element : ElementId
  epoch : StyleVersion
  deriving DecidableEq, Repr
structure Zoom (owner : Owner) where
  value : Rat
  positive : 0 < value
  nonzero : value ≠ 0
structure Scaled (owner : Owner) where
  value : Rat
  deriving DecidableEq, Repr
structure Unscaled (owner : Owner) where
  value : Rat
  deriving DecidableEq, Repr
structure Coefficient where
  value : Rat
  deriving DecidableEq, Repr
structure AppUnits (owner : Owner) where
  value : Int
  deriving DecidableEq, Repr

def scale {o} (z : Zoom o) (x : Unscaled o) : Scaled o := ⟨x.value * z.value⟩
def expose {o} (z : Zoom o) (x : Scaled o) : Unscaled o := ⟨x.value / z.value⟩
def multiply {o} (c : Coefficient) (x : Scaled o) : Scaled o := ⟨x.value * c.value⟩

theorem expose_scale {o} (z : Zoom o) (x : Unscaled o) : expose z (scale z x) = x := by
  cases x
  simp [expose, scale, Rat.mul_div_cancel z.nonzero]
theorem scale_expose {o} (z : Zoom o) (x : Scaled o) : scale z (expose z x) = x := by
  cases x
  simp [expose, scale, Rat.div_mul_cancel z.nonzero]
theorem scale_owner {o} (z : Zoom o) (x : Unscaled o) : (scale z x).value = x.value * z.value := rfl

structure MetricEnvironment where
  context : Nat
  writingMode : Nat
  fontEpoch : Nat
  deriving DecidableEq, Repr

inductive Form where
  | absolute (length : Rat)
  | numeric (factor : Rat)
  | percentageComputed (percent : Rat)
  | normal (metric : Rat) (environment : MetricEnvironment)
  deriving DecidableEq, Repr

def semanticLine (font : Rat) : Form → Rat
  | .absolute length => length
  | .numeric factor => font * factor
  | .percentageComputed percent => font * percent
  | .normal metric _ => metric

structure Provider (owner : Owner) where
  font : Rat
  form : Form
  stored : Scaled owner
  deriving DecidableEq, Repr

def Provider.Valid {o} (p : Provider o) (z : Zoom o) : Prop :=
  p.stored.value = semanticLine p.font p.form * z.value

instance {o} (p : Provider o) (z : Zoom o) : Decidable (p.Valid z) := inferInstanceAs (Decidable (p.stored.value = semanticLine p.font p.form * z.value))

inductive Base where | current | inherited deriving DecidableEq, Repr
inductive Role where | root | media | descendant deriving DecidableEq, Repr
inductive Source where
  | current (owner : Owner)
  | inherited (owner : Owner)
  | initial (owner : Owner)
  | cache (owner : Owner)
  deriving DecidableEq, Repr
structure Observation where
  source : Source
  scaled : Rat
  exposed : Rat
  coefficient : Rat
  cacheUsed : Bool
  deriving DecidableEq, Repr
structure World where
  consumer : Owner
  parent : Owner
  root : Owner
  initial : Owner
  consumerZoom : Zoom consumer
  parentZoom : Zoom parent
  inheritanceZoom : Rat
  current : Provider consumer
  inherited : Provider parent
  initialFont : Rat
  initialForm : Form
  initialStored : Unscaled initial
  rootSemantic : Rat
  cache : Unscaled root
  role : Role
  base : Base
  coefficient : Coefficient

structure Valid (w : World) : Prop where
  current : w.current.Valid w.consumerZoom
  inherited : w.inherited.Valid w.parentZoom
  transport : w.parentZoom.value * w.inheritanceZoom = w.consumerZoom.value
  initial : w.initialStored.value = semanticLine w.initialFont w.initialForm
  cache : w.cache.value = w.rootSemantic
  rootOwner : w.role = .root → w.consumer = w.root
  sameDocument : w.consumer.document = w.root.document
  parentDocument : w.parent.document = w.consumer.document
  initialDocument : w.initial.document = w.consumer.document

-- This algorithm reads semantic records, not the implementation's stored lengths.
def reference (w : World) : Observation :=
  let (source, value, used) := match w.role with
    | .root => match w.base with
      | .current => (.current w.consumer, semanticLine w.current.font w.current.form, false)
      | .inherited => (.inherited w.parent, semanticLine w.inherited.font w.inherited.form, false)
    | .media => (.initial w.initial, semanticLine w.initialFont w.initialForm, false)
    | .descendant => (.cache w.root, w.rootSemantic, true)
  let scaled := (value * w.consumerZoom.value) * w.coefficient.value
  { source, scaled, exposed := scaled / w.consumerZoom.value,
    coefficient := w.coefficient.value, cacheUsed := used }

def builderValue (w : World) : Source × Rat :=
  if w.base = .current then (.current w.consumer, w.current.stored.value)
  else (.inherited w.parent, w.inherited.stored.value * w.inheritanceZoom)

def implementation (w : World) : Observation :=
  let (source, value, used) :=
    if w.role = .root then
      let v := builderValue w
      (v.1, v.2, false)
    else if w.role = .media then
      (.initial w.initial, w.initialStored.value * w.consumerZoom.value, false)
    else (.cache w.root, w.cache.value * w.consumerZoom.value, true)
  let scaled := value * w.coefficient.value
  { source, scaled, exposed := scaled / w.consumerZoom.value,
    coefficient := w.coefficient.value, cacheUsed := used }

theorem inherited_transport (w : World) (h : Valid w) :
    w.inherited.stored.value * w.inheritanceZoom =
      semanticLine w.inherited.font w.inherited.form * w.consumerZoom.value := by
  rw [h.inherited, Rat.mul_assoc, h.transport]

theorem candidate_refines_reference (w : World) (h : Valid w) :
    implementation w = reference w := by
  have hc := h.current
  have hi := inherited_transport w h
  have hm := h.initial
  have hr := h.cache
  unfold Provider.Valid at hc
  cases he : w.role <;> cases hb : w.base <;>
    simp [implementation, reference, builderValue, he, hb, hc, hi, hm, hr]

def original (w : World) : Observation :=
  if w.role = .root then
    let b := builderValue w
    let scaled := (b.2 * w.consumerZoom.value) * w.coefficient.value
    { source := b.1, scaled, exposed := scaled / w.consumerZoom.value,
      coefficient := w.coefficient.value, cacheUsed := false }
  else implementation w

theorem nonroot_preservation (w : World) (h : w.role ≠ .root) :
    original w = implementation w := by simp [original, h]

def localLh (w : World) : Observation :=
  let b := builderValue w
  let scaled := b.2 * w.coefficient.value
  { source := b.1, scaled, exposed := scaled / w.consumerZoom.value,
    coefficient := w.coefficient.value, cacheUsed := false }

theorem root_lh_rlh (w : World) (h : w.role = .root) :
    implementation w = localLh w := by simp [implementation, localLh, h]
theorem root_no_cache (w : World) (h : w.role = .root) :
    (implementation w).cacheUsed = false := by simp [implementation, h]
theorem media_no_cache (w : World) (h : w.role = .media) :
    (implementation w).cacheUsed = false := by simp [implementation, h]
theorem descendant_marks_cache (w : World) (h : w.role = .descendant) :
    (implementation w).cacheUsed = true := by simp [implementation, h]
theorem current_source (w : World) (hr : w.role = .root) (hb : w.base = .current) :
    (implementation w).source = .current w.consumer := by simp [implementation, builderValue, hr, hb]
theorem inherited_source (w : World) (hr : w.role = .root) (hb : w.base = .inherited) :
    (implementation w).source = .inherited w.parent := by simp [implementation, builderValue, hr, hb]
theorem media_source (w : World) (hr : w.role = .media) :
    (implementation w).source = .initial w.initial := by simp [implementation, hr]
theorem descendant_source (w : World) (hr : w.role = .descendant) :
    (implementation w).source = .cache w.root := by simp [implementation, hr]

theorem coefficient_exposure (v c : Rat) {o} (z : Zoom o) :
    (v * z.value * c) / z.value = v * c := by
  have h : v * z.value * c = (v * c) * z.value := by
    rw [Rat.mul_assoc, Rat.mul_comm z.value c, ← Rat.mul_assoc]
  rw [h, Rat.mul_div_cancel z.nonzero]

theorem ordinary_exposed (w : World) (h : Valid w) :
    (implementation w).exposed =
      (match w.role with
       | .root => match w.base with
         | .current => semanticLine w.current.font w.current.form
         | .inherited => semanticLine w.inherited.font w.inherited.form
       | .media => semanticLine w.initialFont w.initialForm
       | .descendant => w.rootSemantic) * w.coefficient.value := by
  rw [candidate_refines_reference w h]
  cases hr : w.role <;> cases hb : w.base <;>
    simp [reference, hr, hb, coefficient_exposure]

def validBool (w : World) : Bool :=
  decide (w.current.Valid w.consumerZoom) && decide (w.inherited.Valid w.parentZoom) &&
  decide (w.parentZoom.value * w.inheritanceZoom = w.consumerZoom.value) &&
  decide (w.initialStored.value = semanticLine w.initialFont w.initialForm) &&
  decide (w.cache.value = w.rootSemantic) &&
  decide (w.role ≠ .root ∨ w.consumer = w.root) &&
  decide (w.consumer.document = w.root.document) &&
  decide (w.parent.document = w.consumer.document) &&
  decide (w.initial.document = w.consumer.document)

theorem validBool_sound (w : World) (h : validBool w = true) : Valid w := by
  simp only [validBool, Bool.and_eq_true, decide_eq_true_eq] at h
  rcases h with ⟨⟨⟨⟨⟨⟨⟨⟨a,b⟩,c⟩,d⟩,e⟩,f⟩,g⟩,i⟩,j⟩
  exact ⟨a,b,c,d,e,fun hr => f.resolve_left (not_not_intro hr),g,i,j⟩
theorem validBool_complete (w : World) (h : Valid w) : validBool w = true := by
  simp only [validBool, Bool.and_eq_true, decide_eq_true_eq]
  exact ⟨⟨⟨⟨⟨⟨⟨⟨h.current,h.inherited⟩,h.transport⟩,h.initial⟩,h.cache⟩,
    by by_cases hr : w.role = .root; exact Or.inr (h.rootOwner hr); exact Or.inl hr⟩,
    h.sameDocument⟩,h.parentDocument⟩,h.initialDocument⟩
theorem invalid_owner_rejected (w : World) (h : w.consumer.document ≠ w.root.document) :
    validBool w = false := by
  cases he : validBool w
  · rfl
  · exact False.elim (h (validBool_sound w he).sameDocument)
theorem invalid_role_rejected (w : World) (hr : w.role = .root)
    (ho : w.consumer ≠ w.root) : validBool w = false := by
  cases he : validBool w
  · rfl
  · exact False.elim (ho ((validBool_sound w he).rootOwner hr))
theorem coefficient_linearity (w : World) (a b : Rat) :
    (implementation {w with coefficient := ⟨a+b⟩}).scaled =
      (implementation {w with coefficient := ⟨a⟩}).scaled +
      (implementation {w with coefficient := ⟨b⟩}).scaled := by
  cases hr : w.role <;> cases hb : w.base <;> simp [implementation,builderValue,hr,hb,Rat.mul_add]
end Rlh
