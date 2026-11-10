import LifetimeDelivery

namespace IndependentLifetimeReview
open DrainLifetime DrainLifetimeDelivery

def arbitraryLaterInitial : Cell := ⟨false, 7, 7, some .initial, none⟩

theorem local_valid_allows_later_initial : Valid arbitraryLaterInitial := by
  simp [Valid, arbitraryLaterInitial]

theorem local_causal_allows_later_initial (tree : CertifiedPath.Tree) (target : Nat) :
    Causal tree target arbitraryLaterInitial := by
  intro origin ticket
  cases ticket
  trivial

theorem initial_only_excludes_later_initial : ¬ InitialOnly arbitraryLaterInitial := by
  intro initialOnly
  have impossible : 7 = 0 := initialOnly rfl
  contradiction

theorem quiet_phases_can_retain_dormant_ticket :
    DescendingPhases.quiet finish.pending ∧
    (finish.cells 2).ticket = some (.ancestor 0 0) := by
  constructor
  · simp [DescendingPhases.quiet, finish, DescendingPhases.dispatch,
      DescendingPhases.mark, DescendingPhases.maskedGraph]
  · decide +kernel

def metadata : Metadata := ⟨1, 7, .animations, 0⟩
def absentCell : Cell := clear (.ancestor 0 0) (ensure initial)
def futureKey : LifetimeLedger.Key := key (ensure absentCell) metadata

def alreadyInstalledFuture : Ledgers := fun _ =>
  { LifetimeLedger.empty with installed := fun k => k == futureKey }

theorem missing_freshness_allows_new_key_already_settled :
    LifetimeLedger.settled (requestAdmission 1 absentCell metadata alreadyInstalledFuture 1) futureKey = true := by
  decide

theorem such_state_violates_no_future : ¬ NoFuture (alreadyInstalledFuture 1) absentCell := by
  intro noFuture
  have fresh := noFuture futureKey (by decide)
  have impossible : true = false := fresh.2.1
  contradiction

def futureEvent : Cell := clear (.ancestor 0 999) (ensure initial)

theorem causal_geometry_does_not_validate_event_clock :
    Causal smallTree 1 futureEvent := by
  intro origin ticket
  have equal : Origin.ancestor 0 999 = origin := by simpa [futureEvent, clear, ensure, initial] using ticket
  rw [← equal]
  decide +kernel

def otherLevel : Metadata := { metadata with level := .transitions }
def firstAdmission : Ledgers := requestAdmission 1 absentCell metadata (fun _ => LifetimeLedger.empty)
def repeatedNormal : Ledgers := requestAdmission 1 (ensure absentCell) otherLevel firstAdmission

theorem one_metadata_parameter_does_not_admit_both_levels :
    (repeatedNormal 1).required (key (ensure absentCell) otherLevel) = false := by decide

end IndependentLifetimeReview
