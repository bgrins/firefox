import ImportantBucketSort
import TwoPhaseQuotient
namespace ShadowOrder

def projectedEntryDeclaration (declaration : Declaration) : ProjectedDeclaration Action :=
 ⟨declaration.property,declaration.important,
   match declaration.action with | .revertRule => .rule | other => .effect other⟩

def entryPropertyHalf (physical : Nat → Nat) (property : Nat) (important : Bool)
 (entry : Entry) :=
 propertyHalf physical property important (entry.rule.declarations.map projectedEntryDeclaration)

theorem important_projection_has_important_bit (physical : Nat → Nat) (property : Nat)
 (entry : Entry) (action : AliasDecision Action)
 (present : action ∈ entryPropertyHalf physical property true entry) :
 hasImportant entry = true := by
 unfold entryPropertyHalf propertyHalf at present
 rcases List.mem_map.mp present with ⟨projected,present,actionEq⟩
 have filtered := List.mem_filter.mp present
 have original := List.mem_reverse.mp filtered.1
 rcases List.mem_map.mp original with ⟨declaration,member,rfl⟩
 have bit : declaration.important = true := by
   have selection := filtered.2
   simp only [Bool.and_eq_true] at selection
   simpa [projectedEntryDeclaration] using selection.2
 exact List.any_eq_true.mpr ⟨declaration,member,bit⟩

def constructedImportant (sort : List Entry → List Entry) (entries : List Entry) : List Entry :=
 let buckets := (treePartition entries emptyPartition).buckets
 (sort buckets.author ++ sort buckets.user ++ sort buckets.ua).reverse

theorem constructed_important_covers_projected_rule
 (sort : List Entry → List Entry) (sortMembership : ∀ entries, (sort entries).Perm entries)
 (entries : List Entry) (entry : Entry) (member : entry ∈ entries)
 (physical : Nat → Nat) (property : Nat)
 (rule : AliasDecision.rule ∈ entryPropertyHalf physical property true entry)
 (origin : entry.origin = 3 ∨ entry.origin = 1 ∨ entry.origin = 0) :
 entry ∈ constructedImportant sort entries := by
 have bit := important_projection_has_important_bit physical property entry .rule rule
 have buckets := empty_tree_partition_important_buckets entries
 have author := congrArg Prod.fst buckets
 have user := congrArg (fun state => state.2.1) buckets
 have ua := congrArg (fun state => state.2.2) buckets
 simp only [importantBuckets] at author user ua
 simp only [constructedImportant,List.mem_reverse,List.mem_append,author,user,ua]
 rcases origin with authorOrigin | userOrigin | uaOrigin
 · exact Or.inl (Or.inl ((sortMembership _).mem_iff.mpr
     (by simp [importantOrigin,member,bit,authorOrigin])))
 · exact Or.inl (Or.inr ((sortMembership _).mem_iff.mpr
     (by simp [importantOrigin,member,bit,userOrigin])))
 · exact Or.inr ((sortMembership _).mem_iff.mpr
     (by simp [importantOrigin,member,bit,uaOrigin]))

theorem normal_only_has_no_important_projection (physical : Nat → Nat) (property : Nat)
 (entry : Entry) (normal : ∀ declaration ∈ entry.rule.declarations, declaration.important = false) :
 entryPropertyHalf physical property true entry = [] := by
 apply List.eq_nil_iff_forall_not_mem.mpr
 intro action present
 have bit := important_projection_has_important_bit physical property entry action present
 rcases List.any_eq_true.mp bit with ⟨declaration,member,important⟩
 have notImportant := normal declaration member
 simp [notImportant] at important

theorem constructor_coverage_without_per_rule_coverage_premise
 (sort : List Entry → List Entry) (sortMembership : ∀ entries, (sort entries).Perm entries)
 (entries : List Entry) (physical : Nat → Nat) (property : Nat)
 (provider : ∀ entry ∈ entries,
   entry.origin = 3 ∨ entry.origin = 1 ∨ entry.origin = 0 ∨
   ∀ declaration ∈ entry.rule.declarations, declaration.important = false) :
 ∀ entry ∈ entries.reverse,
 AliasDecision.rule ∈ entryPropertyHalf physical property true entry →
 entry ∈ constructedImportant sort entries := by
 intro entry member rule
 have rawMember := List.mem_reverse.mp member
 rcases provider entry rawMember with author | user | ua | normal
 · exact constructed_important_covers_projected_rule sort sortMembership entries entry rawMember
     physical property rule (Or.inl author)
 · exact constructed_important_covers_projected_rule sort sortMembership entries entry rawMember
     physical property rule (Or.inr (Or.inl user))
 · exact constructed_important_covers_projected_rule sort sortMembership entries entry rawMember
     physical property rule (Or.inr (Or.inr ua))
 · rw [normal_only_has_no_important_projection physical property entry normal] at rule
   exact False.elim (List.not_mem_nil rule)

