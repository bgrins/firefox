import ScalarFilter

namespace HyphenRecordedFilter
open HyphenScalarFilter

@[simp] theorem filterTrue (xs : List α) : xs.filter (fun _ => true) = xs := by
  induction xs with
  | nil => rfl
  | cons x rest ih => simp [ih]

@[simp] theorem filterFalse (xs : List α) : xs.filter (fun _ => false) = [] := by
  apply List.filter_eq_nil_iff.mpr
  intros
  simp

def recordWrites : List Candidate → (Nat → Nat) → List Candidate × (Nat → Nat)
  | [], buffer => ([], buffer)
  | c :: rest, buffer =>
    let recorded := { c with previous := buffer c.index }
    let next := fun i => if i = c.index then 2 else buffer i
    let result := recordWrites rest next
    (recorded :: result.1, result.2)

def recordingCorrect (xs : List Candidate) (old : Nat → Nat) : Prop :=
  ∀ c ∈ xs, c.previous = old c.index

theorem record_writes_exact (xs : List Candidate) (old buffer : Nat → Nat)
    (ordered : xs.Pairwise fun a b => a.index < b.index)
    (unwritten : ∀ c ∈ xs, buffer c.index = old c.index) :
    recordWrites xs buffer =
      (xs.map (fun c => { c with previous := old c.index }), writes xs (fun _ => 2) buffer) := by
  induction xs generalizing buffer with
  | nil => rfl
  | cons c rest ih =>
    have hp := List.pairwise_cons.mp ordered
    have hc := unwritten c (by simp)
    have hn : ∀ d ∈ rest,
        (if d.index = c.index then 2 else buffer d.index) = old d.index := by
      intro d hd
      have hlt := hp.1 d hd
      have he : d.index ≠ c.index := by omega
      simp [he, unwritten d (by simp [hd])]
    have ht := ih (fun i => if i = c.index then 2 else buffer i) hp.2 hn
    simp only [recordWrites, ht, List.map_cons, writes, List.foldl_cons, hc]

theorem recorded_identity (xs : List Candidate) (old : Nat → Nat)
    (correct : recordingCorrect xs old) :
    xs.map (fun c => { c with previous := old c.index }) = xs := by
  induction xs with
  | nil => rfl
  | cons c rest ih =>
    have hc := correct c (by simp)
    have hr : recordingCorrect rest old := by
      intro d hd
      exact correct d (by simp [hd])
    have he : { c with previous := old c.index } = c := by
      cases c
      simp_all
    simpa only [List.map_cons, he] using congrArg (List.cons c) (ih hr)

theorem captures_unwritten_value (xs : List Candidate) (old : Nat → Nat)
    (ordered : xs.Pairwise fun a b => a.index < b.index)
    (correct : recordingCorrect xs old) :
    recordWrites xs old = (xs, writes xs (fun _ => 2) old) := by
  rw [record_writes_exact xs old old ordered (by intros; rfl), recorded_identity xs old correct]

def restoreRecorded (xs : List Candidate) (base : Nat → Nat) : Nat → Nat :=
  xs.foldl (fun buffer c => fun i => if i = c.index then c.previous else buffer i) base

theorem stored_restore_exact (xs : List Candidate) (old buffer : Nat → Nat)
    (correct : recordingCorrect xs old) :
    restoreRecorded xs buffer = writes xs old buffer := by
  induction xs generalizing buffer with
  | nil => rfl
  | cons c rest ih =>
    have hc := correct c (by simp)
    have hr : recordingCorrect rest old := by intro d hd; exact correct d (by simp [hd])
    simp only [restoreRecorded, writes, List.foldl_cons]
    have hb : (fun i => if i = c.index then c.previous else buffer i) =
        (fun i => if i = c.index then old i else buffer i) := by
      funext i
      split <;> simp_all
    rw [hb]
    exact ih _ hr

