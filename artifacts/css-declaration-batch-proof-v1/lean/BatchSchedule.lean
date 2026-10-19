import BatchStorage
import BatchRank
set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false
namespace BatchSchedule
open AllOrder BatchOrder
open BatchBase (Comparator)
variable {ι ν : Type} [DecidableEq ι] [DecidableEq ν]
local notation "E" => Entry ι ν

def event : Plan → Option (Nat × Bool)
  | .replace n => some (n,false)
  | .move n => some (n,true)
  | _ => none

def events (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E) : List (Nat × Bool) :=
  actions.filterMap (fun new => event (BatchBase.planner cmp op initial new))

def removals (events : List (Nat × Bool)) : List Nat :=
  events.filterMap (fun e => if e.2 then some e.1 else none)

theorem events_positions (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E) :
    (events cmp op initial actions).map Prod.fst = plannedPositions cmp op initial actions := by
  induction actions with
  | nil => rfl
  | cons new rest ih =>
    simp only [events,plannedPositions,List.filterMap_cons]
    cases BatchBase.planner cmp op initial new <;> simp only [event,planPosition,List.map_cons,List.cons.injEq,true_and] <;> simpa only [events,plannedPositions,event,planPosition] using ih

theorem events_removals (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E) :
    removals (events cmp op initial actions) = movePositions cmp op initial actions := by
  induction actions with
  | nil => rfl
  | cons new rest ih =>
    simp only [events,movePositions,List.filterMap_cons]
    cases BatchBase.planner cmp op initial new <;> simp only [event,movePosition,removals,List.filterMap_cons,Bool.false_eq_true,↓reduceIte,List.cons.injEq,true_and] <;> simpa only [events,movePositions,removals,event,movePosition] using ih

theorem before_is_rank (es : List (Nat × Bool)) (n : Nat) :
    BatchRank.before es n = (BatchIndices.earlierRemovals (removals es) n).length := by
  induction es with
  | nil => rfl
  | cons e rest ih =>
    obtain ⟨p,b⟩ := e
    cases b <;> by_cases h : p<n <;> simp [BatchRank.before,removals,BatchIndices.earlierRemovals,h] at * <;> omega

theorem removal_permutation {xs ys : List (Nat × Bool)} (hp : xs.Perm ys) :
    (removals xs).Perm (removals ys) := hp.filterMap _

theorem rank_permutation {xs ys : List Nat} (hp : xs.Perm ys) (n : Nat) :
    (BatchIndices.earlierRemovals xs n).length = (BatchIndices.earlierRemovals ys n).length :=
  (hp.filter _).length_eq

def SortedSchedule (es original : List (Nat × Bool)) : Prop :=
  es.Perm original ∧ es.Pairwise (fun a b => a.1 < b.1)

theorem schedule_rank_connection (cmp : Comparator ι ν) (op : ι → ι → Bool)
    (initial actions : List E) (es : List (Nat × Bool))
    (hs : SortedSchedule es (events cmp op initial actions)) :
    BatchRank.walk 0 es = es.filterMap (fun e => if e.2 then none else
      some (e.1,e.1-(BatchIndices.earlierRemovals (descending (movePositions cmp op initial actions)) e.1).length)) := by
  rw [BatchRank.ascending_rank_loop es 0 hs.2]
  unfold BatchRank.projected
  apply BatchRank.filterMap_congr_mem
  intro e he
  have hp : (removals es).Perm (descending (movePositions cmp op initial actions)) := by
    have h := removal_permutation hs.1
    rw [events_removals] at h
    exact h.trans (descending_permutation _).symm
  rw [before_is_rank,rank_permutation hp]
  simp

theorem removals_sorted (es : List (Nat × Bool)) (hs : es.Pairwise (fun a b => a.1 < b.1)) :
    (removals es).Pairwise (fun a b => a < b) := by
  induction es with
  | nil => exact .nil
  | cons e rest ih =>
    have ht := (List.pairwise_cons.mp hs).2
    have hh := (List.pairwise_cons.mp hs).1
    obtain ⟨p,b⟩ := e
    cases b
    · exact ih ht
    · apply List.pairwise_cons.mpr
      refine ⟨?_,ih ht⟩
      intro q hq
      obtain ⟨entry,he,hval⟩ := List.mem_filterMap.mp hq
      have hp := hh entry he
      cases hb : entry.2 <;> simp [hb] at hval
      omega

