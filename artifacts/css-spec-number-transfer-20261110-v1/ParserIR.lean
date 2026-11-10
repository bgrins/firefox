import FOBridge

namespace CssDerivation.ParserIR

inductive Shape where
  | base : FirstOrder.Ty → Shape
  | pair : Shape → Shape → Shape
  | optional : Shape → Shape

abbrev Shape.Value : Shape → Type
  | .base t => t.Value
  | .pair a b => a.Value × b.Value
  | .optional a => Option a.Value

abbrev Predicate := FirstOrder.Expr [.scalar] .bool

def accepts (predicate : Predicate) (c : Char) : Bool := FirstOrder.eval predicate (.cons c .nil)

def scanWhile (predicate : Predicate) : List Char → List Char × List Char
  | [] => ([], [])
  | c :: rest =>
      if accepts predicate c then
        let next := scanWhile predicate rest
        (c :: next.1, next.2)
      else ([], c :: rest)

inductive Scanned (predicate : Predicate) : List Char → List Char → List Char → Prop where
  | empty : Scanned predicate [] [] []
  | stop (c rest) : accepts predicate c = false → Scanned predicate (c :: rest) [] (c :: rest)
  | next (c) {source chars rest} : accepts predicate c = true → Scanned predicate source chars rest →
      Scanned predicate (c :: source) (c :: chars) rest

inductive Parser : Shape → Type where
  | legacy {t} : FirstOrder.Stmt [] t → Parser (.base t)
  | take : Predicate → Parser (.base .scalar)
  | scan : Predicate → Parser (.base .chars)
  | nonempty : Parser (.base .chars) → Parser (.base .chars)
  | pair {a b} : Parser a → Parser b → Parser (.pair a b)
  | right {a b} : Parser a → Parser b → Parser b
  | optional {a} : Parser a → Parser (.optional a)

def run : Parser t → State → Option (t.Value × State)
  | .legacy program, state => some (FirstOrder.interpret program .nil state)
  | .take predicate, state =>
      match state.input with
      | [] => none
      | c :: rest => if accepts predicate c then some (c, { state with input := rest }) else none
  | .scan predicate, state =>
      let scanned := scanWhile predicate state.input
      some (scanned.1, { state with input := scanned.2 })
  | .nonempty parser, state =>
      match run parser state with
      | some ([], _) => none
      | result => result
  | .pair left right, state => do
      let (a, next) ← run left state
      let (b, final) ← run right next
      pure ((a, b), final)
  | .right left right, state => do
      let (_, next) ← run left state
      run right next
  | .optional parser, state =>
      match run parser state with
      | none => some (none, state)
      | some (value, next) => some (some value, next)

theorem Scanned.result {predicate source chars rest} (parsed : Scanned predicate source chars rest) :
    scanWhile predicate source = (chars, rest) := by
  induction parsed with
  | empty => rfl
  | stop c rest no => simp [scanWhile, no]
  | next c yes tail ih => simp [scanWhile, yes, ih]

theorem scan_sound (predicate : Predicate) (source : List Char) :
    Scanned predicate source (scanWhile predicate source).1 (scanWhile predicate source).2 := by
  induction source with
  | nil => exact .empty
  | cons c rest ih =>
      simp only [scanWhile]
      split
      · exact .next c ‹_› ih
      · exact .stop c rest (by simpa using ‹¬ accepts predicate c = true›)

theorem scan_iff (predicate : Predicate) (source chars rest : List Char) :
    scanWhile predicate source = (chars, rest) ↔ Scanned predicate source chars rest := by
  constructor
  · intro same; simpa [same] using scan_sound predicate source
  · exact Scanned.result

theorem Scanned.decomposition {predicate source chars rest} (parsed : Scanned predicate source chars rest) :
    source = chars ++ rest := by
  induction parsed with
  | empty => rfl
  | stop => rfl
  | next c yes tail ih => simp [ih]

theorem Scanned.boundary {predicate source chars rest} (parsed : Scanned predicate source chars rest) :
    ∀ c tail, rest = c :: tail → accepts predicate c = false := by
  induction parsed with
  | empty => simp
  | stop c rest no => simpa using no
  | next c yes tail ih => exact ih

theorem scan_matches_length_bound (predicate : Predicate) (source : List Char) :
    scanWhile predicate source = FirstOrder.scanData predicate .nil source.length source := by
  induction source with
  | nil => rfl
  | cons c rest ih => simp [scanWhile, FirstOrder.scanData, accepts, ih]

theorem legacy_preserved (program : FirstOrder.Stmt [] t) (state : State) :
    run (.legacy program) state = some (FirstOrder.interpret program .nil state) := rfl

theorem legacy_lowering (program : FirstOrder.Stmt [] t) (state : State) :
    run (.legacy program) state = some (CssDerivation.run (FirstOrder.lower program .nil) state) := by
  rw [FirstOrder.lowering_correct]
  rfl

theorem optional_rollback (parser : Parser t) (state : State) (failed : run parser state = none) :
    run (.optional parser) state = some (none, state) := by simp [run, failed]

theorem escape_preserved (source : List Char) :
    run (.legacy FirstOrder.escapeTree) ⟨source, false⟩ =
      some ((FirstOrder.execute FirstOrder.escapeTree source).value,
        ⟨(FirstOrder.execute FirstOrder.escapeTree source).rest, (FirstOrder.execute FirstOrder.escapeTree source).error⟩) := rfl

end CssDerivation.ParserIR