def nativeSpeculateRestore (xs : List Candidate) (old : Nat → Nat)
    (accept : Candidate → Bool) : Nat → Nat :=
  let result := recordWrites xs old
  restoreRecorded (result.1.filter fun c => !accept c) result.2

theorem recorded_speculation_equivalence (xs : List Candidate) (old : Nat → Nat)
    (accept : Candidate → Bool)
    (ordered : xs.Pairwise fun a b => a.index < b.index)
    (correct : recordingCorrect xs old) :
    nativeSpeculateRestore xs old accept = writes (xs.filter accept) (fun _ => 2) old := by
  unfold nativeSpeculateRestore
  rw [captures_unwritten_value xs old ordered correct]
  dsimp only
  have hf : recordingCorrect (xs.filter fun c => !accept c) old := by
    intro c hc
    exact correct c (List.mem_filter.mp hc).1
  rw [stored_restore_exact _ old _ hf]
  exact speculative_array_restores xs accept old (ordered_unique xs ordered)

theorem generated_records_correct (category : Nat → Category) (units : List Nat)
    (pre after : Nat) (mask : Nat → Bool) (old : Nat → Nat) :
    recordingCorrect (candidates category units pre after mask old) old := by
  intro c hc
  simp only [candidates, List.mem_map] at hc
  obtain ⟨v, _, he⟩ := hc
  subst c
  rfl

theorem complete_record_and_restore (category : Nat → Category) (units : List Nat)
    (pre after : Nat) (mask : Nat → Bool) (old : Nat → Nat) (accept : Candidate → Bool) :
    nativeSpeculateRestore (candidates category units pre after mask old) old accept =
      writes ((candidates category units pre after mask old).filter accept) (fun _ => 2) old :=
  recorded_speculation_equivalence _ old accept
    (candidate_indices_unique category units pre after mask old)
    (generated_records_correct category units pre after mask old)

def rejectedSuffix (total suffix : Nat) : List Candidate → List Candidate
  | [] => []
  | c :: rest => if keep total suffix c then [] else c :: rejectedSuffix total suffix rest

theorem rejected_suffix_exact (total suffix : Nat) (xs : List Candidate)
    (descending : Descending xs) :
    rejectedSuffix total suffix xs = xs.filter (fun c => !keep total suffix c) := by
  induction xs with
  | nil => rfl
  | cons c rest ih =>
    have hp := List.pairwise_cons.mp (show List.Pairwise _ (c :: rest) from descending)
    by_cases hk : keep total suffix c = true
    · have allKeep : ∀ x ∈ rest, keep total suffix x = true := by
        intro x hx
        exact keep_monotone total suffix c x (hp.1 x hx) hk
      have filtered : rest.filter (fun x => !keep total suffix x) = [] := by
        apply List.filter_eq_nil_iff.mpr
        intro x hx
        simp [allKeep x hx]
      simp [rejectedSuffix, hk, filtered]
    · simp [rejectedSuffix, hk, ih hp.2]

theorem reverse_recorded_restore (xs : List Candidate) (old buffer : Nat → Nat)
    (correct : recordingCorrect xs old) :
    restoreRecorded xs.reverse buffer = restoreRecorded xs buffer := by
  have hr : recordingCorrect xs.reverse old := by
    intro c hc
    exact correct c (List.mem_reverse.mp hc)
  rw [stored_restore_exact _ old _ hr, stored_restore_exact _ old _ correct]
  funext i
  simp [writes_at]

def nativeReverseRestore (xs : List Candidate) (old : Nat → Nat)
    (minimum total after : Nat) : Nat → Nat :=
  let result := recordWrites xs old
  let undo := if total < minimum then result.1.reverse
    else rejectedSuffix total after result.1.reverse
  restoreRecorded undo result.2

