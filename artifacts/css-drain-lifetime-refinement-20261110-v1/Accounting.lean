import Std

namespace LifetimeLedger

inductive Level where
  | animations | transitions
  deriving DecidableEq, Repr

structure Key where
  lifetime : Nat
  pseudoType : Nat
  pseudoArgument : Nat
  level : Level
  generation : Nat
  deriving DecidableEq, Repr

abbrev Bits := Key → Bool

structure State where
  required : Bits
  queued : Bits
  hinted : Bits
  flight : Bits
  installed : Bits
  retired : Bits

def covered (s : State) (k : Key) : Bool :=
  s.queued k || s.hinted k || s.flight k || s.installed k || s.retired k

def settled (s : State) (k : Key) : Bool := s.installed k || s.retired k

def Conserved (s : State) : Prop := ∀ k, s.required k = true → covered s k = true
def Ready (s : State) : Prop := ∀ k, s.required k = true → settled s k = true
def ReadyFor (s : State) (relevant : Bits) : Prop :=
  ∀ k, relevant k = true → s.required k = true → settled s k = true

def empty : State := ⟨fun _ => false, fun _ => false, fun _ => false,
  fun _ => false, fun _ => false, fun _ => false⟩

def request (s : State) (key : Key) : State :=
  { s with required := fun k => k == key || s.required k
           queued := fun k => k == key || s.queued k }

def select (s : State) (eligible : Bits) : State :=
  { s with queued := fun k => s.queued k && !eligible k
           hinted := fun k => s.hinted k || (s.queued k && eligible k) }

def selectWithPosting (s : State) (eligible canPost canRetire : Bits) : State :=
  { s with queued := fun k => s.queued k && !eligible k
           hinted := fun k => s.hinted k || (s.queued k && eligible k && canPost k)
           retired := fun k => s.retired k ||
             (s.queued k && eligible k && !canPost k && canRetire k) }

def beginTraversal (s : State) (admitted : Bits) : State :=
  { s with hinted := fun k => s.hinted k && !admitted k
           flight := fun k => s.flight k || (s.hinted k && admitted k) }

def install (s : State) (completed : Bits) : State :=
  { s with flight := fun k => s.flight k && !completed k
           installed := fun k => s.installed k || (s.flight k && completed k) }

def retire (s : State) (irrelevant : Bits) : State :=
  { s with queued := fun k => s.queued k && !irrelevant k
           hinted := fun k => s.hinted k && !irrelevant k
           flight := fun k => s.flight k && !irrelevant k
           retired := fun k => s.retired k || (s.required k && irrelevant k) }

theorem empty_conserved : Conserved empty := by simp [Conserved, empty]

theorem request_conserved (s : State) (key : Key) (h : Conserved s) :
    Conserved (request s key) := by
  intro k required
  by_cases eq : k = key
  · simp [covered, request, eq]
  · have old : s.required k = true := by simpa [request, eq] using required
    simpa [covered, request, eq] using h k old

theorem select_coverage (s : State) (eligible : Bits) (k : Key) :
    covered (select s eligible) k = covered s k := by
  cases hq : s.queued k <;> cases he : eligible k <;> simp [covered, select, hq, he]

theorem begin_coverage (s : State) (admitted : Bits) (k : Key) :
    covered (beginTraversal s admitted) k = covered s k := by
  cases hh : s.hinted k <;> cases ha : admitted k <;>
    simp [covered, beginTraversal, hh, ha, Bool.or_assoc]

theorem posting_coverage (s : State) (eligible canPost canRetire : Bits) (k : Key)
    (fallback : s.queued k = true → eligible k = true → canPost k = false →
      canRetire k = true) :
    covered (selectWithPosting s eligible canPost canRetire) k = covered s k := by
  cases hq : s.queued k <;> cases he : eligible k <;> cases hp : canPost k <;>
    simp_all [covered, selectWithPosting]

theorem posting_conserved (s : State) (eligible canPost canRetire : Bits)
    (h : Conserved s)
    (fallback : ∀ k, s.queued k = true → eligible k = true → canPost k = false →
      canRetire k = true) :
    Conserved (selectWithPosting s eligible canPost canRetire) := by
  intro k required
  rw [posting_coverage s eligible canPost canRetire k (fallback k)]
  exact h k required

theorem install_coverage (s : State) (completed : Bits) (k : Key) :
    covered (install s completed) k = covered s k := by
  cases hf : s.flight k <;> cases hc : completed k <;>
    simp [covered, install, hf, hc, Bool.or_assoc]

theorem select_conserved (s : State) (eligible : Bits) (h : Conserved s) :
    Conserved (select s eligible) := by
  intro k required
  rw [select_coverage]
  exact h k required

theorem begin_conserved (s : State) (admitted : Bits) (h : Conserved s) :
    Conserved (beginTraversal s admitted) := by
  intro k required
  rw [begin_coverage]
  exact h k required

theorem install_conserved (s : State) (completed : Bits) (h : Conserved s) :
    Conserved (install s completed) := by
  intro k required
  rw [install_coverage]
  exact h k required

theorem retire_conserved (s : State) (irrelevant : Bits) (h : Conserved s) :
    Conserved (retire s irrelevant) := by
  intro k required
  change s.required k = true at required
  cases flag : irrelevant k
  · simpa [covered, retire, flag] using h k required
  · simp [covered, retire, flag, required]

theorem request_during_flight_survives (s : State) (key : Key) (completed : Bits) :
    (install (request s key) completed).queued key = true := by
  simp [install, request]

