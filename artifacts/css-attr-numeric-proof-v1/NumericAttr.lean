namespace NumericAttr

structure Payload (α : Type) where
  value : α
  negative : Bool
  explicitSign : Bool
  integer : Bool
  lexeme : String
  deriving DecidableEq, Repr

inductive Token (α : Type) where
  | number (payload : Payload α)
  | whitespace
  | comment
  | other
  deriving DecidableEq, Repr

def significant : List (Token α) → List (Token α)
  | [] => []
  | .whitespace :: rest | .comment :: rest => significant rest
  | token :: rest => token :: significant rest

def grammar : List (Token α) → Option (Payload α)
  | [.number p] => some p
  | _ => none

def parseWhole : List (Token α) → Option (Payload α)
  | [] => none
  | .whitespace :: rest | .comment :: rest => parseWhole rest
  | .number p :: rest => if (significant rest).isEmpty then some p else none
  | .other :: _ => none

theorem whole_token_classification (tokens : List (Token α)) :
    parseWhole tokens = grammar (significant tokens) := by
  induction tokens with
  | nil => rfl
  | cons token rest ih =>
    cases token with
    | whitespace => exact ih
    | comment => exact ih
    | other => simp [parseWhole, significant, grammar]
    | number p =>
      cases h : significant rest <;> simp [parseWhole, significant, grammar, h]

theorem significant_append (a b : List (Token α)) :
    significant (a ++ b) = significant a ++ significant b := by
  induction a with
  | nil => rfl
  | cons token rest ih => cases token <;> simp [significant, ih]

theorem surrounding_trivia_invariant (before tokens after : List (Token α))
    (hb : significant before = []) (ha : significant after = []) :
    parseWhole (before ++ tokens ++ after) = parseWhole tokens := by
  simp only [whole_token_classification, significant_append, hb, ha,
    List.nil_append, List.append_nil]

theorem suffix_rejected (p : Payload α) (suffix : List (Token α))
    (h : significant suffix ≠ []) : parseWhole (.number p :: suffix) = none := by
  cases hs : significant suffix with
  | nil => exact False.elim (h hs)
  | cons token rest => simp [parseWhole, hs]

theorem one_number_accepted (p : Payload α) : parseWhole [.number p] = some p := by
  rfl

inductive Unit where
  | number | percentage | dimension (name : String)
  deriving DecidableEq, Repr

inductive Value (α : Type) where
  | number (p : Payload α)
  | percentage (p : Payload α)
  | dimension (p : Payload α) (name : String)
  deriving DecidableEq, Repr

def construct (p : Payload α) : Unit → Value α
  | .number => .number p
  | .percentage => .percentage p
  | .dimension name => .dimension p name

def payload : Value α → Payload α
  | .number p | .percentage p | .dimension p _ => p

def valueUnit : Value α → Unit
  | .number _ => .number
  | .percentage _ => .percentage
  | .dimension _ name => .dimension name

structure Substitution (α : Type) where
  value : Value α
  tainted : Bool
  deriving DecidableEq, Repr

def primary (input : Option (List (Token α))) (unit : Unit) : Option (Substitution α) :=
  input.bind fun tokens => (parseWhole tokens).map fun p => ⟨construct p unit, true⟩

def evaluate (input : Option (List (Token α))) (unit : Unit)
    (fallback : Option (Substitution α)) : Option (Substitution α) :=
  match primary input unit with
  | some value => some value
  | none => fallback

def grammarPrimary (input : Option (List (Token α))) (unit : Unit) :
    Option (Substitution α) :=
  input.bind fun tokens => (grammar (significant tokens)).map fun p => ⟨construct p unit, true⟩

theorem primary_refinement (input : Option (List (Token α))) (unit : Unit) :
    primary input unit = grammarPrimary input unit := by
  cases input with
  | none => rfl
  | some tokens => simp [primary, grammarPrimary, whole_token_classification]

theorem construction_preserves_payload (p : Payload α) (unit : Unit) :
    payload (construct p unit) = p := by
  cases unit <;> rfl

theorem construction_preserves_unit (p : Payload α) (unit : Unit) :
    valueUnit (construct p unit) = unit := by
  cases unit <;> rfl

theorem accepted_primary (p : Payload α) (unit : Unit) (fallback : Option (Substitution α)) :
    evaluate (some [.number p]) unit fallback = some ⟨construct p unit, true⟩ := by
  rfl

theorem rejected_suffix_selects_fallback (p : Payload α) (suffix : List (Token α))
    (h : significant suffix ≠ []) (unit : Unit) (fallback : Option (Substitution α)) :
    evaluate (some (.number p :: suffix)) unit fallback = fallback := by
  simp [evaluate, primary, suffix_rejected p suffix h]

theorem missing_selects_fallback (unit : Unit) (fallback : Option (Substitution α)) :
    evaluate none unit fallback = fallback := by
  rfl

theorem primary_tainted (input : Option (List (Token α))) (unit : Unit)
    (result : Substitution α) (h : primary input unit = some result) :
    result.tainted = true := by
  cases input with
  | none => simp [primary] at h
  | some tokens =>
    cases hp : parseWhole tokens with
    | none => simp [primary, hp] at h
    | some p => simp [primary, hp] at h; cases h; rfl

theorem substitution_trivia_invariant (before tokens after : List (Token α))
    (hb : significant before = []) (ha : significant after = [])
    (unit : Unit) (fallback : Option (Substitution α)) :
    evaluate (some (before ++ tokens ++ after)) unit fallback =
      evaluate (some tokens) unit fallback := by
  unfold evaluate primary
  simp only [Option.bind_some, surrounding_trivia_invariant before tokens after hb ha]

def oldParse : List (Token α) → Option (Payload α)
  | [] => none
  | .whitespace :: rest | .comment :: rest => oldParse rest
  | .number p :: _ => some p
  | .other :: _ => none

theorem old_prefix_counterexample (p : Payload α) :
    oldParse [.number p, .other] ≠ grammar (significant [.number p, .other]) := by
  simp [oldParse, grammar, significant]

#print axioms whole_token_classification
#print axioms significant_append
#print axioms surrounding_trivia_invariant
#print axioms suffix_rejected
#print axioms one_number_accepted
#print axioms primary_refinement
#print axioms construction_preserves_payload
#print axioms construction_preserves_unit
#print axioms accepted_primary
#print axioms rejected_suffix_selects_fallback
#print axioms missing_selects_fallback
#print axioms primary_tainted
#print axioms substitution_trivia_invariant
#print axioms old_prefix_counterexample

end NumericAttr
