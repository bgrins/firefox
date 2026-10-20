import ProtectedMetadata
set_option autoImplicit false
namespace ProtectedSpan

def skipInitial : List Token → List Token
  | [] => []
  | t::ts => if white t then ts else t::ts

theorem initial_ready (ts : List Token) (h : coalesced ts) : InitialReady (skipInitial ts) := by
  cases ts with
  | nil => simp [skipInitial,InitialReady]
  | cons t ts =>
    cases hw : white t with
    | false => simp [skipInitial,hw,InitialReady]
    | true =>
      cases ts with
      | nil => simp [skipInitial,hw,InitialReady]
      | cons u rest =>
        have hu : white u=false := by
          cases hu : white u
          · rfl
          · exact False.elim (h.1 ⟨hw,hu⟩)
        simp [skipInitial,hw,hu,InitialReady]

theorem trailing_nonwhite (ts : List Token) (t : Token)
    (last : ts.getLast?=some t) (hw : white t=false) : (scan {} ts).trailing=0 := by
  rw [trailing_reference]
  have head : ts.reverse.head?=some t := by simpa using last
  cases hr : ts.reverse with
  | nil => simp [hr] at head
  | cons u rest =>
    have eq : u=t := by simpa [hr] using head
    subst u
    simp [lastTwoExtent,hw]

def completed (ts : List Token) (dropCount : Nat) (closers : List UInt8) : List UInt8 :=
  (bytes ts).take ((bytes ts).length-dropCount) ++ closers

def finishStored (ts : List Token) (dropCount : Nat) (closers : List UInt8) : List UInt8 :=
  let raw := completed ts dropCount closers
  raw.take (raw.length-(scan {} ts).trailing)

def EOFReady (ts : List Token) (dropCount : Nat) (closers : List UInt8) : Prop :=
  dropCount≤(bytes ts).length ∧
  (dropCount≠0 ∨ closers≠[] → ∃ t, ts.getLast?=some t ∧ white t=false)

theorem repaired_no_trim (ts : List Token) (d : Nat) (cs : List UInt8)
    (h : EOFReady ts d cs) (changed : d≠0 ∨ cs≠[]) :
    finishStored ts d cs=completed ts d cs := by
  obtain ⟨t,last,hw⟩ := h.2 changed
  simp [finishStored,trailing_nonwhite ts t last hw]

theorem finish_partition (ts : List Token) (d : Nat) (cs : List UInt8)
    (h : EOFReady ts d cs) (co : coalesced ts.reverse) :
    finishStored ts d cs = if d=0 ∧ cs=[] then bytes (retained ts) else completed ts d cs := by
  by_cases identity : d=0 ∧ cs=[]
  · rcases identity with ⟨rfl,rfl⟩
    simpa [finishStored,completed,stored] using exact_prefix ts co
  · have changed : d≠0 ∨ cs≠[] := by
      by_cases hd : d=0
      · exact Or.inr (fun hc => identity ⟨hd,hc⟩)
      · exact Or.inl hd
    simp [identity,repaired_no_trim ts d cs h changed]

theorem retained_slice (ts : List Token) (co : coalesced ts.reverse)
    (start stop : Nat) (bound : stop≤(bytes (retained ts)).length) :
    ((stored ts).take stop).drop start=((bytes ts).take stop).drop start := by
  rw [exact_prefix ts co]
  have partition := congrArg bytes (retained_partition ts)
  rw [bytes_append] at partition
  rw [←partition,List.take_append]
  have length : stop-(bytes (retained ts)).length=0 := by omega
  simp [length]

theorem adjacent_backslash_keeps_whitespace (before : List Token) (b w : Token)
    (backslash : b.backslash=true) (whitespace : white w=true) :
    stored (before++[b,w])=bytes (before++[b,w]) := by
  unfold stored
  rw [scan_append]
  simp [scan,step,backslash,whitespace]

theorem protected_component (ts : List Token) (co : coalesced ts.reverse)
    (followed : Followed ts) (positive : ∀ t∈ts,t.raw≠[]) (ready : InitialReady ts) :
    persistent ts=protect ts ∧
    stored ts=bytes (retained ts) ∧
    (scan {} ts).first=(retained ts).head?.map Token.kind ∧
    lastMetadata ts=(retained ts).getLast?.map Token.kind :=
  ⟨admitted_standalone_guard ts followed,stored_observations ts co positive ready⟩

end ProtectedSpan
