import PhaseCoverage
namespace ShadowOrder

structure ProjectedDeclaration (α : Type) where
 originalProperty : Nat
 important : Bool
 action : AliasDecision α

def propertyHalf (physical : Nat → Nat) (property : Nat) (important : Bool)
 (declarations : List (ProjectedDeclaration α)) : List (AliasDecision α) :=
 ((declarations.reverse).filter fun d =>
   decide (physical d.originalProperty = property) && (d.important == important)).map (·.action)

def sourceHalves (key : ι → κ) (blocks : κ → List (ProjectedDeclaration α))
 (physical : Nat → Nat) (property : Nat) (important : Bool) (occurrences : List ι) :=
 occurrences.map fun occurrence =>
   (occurrence, propertyHalf physical property important (blocks (key occurrence)))

theorem source_half_membership (key : ι → κ) (blocks : κ → List (ProjectedDeclaration α))
 (physical : Nat → Nat) (property : Nat) (important : Bool) (occurrences : List ι)
 (event : OccurrenceEvent ι α) :
 event ∈ halfStream (sourceHalves key blocks physical property important occurrences) ↔
 event.identity ∈ occurrences ∧
 event.action ∈ propertyHalf physical property important (blocks (key event.identity)) := by
 simp only [halfStream,sourceHalves,List.mem_flatMap,List.mem_map,blockHalfEvents]
 constructor
 · rintro ⟨half,⟨occurrence,member,rfl⟩,action,inHalf,same⟩
   cases same
   exact ⟨member,inHalf⟩
 · rintro ⟨member,inHalf⟩
   exact ⟨_,⟨event.identity,member,rfl⟩,event.action,inHalf,by cases event; rfl⟩

theorem coherent_alias_has_important_rule (key : ι → κ)
 (blocks : κ → List (ProjectedDeclaration α)) (physical : Nat → Nat) (property : Nat)
 (importantOccurrences normalOccurrences : List ι)
 (coverage : ∀ occurrence ∈ normalOccurrences, occurrence ∈ importantOccurrences)
 (normal : OccurrenceEvent ι α)
 (present : normal ∈ halfStream (sourceHalves key blocks physical property false normalOccurrences))
 (rule : AliasDecision.rule ∈ propertyHalf physical property true (blocks (key normal.identity))) :
 ∃ earlier ∈ halfStream (sourceHalves key blocks physical property true importantOccurrences),
   earlier.identity = normal.identity ∧ earlier.action = .rule := by
 have member := (source_half_membership key blocks physical property false normalOccurrences normal).mp present
 refine ⟨⟨normal.identity,.rule⟩,?_,rfl,rfl⟩
 exact (source_half_membership key blocks physical property true importantOccurrences _).mpr
   ⟨coverage normal.identity member.1,rule⟩

theorem source_derived_normal_alias_blocked [DecidableEq ι]
 (key : ι → κ) (blocks : κ → List (ProjectedDeclaration α))
 (physical : Nat → Nat) (property : Nat)
 (eligible : σ → κ → Bool) (apply : σ → κ → α → σ)
 (monotone : ∀ state identity value other,
   eligible state other = false → eligible (apply state identity value) other = false)
 (importantOccurrences normalOccurrences : List ι)
 (coverage : ∀ occurrence ∈ normalOccurrences, occurrence ∈ importantOccurrences)
 (state : List ι × σ) (normal : OccurrenceEvent ι α)
 (present : normal ∈ halfStream (sourceHalves key blocks physical property false normalOccurrences))
 (rule : AliasDecision.rule ∈ propertyHalf physical property true (blocks (key normal.identity))) :
 occurrenceBlocked (fun s occurrence => eligible s (key occurrence))
   (occurrenceStateExecution (fun s occurrence => eligible s (key occurrence))
     (fun s event value => apply s (key event.identity) value)
     (halfStream (sourceHalves key blocks physical property true importantOccurrences)) state)
   normal.identity := by
 rcases coherent_alias_has_important_rule key blocks physical property importantOccurrences
   normalOccurrences coverage normal present rule with ⟨earlier,member,same,rule⟩
 rw [← same]
 apply encountered_rule_blocks
 · intro s event value other disabled
   exact monotone s (key event.identity) value (key other) disabled
 · exact member
 · exact rule

theorem same_occurrence_list_coverage (key : ι → κ)
 (blocks : κ → List (ProjectedDeclaration α)) (physical : Nat → Nat) (property : Nat)
 (occurrences : List ι) (normal : OccurrenceEvent ι α)
 (present : normal ∈ halfStream (sourceHalves key blocks physical property false occurrences))
 (rule : AliasDecision.rule ∈ propertyHalf physical property true (blocks (key normal.identity))) :
 ∃ earlier ∈ halfStream (sourceHalves key blocks physical property true occurrences),
   earlier.identity = normal.identity ∧ earlier.action = .rule :=
 coherent_alias_has_important_rule key blocks physical property occurrences occurrences
   (by intro occurrence member; exact member) normal present rule

#print axioms source_half_membership
#print axioms coherent_alias_has_important_rule
#print axioms source_derived_normal_alias_blocked
#print axioms same_occurrence_list_coverage
end ShadowOrder
