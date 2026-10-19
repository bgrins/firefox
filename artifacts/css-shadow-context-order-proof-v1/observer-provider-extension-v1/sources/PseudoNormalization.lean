import Dispatch
namespace ShadowOrder
structure PseudoNode where
 implemented : Option Nat
 originating : Option Nat
 deriving DecidableEq, Repr

def nativePseudo (nodes : List PseudoNode) : Nat → Nat → List Nat → Option (Nat × List Nat)
 | 0, _, _ => none
 | fuel+1, current, accumulated => do
   let node ← nodes[current]?
   match node.implemented with
   | none => return (current,accumulated)
   | some pseudo =>
     let accumulated := accumulated ++ [pseudo]
     match node.originating with
     | none => return (current,accumulated)
     | some parent => nativePseudo nodes fuel parent accumulated

def referencePseudo (nodes : List PseudoNode) : Nat → Nat → Option (Nat × List Nat)
 | 0, _ => none
 | fuel+1, current => do
   let node ← nodes[current]?
   match node.implemented with
   | none => return (current,[])
   | some pseudo =>
     match node.originating with
     | none => return (current,[pseudo])
     | some parent =>
       let result ← referencePseudo nodes fuel parent
       return (result.1,pseudo::result.2)

theorem pseudo_normalization (nodes : List PseudoNode) (fuel current : Nat)
 (accumulated : List Nat) :
 nativePseudo nodes fuel current accumulated =
 (referencePseudo nodes fuel current).map (fun result => (result.1,accumulated++result.2)) := by
 induction fuel generalizing current accumulated with
 | zero => rfl
 | succ fuel ih =>
   simp only [nativePseudo,referencePseudo]
   cases hn : nodes[current]? with
   | none => simp [hn]
   | some node =>
     cases hi : node.implemented with
     | none => simp [hn,hi]
     | some pseudo =>
       cases hp : node.originating with
       | none => simp [hn,hi,hp]
       | some parent =>
         simp only [hn,hi,hp,Option.bind_some,ih]
         cases hr : referencePseudo nodes fuel parent <;> simp [hi,hp,hr,List.append_assoc]

def nativeNormalizedDispatch (nodes : List PseudoNode) (current : Nat)
 (explicitPseudo : Option Nat) (providers : Nat → List Nat → RawInput) : Option (List Entry) := do
 let normalized ← nativePseudo nodes (nodes.length+1) current explicitPseudo.toList
 return nativeCollected (providers normalized.1 normalized.2)

def referenceNormalizedDispatch (nodes : List PseudoNode) (current : Nat)
 (explicitPseudo : Option Nat) (providers : Nat → List Nat → RawInput) : Option (List Entry) := do
 let normalized ← referencePseudo nodes (nodes.length+1) current
 return referenceCollected (providers normalized.1 (explicitPseudo.toList++normalized.2))

theorem normalized_dispatch (nodes : List PseudoNode) (current : Nat)
 (explicitPseudo : Option Nat) (providers : Nat → List Nat → RawInput) :
 nativeNormalizedDispatch nodes current explicitPseudo providers =
 referenceNormalizedDispatch nodes current explicitPseudo providers := by
 simp only [nativeNormalizedDispatch,referenceNormalizedDispatch,pseudo_normalization]
 cases h : referencePseudo nodes (nodes.length+1) current <;> simp [h,raw_dispatch_refinement]

#print axioms pseudo_normalization
#print axioms normalized_dispatch
end ShadowOrder
