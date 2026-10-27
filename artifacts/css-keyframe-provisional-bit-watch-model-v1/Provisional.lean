import Bits

namespace ProvisionalWatches

inductive Matches {α β : Type} (R : α → β → Prop) : List α → List β → Prop where
  | nil : Matches R [] []
  | cons {first : α} {second : β} {rest : List α} {others : List β} :
      R first second → Matches R rest others → Matches R (first :: rest) (second :: others)

abbrev FineState := AttributeWatches.State
abbrev CoarseState := AttributeWatchBits.BitState

def PairRel (fine : Nat × AttributeWatches.Watch)
    (coarse : Nat × AttributeWatchBits.BitWatch) : Prop :=
  coarse.1 = fine.1 ∧ coarse.2.target = fine.2.target ∧
    ((AttributeWatchBits.abstractWatch fine.2).sensitive = true → coarse.2.sensitive = true)

def Rel (fine : FineState) (coarse : CoarseState) : Prop :=
  Matches PairRel fine.published coarse.watches ∧
    ∀ target, target ∈ fine.pending → target ∈ coarse.pending

def boost (selected : Nat → Bool) (pair : Nat × AttributeWatchBits.BitWatch) :
    Nat × AttributeWatchBits.BitWatch :=
  (pair.1, { pair.2 with sensitive := selected pair.1 || pair.2.sensitive })

def strengthen (s : CoarseState) (selected : Nat → Bool) : CoarseState :=
  { s with watches := s.watches.map (boost selected) }

theorem exact_pair (pair : Nat × AttributeWatches.Watch) :
    PairRel pair (AttributeWatchBits.abstractPair pair) := by
  simp [PairRel, AttributeWatchBits.abstractPair, AttributeWatchBits.abstractWatch]

theorem exact_relation_is_conservative (fine : FineState) (coarse : CoarseState)
    (h : AttributeWatchBits.Simulates fine coarse) : Rel fine coarse := by
  constructor
  · rw [h.1]
    have all : ∀ xs : List (Nat × AttributeWatches.Watch),
        Matches PairRel xs (xs.map AttributeWatchBits.abstractPair) := by
      intro xs
      induction xs with
      | nil => exact .nil
      | cons pair rest ih => exact .cons (exact_pair pair) ih
    exact all fine.published
  · exact h.2

theorem related_member {xs : List (Nat × AttributeWatches.Watch)}
    {ys : List (Nat × AttributeWatchBits.BitWatch)} (h : Matches PairRel xs ys)
    (pair : Nat × AttributeWatches.Watch) (member : pair ∈ xs) :
    ∃ other, other ∈ ys ∧ PairRel pair other := by
  induction h with
  | nil => simp at member
  | @cons first second rest others matched tail ih =>
    simp only [List.mem_cons] at member
    rcases member with same | later
    · subst pair
      exact ⟨second, by simp, matched⟩
    · obtain ⟨other, otherMember, related⟩ := ih later
      exact ⟨other, by simp [otherMember], related⟩

theorem named_hit_preserved (fine : FineState) (coarse : CoarseState)
    (target name : Nat) (h : Rel fine coarse)
    (hit : AttributeWatches.watching fine target name = true) :
    AttributeWatchBits.watching coarse target = true := by
  obtain ⟨pair, member, matched⟩ := List.any_eq_true.mp hit
  have parts : (pair.2.target == target) = true ∧ pair.2.names.contains name = true := by
    simpa only [Bool.and_eq_true] using matched
  obtain ⟨other, present, related⟩ := related_member h.1 pair member
  have sensitive := related.2.2 (AttributeWatchBits.nonempty_query_sensitive pair.2 name
    (List.contains_iff_mem.mp parts.2))
  apply List.any_eq_true.mpr
  refine ⟨other, present, ?_⟩
  simp only [related.2.1, sensitive, Bool.and_true]
  exact parts.1

theorem strengthening_preserves_bit_hit (s : CoarseState) (selected : Nat → Bool)
    (target : Nat) (hit : AttributeWatchBits.watching s target = true) :
    AttributeWatchBits.watching (strengthen s selected) target = true := by
  obtain ⟨pair, member, matched⟩ := List.any_eq_true.mp hit
  have parts : (pair.2.target == target) = true ∧ pair.2.sensitive = true := by
    simpa only [Bool.and_eq_true] using matched
  apply List.any_eq_true.mpr
  refine ⟨boost selected pair, List.mem_map.mpr ⟨pair, member, rfl⟩, ?_⟩
  simp [boost, parts.1, parts.2]

theorem strengthen_related (fine : FineState) (coarse : CoarseState)
    (selected : Nat → Bool) (h : Rel fine coarse) : Rel fine (strengthen coarse selected) := by
  constructor
  · have mapped : ∀ {xs ys}, Matches PairRel xs ys →
        Matches PairRel xs (ys.map (boost selected)) := by
      intro xs ys watches
      induction watches with
      | nil => exact .nil
      | @cons first second rest others matched tail ih =>
        apply Matches.cons _ ih
        refine ⟨matched.1, matched.2.1, ?_⟩
        intro required
        simp [boost, matched.2.2 required]
    exact mapped h.1
  · exact h.2

theorem erase_related {xs : List (Nat × AttributeWatches.Watch)}
    {ys : List (Nat × AttributeWatchBits.BitWatch)}
    (h : Matches PairRel xs ys) (id : Nat) :
    Matches PairRel (AttributeWatches.eraseId id xs) (AttributeWatches.eraseId id ys) := by
  induction h with
  | nil => exact .nil
  | @cons first second rest others matched tail ih =>
    by_cases equal : first.1 = id
    · simpa [AttributeWatches.eraseId, matched.1, equal] using ih
    · simpa [AttributeWatches.eraseId, matched.1, equal] using Matches.cons matched ih

