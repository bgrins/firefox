import Std
namespace ShadowOrder
inductive AliasDecision (α : Type) where
 | rule
 | effect (value : α)
 deriving DecidableEq, Repr

def occurrenceReference (decision : κ → AliasDecision α)
 (enabled : σ → κ → Bool) (apply : σ → κ → α → σ) : List κ → σ → σ
 | [], state => state
 | key::rest, state =>
   let next := if enabled state key then
     match decision key with
     | .rule => state
     | .effect value => apply state key value
     else state
   occurrenceReference decision enabled apply rest next

def aliasExcludedExecution [DecidableEq κ] (decision : κ → AliasDecision α)
 (enabled : σ → κ → Bool) (apply : σ → κ → α → σ) : List κ → List κ → σ → σ
 | [], _, state => state
 | key::rest, excluded, state =>
   if key ∈ excluded then aliasExcludedExecution decision enabled apply rest excluded state
   else if enabled state key then
     match decision key with
     | .rule => aliasExcludedExecution decision enabled apply rest (key::excluded) state
     | .effect value => aliasExcludedExecution decision enabled apply rest excluded (apply state key value)
   else aliasExcludedExecution decision enabled apply rest excluded state

theorem arbitrary_alias_equivalence [DecidableEq κ]
 (decision : κ → AliasDecision α) (enabled : σ → κ → Bool) (apply : σ → κ → α → σ)
 (stream excluded : List κ) (state : σ)
 (soundExclusions : ∀ key ∈ excluded, decision key = .rule) :
 aliasExcludedExecution decision enabled apply stream excluded state =
 occurrenceReference decision enabled apply stream state := by
 induction stream generalizing excluded state with
 | nil => rfl
 | cons key rest ih =>
   simp only [aliasExcludedExecution,occurrenceReference]
   by_cases banned : key ∈ excluded
   · simp only [banned,↓reduceIte]
     have rule := soundExclusions key banned
     cases allow : enabled state key <;> simp [allow,rule,ih _ _ soundExclusions]
   · simp only [banned,↓reduceIte]
     cases allow : enabled state key
     · simp [allow,ih _ _ soundExclusions]
     · simp only [allow,↓reduceIte]
       cases action : decision key with
       | rule =>
         simp only [action]
         apply ih
         intro other member
         simp only [List.mem_cons] at member
         rcases member with rfl | member
         · exact action
         · exact soundExclusions other member
       | effect value => simp [action,ih _ _ soundExclusions]

theorem empty_exclusion_refinement [DecidableEq κ]
 (decision : κ → AliasDecision α) (enabled : σ → κ → Bool) (apply : σ → κ → α → σ)
 (stream : List κ) (state : σ) :
 aliasExcludedExecution decision enabled apply stream [] state =
 occurrenceReference decision enabled apply stream state :=
 arbitrary_alias_equivalence decision enabled apply stream [] state (by simp)

#print axioms arbitrary_alias_equivalence
#print axioms empty_exclusion_refinement
end ShadowOrder
