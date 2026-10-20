import TypeObservation
namespace LiveAtoms
open OrderedTypes TypeMutations
variable {Atom Value : Type} [DecidableEq Atom] [DecidableEq Value]

structure State (Atom Value : Type) where
  native : List Atom
  backing : List Value
  deriving Repr, DecidableEq

def Good (text : Atom → Value) (s : State Atom Value) : Prop :=
  s.native.map text = s.backing ∧ s.backing.Nodup

def Canonical (text : Atom → Value) (native : List Atom) (value : Value) (atom : Atom) : Prop :=
  text atom = value ∧ ∀ b, b ∈ native → text b = value → b = atom

theorem canonical_member (text : Atom → Value) (s : State Atom Value)
    (value : Value) (atom : Atom) (good : Good text s)
    (canonical : Canonical text s.native value atom) : atom ∈ s.native ↔ value ∈ s.backing := by
  rw [← good.1]
  constructor
  · intro h; exact List.mem_map.mpr ⟨atom, h, canonical.1⟩
  · intro h
    obtain ⟨b, hb, he⟩ := List.mem_map.mp h
    simpa [canonical.2 b hb he] using hb

theorem erase_map_local (text : Atom → Value) (xs : List Atom) (atom : Atom)
    (canonical : ∀ b, b ∈ xs → text b = text atom → b = atom) :
    (xs.erase atom).map text = (xs.map text).erase (text atom) := by
  induction xs with
  | nil => rfl
  | cons b xs ih =>
    by_cases he : b = atom
    · subst b; simp
    · have hv : text b ≠ text atom := fun e => he (canonical b (by simp) e)
      have ht : ∀ c, c ∈ xs → text c = text atom → c = atom := by
        intro c hc; exact canonical c (by simp [hc])
      simp [List.erase_cons_tail, he, hv, ih ht]

inductive Op (Atom Value : Type) where
  | add (value : Value) (atom : Atom)
  | delete (value : Value) (atom : Atom)
  | clear
  | observe
  deriving Repr, DecidableEq

def valueOp : Op Atom Value → TypeMutations.Op Value
  | .add v _ => .add v
  | .delete v _ => .delete v
  | .clear => .clear
  | .observe => .observe

def admitted (text : Atom → Value) (s : State Atom Value) : Op Atom Value → Prop
  | .add v a => v ∉ s.backing → text a = v
  | .delete v a => v ∈ s.backing → Canonical text s.native v a
  | .clear => True
  | .observe => True

def operation (s : State Atom Value) : Op Atom Value → State Atom Value × Reply
  | .add v a => if v ∈ s.backing then (s, .self 7)
      else (⟨s.native ++ [a], s.backing ++ [v]⟩, .self 7)
  | .delete v a => if v ∈ s.backing then
      (⟨s.native.erase a, s.backing.filter (fun x => decide (x ≠ v))⟩, .deleted true)
      else (s, .deleted false)
  | .clear => (⟨[], []⟩, .undefined)
  | .observe => (s, .observed)

theorem operation_good (text : Atom → Value) (s : State Atom Value)
    (op : Op Atom Value) (good : Good text s) (provider : admitted text s op) :
    Good text (operation s op).1 := by
  cases op with
  | add v a =>
    simp only [operation]
    split
    · exact good
    · rename_i absent
      constructor
      · simp only [List.map_append, List.map_cons, List.map_nil, good.1, provider absent]
      · have hn := nodup_appendNew s.backing v good.2
        simpa [appendNew, absent] using hn
  | delete v a =>
    simp only [operation]
    split
    · rename_i present
      have hc := provider present
      constructor
      · rw [erase_map_local text s.native a (by intro b hb he; exact hc.2 b hb (he.trans hc.1)),
          good.1, hc.1, erase_matches_filter _ _ good.2]
      · exact good.2.filter _
    · exact good
  | clear => simp [operation, Good]
  | observe => exact good

