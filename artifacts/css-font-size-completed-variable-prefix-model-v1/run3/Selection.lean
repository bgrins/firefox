import Demand

namespace SelectedDeclaration

inductive Next (State Value : Type) where
  | terminal (value : Option Value)
  | rollback (state : State)
  | blocked
  deriving DecidableEq, Repr

structure Evaluation (State Value Edge : Type) where
  next : Next State Value
  reads : List Edge
  deriving DecidableEq, Repr

inductive Finish (Value : Type) where
  | exhausted
  | terminal (value : Option Value)
  | blocked
  deriving DecidableEq, Repr

structure Result (Decl Value Edge : Type) where
  finish : Finish Value
  evaluated : List Decl
  reads : List Edge
  deriving DecidableEq, Repr

def prepend (d : D) (edges : List E) (r : Result D V E) : Result D V E :=
  {r with evaluated := d :: r.evaluated, reads := edges ++ r.reads}

def scan (eligible : S → D → Bool) (evaluate : S → D → Evaluation S V E)
    (state : S) : List D → Result D V E
  | [] => ⟨.exhausted, [], []⟩
  | d :: rest =>
      if eligible state d then
        let step := evaluate state d
        match step.next with
        | .terminal value => ⟨.terminal value, [d], step.reads⟩
        | .blocked => ⟨.blocked, [d], step.reads⟩
        | .rollback next => prepend d step.reads (scan eligible evaluate next rest)
      else scan eligible evaluate state rest

def stopped (r : Result D V E) : Prop := r.finish ≠ .exhausted

theorem losing_suffix_irrelevant (eligible : S → D → Bool)
    (evaluate : S → D → Evaluation S V E) (state : S) (leading suffix : List D)
    (done : stopped (scan eligible evaluate state leading)) :
    scan eligible evaluate state (leading ++ suffix) = scan eligible evaluate state leading := by
  induction leading generalizing state with
  | nil => simp [stopped, scan] at done
  | cons d rest ih =>
      simp only [List.cons_append, scan]
      split
      next yes =>
        cases step : (evaluate state d).next with
        | terminal value => simp [step]
        | blocked => simp [step]
        | rollback next =>
            simp only [step]
            apply congrArg (prepend d (evaluate state d).reads)
            apply ih next
            simpa [stopped, scan, yes, step, prepend] using done
      next no =>
        apply ih state
        simpa [stopped, scan, no] using done

theorem terminal_ignores_tail (eligible : S → D → Bool)
    (evaluate : S → D → Evaluation S V E) (state : S) (d : D) (rest : List D)
    (yes : eligible state d = true) (value : Option V)
    (ends : (evaluate state d).next = .terminal value) :
    scan eligible evaluate state (d :: rest) = ⟨.terminal value, [d], (evaluate state d).reads⟩ := by
  simp [scan, yes, ends]

theorem rollback_preserves_reads (eligible : S → D → Bool)
    (evaluate : S → D → Evaluation S V E) (state next : S) (d : D) (rest : List D)
    (yes : eligible state d = true) (rolls : (evaluate state d).next = .rollback next) :
    (scan eligible evaluate state (d :: rest)).reads =
      (evaluate state d).reads ++ (scan eligible evaluate next rest).reads := by
  simp [scan, yes, rolls, prepend]

theorem skipped_candidate_adds_no_reads (eligible : S → D → Bool)
    (evaluate : S → D → Evaluation S V E) (state : S) (d : D) (rest : List D)
    (no : eligible state d = false) :
    scan eligible evaluate state (d :: rest) = scan eligible evaluate state rest := by
  simp [scan, no]