theorem reverse_loop_exact (xs : List Candidate) (old : Nat → Nat)
    (minimum total after : Nat)
    (ordered : xs.Pairwise fun a b => a.index < b.index)
    (descending : Descending xs.reverse) (correct : recordingCorrect xs old) :
    nativeReverseRestore xs old minimum total after =
      nativeSpeculateRestore xs old
        (fun c => minimum ≤ total && after ≤ total - c.countBefore) := by
  unfold nativeReverseRestore nativeSpeculateRestore
  rw [captures_unwritten_value xs old ordered correct]
  dsimp only
  by_cases hm : total < minimum
  · simp only [hm, ↓reduceIte, show ¬minimum ≤ total by omega, decide_false,
      Bool.false_and, Bool.not_false, filterTrue]
    exact reverse_recorded_restore xs old _ correct
  · simp only [hm, ↓reduceIte, show minimum ≤ total by omega, decide_true, Bool.true_and]
    rw [rejected_suffix_exact total after xs.reverse descending, List.filter_reverse]
    have hc : recordingCorrect (xs.filter fun c => !keep total after c) old := by
      intro c h
      exact correct c (List.mem_filter.mp h).1
    exact reverse_recorded_restore _ old _ hc

def nativeFilter (category : Nat → Category) (units : List Nat)
    (minimum pre after : Nat) (mask : Nat → Bool) (old : Nat → Nat) : Nat → Nat :=
  if units.length < minimum then old else
    nativeReverseRestore (candidates category units pre after mask old) old
      minimum (count category (decode units)) after

def referenceCandidates (category : Nat → Category) (units : List Nat)
    (minimum pre after : Nat) (mask : Nat → Bool) (old : Nat → Nat) : List Candidate :=
  ((referenceVisits category (decode units) 0 0).filter
    (declarativeEligible units (count category (decode units)) minimum pre after mask)).map
      fun v => ⟨v.index + 1, v.countBefore, old (v.index + 1)⟩

theorem filtered_candidates_exact (category : Nat → Category) (units : List Nat)
    (minimum pre after : Nat) (mask : Nat → Bool) (old : Nat → Nat) :
    (candidates category units pre after mask old).filter
        (fun c => minimum ≤ count category (decode units) &&
          after ≤ count category (decode units) - c.countBefore) =
      referenceCandidates category units minimum pre after mask old := by
  unfold candidates referenceCandidates
  rw [← visits_reference]
  rw [List.filter_map, List.filter_filter]
  congr 1
  apply List.filter_congr
  intro v hv
  rw [← exact_eligibility category units minimum pre after mask v hv]
  simp [nativeEligible, Bool.and_assoc, Bool.and_comm, Bool.and_left_comm]

theorem complete_filter_reference (category : Nat → Category) (units : List Nat)
    (minimum pre after : Nat) (mask : Nat → Bool) (old : Nat → Nat) :
    nativeFilter category units minimum pre after mask old =
      writes (referenceCandidates category units minimum pre after mask old) (fun _ => 2) old := by
  unfold nativeFilter
  split
  next short =>
    have totalShort := short_unit_guard_sound category units minimum short
    have hn : ¬minimum ≤ count category (decode units) := by omega
    have noEligible : declarativeEligible units (count category (decode units))
        minimum pre after mask = fun _ => false := by
      funext v
      simp [declarativeEligible, hn]
    simp [referenceCandidates, noEligible, writes]
  next _ =>
    rw [reverse_loop_exact _ old minimum _ after
      (candidate_indices_unique category units pre after mask old)
      (candidate_prefix_order category units pre after mask old)
      (generated_records_correct category units pre after mask old),
      complete_record_and_restore, filtered_candidates_exact]

#print axioms reverse_loop_exact
#print axioms filtered_candidates_exact
#print axioms complete_filter_reference

#print axioms captures_unwritten_value
#print axioms stored_restore_exact
#print axioms recorded_speculation_equivalence
#print axioms complete_record_and_restore
end HyphenRecordedFilter
