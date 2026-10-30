import Std

namespace Ancestry

set_option maxRecDepth 20000
set_option maxHeartbeats 30000000

inductive Request where
  | leafA | loopA | readD | parent | rootD | leafD
  deriving DecidableEq, Repr

inductive Result where
  | value (n : Nat) | cycle | exhausted
  deriving DecidableEq, Repr

def physical : Request → Nat
  | .leafA | .loopA => 0
  | .readD => 1
  | .parent => 2
  | .rootD | .leafD => 3

def next : Request → Option Request
  | .loopA => some .leafA
  | .readD => some .leafD
  | .parent => some .readD
  | .rootD => some .parent
  | _ => none

def literal (input : Nat) : Request → Nat
  | .leafA => input
  | _ => 9

def reference : Nat → Nat → List Nat → Request → Result
  | 0, _, _, _ => .exhausted
  | fuel + 1, input, active, request =>
      if physical request ∈ active then .cycle else
      match next request with
      | none => .value (literal input request)
      | some child => reference fuel input (physical request :: active) child

inductive Strategy where
  | context | parentOnly | ancestry | session
  deriving DecidableEq, Repr

structure Key where
  request : Request
  active : List Nat
  epoch : Nat
  deriving DecidableEq, Repr

def key (strategy : Strategy) (epoch : Nat) (active : List Nat) (request : Request) : Key :=
  ⟨request, match strategy with
    | .context => []
    | .parentOnly => active.take 1
    | .ancestry | .session => active,
   if strategy == .session then epoch else 0⟩

abbrev Cache := List (Key × Result)

def lookup (k : Key) : Cache → Option Result
  | [] => none
  | (other, result) :: rest => if k = other then some result else lookup k rest

def memo : Nat → Strategy → Nat → Nat → List Nat → Request → Cache → Result × Cache
  | 0, _, _, _, _, _, cache => (.exhausted, cache)
  | fuel + 1, strategy, epoch, input, active, request, cache =>
      let k := key strategy epoch active request
      if physical request ∈ active then
        (.cycle, (k, .cycle) :: cache)
      else match lookup k cache with
      | some result => (result, cache)
      | none =>
          let (result, updated) := match next request with
            | none => (.value (literal input request), cache)
            | some child => memo fuel strategy epoch input (physical request :: active) child cache
          (result, (k, result) :: updated)

def poisonSequence : Result × Cache :=
  let (_, first) := memo 12 .context 0 7 [] .leafA []
  let (_, second) := memo 12 .context 0 7 [] .loopA first
  memo 12 .context 0 7 [] .leafA second

def parentCollision : Result × Cache :=
  let (_, first) := memo 12 .parentOnly 0 7 [] .parent []
  memo 12 .parentOnly 0 7 [] .rootD first

def inputChange (strategy : Strategy) (nextEpoch : Nat) : Result × Cache :=
  let (_, first) := memo 12 strategy 0 7 [] .leafA []
  memo 12 strategy nextEpoch 8 [] .leafA first

def requests : List Request := [.leafA, .loopA, .readD, .parent, .rootD, .leafD]

def guardHistories : Nat → List (List Nat)
  | 0 => [[]]
  | n + 1 => [] :: ([0,1,2,3].flatMap fun node =>
      ((guardHistories n).filter fun history => !(history.contains node)).map (node :: ·))

def queries : List (List Nat × Request) :=
  (guardHistories 4).flatMap fun active => requests.map (active, ·)

def warmed (strategy : Strategy) : Cache :=
  queries.foldl (fun cache (active, request) =>
    (memo 12 strategy 0 7 active request cache).2) []

def agrees (strategy : Strategy) : Bool :=
  queries.all fun (active, request) =>
    (memo 12 strategy 0 7 active request (warmed strategy)).1 == reference 12 7 active request

theorem distinct_reference_invocations :
    reference 12 7 [] .leafA = .value 7 ∧
    reference 12 7 [0] .leafA = .cycle ∧
    reference 12 7 [] .loopA = .cycle := by decide

theorem checked_before_cache_still_poisoned :
    poisonSequence.1 = .cycle ∧
    poisonSequence.1 ≠ reference 12 7 [] .leafA := by decide

theorem immediate_parent_is_not_full_ancestry :
    key .parentOnly 0 [2] .readD = key .parentOnly 0 [2,3] .readD ∧
    reference 12 7 [2] .readD = .value 9 ∧
    reference 12 7 [2,3] .readD = .cycle ∧
    parentCollision.1 = .value 9 ∧
    parentCollision.1 ≠ reference 12 7 [] .rootD := by decide

theorem finite_fixed_input_ancestry_cache :
    (guardHistories 4).length = 65 ∧ queries.length = 390 ∧
    (queries.all fun (active, request) => reference 12 7 active request != .exhausted) = true ∧
    agrees .ancestry = true := by decide

theorem ancestry_does_not_replace_input_session :
    inputChange .ancestry 1 |>.1 = .value 7 ∧
    inputChange .ancestry 1 |>.1 ≠ reference 12 8 [] .leafA ∧
    inputChange .session 1 |>.1 = .value 8 ∧
    inputChange .session 0 |>.1 = .value 7 := by decide

theorem ancestry_determined_identity_suffices_for_reference
    {Identity : Type} (identify : List Nat → Identity)
    (recoversAncestry : ∀ a b, identify a = identify b → a = b)
    (a b : List Nat) (same : identify a = identify b)
    (fuel input : Nat) (request : Request) :
    reference fuel input a request = reference fuel input b request := by
  rw [recoversAncestry a b same]

end Ancestry