theorem install_related (fine : FineState) (coarse : CoarseState) (id : Nat)
    (e : AttributeWatches.Entry) (h : Rel fine coarse) :
    Rel (AttributeWatches.install fine id e) (AttributeWatchBits.install coarse id e) := by
  constructor
  · exact .cons (exact_pair (id, AttributeWatches.publish e)) (erase_related h.1 id)
  · exact h.2

def installConservative (s : CoarseState) (id : Nat) (e : AttributeWatches.Entry)
    (extra : Bool) : CoarseState :=
  { s with watches :=
      (id, ⟨e.target, extra || (AttributeWatchBits.abstractWatch (AttributeWatches.publish e)).sensitive⟩) ::
        AttributeWatches.eraseId id s.watches }

theorem install_conservative_related (fine : FineState) (coarse : CoarseState) (id : Nat)
    (e : AttributeWatches.Entry) (extra : Bool) (h : Rel fine coarse) :
    Rel (AttributeWatches.install fine id e) (installConservative coarse id e extra) := by
  constructor
  · apply Matches.cons _ (erase_related h.1 id)
    refine ⟨rfl, rfl, ?_⟩
    intro required
    simp [required]
  · exact h.2

theorem remove_related (fine : FineState) (coarse : CoarseState) (id : Nat)
    (h : Rel fine coarse) :
    Rel (AttributeWatches.remove fine id) (AttributeWatchBits.remove coarse id) :=
  ⟨erase_related h.1 id, h.2⟩

theorem change_related (fine : FineState) (coarse : CoarseState) (target name : Nat)
    (h : Rel fine coarse) :
    Rel (AttributeWatches.change fine target name) (AttributeWatchBits.change coarse target) := by
  constructor
  · exact h.1
  · intro queried member
    by_cases hit : AttributeWatches.watching fine target name = true
    · have coarseHit := named_hit_preserved fine coarse target name h hit
      simp only [AttributeWatches.change, hit, ↓reduceIte, List.mem_cons] at member
      rcases member with same | prior
      · subst queried
        exact AttributeWatchBits.bit_hit_admits coarse target coarseHit
      · exact AttributeWatchBits.change_keeps_pending coarse target queried (h.2 queried prior)
    · have prior : queried ∈ fine.pending := by
        simpa [AttributeWatches.change, hit] using member
      exact AttributeWatchBits.change_keeps_pending coarse target queried (h.2 queried prior)

inductive Event where
  | completed (event : AttributeWatches.Event)
  | provisional (selected : Nat → Bool)
  | completedInstall (id : Nat) (entry : AttributeWatches.Entry) (extra : Bool)

def fineStep (s : FineState) : Event → FineState
  | .completed event => AttributeWatches.step s event
  | .provisional _ => s
  | .completedInstall id entry _ => AttributeWatches.install s id entry

def coarseStep (s : CoarseState) : Event → CoarseState
  | .completed event => AttributeWatchBits.step s event
  | .provisional selected => strengthen s selected
  | .completedInstall id entry extra => installConservative s id entry extra

def fineRun (events : List Event) : FineState := events.foldl fineStep AttributeWatches.empty
def coarseRun (events : List Event) : CoarseState := events.foldl coarseStep AttributeWatchBits.empty

theorem step_related (fine : FineState) (coarse : CoarseState) (event : Event)
    (h : Rel fine coarse) : Rel (fineStep fine event) (coarseStep coarse event) := by
  cases event with
  | provisional selected => exact strengthen_related fine coarse selected h
  | completedInstall id entry extra => exact install_conservative_related fine coarse id entry extra h
  | completed event =>
    cases event with
    | install id e => exact install_related fine coarse id e h
    | remove id => exact remove_related fine coarse id h
    | change target name => exact change_related fine coarse target name h

theorem finite_history_related (events : List Event) : Rel (fineRun events) (coarseRun events) := by
  have general : ∀ xs : List Event, ∀ fine coarse, Rel fine coarse →
      Rel (xs.foldl fineStep fine) (xs.foldl coarseStep coarse) := by
    intro xs
    induction xs with
    | nil => intro fine coarse h; exact h
    | cons event rest ih => intro fine coarse h; exact ih _ _ (step_related fine coarse event h)
  exact general events _ _ (exact_relation_is_conservative _ _ AttributeWatchBits.empty_simulates)

theorem finite_history_published (events : List Event) : AttributeWatches.Published (fineRun events) := by
  have general : ∀ xs : List Event, ∀ fine, AttributeWatches.Published fine →
      AttributeWatches.Published (xs.foldl fineStep fine) := by
    intro xs
    induction xs with
    | nil => intro fine h; exact h
    | cons event rest ih =>
      intro fine h
      apply ih
      cases event with
      | provisional selected => exact h
      | completedInstall id entry extra => exact AttributeWatches.install_published fine id entry h
      | completed event => exact AttributeWatches.step_published fine event h
  exact general events _ AttributeWatches.empty_published

theorem queried_mutation_admitted (events : List Event) (id : Nat)
    (e : AttributeWatches.Entry) (q : AttributeWatches.Query)
    (active : (id, e) ∈ (fineRun events).active) (queried : q ∈ e.queries) :
    e.target ∈ (AttributeWatchBits.change (coarseRun events) e.target).pending := by
  have hit := AttributeWatches.published_covers_query _ id e q
    (finite_history_published events) active queried
  exact AttributeWatchBits.bit_hit_admits _ _
    (named_hit_preserved _ _ _ _ (finite_history_related events) hit)

end ProvisionalWatches
