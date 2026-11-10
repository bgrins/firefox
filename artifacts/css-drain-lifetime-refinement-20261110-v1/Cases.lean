import LifetimeDelivery
open DrainLifetime DrainLifetimeDelivery

def exampleMetadata : Metadata := ⟨1, 7, .animations, 0⟩
def oldCell : Cell := ensure initial
def recreatedInput : Cell := clear (.ancestor 0 0) oldCell
def oldKey : LifetimeLedger.Key := key oldCell exampleMetadata
def newKey : LifetimeLedger.Key := key (ensure recreatedInput) exampleMetadata
def oldLedgers : Ledgers := fun _ =>
  { LifetimeLedger.empty with installed := fun k => k == oldKey }
def admitted : Ledgers := requestAdmission 1 recreatedInput exampleMetadata oldLedgers
def inFlight : Ledgers := fun node =>
  LifetimeLedger.beginTraversal (LifetimeLedger.select (admitted node) (fun _ => true)) (fun _ => true)
def completedOld : Ledgers := complete 1 oldKey inFlight

def completeIgnoringLifetime (done : LifetimeLedger.Key) (ledger : LifetimeLedger.State) : LifetimeLedger.State :=
  LifetimeLedger.install ledger fun k =>
    k.pseudoType == done.pseudoType && k.pseudoArgument == done.pseudoArgument &&
    k.level == done.level && k.generation == done.generation

def checks : List (String × Bool) := [
  ("initial ticket", decide (initial.ticket = some .initial)),
  ("first allocation consumes ticket", decide ((ensure initial).ticket = none)),
  ("ensure existing is idempotent", decide (ensure (ensure initial) = ensure initial)),
  ("clear absent does not renew ticket", decide (clear (.ancestor 1 8) initial = initial)),
  ("producer lifetime retained", decide (middle.cells 0 = start.cells 0)),
  ("descendant data cleared", decide ((middle.cells 1).present = false)),
  ("clear preserves old serial", decide ((middle.cells 1).lifetime = 1)),
  ("recreated lifetime advances", decide ((finish.cells 1).lifetime = 2)),
  ("recreation records ancestor cause", decide ((finish.cells 1).admittedFrom = some (.ancestor 0 0))),
  ("unrevealed sibling stays absent", decide ((finish.cells 2).present = false)),
  ("unrevealed sibling retains ticket", decide ((finish.cells 2).ticket = some (.ancestor 0 0))),
  ("productive phases drain", decide (finish.pending = [false, false, false, false, false, false])),
  ("phase clock advances", decide (finish.clock = 2)),
  ("unrestricted reset creates new lifetime", decide ((unrestrictedRenewal oldCell).lifetime = 2)),
  ("new lifetime request is required", decide ((admitted 1).required newKey = true)),
  ("old installation does not settle new key", decide (LifetimeLedger.settled (admitted 1) newKey = false)),
  ("new key reaches flight", decide ((inFlight 1).flight newKey = true)),
  ("old completion cannot settle new flight", decide (LifetimeLedger.settled (completedOld 1) newKey = false)),
  ("different target completion cannot settle", decide (LifetimeLedger.settled (complete 0 newKey inFlight 1) newKey = false)),
  ("different pseudo type cannot settle", decide (LifetimeLedger.settled (complete 1 {newKey with pseudoType := 2} inFlight 1) newKey = false)),
  ("different pseudo argument cannot settle", decide (LifetimeLedger.settled (complete 1 {newKey with pseudoArgument := 8} inFlight 1) newKey = false)),
  ("different cascade level cannot settle", decide (LifetimeLedger.settled (complete 1 {newKey with level := .transitions} inFlight 1) newKey = false)),
  ("different generation cannot settle", decide (LifetimeLedger.settled (complete 1 {newKey with generation := 1} inFlight 1) newKey = false)),
  ("lifetime-erasing completion is unsound", decide (LifetimeLedger.settled (completeIgnoringLifetime oldKey (inFlight 1)) newKey = true)),
  ("exact full identity completes flight", decide (LifetimeLedger.settled (complete 1 newKey inFlight 1) newKey = true))
]

def main : IO Unit := do
  for (name, ok) in checks do IO.println s!"{name}: {ok}"