theorem ineligible_preserved (s : State) (eligible : Bits) (k : Key)
    (h : eligible k = false) : (select s eligible).queued k = s.queued k := by
  simp [select, h]

theorem unadmitted_hint_preserved (s : State) (admitted : Bits) (k : Key)
    (h : admitted k = false) : (beginTraversal s admitted).hinted k = s.hinted k := by
  simp [beginTraversal, h]

theorem selection_not_installation (s : State) (eligible : Bits) :
    (select s eligible).installed = s.installed := rfl

theorem drained_conserved_ready (s : State) (h : Conserved s)
    (q : ∀ k, s.queued k = false) (a : ∀ k, s.hinted k = false)
    (i : ∀ k, s.flight k = false) : Ready s := by
  intro k required
  simpa [covered, settled, q k, a k, i k] using h k required

theorem relevant_drained_ready (s : State) (relevant : Bits) (h : Conserved s)
    (q : ∀ k, relevant k = true → s.queued k = false)
    (a : ∀ k, relevant k = true → s.hinted k = false)
    (i : ∀ k, relevant k = true → s.flight k = false) : ReadyFor s relevant := by
  intro k needed required
  simpa [covered, settled, q k needed, a k needed, i k needed] using h k required

def Fresh (s : State) (k : Key) : Prop :=
  s.required k = false ∧ s.installed k = false ∧ s.retired k = false

theorem fresh_request_unsettled (s : State) (key : Key) (h : Fresh s key) :
    settled (request s key) key = false := by simp [settled, request, h.2.1, h.2.2]

inductive Step : State → State → Prop where
  | request (s key) : Fresh s key → Step s (request s key)
  | select (s eligible) : Step s (select s eligible)
  | posting (s eligible canPost canRetire) :
      (∀ k, s.queued k = true → eligible k = true → canPost k = false →
        canRetire k = true) →
      Step s (selectWithPosting s eligible canPost canRetire)
  | beginTraversal (s admitted) : Step s (beginTraversal s admitted)
  | install (s completed) : Step s (install s completed)
  | retire (s irrelevant) : Step s (retire s irrelevant)

theorem step_conserved {s t : State} (h : Conserved s) (step : Step s t) : Conserved t := by
  cases step with
  | request => exact request_conserved _ _ h
  | select => exact select_conserved _ _ h
  | posting eligible canPost canRetire fallback =>
      exact posting_conserved _ eligible canPost canRetire h fallback
  | beginTraversal => exact begin_conserved _ _ h
  | install => exact install_conserved _ _ h
  | retire => exact retire_conserved _ _ h

inductive History : State → State → Prop where
  | refl (s) : History s s
  | tail {s t u} : History s t → Step t u → History s u

theorem history_conserved {s t : State} (h : Conserved s)
    (history : History s t) : Conserved t := by
  induction history with
  | refl => exact h
  | tail _ step ih => exact step_conserved ih step

def animationKey : Key := ⟨1, 95, 0, .animations, 0⟩
def transitionKey : Key := { animationKey with level := .transitions }
def newerKey : Key := { animationKey with generation := 1 }
def functionalPseudoKey : Key := { animationKey with pseudoArgument := 7 }
def reusedAddressKey : Key := { animationKey with lifetime := 2 }
def all : Bits := fun _ => true
def none : Bits := fun _ => false
def selected := select (request empty animationKey) all

theorem selected_queue_empty (k : Key) : selected.queued k = false := by simp [selected, select, all]
theorem selected_not_ready : ¬ Ready selected := by
  intro ready
  have impossible := ready animationKey (by decide)
  contradiction

def bothLevels := request (request empty animationKey) transitionKey
def selectedBoth := select bothLevels all

theorem both_level_hints : selectedBoth.hinted animationKey = true ∧
    selectedBoth.hinted transitionKey = true := by decide

def completedBoth := install (beginTraversal selectedBoth all) all

theorem both_levels_installed : completedBoth.installed animationKey = true ∧
    completedBoth.installed transitionKey = true := by decide

theorem completed_both_ready : Ready completedBoth := by
  apply drained_conserved_ready
  · exact install_conserved _ _ (begin_conserved _ _ (select_conserved _ _
      (request_conserved _ _ (request_conserved _ _ empty_conserved))))
  · intro k; simp [completedBoth, install, beginTraversal, selectedBoth, select, all]
  · intro k; simp [completedBoth, install, beginTraversal, all]
  · intro k; simp [completedBoth, install, all]

def eraseQueue (s : State) : State := { s with queued := fun _ => false }
def buggySelection := eraseQueue (request selected newerKey)

theorem reentrant_erase_loses_newer : buggySelection.required newerKey = true ∧
    covered buggySelection newerKey = false := by decide

def failedPosting := selectWithPosting (request empty animationKey) all none none

theorem selected_without_posting_loses_work : failedPosting.required animationKey = true ∧
    covered failedPosting animationKey = false := by decide

theorem retirement_not_installation :
    (selectWithPosting (request empty animationKey) all none all).retired animationKey = true ∧
    (selectWithPosting (request empty animationKey) all none all).installed animationKey = false := by
  decide

def collapsedLevel : State :=
  { selectedBoth with hinted := fun k => k == animationKey }

theorem level_collapse_loses_transition : collapsedLevel.required transitionKey = true ∧
    covered collapsedLevel transitionKey = false := by decide

theorem full_identity_distinct : animationKey ≠ transitionKey ∧ animationKey ≠ newerKey ∧
    animationKey ≠ functionalPseudoKey ∧ animationKey ≠ reusedAddressKey := by decide

end LifetimeLedger
