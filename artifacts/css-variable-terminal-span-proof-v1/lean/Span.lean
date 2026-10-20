import Std
namespace TerminalSpan
inductive Kind where
  | whitespace | atKeywordOrHash | number | dimension | percentage | urlOrBadUrl
  | function | ident | cdc | dashMatch | substringMatch | openParen | delimHash
  | delimAt | delimDotOrPlus | delimMinus | delimQuestion | delimAssorted
  | delimEquals | delimBar | delimSlash | delimAsterisk | delimPercent | other
  deriving DecidableEq, Repr
structure Token where
  kind : Kind
  raw : List UInt8
  deriving DecidableEq, Repr
def white (t : Token) : Bool := t.kind == .whitespace
def bytes (ts : List Token) : List UInt8 := ts.flatMap Token.raw
theorem bytes_append (a b : List Token) : bytes (a ++ b) = bytes a ++ bytes b := by
  simp [bytes]
structure State where
  first : Option Kind := none
  last : Option Kind := none
  nonwhite : Option Kind := none
  trailing : Nat := 0
  deriving DecidableEq, Repr
def step (s : State) (t : Token) : State :=
  ⟨s.first.or (some t.kind), some t.kind,
   if white t then s.nonwhite else some t.kind,
   if white t then t.raw.length else 0⟩
def scan (s : State) (ts : List Token) : State := ts.foldl step s

theorem scan_append (s : State) (a b : List Token) :
    scan s (a ++ b) = scan (scan s a) b := by simp [scan, List.foldl_append]
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
theorem scan_trailing (s : State) (ts : List Token) :
    (scan s ts).trailing = match ts.getLast? with
      | none => s.trailing
      | some t => if white t then t.raw.length else 0 := by
  induction ts generalizing s with
  | nil => simp [scan]
  | cons t ts ih =>
    simp only [scan, List.foldl_cons] at *
    rw [ih]
    cases h : ts.getLast? <;> simp [step, List.getLast?_cons, h]

-- The reference groups the complete terminal whitespace run from the right.
def splitRev : List Token → List Token × List Token
  | [] => ([], [])
  | t :: ts => if white t then
      let p := splitRev ts
      (p.1, t :: p.2)
    else (t :: ts, [])
def retained (ts : List Token) : List Token := (splitRev ts.reverse).1.reverse
def removed (ts : List Token) : List Token := (splitRev ts.reverse).2.reverse
def coalesced : List Token → Prop
  | a :: b :: rest => ¬(white a = true ∧ white b = true) ∧ coalesced (b :: rest)
  | _ => True

theorem splitRev_partition (ts : List Token) :
    (splitRev ts).2 ++ (splitRev ts).1 = ts := by
  induction ts with
  | nil => rfl
  | cons t ts ih => cases h : white t <;> simp [splitRev, h, ih]
theorem partition (ts : List Token) : retained ts ++ removed ts = ts := by
  have h := congrArg List.reverse (splitRev_partition ts.reverse)
  simpa [retained, removed, List.reverse_append] using h

theorem splitRev_white (ts : List Token) :
    ∀ t ∈ (splitRev ts).2, white t = true := by
  induction ts with
  | nil => simp [splitRev]
  | cons t ts ih =>
    cases h : white t with
    | false => simp [splitRev, h]
    | true =>
      intro x hx
      simp only [splitRev, h, ite_true, List.mem_cons] at hx
      rcases hx with hx | hx
      · simpa [hx] using h
      · exact ih x hx

theorem splitRev_coalesced (ts : List Token) (h : coalesced ts) :
    (splitRev ts).2 = match ts with
      | [] => []
      | t :: _ => if white t then [t] else [] := by
  cases ts with
  | nil => rfl
  | cons t ts =>
    cases ht : white t with
    | false => simp [splitRev, ht]
    | true =>
      cases ts with
      | nil => simp [splitRev, ht]
      | cons u us =>
        have hu : white u = false := by
          cases hu : white u
          · rfl
          · exact False.elim (h.1 ⟨ht, hu⟩)
        simp [splitRev, ht, hu]

theorem splitRev_width (ts : List Token) (h : coalesced ts) :
    (bytes (splitRev ts).2.reverse).length = match ts.head? with
      | none => 0
      | some t => if white t then t.raw.length else 0 := by
  rw [splitRev_coalesced ts h]
  cases ts with
  | nil => rfl
  | cons t ts => cases hw : white t <;> simp [hw, bytes]