theorem operation_reference (text : Atom → Value) (s : State Atom Value)
    (op : Op Atom Value) :
    ((operation s op).1.backing, (operation s op).2) = reference 7 s.backing (valueOp op) := by
  cases op <;> simp only [operation, valueOp, reference, appendNew] <;> (try split) <;> simp_all
  symm
  apply List.filter_eq_self.mpr
  intro a ha
  simp only [Bool.not_eq_true', decide_eq_false_iff_not]
  grind

def history (s : State Atom Value) : List (Op Atom Value) → State Atom Value × List Reply
  | [] => (s, [])
  | op :: ops =>
      let one := operation s op
      let rest := history one.1 ops
      (rest.1, one.2 :: rest.2)

def AdmittedHistory (text : Atom → Value) (s : State Atom Value) : List (Op Atom Value) → Prop
  | [] => True
  | op :: ops => admitted text s op ∧ AdmittedHistory text (operation s op).1 ops

theorem history_good (text : Atom → Value) (s : State Atom Value)
    (ops : List (Op Atom Value)) (good : Good text s) (provider : AdmittedHistory text s ops) :
    Good text (history s ops).1 := by
  induction ops generalizing s with
  | nil => exact good
  | cons op ops ih => exact ih _ (operation_good text s op good provider.1) provider.2

theorem history_reference (text : Atom → Value) (s : State Atom Value)
    (ops : List (Op Atom Value)) :
    ((history s ops).1.backing, (history s ops).2) =
      referenceHistory 7 s.backing (ops.map valueOp) := by
  induction ops generalizing s with
  | nil => rfl
  | cons op ops ih =>
    have one := operation_reference text s op
    have hp := congrArg Prod.fst one
    have hr := congrArg Prod.snd one
    simp only [history, List.map_cons, referenceHistory]
    simp only at hp hr
    have hh := ih (operation s op).1
    rw [hp] at hh
    have hhp := congrArg Prod.fst hh
    have hhr := congrArg Prod.snd hh
    simp only at hp hr hhp hhr
    rw [hhp, hhr, hr]

theorem live_history_observation (text : Atom → Value) (s : State Atom Value)
    (ops : List (Op Atom Value)) (good : Good text s) (provider : AdmittedHistory text s ops) :
    (history s ops).1.native.map text =
      (referenceHistory 7 s.backing (ops.map valueOp)).1 ∧
    (history s ops).2 = (referenceHistory 7 s.backing (ops.map valueOp)).2 := by
  have hg := history_good text s ops good provider
  have hr := history_reference text s ops
  exact ⟨hg.1.trans (congrArg Prod.fst hr), congrArg Prod.snd hr⟩

theorem pointer_query_observation (text : Atom → Value) (s : State Atom Value)
    (v : Value) (a : Atom) (good : Good text s) (provider : Canonical text s.native v a) :
    decide (a ∈ s.native) = decide (v ∈ s.backing) := by
  simp only [canonical_member text s v a good provider]

theorem initializer_step_bridge (text : Atom → Value) (s : Initial Atom)
    (v : Value) (a : Atom) (invariant : InitInvariant s)
    (provider : Canonical text s.native v a) :
    (initialStep s a).native =
      (operation (⟨s.native, s.native.map text⟩ : State Atom Value) (.add v a)).1.native := by
  have hm : a ∈ s.native ↔ v ∈ s.native.map text := by
    constructor
    · intro h; exact List.mem_map.mpr ⟨a,h,provider.1⟩
    · intro h
      obtain ⟨b,hb,he⟩ := List.mem_map.mp h
      simpa [provider.2 b hb he] using hb
  simp only [initialStep, operation]
  simp only [invariant.2 a, hm]
  split <;> rfl

def projectInit (text : Atom → Value) (s : Initial Atom) : Initial Value :=
  ⟨s.seen.map text, s.native.map text⟩

def InitProviders (text : Atom → Value) (s : Initial Atom) : List Atom → Prop
  | [] => True
  | a :: atoms => Canonical text s.native (text a) a ∧
      InitProviders text (initialStep s a) atoms

theorem initial_step_projection (text : Atom → Value) (s : Initial Atom)
    (a : Atom) (invariant : InitInvariant s)
    (provider : Canonical text s.native (text a) a) :
    projectInit text (initialStep s a) = initialStep (projectInit text s) (text a) := by
  have hm : a ∈ s.seen ↔ text a ∈ s.seen.map text := by
    constructor
    · intro ha; exact List.mem_map.mpr ⟨a,ha,rfl⟩
    · intro ha
      obtain ⟨b,hb,he⟩ := List.mem_map.mp ha
      have eq := provider.2 b ((invariant.2 b).mp hb) he
      simpa [eq] using hb
  unfold initialStep projectInit
  simp only [hm]
  split <;> simp [List.map_append]

theorem initial_run_projection (text : Atom → Value) (s : Initial Atom)
    (atoms : List Atom) (invariant : InitInvariant s) (provider : InitProviders text s atoms) :
    projectInit text (initialRun s atoms) = initialRun (projectInit text s) (atoms.map text) := by
  induction atoms generalizing s with
  | nil => rfl
  | cons a atoms ih =>
    simp only [initialRun, List.map_cons]
    rw [ih (initialStep s a) (initial_step_preserves s a invariant) provider.2,
      initial_step_projection text s a invariant provider.1]

theorem decoded_initial_prefix (text : Atom → Value) (atoms : List Atom)
    (provider : InitProviders text ⟨[],[]⟩ atoms) :
    (initialRun ⟨[],[]⟩ atoms).native.map text = firsts [] (atoms.map text) := by
  have h := initial_run_projection text (⟨[],[]⟩ : Initial Atom) atoms initial_empty provider
  have hn := congrArg Initial.native h
  simpa only [projectInit, List.map_nil, (initial_prefix (atoms.map text)).1] using hn

theorem decoded_initial_good (text : Atom → Value) (atoms : List Atom)
    (provider : InitProviders text ⟨[],[]⟩ atoms) :
    Good text ⟨(initialRun ⟨[],[]⟩ atoms).native, firsts [] (atoms.map text)⟩ :=
  ⟨decoded_initial_prefix text atoms provider, firsts_nodup [] (atoms.map text)⟩

theorem live_history_member (text : Atom → Value) (s : State Atom Value)
    (ops : List (Op Atom Value)) (v : Value) (a : Atom) (good : Good text s)
    (provider : AdmittedHistory text s ops)
    (queryProvider : Canonical text (history s ops).1.native v a) :
    decide (a ∈ (history s ops).1.native) =
      decide (v ∈ (referenceHistory 7 s.backing (ops.map valueOp)).1) := by
  have hg := history_good text s ops good provider
  have hm := canonical_member text (history s ops).1 v a hg queryProvider
  have hr := congrArg Prod.fst (history_reference text s ops)
  simp only at hr
  simp only [hm, hr]

theorem live_queries (text : Atom → Value) (s : State Atom Value)
    (queries : List Atom) (valid : Atom → Bool) (good : Good text s)
    (provider : ∀ a, a ∈ queries → Canonical text s.native (text a) a)
    (accepted : ∀ a, a ∈ queries → valid a = true) :
    TypeObservation.nativeQuery s.native queries valid =
      TypeObservation.query s.backing (queries.map text) := by
  induction queries with
  | nil => rfl
  | cons a queries ih =>
    have hm := canonical_member text s (text a) a good (provider a (by simp))
    have ha := accepted a (by simp)
    have ht := ih (by intro b hb; exact provider b (by simp [hb]))
      (by intro b hb; exact accepted b (by simp [hb]))
    simpa [TypeObservation.nativeQuery, TypeObservation.query, hm, ha] using
      congrArg (fun rest => decide (text a ∈ s.backing) || rest) ht

theorem live_history_queries (text : Atom → Value) (s : State Atom Value)
    (ops : List (Op Atom Value)) (queries : List Atom) (valid : Atom → Bool)
    (good : Good text s) (provider : AdmittedHistory text s ops)
    (queryProvider : ∀ a, a ∈ queries → Canonical text (history s ops).1.native (text a) a)
    (accepted : ∀ a, a ∈ queries → valid a = true) :
    TypeObservation.nativeQuery (history s ops).1.native queries valid =
      TypeObservation.query (referenceHistory 7 s.backing (ops.map valueOp)).1 (queries.map text) := by
  have h := live_queries text (history s ops).1 queries valid
    (history_good text s ops good provider) queryProvider accepted
  have hr := congrArg Prod.fst (history_reference text s ops)
  simp only at hr
  simpa only [hr] using h

def regenerated : List (Op Nat Nat) := [.add 0 0, .delete 0 0, .add 0 2]

theorem regenerated_admitted : AdmittedHistory (fun a => a % 2) ⟨[],[]⟩ regenerated := by
  simp [AdmittedHistory, admitted, regenerated, operation, Canonical]

theorem regenerated_live_atom :
    (history (⟨[],[]⟩ : State Nat Nat) regenerated).1 = ⟨[2],[0]⟩ := by decide +kernel

end LiveAtoms
