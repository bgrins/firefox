import OccurrenceDeletion
import RepresentedControl
namespace ShadowOrder

theorem uniform_key_skipped [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ) (events : List (OccurrenceEvent κ α))
 (key : κ) (excluded : List κ) (state : σ)
 (uniform : ∀ event ∈ events, event.identity = key)
 (blocked : key ∈ excluded ∨ eligible state key = false) :
 occurrenceSetExecution (fun s e => eligible s e.identity) apply events excluded state = state := by
 induction events with
 | nil => rfl
 | cons event rest ih =>
   have identity := uniform event (by simp)
   have tail := ih (fun e he => uniform e (by simp [he]))
   rcases blocked with banned | disabled
   · simp [occurrenceSetExecution,identity,banned,tail]
   · by_cases banned : key ∈ excluded
     · simp [occurrenceSetExecution,identity,banned,tail]
     · simp [occurrenceSetExecution,identity,banned,disabled,tail]

theorem mixed_half_first_effect [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (disables : ∀ state event value, eligible (apply state event value) event.identity = false)
 (first : OccurrenceEvent κ α) (rest : List (OccurrenceEvent κ α))
 (uniform : ∀ event ∈ rest, event.identity = first.identity)
 (excluded : List κ) (state : σ) :
 occurrenceSetExecution (fun s e => eligible s e.identity) apply (first::rest) excluded state =
 occurrenceSetExecution (fun s e => eligible s e.identity) apply [first] excluded state := by
 by_cases banned : first.identity ∈ excluded
 · simp only [occurrenceSetExecution,banned,↓reduceIte]
   exact uniform_key_skipped eligible apply rest first.identity excluded state uniform (Or.inl banned)
 · cases enabled : eligible state first.identity with
   | false =>
     simp only [occurrenceSetExecution,banned,↓reduceIte,enabled,Bool.false_eq_true]
     exact uniform_key_skipped eligible apply rest first.identity excluded state uniform (Or.inr enabled)
   | true =>
     simp only [occurrenceSetExecution,banned,↓reduceIte,enabled]
     cases decision : first.action with
     | rule =>
       exact uniform_key_skipped eligible apply rest first.identity (first.identity::excluded) state uniform
         (Or.inl (by simp))
     | effect value =>
       exact uniform_key_skipped eligible apply rest first.identity excluded (apply state first value) uniform
         (Or.inr (disables state first value))

def blockHalfEvents (key : κ) (actions : List (AliasDecision α)) : List (OccurrenceEvent κ α) :=
 actions.map fun action => ⟨key,action⟩

theorem block_half_atomic [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (disables : ∀ state event value, eligible (apply state event value) event.identity = false)
 (key : κ) (first : AliasDecision α) (rest : List (AliasDecision α))
 (excluded : List κ) (state : σ) :
 occurrenceSetExecution (fun s e => eligible s e.identity) apply
   (blockHalfEvents key (first::rest)) excluded state =
 occurrenceSetExecution (fun s e => eligible s e.identity) apply
   (blockHalfEvents key [first]) excluded state := by
 apply mixed_half_first_effect eligible apply disables
 intro event member
 rcases List.mem_map.mp member with ⟨action,ha,rfl⟩
 rfl

theorem equal_normal_priority_coordinates (a b : Priority)
 (same : unimportantPriority a = unimportantPriority b) : coordinates a = coordinates b := by
 calc
   coordinates a = coordinates (unimportantPriority a) := rfl
   _ = coordinates (unimportantPriority b) := congrArg coordinates same
   _ = coordinates b := rfl

theorem priority_cut_rejects_same_normal_key (cut candidate : Priority) (kind : RevertKind)
 (same : unimportantPriority cut = unimportantPriority candidate) (nonRule : kind ≠ .rule) :
 repairedAllows cut candidate kind = false := by
 have coordinatesEq := equal_normal_priority_coordinates cut candidate same
 have predicateEq : repairedAllows cut candidate kind = repairedAllows cut cut kind := by
   rw [← classification_preserves_predicate,← classification_preserves_predicate,← coordinatesEq]
 cases kind with
 | origin => rw [predicateEq]; exact (repaired_allows_self cut).1
 | layer => rw [predicateEq]; exact (repaired_allows_self cut).2
 | rule => contradiction

theorem retained_cut_rejects_same_normal_key (state : RevertRepresentatives)
 (valid : representativeValid state) (cut candidate : Priority) (kind : RevertKind)
 (same : unimportantPriority cut = unimportantPriority candidate) (nonRule : kind ≠ .rule) :
 representativeAllows (representativeAdd state (cut,kind)) candidate = false := by
 rw [representative_step_intersection state (cut,kind) candidate valid]
 simp only [priority_cut_rejects_same_normal_key cut candidate kind same nonRule,Bool.and_false]

#print axioms mixed_half_first_effect
#print axioms block_half_atomic
end ShadowOrder
