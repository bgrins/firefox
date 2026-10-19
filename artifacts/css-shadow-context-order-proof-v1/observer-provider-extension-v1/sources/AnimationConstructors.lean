import ConstructedCoverage
import TransitionObservers
import DeclarationProvider
namespace ShadowOrder
variable {σ ω : Type}

inductive ConstructedAnimationValue where
 | longhand (property token : Nat)
 | custom (property : Nat) (value : Option Nat)
 deriving DecidableEq, Repr

def uncomputeConstructedAnimation : ConstructedAnimationValue → Declaration
 | .longhand property token => ⟨property,false,.value token⟩
 | .custom property (some token) => ⟨property,false,.value token⟩
 | .custom property none => ⟨property,false,.initial⟩

def fromAnimationValueMap (values : List ConstructedAnimationValue) : List Declaration × List Bool :=
 (values.map uncomputeConstructedAnimation,List.replicate values.length false)

theorem animation_constructor_lengths (values : List ConstructedAnimationValue) :
 (fromAnimationValueMap values).1.length = (fromAnimationValueMap values).2.length := by
 simp [fromAnimationValueMap]

theorem animation_constructor_no_important (values : List ConstructedAnimationValue) :
 anyImportantBits (fromAnimationValueMap values).2 = false := by
 simp [fromAnimationValueMap,anyImportantBits]

theorem animation_constructor_normal_only (values : List ConstructedAnimationValue) :
 ∀ declaration ∈ (fromAnimationValueMap values).1, declaration.important = false := by
 intro declaration member
 rcases List.mem_map.mp member with ⟨value,present,rfl⟩
 cases value with
 | longhand property token => rfl
 | custom property value => cases value <;> rfl

theorem animation_constructor_no_rollback (values : List ConstructedAnimationValue) :
 ∀ declaration ∈ (fromAnimationValueMap values).1,
 declaration.action ≠ .revertRule ∧ declaration.action ≠ .revertLayer ∧
 declaration.action ≠ .revertOrigin := by
 intro declaration member
 rcases List.mem_map.mp member with ⟨value,present,rfl⟩
 cases value with
 | longhand property token => simp [uncomputeConstructedAnimation]
 | custom property value => cases value <;> simp [uncomputeConstructedAnimation]

theorem animation_zip_provider_consistency (values : List ConstructedAnimationValue) :
 (rawImportance (fromAnimationValueMap values).1 (fromAnimationValueMap values).2).any Prod.snd = false := by
 rw [← provider_importance_consistent _ _ (animation_constructor_lengths values)]
 exact animation_constructor_no_important values

def animationObservedPrefix (identity : ι) (annotation : ConstructedAnimationValue → β)
 (values : List ConstructedAnimationValue) : List (AnnotatedOccurrence ι Action β) :=
 values.map fun value =>
   ⟨⟨identity,.effect (uncomputeConstructedAnimation value).action⟩,annotation value⟩

theorem animation_observed_prefix_no_rule (identity : ι)
 (annotation : ConstructedAnimationValue → β) (values : List ConstructedAnimationValue) :
 ∀ entry ∈ animationObservedPrefix identity annotation values, entry.event.action ≠ .rule := by
 intro entry member
 rcases List.mem_map.mp member with ⟨value,present,rfl⟩
 simp

theorem constructed_transition_observer_refinement [DecidableEq ι] [DecidableEq κ]
 (key : ι → κ) (important normal : κ → List (AliasDecision Action × β))
 (observe : ω → β → ω) (eligible : σ → κ → Bool) (apply : σ → κ → Action → σ)
 (disables : ∀ state identity value, eligible (apply state identity value) identity = false)
 (monotone : ∀ state identity value other,
   eligible state other = false → eligible (apply state identity value) other = false)
 (identity : ι) (annotation : ConstructedAnimationValue → β) (values : List ConstructedAnimationValue)
 (is ns : List ι)
 (coverage : ∀ occurrence ∈ ns,
   AliasDecision.rule ∈ (important (key occurrence)).map Prod.fst → occurrence ∈ is)
 (observation : ω) (state : σ) :
 observedDeletionReference observe (fun s event => eligible s (key event.identity))
   (fun s event value => apply s (key event.identity) value)
   (animationObservedPrefix identity annotation values ++
    (annotatedPhase key important is ++ annotatedPhase key normal ns)) observation state =
 preObservedExecution observe (fun s event => eligible s event.identity)
   (fun s event value => apply s event.identity value)
   ((animationObservedPrefix identity annotation values).map (mapAnnotatedKey key) ++
    (annotatedPhase (fun x => x) important (is.map key) ++
     annotatedPhase (fun x => x) normal (ns.map key))) [] observation state :=
 transition_prefixed_observer_refinement key important normal observe eligible apply disables monotone
   (animationObservedPrefix identity annotation values)
   (animation_observed_prefix_no_rule identity annotation values) is ns coverage observation state

#print axioms animation_constructor_lengths
#print axioms animation_constructor_no_important
#print axioms animation_constructor_normal_only
#print axioms animation_constructor_no_rollback
#print axioms animation_zip_provider_consistency
#print axioms constructed_transition_observer_refinement
end ShadowOrder
