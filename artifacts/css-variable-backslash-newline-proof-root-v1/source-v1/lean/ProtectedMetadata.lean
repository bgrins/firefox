import PreservationGuard
set_option autoImplicit false
namespace ProtectedSpan
theorem scan_first (s : State) (ts : List Token) :
    (scan s ts).first = s.first.or (ts.head?.map Token.kind) := by
  induction ts generalizing s with
  | nil => simp [scan]
  | cons t ts ih =>
    simp only [scan, List.foldl_cons] at *
    rw [ih]
    cases h : s.first <;> simp [step, h, Option.or]
theorem scan_last (s : State) (ts : List Token) :
    (scan s ts).last = (ts.getLast?.map Token.kind).or s.last := by
  induction ts generalizing s with
  | nil => simp [scan]
  | cons t ts ih =>
    simp only [scan, List.foldl_cons] at *
    rw [ih]
    cases h : ts.getLast? <;> simp [step, List.getLast?_cons, h, Option.or]
theorem scan_nonwhite (s : State) (ts : List Token) :
    (scan s ts).nonwhite = ((ts.filter (fun t => !white t)).getLast?.map Token.kind).or s.nonwhite := by
  induction ts generalizing s with
  | nil => simp [scan]
  | cons t ts ih =>
    simp only [scan, List.foldl_cons] at *
    rw [ih]
    cases hw : white t <;> cases h : (ts.filter (fun t => !white t)).getLast? <;>
      simp [step, hw, List.filter, List.getLast?_cons, h, Option.or]
theorem suffix_white (ts : List Token) : ∀ t ∈ suffix ts, white t=true := by
  intro t ht
  apply split_white ts.reverse t
  simpa [suffix] using ht

def InitialReady (ts : List Token) : Prop := ∀ t ∈ ts.head?, white t=false

theorem basePrefix_first (ts : List Token) (ready : InitialReady ts) :
    (basePrefix ts).head?=ts.head? := by
  have p := suffix_partition ts
  cases hp : basePrefix ts with
  | cons t rest => rw [hp] at p; rw [←p]; simp
  | nil =>
    have eq : suffix ts=ts := by simpa [hp] using p
    cases ts with
    | nil => simp
    | cons t rest =>
      have hw := suffix_white (t::rest) t (by simp [eq])
      have hn := ready t (by simp)
      simp [hw] at hn

theorem metadata_first (ts : List Token) (ready : InitialReady ts) :
    (scan {} ts).first=(retained ts).head?.map Token.kind := by
  rw [scan_first]
  unfold retained
  split
  · rfl
  · rw [basePrefix_first ts ready]
    rfl

theorem suffix_last_white (ts : List Token) (co : coalesced ts.reverse)
    (t : Token) (last : ts.getLast?=some t) (white_t : white t=true) : suffix ts=[t] := by
  have head : ts.reverse.head?=some t := by simpa using last
  cases hr : ts.reverse with
  | nil => simp [hr] at head
  | cons u rest =>
    have eq : u=t := by simpa [hr] using head
    subst u
    have hco : coalesced (t::rest) := by simpa [hr] using co
    simp [suffix,hr,split_coalesced _ hco,white_t]

def lastMetadata (ts : List Token) : Option Kind :=
  if (scan {} ts).trailing>0 then (scan {} ts).nonwhite else (scan {} ts).last

theorem metadata_last (ts : List Token) (co : coalesced ts.reverse)
    (positive : ∀ t ∈ ts, t.raw≠[]) :
    lastMetadata ts=(retained ts).getLast?.map Token.kind := by
  by_cases hp : protect ts=true
  · simp [lastMetadata,protected_extent_zero ts co hp,scan_last,retained,hp]
  · have hn : protect ts=false := by simpa using hp
    simp only [retained,hn,Bool.false_eq_true,↓reduceIte,basePrefix_last]
    unfold lastMetadata
    rw [scan_nonwhite,scan_last]
    cases hl : ts.getLast? with
    | none =>
      have empty : ts=[] := List.getLast?_eq_none_iff.mp hl
      subst ts
      rfl
    | some t =>
      have member : t∈ts := List.mem_of_getLast? hl
      cases hw : white t with
      | true =>
        have suffix_eq := suffix_last_white ts co t hl hw
        have extent : (scan {} ts).trailing=t.raw.length := by
          rw [←removed_extent ts co]
          simp [removed,hn,suffix_eq,bytes]
        have pos : 0<t.raw.length := List.length_pos_iff.mpr (positive t member)
        simp [extent,pos]
      | false =>
        have last_nonwhite : (ts.filter (fun t => !white t)).getLast?=some t := by
          have head : ts.reverse.head?=some t := by simpa using hl
          cases hr : ts.reverse with
          | nil => simp [hr] at head
          | cons u rest =>
            have eq : u=t := by simpa [hr] using head
            subst u
            rw [←List.head?_reverse,←List.filter_reverse,hr]
            simp [List.filter,hw]
        have extent : (scan {} ts).trailing=0 := by
          rw [trailing_reference]
          have head : ts.reverse.head?=some t := by simpa using hl
          cases hr : ts.reverse with
          | nil => simp [hr] at head
          | cons u rest =>
            have eq : u=t := by simpa [hr] using head
            subst u
            simp [lastTwoExtent,hw]
        simp [extent,last_nonwhite]

theorem stored_observations (ts : List Token) (co : coalesced ts.reverse)
    (positive : ∀ t∈ts,t.raw≠[]) (ready : InitialReady ts) :
    stored ts=bytes (retained ts) ∧
    (scan {} ts).first=(retained ts).head?.map Token.kind ∧
    lastMetadata ts=(retained ts).getLast?.map Token.kind :=
  ⟨exact_prefix ts co,metadata_first ts ready,metadata_last ts co positive⟩

end ProtectedSpan
