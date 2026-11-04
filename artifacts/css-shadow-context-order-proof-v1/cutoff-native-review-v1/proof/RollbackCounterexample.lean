import Priority
namespace ShadowOrder
inductive RevertKind where
 | origin | layer | rule
 deriving DecidableEq, Repr

def simpleOrigin (origin : Nat) : Nat := if origin = 0 then 0 else if origin = 1 then 1 else 2

def unimportantPriority (p : Priority) : Priority := {p with important := false}

def nativeAllows (cut candidate : Priority) (kind : RevertKind) : Bool :=
 match kind with
 | .origin => simpleOrigin candidate.origin < simpleOrigin cut.origin
 | .layer => priorityKey (unimportantPriority candidate) < priorityKey (unimportantPriority cut)
 | .rule => true

def inlineCut : Priority := ⟨3,true,0,65535,0⟩
def localRuleCut : Priority := ⟨3,true,0,65534,0⟩
def outerNormal : Priority := ⟨3,false,1,65534,0⟩
def localNormal : Priority := ⟨3,false,0,65534,0⟩
def animation : Priority := ⟨6,false,0,65534,0⟩

theorem witness_priorities_admitted :
 inlineCut.admitted ∧ localRuleCut.admitted ∧ outerNormal.admitted ∧
 localNormal.admitted ∧ animation.admitted := by
 unfold Priority.admitted inlineCut localRuleCut outerNormal localNormal animation maxOrder
 decide

theorem witness_descending :
 priorityKey inlineCut > priorityKey localRuleCut ∧
 priorityKey localRuleCut > priorityKey animation ∧
 priorityKey animation > priorityKey outerNormal ∧
 priorityKey outerNormal > priorityKey localNormal := by decide

theorem inline_cutoff_excludes_outer :
 nativeAllows inlineCut outerNormal .layer = false ∧
 nativeAllows inlineCut localNormal .layer = true := by decide

theorem replacement_resurrects_animation :
 nativeAllows inlineCut localRuleCut .layer = true ∧
 nativeAllows inlineCut animation .layer = false ∧
 nativeAllows localRuleCut animation .rule = true := by decide

def specInlineAllows (candidate : Priority) : Bool :=
 !(candidate.origin == 3 && candidate.layer == 65535) && candidate.origin != 6

theorem failed_inline_reference_obligation :
 nativeAllows inlineCut outerNormal .layer ≠ specInlineAllows outerNormal := by decide

theorem failed_animation_reference_obligation :
 nativeAllows localRuleCut animation .rule ≠ specInlineAllows animation := by decide

#print axioms witness_priorities_admitted
#print axioms witness_descending
#print axioms failed_inline_reference_obligation
#print axioms failed_animation_reference_obligation
end ShadowOrder