theorem skip_sort_preserves_membership (identity : α → β) [DecidableEq β]
 (key : α → Nat) (entries : List α) : (skipSort identity key entries).Perm entries := by
 cases entries with
 | nil => exact List.Perm.refl _
 | cons first rest =>
   simp only [skipSort]
   split
   · exact List.Perm.refl _
   · exact sort_perm key _

theorem exact_skip_constructor_coverage
 (entries : List Entry) (physical : Nat → Nat) (property : Nat)
 (provider : ∀ entry ∈ entries,
   entry.origin = 3 ∨ entry.origin = 1 ∨ entry.origin = 0 ∨
   ∀ declaration ∈ entry.rule.declarations, declaration.important = false) :
 ∀ entry ∈ entries.reverse,
 AliasDecision.rule ∈ entryPropertyHalf physical property true entry →
 entry ∈ constructedImportant (skipSort entryPriorityIdentity entryImportantKey) entries :=
 constructor_coverage_without_per_rule_coverage_premise
   (skipSort entryPriorityIdentity entryImportantKey)
   (skip_sort_preserves_membership entryPriorityIdentity entryImportantKey)
   entries physical property provider

def resolvedImportantHalf (resolve : Declaration → AliasDecision α)
 (physical : Nat → Nat) (property : Nat) (entry : Entry) : List (AliasDecision α) :=
 (entry.rule.declarations.reverse.filter fun declaration =>
   declaration.important && decide (physical declaration.property = property)).map resolve

theorem resolved_event_has_important_bit (resolve : Declaration → AliasDecision α)
 (physical : Nat → Nat) (property : Nat) (entry : Entry) (action : AliasDecision α)
 (present : action ∈ resolvedImportantHalf resolve physical property entry) :
 hasImportant entry = true := by
 rcases List.mem_map.mp present with ⟨declaration,member,same⟩
 have selected := List.mem_filter.mp member
 have bit := selected.2
 simp only [Bool.and_eq_true] at bit
 exact List.any_eq_true.mpr ⟨declaration,List.mem_reverse.mp selected.1,bit.1⟩

theorem constructed_important_covers_resolved_event
 (resolve : Declaration → AliasDecision α) (physical : Nat → Nat) (property : Nat)
 (sort : List Entry → List Entry) (sortMembership : ∀ entries, (sort entries).Perm entries)
 (entries : List Entry) (entry : Entry) (member : entry ∈ entries)
 (action : AliasDecision α) (present : action ∈ resolvedImportantHalf resolve physical property entry)
 (origin : entry.origin = 3 ∨ entry.origin = 1 ∨ entry.origin = 0) :
 entry ∈ constructedImportant sort entries := by
 have bit := resolved_event_has_important_bit resolve physical property entry action present
 have buckets := empty_tree_partition_important_buckets entries
 have author := congrArg Prod.fst buckets
 have user := congrArg (fun state => state.2.1) buckets
 have ua := congrArg (fun state => state.2.2) buckets
 simp only [importantBuckets] at author user ua
 simp only [constructedImportant,List.mem_reverse,List.mem_append,author,user,ua]
 rcases origin with authorOrigin | userOrigin | uaOrigin
 · exact Or.inl (Or.inl ((sortMembership _).mem_iff.mpr
     (by simp [importantOrigin,member,bit,authorOrigin])))
 · exact Or.inl (Or.inr ((sortMembership _).mem_iff.mpr
     (by simp [importantOrigin,member,bit,userOrigin])))
 · exact Or.inr ((sortMembership _).mem_iff.mpr
     (by simp [importantOrigin,member,bit,uaOrigin]))

#print axioms resolved_event_has_important_bit
#print axioms constructed_important_covers_resolved_event
#print axioms exact_skip_constructor_coverage
#print axioms important_projection_has_important_bit
#print axioms constructed_important_covers_projected_rule
#print axioms constructor_coverage_without_per_rule_coverage_premise
end ShadowOrder
