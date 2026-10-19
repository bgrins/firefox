import Std
namespace PostGuardObservers

abbrev AttributeQuery := Nat × Nat
abbrev AttributeReferences := Nat → List Nat

def recordQuery (references : AttributeReferences) (query : AttributeQuery) : AttributeReferences :=
 fun name => if name = query.1 then references name ++ [query.2] else references name

def recordQueries (references : AttributeReferences) (queries : List AttributeQuery) :=
 queries.foldl recordQuery references

def supports (references : AttributeReferences) (query : AttributeQuery) : Prop :=
 query.2 ∈ references query.1

def haveSameReferencedAttributes (target candidate : Nat → Nat → Option String)
 (references : AttributeReferences) : Prop :=
 ∀ name ns, ns ∈ references name → target name ns = candidate name ns

theorem record_query_membership (references : AttributeReferences)
 (query other : AttributeQuery) :
 supports (recordQuery references query) other ↔ supports references other ∨ other = query := by
 rcases query with ⟨name,ns⟩
 rcases other with ⟨otherName,otherNamespace⟩
 by_cases same : otherName = name
 · subst otherName
   simp [supports,recordQuery]
 · simp [supports,recordQuery,same]

theorem record_query_history_membership (references : AttributeReferences)
 (queries : List AttributeQuery) (query : AttributeQuery) :
 supports (recordQueries references queries) query ↔ supports references query ∨ query ∈ queries := by
 induction queries generalizing references with
 | nil => simp [recordQueries]
 | cons first rest ih =>
   simp only [recordQueries,List.foldl_cons]
   rw [← recordQueries,ih,record_query_membership]
   simp [List.mem_cons,or_assoc]

theorem sharing_check_depends_only_on_support
 (target candidate : Nat → Nat → Option String) (left right : AttributeReferences)
 (same : ∀ query, supports left query ↔ supports right query) :
 haveSameReferencedAttributes target candidate left ↔
 haveSameReferencedAttributes target candidate right := by
 constructor
 · intro valid name ns member
   exact valid name ns ((same (name,ns)).mpr member)
 · intro valid name ns member
   exact valid name ns ((same (name,ns)).mp member)

theorem sharing_check_after_query_history
 (target candidate : Nat → Nat → Option String) (references : AttributeReferences)
 (queries : List AttributeQuery) :
 haveSameReferencedAttributes target candidate (recordQueries references queries) ↔
 haveSameReferencedAttributes target candidate references ∧
 ∀ query ∈ queries, target query.1 query.2 = candidate query.1 query.2 := by
 constructor
 · intro valid
   constructor
   · intro name ns member
     exact valid name ns ((record_query_history_membership references queries (name,ns)).mpr
       (Or.inl member))
   · intro query member
     exact valid query.1 query.2 ((record_query_history_membership references queries query).mpr
       (Or.inr member))
 · rintro ⟨valid,queriesValid⟩ name ns member
   rcases (record_query_history_membership references queries (name,ns)).mp member with old | fresh
   · exact valid name ns old
   · exact queriesValid (name,ns) fresh

theorem repeated_queries_preserve_sharing_decision
 (target candidate : Nat → Nat → Option String) (references : AttributeReferences)
 (queries : List AttributeQuery) :
 haveSameReferencedAttributes target candidate (recordQueries references (queries ++ queries)) ↔
 haveSameReferencedAttributes target candidate (recordQueries references queries) := by
 apply sharing_check_depends_only_on_support
 intro query
 simp [record_query_history_membership,List.mem_append]

theorem equal_query_support_preserves_sharing
 (target candidate : Nat → Nat → Option String) (references : AttributeReferences)
 (left right : List AttributeQuery) (same : ∀ query, query ∈ left ↔ query ∈ right) :
 haveSameReferencedAttributes target candidate (recordQueries references left) ↔
 haveSameReferencedAttributes target candidate (recordQueries references right) := by
 apply sharing_check_depends_only_on_support
 intro query
 simp only [record_query_history_membership,same]

def trackedQuery (getAttribute : Nat → Nat → Option String)
 (references : AttributeReferences) (query : AttributeQuery) :=
 (recordQuery references query,getAttribute query.1 query.2)

theorem tracked_query_return_independent_of_tracker
 (getAttribute : Nat → Nat → Option String) (left right : AttributeReferences)
 (query : AttributeQuery) :
 (trackedQuery getAttribute left query).2 = (trackedQuery getAttribute right query).2 := rfl

theorem stored_namespace_vector_is_not_idempotent :
 (recordQuery (recordQuery (fun _ => []) (1,2)) (1,2)) 1 = [2,2] ∧
 (recordQuery (fun _ => []) (1,2)) 1 = [2] := by
 decide

#print axioms record_query_history_membership
#print axioms sharing_check_after_query_history
#print axioms repeated_queries_preserve_sharing_decision
#print axioms equal_query_support_preserves_sharing
#print axioms stored_namespace_vector_is_not_idempotent
end PostGuardObservers