theorem reverse_removals (es : List (Nat × Bool)) : removals es.reverse = (removals es).reverse := by
  exact List.filterMap_reverse

theorem schedule_removal_connection (cmp : Comparator ι ν) (op : ι → ι → Bool)
    (initial actions : List E) (es : List (Nat × Bool)) (hu : unique initial) (ha : unique actions)
    (hs : SortedSchedule es (events cmp op initial actions)) :
    removals es.reverse = descending (movePositions cmp op initial actions) := by
  have hp := removal_permutation hs.1
  rw [events_removals] at hp
  rw [reverse_removals]
  have hsorted : (removals es).reverse.Pairwise (fun a b => b < a) := by
    simpa only [List.pairwise_reverse] using removals_sorted es hs.2
  apply List.Perm.eq_of_pairwise (le := fun a b => b<a) (by intros; omega) hsorted
    (descending_strict _ (move_positions_unique cmp op initial actions hu ha))
  exact (List.reverse_perm _).trans (hp.trans (descending_permutation _).symm)

theorem schedule_unique_positions (cmp : Comparator ι ν) (op : ι → ι → Bool)
    (initial actions : List E) (hu : unique initial) (ha : unique actions) :
    ((events cmp op initial actions).map Prod.fst).Nodup := by
  rw [events_positions]
  exact planned_positions_unique cmp op initial actions hu ha

def lookupRank : List (Nat × Nat) → Nat → Option Nat
  | [], _ => none
  | (p,value)::rest, target => if p=target then some value else lookupRank rest target

theorem lookup_projection (es : List (Nat × Bool)) (value : Nat → Nat) (p : Nat)
    (hm : (p,false) ∈ es) :
    lookupRank (es.filterMap (fun e => if e.2 then none else some (e.1,value e.1))) p = some (value p) := by
  induction es with
  | nil => simp at hm
  | cons e rest ih =>
    obtain ⟨q,b⟩ := e
    rcases List.mem_cons.mp hm with he | hr
    · cases he
      simp [lookupRank]
    · cases b
      · by_cases he : q=p
        · simp [lookupRank,he]
        · simp [lookupRank,he,ih hr]
      · simpa using ih hr

def streamCorrect (es : List (Nat × Bool)) : Plan → Plan
  | .replace n => .replace ((lookupRank (BatchRank.walk 0 es) n).getD n)
  | .move _ => .append
  | p => p

theorem stream_correction_connection (cmp : Comparator ι ν) (op : ι → ι → Bool)
    (initial actions : List E) (es : List (Nat × Bool))
    (hs : SortedSchedule es (events cmp op initial actions)) (new : E) (hm : new ∈ actions) :
    streamCorrect es (BatchBase.planner cmp op initial new) =
      corrected (descending (movePositions cmp op initial actions)) (BatchBase.planner cmp op initial new) := by
  cases hp : BatchBase.planner cmp op initial new with
  | none | append | move n => rfl
  | replace n =>
    have he : (n,false) ∈ events cmp op initial actions := by
      apply List.mem_filterMap.mpr
      exact ⟨new,hm,by simp [hp,event]⟩
    have hn := hs.1.mem_iff.mpr he
    simp only [streamCorrect]
    rw [schedule_rank_connection cmp op initial actions es hs, lookup_projection es (fun p => p-(BatchIndices.earlierRemovals (descending (movePositions cmp op initial actions)) p).length) n hn]
    rfl

def streamAfter (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial : List E)
    (es : List (Nat × Bool)) : Storage ι ν → List E → Storage ι ν
  | raw, [] => raw
  | raw,new::rest => streamAfter cmp op initial es
      (rawStep raw new (streamCorrect es (BatchBase.planner cmp op initial new))) rest

