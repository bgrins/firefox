import PhasePruning
namespace ShadowOrder
variable {σ : Type}

def phaseEvents (key : ι → κ) (actions : κ → List (AliasDecision α))
 (occurrences : List ι) :=
 halfStream (occurrences.map fun occurrence => (occurrence,actions (key occurrence)))

noncomputable def keepNormal (important : κ → List (AliasDecision α)) (key : κ) : Bool :=
 @decide (AliasDecision.rule ∉ important key) (Classical.propDecidable _)

theorem phase_event_membership (key : ι → κ) (actions : κ → List (AliasDecision α))
 (occurrences : List ι) (event : OccurrenceEvent ι α) :
 event ∈ phaseEvents key actions occurrences ↔
 event.identity ∈ occurrences ∧ event.action ∈ actions (key event.identity) := by
 simp only [phaseEvents,halfStream,List.mem_flatMap,List.mem_map,blockHalfEvents]
 constructor
 · rintro ⟨half,⟨occurrence,member,rfl⟩,action,inHalf,same⟩
   cases same
   exact ⟨member,inHalf⟩
 · rintro ⟨member,inHalf⟩
   exact ⟨_,⟨event.identity,member,rfl⟩,event.action,inHalf,by cases event; rfl⟩

theorem phase_filter (key : ι → κ) (actions : κ → List (AliasDecision α))
 (keep : κ → Bool) (occurrences : List ι) :
 (phaseEvents key actions occurrences).filter (fun event => keep (key event.identity)) =
 phaseEvents key actions (occurrences.filter fun occurrence => keep (key occurrence)) := by
 induction occurrences with
 | nil => rfl
 | cons occurrence rest ih =>
   simp only [phaseEvents,halfStream,List.map_cons,List.flatMap_cons,List.filter_append]
   have uniform : (blockHalfEvents occurrence (actions (key occurrence))).filter
     (fun event => keep (key event.identity)) =
     if keep (key occurrence) then blockHalfEvents occurrence (actions (key occurrence)) else [] := by
     generalize actions (key occurrence) = entries
     induction entries with
     | nil => simp [blockHalfEvents]
     | cons action rest ih =>
       cases value : keep (key occurrence) <;> simp_all [blockHalfEvents]
   rw [uniform]
   cases value : keep (key occurrence) <;>
     simpa [value,phaseEvents,halfStream] using ih

theorem normal_phase_reduction [DecidableEq ι]
 (key : ι → κ) (important normal : κ → List (AliasDecision α))
 (eligible : σ → κ → Bool) (apply : σ → κ → α → σ)
 (monotone : ∀ state identity value other,
   eligible state other = false → eligible (apply state identity value) other = false)
 (is ns : List ι) (coverage : ∀ occurrence ∈ ns, AliasDecision.rule ∈ important (key occurrence) → occurrence ∈ is) (state : σ) :
 let afterImportant := occurrenceStateExecution (fun s occurrence => eligible s (key occurrence))
   (fun s event value => apply s (key event.identity) value) (phaseEvents key important is) ([],state)
 occurrenceSetExecution (fun s event => eligible s (key event.identity))
   (fun s event value => apply s (key event.identity) value)
   (phaseEvents key normal ns) afterImportant.1 afterImportant.2 =
 occurrenceSetExecution (fun s event => eligible s (key event.identity))
   (fun s event value => apply s (key event.identity) value)
   (phaseEvents key normal (ns.filter fun occurrence => keepNormal important (key occurrence)))
   [] afterImportant.2 := by
 classical
 dsimp only
 let afterImportant := occurrenceStateExecution (fun s occurrence => eligible s (key occurrence))
   (fun s event value => apply s (key event.identity) value) (phaseEvents key important is) ([],state)
 have blocked : ∀ event ∈ phaseEvents key normal ns,
   keepNormal important (key event.identity) = false →
   occurrenceBlocked (fun s occurrence => eligible s (key occurrence)) afterImportant event.identity := by
   intro event present removed
   have member := (phase_event_membership key normal ns event).mp present
   have rule : AliasDecision.rule ∈ important (key event.identity) := by
     simpa [keepNormal] using removed
   apply encountered_rule_blocks (event := ⟨event.identity,.rule⟩)
   · intro s e value other disabled
     exact monotone s (key e.identity) value (key other) disabled
   · exact (phase_event_membership key important is _).mpr ⟨coverage _ member.1 rule,rule⟩
   · rfl
 have pruning := congrArg Prod.snd (prune_blocked_events
   (fun s occurrence => eligible s (key occurrence))
   (fun s event value => apply s (key event.identity) value)
   (by intro s e value other disabled; exact monotone s (key e.identity) value (key other) disabled)
   (fun occurrence => keepNormal important (key occurrence)) (phaseEvents key normal ns)
   afterImportant blocked)
 rw [occurrence_state_projection _ _ (phaseEvents key normal ns) afterImportant,
   occurrence_state_projection _ _ ((phaseEvents key normal ns).filter _) afterImportant,
   phase_filter] at pruning
 rw [pruning]
 apply exclusion_membership_local
 intro event member
 simp only [List.not_mem_nil,iff_false]
 intro banned
 have origin := fresh_exclusion_origin
   (fun s occurrence => eligible s (key occurrence))
   (fun s event value => apply s (key event.identity) value)
   (phaseEvents key important is) ([],state) event.identity banned
 rcases origin with impossible | ⟨earlier,present,same,rule⟩
 · exact List.not_mem_nil impossible
 · have earlierMember := (phase_event_membership key important is earlier).mp present
   have normalMember := (phase_event_membership key normal _ event).mp member
   have kept := (List.mem_filter.mp normalMember.1).2
   have noRule : AliasDecision.rule ∉ important (key event.identity) := by
     simpa [keepNormal] using kept
   apply noRule
   simpa [same,rule] using earlierMember.2