theorem read_provenance (eligible : S → D → Bool)
    (evaluate : S → D → Evaluation S V E) (state : S) (decls : List D) (edge : E)
    (member : edge ∈ (scan eligible evaluate state decls).reads) :
    ∃ d ∈ (scan eligible evaluate state decls).evaluated,
      ∃ atState, eligible atState d = true ∧ edge ∈ (evaluate atState d).reads := by
  induction decls generalizing state with
  | nil => simp [scan] at member
  | cons d rest ih =>
      by_cases yes : eligible state d = true
      · cases step : (evaluate state d).next with
        | terminal value =>
            exact ⟨d, by simp [scan, yes, step], state, yes,
              by simpa [scan, yes, step] using member⟩
        | blocked =>
            exact ⟨d, by simp [scan, yes, step], state, yes,
              by simpa [scan, yes, step] using member⟩
        | rollback next =>
            have splitReads : edge ∈ (evaluate state d).reads ∨
                edge ∈ (scan eligible evaluate next rest).reads := by
              simpa [scan, yes, step, prepend] using member
            rcases splitReads with here | later
            · exact ⟨d, by simp [scan, yes, step, prepend], state, yes, here⟩
            · obtain ⟨selected, present, atState, allowed, reads⟩ := ih next later
              exact ⟨selected, by simp [scan, yes, step, prepend, present], atState, allowed, reads⟩
      · have no : eligible state d = false := Bool.eq_false_iff.mpr yes
        have later : edge ∈ (scan eligible evaluate state rest).reads := by
          simpa [scan, no] using member
        simpa [scan, no] using ih state later

def lookup (name : String) : Option DemandFallback.Expr :=
  if name = "--ok" then some (.literal ["revert-layer"])
  else if name = "--fallback" then some (.literal ["blue"])
  else none

def readsFor (expr : DemandFallback.Expr) : List String :=
  ((DemandFallback.eval lookup 5 [] [] (.expression expr)).getD ⟨none, [], []⟩).reads

def allowed (state declaration : Nat) : Bool := state ≤ declaration

def evaluate (_ : Nat) (d : Nat) : Evaluation Nat Nat String :=
  if d = 0 then ⟨.rollback 2, readsFor (.fallback "--ok" (.reference "--unused"))⟩
  else if d = 1 then ⟨.terminal (some 1), ["--loser"]⟩
  else ⟨.terminal (some 2), readsFor (.fallback "--missing" (.reference "--fallback"))⟩

theorem rollback_and_selected_fallback_trace :
    scan allowed evaluate 0 [0, 1, 2, 3] =
      ⟨.terminal (some 2), [0, 2], ["--ok", "--missing", "--fallback"]⟩ := by decide

theorem arbitrary_suffix_after_rollback (tail : List Nat) :
    scan allowed evaluate 0 ([0, 1, 2] ++ tail) =
      ⟨.terminal (some 2), [0, 2], ["--ok", "--missing", "--fallback"]⟩ := by
  rw [losing_suffix_irrelevant allowed evaluate 0 [0, 1, 2] tail (by unfold stopped; decide)]
  decide

theorem unused_fallback_not_collected :
    "--unused" ∉ (scan allowed evaluate 0 [0, 1, 2]).reads := by decide

theorem evaluated_rollback_not_discarded :
    "--ok" ∈ (scan allowed evaluate 0 [0, 1, 2]).reads := by decide

def direct (_ : Unit) (d : Nat) : Evaluation Unit Nat String :=
  if d = 0 then ⟨.terminal (some 7), []⟩
  else ⟨.terminal (some 8), ["--x"]⟩

def eager (decls : List Nat) : List String := decls.flatMap fun d => (direct () d).reads

inductive Node where
  | property | custom
  deriving DecidableEq, Repr

def edge (propertyReads : List String) : Node → Node → Bool
  | .custom, .property => true
  | .property, .custom => "--x" ∈ propertyReads
  | _, _ => false

def twoNodeCycle (propertyReads : List String) : Bool :=
  [Node.property, Node.custom].any fun a =>
    [Node.property, Node.custom].any fun b =>
      edge propertyReads a b && edge propertyReads b a

theorem eager_adds_losing_edge :
    eager [0, 1] = ["--x"] ∧ (scan (fun _ _ => true) direct () [0, 1]).reads = [] := by decide

theorem eager_false_cycle_witness :
    twoNodeCycle (eager [0, 1]) = true ∧
      twoNodeCycle (scan (fun _ _ => true) direct () [0, 1]).reads = false := by decide

end SelectedDeclaration
