namespace ResolvedDependencies

inductive Dependency where
  | font | line | rootFont | rootLine
  deriving DecidableEq

inductive Unit where
  | absolute | font | line | rootFont | rootLine
  deriving DecidableEq

inductive Token where
  | dimension (unit : Unit)
  | inert (identity : Nat)
  | separator
  | unresolved
  deriving DecidableEq

abbrev Flags := Dependency → Bool
abbrev Scan := Option Flags

def emptyFlags : Flags := fun _ => false
def join (left right : Flags) : Flags := fun dep => left dep || right dep

def unitFlags : Unit → Flags
  | .absolute => emptyFlags
  | .font => fun dep => dep == .font
  | .line => fun dep => dep == .font || dep == .line
  | .rootFont => fun dep => dep == .rootFont
  | .rootLine => fun dep => dep == .rootFont || dep == .rootLine

def combine : Scan → Scan → Scan
  | some left, some right => some (join left right)
  | _, _ => none

def tokenScan : Token → Scan
  | .dimension unit => some (unitFlags unit)
  | .inert _ => some emptyFlags
  | .separator => some emptyFlags
  | .unresolved => none

def scan : List Token → Scan
  | [] => some emptyFlags
  | token :: rest => combine (tokenScan token) (scan rest)

theorem join_assoc (a b c : Flags) : join (join a b) c = join a (join b c) := by
  funext dep
  exact Bool.or_assoc (a dep) (b dep) (c dep)

@[simp] theorem join_empty_left (a : Flags) : join emptyFlags a = a := by
  funext dep
  simp [join, emptyFlags]

@[simp] theorem join_empty_right (a : Flags) : join a emptyFlags = a := by
  funext dep
  simp [join, emptyFlags]

theorem combine_assoc (a b c : Scan) : combine (combine a b) c = combine a (combine b c) := by
  cases a <;> cases b <;> cases c <;> simp [combine, join_assoc]

@[simp] theorem combine_empty_left (a : Scan) : combine (some emptyFlags) a = a := by
  cases a <;> simp [combine]

@[simp] theorem combine_empty_right (a : Scan) : combine a (some emptyFlags) = a := by
  cases a <;> simp [combine]

@[simp] theorem combine_incomplete_left (a : Scan) : combine none a = none := by
  cases a <;> rfl

@[simp] theorem combine_incomplete_right (a : Scan) : combine a none = none := by
  cases a <;> rfl

theorem scan_append (left right : List Token) :
    scan (left ++ right) = combine (scan left) (scan right) := by
  induction left with
  | nil => simp [scan]
  | cons token rest ih => simp [scan, ih, combine_assoc]

theorem inert_separator_preserves_summary (left right : List Token) :
    scan (left ++ .separator :: right) = scan (left ++ right) := by
  simp [scan_append, scan, tokenScan]

theorem unresolved_output_is_not_exact_zero : scan [.unresolved] ≠ scan [] := by
  simp [scan, tokenScan, combine]

theorem unresolved_anywhere_is_incomplete (left right : List Token) :
    scan (left ++ .unresolved :: right) = none := by
  simp [scan_append, scan, tokenScan]

abbrev Boundary := List Token → List Token → Bool

def emit (boundary : Boundary) (out piece : List Token) : List Token :=
  if piece.isEmpty then out
  else if out.isEmpty then piece
  else if boundary out piece then out ++ .separator :: piece
  else out ++ piece

theorem emit_scan (boundary : Boundary) (out piece : List Token) :
    scan (emit boundary out piece) = combine (scan out) (scan piece) := by
  cases piece with
  | nil => simp [emit, scan]
  | cons token rest =>
    cases out with
    | nil => simp [emit, scan]
    | cons previous before =>
      simp only [emit, List.isEmpty_cons, Bool.false_eq_true, ↓reduceIte]
      split
      · exact (inert_separator_preserves_summary (previous :: before) (token :: rest)).trans
          (scan_append (previous :: before) (token :: rest))
      · exact scan_append (previous :: before) (token :: rest)

def eraseSeparators : List Token → List Token
  | [] => []
  | .separator :: rest => eraseSeparators rest
  | token :: rest => token :: eraseSeparators rest

theorem erase_separators_preserves_summary (tokens : List Token) :
    scan (eraseSeparators tokens) = scan tokens := by
  induction tokens with
  | nil => rfl
  | cons token rest ih =>
    cases token <;> simp [eraseSeparators, scan, tokenScan, ih]

theorem equal_tokens_modulo_separators (left right : List Token)
    (tokens_eq : eraseSeparators left = eraseSeparators right) : scan left = scan right := by
  rw [← erase_separators_preserves_summary left, ← erase_separators_preserves_summary right, tokens_eq]

theorem missing_lexical_boundary_can_create_dependency :
    (scan [.inert 1, .inert 2]).map (fun flags => flags .font) = some false ∧
    (scan [.dimension .font]).map (fun flags => flags .font) = some true := by
  decide

end ResolvedDependencies