def twoPhaseExecution [DecidableEq ι]
 (key : ι → κ) (important normal : κ → List (AliasDecision α))
 (eligible : σ → κ → Bool) (apply : σ → κ → α → σ)
 (is ns : List ι) (state : σ) : σ :=
 (occurrenceStateExecution (fun s occurrence => eligible s (key occurrence))
   (fun s event value => apply s (key event.identity) value)
   (phaseEvents key important is ++ phaseEvents key normal ns) ([],state)).2

theorem two_phase_reduced [DecidableEq ι]
 (key : ι → κ) (important normal : κ → List (AliasDecision α))
 (eligible : σ → κ → Bool) (apply : σ → κ → α → σ)
 (monotone : ∀ state identity value other,
   eligible state other = false → eligible (apply state identity value) other = false)
 (is ns : List ι) (coverage : ∀ occurrence ∈ ns, AliasDecision.rule ∈ important (key occurrence) → occurrence ∈ is) (state : σ) :
 twoPhaseExecution key important normal eligible apply is ns state =
 occurrenceSetExecution (fun s event => eligible s (key event.identity))
   (fun s event value => apply s (key event.identity) value)
   (phaseEvents key normal (ns.filter fun occurrence => keepNormal important (key occurrence))) []
   (occurrenceSetExecution (fun s event => eligible s (key event.identity))
     (fun s event value => apply s (key event.identity) value) (phaseEvents key important is) [] state) := by
 unfold twoPhaseExecution
 rw [occurrence_state_append,occurrence_state_projection]
 have reduced := normal_phase_reduction key important normal eligible apply monotone is ns coverage state
 simpa only [occurrence_state_projection] using reduced

theorem filter_occurrences_map (key : ι → κ) (keep : κ → Bool) (occurrences : List ι) :
 (occurrences.map key).filter keep =
 (occurrences.filter fun occurrence => keep (key occurrence)).map key := by
 induction occurrences with
 | nil => rfl
 | cons occurrence rest ih =>
   cases value : keep (key occurrence) <;> simp [value,ih]

theorem two_phase_occurrence_quotient [DecidableEq ι] [DecidableEq κ]
 (key : ι → κ) (important normal : κ → List (AliasDecision α))
 (eligible : σ → κ → Bool) (apply : σ → κ → α → σ)
 (disables : ∀ state identity value, eligible (apply state identity value) identity = false)
 (monotone : ∀ state identity value other,
   eligible state other = false → eligible (apply state identity value) other = false)
 (is ns : List ι) (coverage : ∀ occurrence ∈ ns, AliasDecision.rule ∈ important (key occurrence) → occurrence ∈ is) (state : σ) :
 twoPhaseExecution key important normal eligible apply is ns state =
 twoPhaseExecution (fun x => x) important normal eligible apply (is.map key) (ns.map key) state := by
 have mappedCoverage : ∀ identity ∈ ns.map key, AliasDecision.rule ∈ important identity →
   identity ∈ is.map key := by
   intro identity member rule
   rcases List.mem_map.mp member with ⟨occurrence,present,rfl⟩
   exact List.mem_map.mpr ⟨occurrence,coverage _ present rule,rfl⟩
 rw [two_phase_reduced key important normal eligible apply monotone is ns coverage,
   two_phase_reduced (fun x => x) important normal eligible apply monotone _ _ mappedCoverage,
   filter_occurrences_map]
 have importantEqual := mixed_block_phase_quotient key important eligible apply disables is state
 change occurrenceSetExecution _ _ (phaseEvents key important is) [] state =
   occurrenceSetExecution _ _ (phaseEvents (fun x => x) important (is.map key)) [] state at importantEqual
 rw [importantEqual]
 exact mixed_block_phase_quotient key normal eligible apply disables
   (ns.filter fun occurrence => keepNormal important (key occurrence)) _

theorem source_projected_deletion_quotient [DecidableEq ι] [DecidableEq κ]
 (key : ι → κ) (blocks : κ → List (ProjectedDeclaration α))
 (physical : Nat → Nat) (property : Nat)
 (eligible : σ → κ → Bool) (apply : σ → κ → α → σ)
 (disables : ∀ state identity value, eligible (apply state identity value) identity = false)
 (monotone : ∀ state identity value other,
   eligible state other = false → eligible (apply state identity value) other = false)
 (is ns : List ι) (coverage : ∀ occurrence ∈ ns, AliasDecision.rule ∈ propertyHalf physical property true (blocks (key occurrence)) → occurrence ∈ is) (state : σ) :
 let important := fun identity => propertyHalf physical property true (blocks identity)
 let normal := fun identity => propertyHalf physical property false (blocks identity)
 occurrenceDeletionReference (fun s event => eligible s (key event.identity))
   (fun s event value => apply s (key event.identity) value)
   (phaseEvents key important is ++ phaseEvents key normal ns) state =
 twoPhaseExecution (fun x => x) important normal eligible apply (is.map key) (ns.map key) state := by
 dsimp only
 rw [← fresh_occurrence_deletion]
 have equality := two_phase_occurrence_quotient key
   (fun identity => propertyHalf physical property true (blocks identity))
   (fun identity => propertyHalf physical property false (blocks identity))
   eligible apply disables monotone is ns coverage state
 simpa only [twoPhaseExecution,occurrence_state_projection] using equality

#print axioms source_projected_deletion_quotient
#print axioms two_phase_occurrence_quotient
#print axioms phase_filter
#print axioms normal_phase_reduction
end ShadowOrder