theorem removed_extent (ts : List Token) (h : coalesced ts.reverse) :
    (bytes (removed ts)).length = (scan {} ts).trailing := by
  rw [scan_trailing]
  unfold removed
  rw [splitRev_width ts.reverse h, List.head?_reverse]

def stored (ts : List Token) : List UInt8 :=
  (bytes ts).take ((bytes ts).length - (scan {} ts).trailing)

theorem exact_prefix (ts : List Token) (h : coalesced ts.reverse) :
    stored ts = bytes (retained ts) := by
  have p := congrArg bytes (partition ts)
  rw [bytes_append] at p
  rw [stored, ← removed_extent ts h]
  rw [← p]
  simp

theorem trim_bound (ts : List Token) (h : coalesced ts.reverse) :
    (scan {} ts).trailing ≤ (bytes ts).length := by
  have p := congrArg bytes (partition ts)
  rw [bytes_append] at p
  rw [← removed_extent ts h, ← p, List.length_append]
  omega

theorem preserved_token_bytes (ts : List Token) (h : coalesced ts.reverse)
    (left right : List Token) (hp : retained ts = left ++ right) :
    stored ts = bytes left ++ bytes right := by
  rw [exact_prefix ts h, hp]
  simp [bytes]
theorem splitRev_head (ts : List Token) :
    (splitRev ts).1.head? = (ts.filter (fun t => !white t)).head? := by
  induction ts with
  | nil => rfl
  | cons t ts ih => cases h : white t <;> simp [splitRev, List.filter, h, ih]

theorem retained_last (ts : List Token) :
    (retained ts).getLast? = (ts.filter (fun t => !white t)).getLast? := by
  have h := splitRev_head ts.reverse
  simpa [retained, ← List.head?_reverse, List.filter_reverse] using h

theorem removed_all_white (ts : List Token) :
    ∀ t ∈ removed ts, white t = true := by
  intro t ht
  apply splitRev_white ts.reverse t
  simpa [removed] using ht

def lastMetadata (ts : List Token) : Option Kind :=
  if (scan {} ts).trailing > 0 then (scan {} ts).nonwhite else (scan {} ts).last

theorem metadata_last (ts : List Token) (positive : ∀ t ∈ ts, t.raw ≠ []) :
    lastMetadata ts = (retained ts).getLast?.map Token.kind := by
  rw [retained_last]
  unfold lastMetadata
  rw [scan_trailing, scan_nonwhite, scan_last]
  cases h : ts.getLast? with
  | none =>
    have : ts = [] := List.getLast?_eq_none_iff.mp h
    subst ts
    rfl
  | some t =>
    have mem : t ∈ ts := List.mem_of_getLast? h
    have hp : 0 < t.raw.length := List.length_pos_iff.mpr (positive t mem)
    cases hw : white t with
    | true => simp [hw, hp]
    | false =>
      have hf : (ts.filter (fun t => !white t)).getLast? = some t := by
        have hr : ts.reverse.head? = some t := by simpa using h
        cases rev : ts.reverse with
        | nil => simp [rev] at hr
        | cons u us =>
          have hu : u = t := by simpa [rev] using hr
          subst u
          rw [← List.head?_reverse, ← List.filter_reverse, rev]
          simp [List.filter, hw]
      simp [hw, hf]

def InitialReady (ts : List Token) : Prop := ∀ t ∈ ts.head?, white t = false

theorem retained_first (ts : List Token) (ready : InitialReady ts) :
    (retained ts).head? = ts.head? := by
  have p := partition ts
  cases hr : retained ts with
  | cons t rest =>
    rw [hr] at p
    rw [← p]
    simp
  | nil =>
    have he : removed ts = ts := by simpa [hr] using p
    cases ts with
    | nil => simp
    | cons t rest =>
      have hw := removed_all_white (t :: rest) t (by simp [he])
      have hn := ready t (by simp)
      simp [hw] at hn

theorem metadata_first (ts : List Token) (ready : InitialReady ts) :
    (scan {} ts).first = (retained ts).head?.map Token.kind := by
  rw [scan_first, retained_first ts ready]
  rfl

def skipInitial : List Token → List Token
  | [] => []
  | t :: ts => if white t then ts else t :: ts

