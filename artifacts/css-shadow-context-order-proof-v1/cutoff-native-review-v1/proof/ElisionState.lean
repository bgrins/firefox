import Base
import RulePath
import RollbackCounterexample
namespace ShadowOrder
structure OneState where
 seen : Bool
 cutoff : Option (Priority × RevertKind)
 selected : Option Action
 deriving DecidableEq, Repr

structure EvaluatedDeclaration where
 priority : Priority
 included : Bool
 action : Action
 deriving DecidableEq, Repr

def accepted (state : OneState) (d : EvaluatedDeclaration) : Bool :=
 !state.seen && d.included &&
 (state.cutoff.map fun c => nativeAllows c.1 d.priority c.2).getD true

def actionStep (state : OneState) (d : EvaluatedDeclaration) : OneState :=
 match d.action with
 | .revertOrigin => {state with cutoff := some (d.priority,.origin)}
 | .revertLayer => {state with cutoff := some (d.priority,.layer)}
 | .revertRule => {state with cutoff := some (d.priority,.rule)}
 | _ => {state with seen := true, selected := some d.action}

def declarationStep (state : OneState) (d : EvaluatedDeclaration) : OneState :=
 if accepted state d then actionStep state d else state

theorem native_allows_self (p : Priority) :
 nativeAllows p p .origin = false ∧ nativeAllows p p .layer = false ∧
 nativeAllows p p .rule = true := by simp [nativeAllows]

theorem declaration_step_idempotent (state : OneState) (d : EvaluatedDeclaration) :
 declarationStep (declarationStep state d) d = declarationStep state d := by
 by_cases h : accepted state d = true
 · simp only [declarationStep,h,↓reduceIte]
   cases ha : d.action <;>
     simp [actionStep,ha,accepted,nativeAllows]
 · simp [declarationStep,h]

theorem declaration_duplicate_elision (ds : List EvaluatedDeclaration) (state : OneState) :
 runActions declarationStep (dedupAdjacent ds) state = runActions declarationStep ds state :=
 duplicate_elision declarationStep declaration_step_idempotent ds state

#print axioms declaration_step_idempotent
#print axioms declaration_duplicate_elision
end ShadowOrder
