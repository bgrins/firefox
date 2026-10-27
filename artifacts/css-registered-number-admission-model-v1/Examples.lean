import Admission
namespace RegisteredNumber.Examples
open RegisteredNumber

def env : Nat → Provider
  | 0 => .ready (.number 5)
  | 1 => .pending
  | 2 => .ready (.length .em 1)
  | _ => .invalid

def invalidLength : Expr := .value (.length .em 1)
def unused : Expr := .reference 0 invalidLength
def ratio : Raw := .quotient (.length .em 1) (.length .px 1)

example : plan env unused = .ready (.number 5) false := by decide +kernel
example : plan env invalidLength = .invalid := by decide +kernel
example : plan env (.reference 3 invalidLength) = .invalid := by decide +kernel
example : plan env (.reference 2 (.value (.number 7))) = .invalid := by decide +kernel
example : plan env (.reference 1 (.value (.number 7))) = .demand 1 := by decide +kernel
example : plan env (.value ratio) = .ready ratio true := by decide +kernel
example : plan env (.reference 0 (.value ratio)) = .ready (.number 5) false := by decide +kernel
example : plan env (.reference 3 (.value ratio)) = .ready ratio true := by decide +kernel
example : eval 20 ratio = 20 ∧ eval 30 ratio = 30 := by decide +kernel
example : planRaw (.sum (.number 2) ratio) = .ready (.sum (.number 2) ratio) true := by decide +kernel
example : planRaw (.sum (.number 2) (.length .em 1)) = .invalid := by decide +kernel
example : planRaw (.quotient (.number 1) (.length .px 1)) = .invalid := by decide +kernel
example : (withCyclePolicy (fun _ => .invalidate) (.ready ratio true)).1 =
    (withCyclePolicy (fun _ => .retain) (.ready ratio true)).1 := by decide +kernel
example : (withCyclePolicy (fun _ => .invalidate) (.ready ratio true)).2 ≠
    (withCyclePolicy (fun _ => .retain) (.ready ratio true)).2 := by decide +kernel
end RegisteredNumber.Examples