theorem initial_ready (ts : List Token) (h : coalesced ts) :
    InitialReady (skipInitial ts) := by
  cases ts with
  | nil => simp [skipInitial, InitialReady]
  | cons t ts =>
    cases hw : white t with
    | false => simp [skipInitial, hw, InitialReady]
    | true =>
      cases ts with
      | nil => simp [skipInitial, hw, InitialReady]
      | cons u us =>
        have hu : white u = false := by
          cases hu : white u
          · rfl
          · exact False.elim (h.1 ⟨hw, hu⟩)
        simp [skipInitial, hw, hu, InitialReady]
def storedAfterLeading (ts : List Token) (n : Nat) : List UInt8 :=
  let raw := (bytes ts).drop n
  raw.take (raw.length - (scan {} ts).trailing)

theorem leading_overlap (ts : List Token) (h : coalesced ts.reverse) (n : Nat) :
    storedAfterLeading ts n = (bytes (retained ts)).drop n := by
  have p := congrArg bytes (partition ts)
  rw [bytes_append] at p
  dsimp only [storedAfterLeading]
  rw [← removed_extent ts h, ← p, List.length_drop, List.length_append]
  have hn : (bytes (retained ts)).length + (bytes (removed ts)).length - n -
      (bytes (removed ts)).length = (bytes (retained ts)).length - n := by omega
  rw [hn, ← List.drop_take]
  simp

def completed (ts : List Token) (dropCount : Nat) (closers : List UInt8) : List UInt8 :=
  (bytes ts).take ((bytes ts).length - dropCount) ++ closers

def finishStored (ts : List Token) (dropCount : Nat) (closers : List UInt8) : List UInt8 :=
  let raw := completed ts dropCount closers
  raw.take (raw.length - (scan {} ts).trailing)

def EOFReady (ts : List Token) (dropCount : Nat) (closers : List UInt8) : Prop :=
  dropCount ≤ (bytes ts).length ∧
  (dropCount ≠ 0 ∨ closers ≠ [] → ∃ t, ts.getLast? = some t ∧ white t = false)

theorem repaired_no_trim (ts : List Token) (d : Nat) (cs : List UInt8)
    (h : EOFReady ts d cs) (changed : d ≠ 0 ∨ cs ≠ []) :
    finishStored ts d cs = completed ts d cs := by
  obtain ⟨t, ht, hw⟩ := h.2 changed
  have hz : (scan {} ts).trailing = 0 := by rw [scan_trailing, ht]; simp [hw]
  simp [finishStored, hz]

theorem finish_partition (ts : List Token) (d : Nat) (cs : List UInt8)
    (h : EOFReady ts d cs) (co : coalesced ts.reverse) :
    finishStored ts d cs = if d = 0 ∧ cs = [] then bytes (retained ts)
      else completed ts d cs := by
  by_cases hi : d = 0 ∧ cs = []
  · rcases hi with ⟨rfl, rfl⟩
    simpa [finishStored, completed, stored] using exact_prefix ts co
  · have changed : d ≠ 0 ∨ cs ≠ [] := by
      by_cases hd : d = 0
      · exact Or.inr (fun hc => hi ⟨hd, hc⟩)
      · exact Or.inl hd
    simp [hi, repaired_no_trim ts d cs h changed]

theorem retained_slice (ts : List Token) (co : coalesced ts.reverse)
    (start stop : Nat) (bound : stop ≤ (bytes (retained ts)).length) :
    ((stored ts).take stop).drop start = ((bytes ts).take stop).drop start := by
  rw [exact_prefix ts co]
  have p := congrArg bytes (partition ts)
  rw [bytes_append] at p
  rw [← p, List.take_append]
  have hs : stop - (bytes (retained ts)).length = 0 := by omega
  simp [hs]
theorem stored_observations (ts : List Token) (co : coalesced ts.reverse)
    (positive : ∀ t ∈ ts, t.raw ≠ []) (ready : InitialReady ts) :
    stored ts = bytes (retained ts) ∧
    (scan {} ts).first = (retained ts).head?.map Token.kind ∧
    lastMetadata ts = (retained ts).getLast?.map Token.kind :=
  ⟨exact_prefix ts co, metadata_first ts ready, metadata_last ts positive⟩
end TerminalSpan
