import Names
namespace ComputedNames.Examples
open CssSemantics
inductive Token where
  | name : String → Token
  | text : String → Token
  deriving DecidableEq, Repr

def parse : List Token → Option String
  | [.name name] => some name
  | _ => none

def adapter : NameAdapter Token where
  parse := parse
  accepts := fun tokens name => tokens = [.name name]
  exact := by
    intro tokens name
    cases tokens with
    | nil => simp [parse]
    | cons head tail =>
      cases head <;> cases tail <;> simp [parse]

def lit (text : String) : Expr Token := .static (.literal [.text text])
def name (text : String) : Expr Token := .static (.literal [.name text])
def ref (text : String) : Expr Token := .static (.reference text)
def dyn (fallback : Expr Token) : Expr Token := .fallback (ref "--name") fallback
def complete (_ : String) (value : Option (List Token)) := value
def base (_ : String) : Option (List Token) := none
def run (entries : List (String × Expr Token)) := resolve parse complete base entries [] [] "--x"

def valid := [("--name", name "--ok"), ("--ok", lit "10px"),
  ("--x", dyn (ref "--x"))]
def missing := [("--name", name "--absent"), ("--x", dyn (lit "20px"))]
def invalid := [("--name", lit "10px"), ("--x", dyn (lit "20px"))]
def emptyName := [("--name", .static (.literal [])), ("--x", dyn (lit "20px"))]
def selfCycle := [("--name", name "--x"), ("--x", dyn (lit "20px"))]
def nameCycle := [("--name", ref "--x"), ("--x", dyn (lit "20px"))]
def emptyValue := [("--name", name "--ok"), ("--ok", .static (.literal [])),
  ("--x", dyn (ref "--x"))]

theorem valid_result : run valid = (some [.text "10px"], []) := by decide +kernel
theorem missing_result : run missing = (some [.text "20px"], []) := by decide +kernel
theorem invalid_result : run invalid = (some [.text "20px"], []) := by decide +kernel
theorem empty_name_result : run emptyName = (some [.text "20px"], []) := by decide +kernel
theorem self_cycle_result : run selfCycle = (none, []) := by decide +kernel
theorem name_cycle_result : run nameCycle = (none, []) := by decide +kernel
theorem empty_value_result : run emptyValue = (some [], []) := by decide +kernel

def inner := evaluate parse
  (fun marked target => resolve parse complete base [("--name", ref "--x")]
    ["--x"] marked target) [] (dyn (lit "20px"))
theorem inner_mark_survives : inner = (some [.text "20px"], ["--x"]) := by decide +kernel

def afterFailure := evaluate parse
  (fun state target => ((none : Option (List Token)), state ++ [target]))
  [] (.append (.reference (lit "bad")) (ref "--later"))
theorem later_substitution_runs : afterFailure = (none, ["--later"]) := by decide +kernel
def multipleName := [("--name", .static (.literal [.name "--ok", .name "--other"])),
  ("--ok", lit "10px"), ("--x", dyn (lit "20px"))]
theorem multiple_name_result : run multipleName = (some [.text "20px"], []) := by decide +kernel

def missingName := [("--x", dyn (lit "20px"))]
theorem missing_name_result : run missingName = (some [.text "20px"], []) := by decide +kernel

def nestedName := [("--first", name "--name"), ("--name", name "--ok"),
  ("--ok", lit "10px"), ("--x", .reference (.reference (ref "--first")))]
theorem nested_name_result : run nestedName = (some [.text "10px"], []) := by decide +kernel
end ComputedNames.Examples
