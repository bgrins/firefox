import Dispatch
import TransitionPartition
import ElisionState
namespace ShadowOrder

def witnessRule (tree source layer : Nat) (important : Bool) (action : Action) : Rule :=
 ⟨tree,source,layer,0,65535,source,0,[⟨0,important,action⟩]⟩

def rawWitness (outer intervening animated : Bool) : RawInput :=
 {limit := maxOrder, parts := [0],
  outerContexts := if outer then
    [⟨1,true,[⟨0,witnessRule 1 3 65534 false (.value 37)⟩],[]⟩] else [],
  assignedSlots := [], ownHostRules := [], ua := [], user := [], presHints := [],
  sameTree := [⟨witnessRule 0 0 65534 false (.value 5),3,0⟩] ++
    if intervening then [⟨witnessRule 0 1 65534 true .revertRule,3,0⟩] else [],
  document := [], inlineRules := [⟨witnessRule 0 2 65535 true .revertLayer,3,0⟩],
  animations := if animated then [⟨witnessRule 0 4 65534 false (.value 59),6,0⟩] else [],
  defaultOnly := false, authorEnabled := true}

def entryPriority (entry : Entry) (important : Bool) : Priority :=
 ⟨entry.origin,important,entry.order,entry.rule.layer,entry.rule.flags⟩

def witnessImportantSort (entries : List Entry) : List Entry :=
 localSort (fun e => (priorityKey (entryPriority e true)).toNat) entries

def witnessNativeTrace (raw : RawInput) : List EvaluatedDeclaration :=
 let path := allPathItems witnessImportantSort
   (treePartition (nativeCollected raw) emptyPartition)
 path.reverse.flatMap fun node =>
   (node.1.rule.declarations.reverse.filter fun declaration => declaration.important == node.2).map
     fun declaration => ⟨entryPriority node.1 node.2,true,declaration.action⟩

def witnessNativeResult (raw : RawInput) : Option Action :=
 (runActions declarationStep (witnessNativeTrace raw) ⟨false,none,none⟩).selected

structure ReferenceDeclaration where
 source : Nat
 origin : Nat
 physicalContext : Int
 layer : Nat
 important : Bool
 action : Action
 deriving DecidableEq, Repr

def witnessReferenceCandidates (raw : RawInput) : List ReferenceDeclaration :=
 (referenceCollected raw).flatMap fun entry => entry.rule.declarations.map fun declaration =>
   ⟨entry.rule.source,entry.origin,entry.rule.tree,entry.rule.layer,
    declaration.important,declaration.action⟩

def referencePrecedence (d : ReferenceDeclaration) : Int :=
 let originRank := if d.origin = 7 then 12 else
   if d.important then 11-(d.origin : Int) else d.origin
 let contextRank := if d.important then -d.physicalContext else d.physicalContext
 let layerRank := if d.important && d.layer != 65535 then 65534-d.layer else d.layer
 originRank * 18446744073709551616 + contextRank * 65536 + layerRank

def referenceSurvives (removed candidate : ReferenceDeclaration) : Bool :=
 match removed.action with
 | .revertRule => candidate.source != removed.source
 | .revertOrigin => candidate.origin < removed.origin
 | .revertLayer =>
   if removed.important && removed.layer == 65535 then
     !(candidate.origin == 3 && candidate.layer == 65535) && candidate.origin != 6
   else
     candidate.origin < removed.origin ||
     (candidate.origin == removed.origin &&
       (candidate.physicalContext < removed.physicalContext ||
       (candidate.physicalContext == removed.physicalContext && candidate.layer < removed.layer)))
 | _ => true

def referenceSelect : Nat → List ReferenceDeclaration → Option Action
 | 0, _ => none
 | _, [] => none
 | fuel+1, declaration::rest =>
   match declaration.action with
   | .revertOrigin | .revertLayer | .revertRule =>
     referenceSelect fuel (rest.filter (referenceSurvives declaration))
   | action => some action

def witnessReferenceResult (raw : RawInput) : Option Action :=
 let declarations := witnessReferenceCandidates raw
 referenceSelect declarations.length
   (localSort (fun d => (referencePrecedence d).toNat) declarations).reverse

def witnessInputChecks (raw : RawInput) : Bool :=
 raw.limit == maxOrder && raw.assignedSlots.length < raw.limit &&
 raw.outerContexts.length ≤ raw.limit &&
 let surrounding := raw.ua ++ raw.user ++ raw.presHints ++ raw.sameTree ++ raw.document ++
   raw.inlineRules ++ raw.animations
 let rules := surrounding.map Entry.rule ++ raw.ownHostRules ++
   raw.assignedSlots.flatMap InnerContext.rules ++
   raw.outerContexts.flatMap (fun context => context.rules.map PartRule.rule)
 surrounding.all (fun e => e.origin < 8) &&
 rules.all (fun rule => rule.layer ≤ 65535 && rule.sourceOrder < 16777216 &&
   rule.declarations.length == 1 && rule.flags == 0)

theorem raw_inline_witness_checks : witnessInputChecks (rawWitness true false false) = true := by decide
theorem raw_animation_witness_checks : witnessInputChecks (rawWitness false true true) = true := by decide

theorem raw_inline_counterexample :
 witnessNativeResult (rawWitness true false false) = some (.value 5) ∧
 witnessReferenceResult (rawWitness true false false) = some (.value 37) := by decide

theorem raw_animation_counterexample :
 witnessNativeResult (rawWitness false true true) = some (.value 59) ∧
 witnessReferenceResult (rawWitness false true true) = some (.value 5) := by decide

theorem raw_composition_not_universally_equal :
 ¬ ∀ raw, witnessInputChecks raw = true → witnessNativeResult raw = witnessReferenceResult raw := by
 intro h
 have claimed := h (rawWitness true false false) raw_inline_witness_checks
 rw [raw_inline_counterexample.1,raw_inline_counterexample.2] at claimed
 contradiction

#print axioms raw_inline_counterexample
#print axioms raw_animation_counterexample
#print axioms raw_composition_not_universally_equal
end ShadowOrder
