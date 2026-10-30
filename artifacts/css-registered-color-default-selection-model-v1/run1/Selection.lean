namespace SelectedColor

inductive Token where
  | light | dark | red | canvas | invalid
  deriving DecidableEq, Repr

inductive Clause where
  | ident | color
  deriving DecidableEq, Repr

inductive Value where
  | ident (token : Token) | absolute | system
  deriving DecidableEq, Repr

def parse : Clause → Token → Option Value
  | .ident, .invalid => none
  | .ident, t => some (.ident t)
  | .color, .red => some .absolute
  | .color, .canvas => some .system
  | .color, _ => none

def select : List Clause → Token → Option Value
  | [], _ => none
  | c :: cs, t => match parse c t with
    | some v => some v
    | none => select cs t

def depends : Option Value → Bool
  | some .system => true
  | _ => false

def possibleColor (cs : List Clause) : Bool := cs.contains .color

def primaryOrFallback (primary fallback : Token) (valid : Bool) : Token :=
  if valid then primary else fallback

inductive Node where
  | custom | scheme
  deriving DecidableEq, Repr

def nodes : List Node := [.custom, .scheme]

def edge (sinkReadsCustom customReadsScheme : Bool) : Node → Node → Bool
  | .scheme, .custom => sinkReadsCustom
  | .custom, .scheme => customReadsScheme
  | _, _ => false

def cycleOracle (edges : Node → Node → Bool) : Bool :=
  nodes.any fun a => edges a a || nodes.any fun b => edges a b && edges b a

def selectedCycle (cs : List Clause) (t : Token) (admitted : Bool) : Bool :=
  cycleOracle (edge admitted (depends (select cs t)))

def broadCycle (cs : List Clause) (admitted : Bool) : Bool :=
  cycleOracle (edge admitted (possibleColor cs))

theorem first_success (c : Clause) (cs : List Clause) (t : Token) (v : Value)
    (h : parse c t = some v) : select (c :: cs) t = some v := by
  simp [select, h]

theorem first_failure (c : Clause) (cs : List Clause) (t : Token)
    (h : parse c t = none) : select (c :: cs) t = select cs t := by
  simp [select, h]

theorem independent_cycle_oracle (sink dependency : Bool) :
    cycleOracle (edge sink dependency) = (sink && dependency) := by
  cases sink <;> cases dependency <;> decide

theorem no_self_edges (sink dependency : Bool) (n : Node) :
    edge sink dependency n n = false := by cases n <;> rfl

theorem selected_dependency_requires_color (cs : List Clause) (t : Token)
    (h : depends (select cs t) = true) : possibleColor cs = true := by
  induction cs with
  | nil => simp [select, depends] at h
  | cons c cs ih =>
    cases c <;> cases t <;> simp_all [select, parse, depends, possibleColor, List.contains_cons]

theorem identifiers_avoid_false_cycle :
    selectedCycle [.ident, .color] .light true = false ∧
    selectedCycle [.ident, .color] .dark true = false ∧
    broadCycle [.ident, .color] true = true := by decide

theorem reversed_union_light_still_identifier :
    select [.color, .ident] .light = some (.ident .light) ∧
    selectedCycle [.color, .ident] .light true = false := by decide

theorem overlapping_clause_order :
    select [.ident, .color] .canvas = some (.ident .canvas) ∧
    select [.color, .ident] .canvas = some .system ∧
    selectedCycle [.ident, .color] .canvas true = false ∧
    selectedCycle [.color, .ident] .canvas true = true := by decide

theorem absolute_color_no_scheme_dependency :
    select [.color, .ident] .red = some .absolute ∧
    selectedCycle [.color, .ident] .red true = false := by decide

theorem genuine_system_color_cycle :
    selectedCycle [.color] .canvas true = true ∧
    selectedCycle [.color] .canvas false = false := by decide

theorem unused_fallback_not_selected (p f : Token) :
    primaryOrFallback p f true = p := by rfl

theorem invalid_primary_selects_fallback (p f : Token) :
    primaryOrFallback p f false = f := by rfl

theorem unused_fallback_admission_distinction :
    broadCycle [.ident, .color] false = false ∧
    broadCycle [.ident, .color] true = true ∧
    selectedCycle [.ident, .color] (primaryOrFallback .light .canvas true) true = false := by decide

theorem selected_fallback_can_change_dependency :
    selectedCycle [.color, .ident] (primaryOrFallback .light .canvas false) true = true ∧
    selectedCycle [.color, .ident] (primaryOrFallback .light .canvas true) true = false := by decide

theorem invalid_value_has_no_computation_edge :
    select [.ident, .color] .invalid = none ∧
    selectedCycle [.ident, .color] .invalid true = false := by decide

end SelectedColor