theorem stream_after_connection (cmp : Comparator ι ν) (op : ι → ι → Bool)
    (initial all actions : List E) (es : List (Nat × Bool)) (raw : Storage ι ν)
    (hs : SortedSchedule es (events cmp op initial all)) (ha : actions ⊆ all) :
    streamAfter cmp op initial es raw actions =
      BatchStorage.rawAfter cmp op initial (descending (movePositions cmp op initial all)) raw actions := by
  induction actions generalizing raw with
  | nil => rfl
  | cons new rest ih =>
    simp only [streamAfter,BatchStorage.rawAfter]
    rw [stream_correction_connection cmp op initial all es hs new (ha (by simp))]
    exact ih _ (by intro e he; exact ha (by simp [he]))

def scheduledBatch (cmp : Comparator ι ν) (op : ι → ι → Bool) (initial actions : List E)
    (es : List (Nat × Bool)) (raw : Storage ι ν) : Storage ι ν :=
  streamAfter cmp op initial es (BatchStorage.rawRemove raw (removals es.reverse)) actions

theorem scheduled_batch_refinement (cmp : Comparator ι ν) (op : ι → ι → Bool)
    (initial actions : List E) (es : List (Nat × Bool)) (raw : Storage ι ν)
    (hs : SortedSchedule es (events cmp op initial actions))
    (hu : unique initial) (ha : unique actions) (hc : compatible cmp op actions)
    (hr : Represents raw initial) :
    Represents (scheduledBatch cmp op initial actions es raw) (directRun op initial actions) := by
  unfold scheduledBatch
  rw [stream_after_connection cmp op initial actions actions es _ hs (by intro e he; exact he),
    schedule_removal_connection cmp op initial actions es hu ha hs]
  exact BatchStorage.raw_batch_refinement cmp op initial actions raw hu ha hc hr

def sortedEvents (es : List (Nat × Bool)) : List (Nat × Bool) :=
  es.mergeSort (fun a b => decide (a.1 ≤ b.1))

theorem sorted_events_valid (es : List (Nat × Bool)) (hu : (es.map Prod.fst).Nodup) :
    SortedSchedule (sortedEvents es) es := by
  have hp : (sortedEvents es).Perm es := List.mergeSort_perm _ _
  have hw : (sortedEvents es).Pairwise (fun a b => a.1 ≤ b.1) := by
    have h := List.pairwise_mergeSort (le := fun a b : Nat × Bool => decide (a.1 ≤ b.1))
      (by intro a b c hab hbc; simp at *; omega)
      (by intro a b; simp; omega) es
    simpa [sortedEvents] using h
  have hn : ((sortedEvents es).map Prod.fst).Nodup := (hp.map Prod.fst).nodup_iff.mpr hu
  refine ⟨hp,?_⟩
  have strengthen : ∀ xs : List (Nat × Bool), xs.Pairwise (fun a b => a.1 ≤ b.1) →
      (xs.map Prod.fst).Nodup → xs.Pairwise (fun a b => a.1 < b.1) := by
    intro xs hle hn
    induction xs with
    | nil => exact .nil
    | cons a rest ih =>
      refine List.pairwise_cons.mpr ⟨?_,ih (List.pairwise_cons.mp hle).2 (List.nodup_cons.mp hn).2⟩
      intro b hb
      have hl := (List.pairwise_cons.mp hle).1 b hb
      have he : a.1 ≠ b.1 := by
        intro he
        exact (List.nodup_cons.mp hn).1 (List.mem_map.mpr ⟨b,hb,he.symm⟩)
      omega
  exact strengthen _ hw hn

theorem admitted_schedule_exists (cmp : Comparator ι ν) (op : ι → ι → Bool)
    (initial actions : List E) (hu : unique initial) (ha : unique actions) :
    SortedSchedule (sortedEvents (events cmp op initial actions)) (events cmp op initial actions) :=
  sorted_events_valid _ (schedule_unique_positions cmp op initial actions hu ha)

end BatchSchedule
