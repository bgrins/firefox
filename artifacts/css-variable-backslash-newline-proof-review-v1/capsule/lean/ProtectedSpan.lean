import Span
set_option autoImplicit false
namespace ProtectedSpan
abbrev Kind := TerminalSpan.Kind
structure Token where
  kind : Kind
  raw : List UInt8
  backslash : Bool
  deriving DecidableEq, Repr

def white (t : Token) : Bool := t.kind == .whitespace
def bytes (ts : List Token) : List UInt8 := ts.flatMap Token.raw

def WellFormed (t : Token) : Prop :=
  t.raw ≠ [] ∧ (t.backslash = true → t.kind = .other ∧ t.raw = [92])

structure State where
  first : Option Kind := none
  last : Option Kind := none
  nonwhite : Option Kind := none
  trailing : Nat := 0
  previousBackslash : Bool := false
  deriving DecidableEq, Repr

def step (s : State) (t : Token) : State :=
  ⟨s.first.or (some t.kind),some t.kind,
    if white t then s.nonwhite else some t.kind,
    if white t && !s.previousBackslash then t.raw.length else 0,t.backslash⟩
def scan (s : State) (ts : List Token) : State := ts.foldl step s

def persistentStep (flag : Bool) (t : Token) : Bool :=
  if white t then flag else t.backslash
def persistent (ts : List Token) : Bool := ts.foldl persistentStep false

def splitRev : List Token → List Token × List Token
  | [] => ([],[])
  | t::ts => if white t then let p := splitRev ts; (p.1,t::p.2) else (t::ts,[])
def basePrefix (ts : List Token) : List Token := (splitRev ts.reverse).1.reverse
def suffix (ts : List Token) : List Token := (splitRev ts.reverse).2.reverse
def protect (ts : List Token) : Bool :=
  !(suffix ts).isEmpty && ((basePrefix ts).getLast?.map Token.backslash).getD false
def retained (ts : List Token) : List Token := if protect ts then ts else basePrefix ts
def removed (ts : List Token) : List Token := if protect ts then [] else suffix ts

def coalesced : List Token → Prop
  | a::b::rest => ¬(white a=true ∧ white b=true) ∧ coalesced (b::rest)
  | _ => True

theorem scan_append (s : State) (a b : List Token) :
    scan s (a++b) = scan (scan s a) b := by simp [scan,List.foldl_append]

theorem scan_previous (s : State) (ts : List Token) :
    (scan s ts).previousBackslash = (ts.getLast?.map Token.backslash).getD s.previousBackslash := by
  induction ts generalizing s with
  | nil => rfl
  | cons t ts ih =>
    simp only [scan,List.foldl_cons] at *
    rw [ih]
    cases h : ts.getLast? <;> simp [step,List.getLast?_cons,h]

theorem split_partition (ts : List Token) : (splitRev ts).2 ++ (splitRev ts).1 = ts := by
  induction ts with
  | nil => rfl
  | cons t ts ih => cases h : white t <;> simp [splitRev,h,ih]

theorem suffix_partition (ts : List Token) : basePrefix ts ++ suffix ts = ts := by
  have h := congrArg List.reverse (split_partition ts.reverse)
  simpa [basePrefix,suffix,List.reverse_append] using h

theorem retained_partition (ts : List Token) : retained ts ++ removed ts = ts := by
  unfold retained removed
  split
  · simp
  · exact suffix_partition ts

theorem split_white (ts : List Token) : ∀ t ∈ (splitRev ts).2, white t=true := by
  induction ts with
  | nil => simp [splitRev]
  | cons t ts ih =>
    cases h : white t with
    | false => simp [splitRev,h]
    | true =>
      intro u hu
      simp only [splitRev,h,ite_true,List.mem_cons] at hu
      rcases hu with hu | hu
      · simpa [hu] using h
      · exact ih u hu

theorem split_coalesced (ts : List Token) (h : coalesced ts) :
    (splitRev ts).2 = match ts with | [] => [] | t::_ => if white t then [t] else [] := by
  cases ts with
  | nil => rfl
  | cons t ts =>
    cases ht : white t with
    | false => simp [splitRev,ht]
    | true =>
      cases ts with
      | nil => simp [splitRev,ht]
      | cons u us =>
        have hu : white u=false := by
          cases hu : white u
          · rfl
          · exact False.elim (h.1 ⟨ht,hu⟩)
        simp [splitRev,ht,hu]

def lastTwoExtent (reversed : List Token) : Nat :=
  match reversed with
  | [] => 0
  | t::rest => if white t && !((rest.head?.map Token.backslash).getD false) then t.raw.length else 0

theorem trailing_reference (ts : List Token) :
    (scan {} ts).trailing = lastTwoExtent ts.reverse := by
  cases hr : ts.reverse with
  | nil =>
    have empty : ts=[] := List.reverse_eq_nil_iff.mp hr
    subst ts
    rfl
  | cons t rest =>
    have equal : ts=rest.reverse++[t] := by
      have h := congrArg List.reverse hr
      simpa using h
    rw [equal,scan_append]
    change (if white t && !(scan {} rest.reverse).previousBackslash then t.raw.length else 0) = lastTwoExtent (t::rest)
    rw [scan_previous]
    simp [lastTwoExtent]

theorem removed_extent (ts : List Token) (co : coalesced ts.reverse) :
    (bytes (removed ts)).length = (scan {} ts).trailing := by
  rw [trailing_reference]
  cases hr : ts.reverse with
  | nil => simp [removed,protect,basePrefix,suffix,splitRev,hr,bytes,lastTwoExtent]
  | cons t rest =>
    cases ht : white t with
    | false => simp [removed,protect,basePrefix,suffix,splitRev,hr,ht,bytes,lastTwoExtent]
    | true =>
      cases rest with
      | nil => simp [removed,protect,basePrefix,suffix,splitRev,hr,ht,bytes,lastTwoExtent]
      | cons u us =>
        have hu : white u=false := by
          have hco : coalesced (t::u::us) := by simpa [hr] using co
          cases hu : white u
          · rfl
          · exact False.elim (hco.1 ⟨ht,hu⟩)
        cases hb : u.backslash <;>
          simp [removed,protect,basePrefix,suffix,splitRev,hr,ht,hu,hb,bytes,lastTwoExtent]

def stored (ts : List Token) : List UInt8 :=
  (bytes ts).take ((bytes ts).length-(scan {} ts).trailing)

theorem bytes_append (a b : List Token) : bytes (a++b)=bytes a++bytes b := by simp [bytes]

theorem exact_prefix (ts : List Token) (co : coalesced ts.reverse) :
    stored ts=bytes (retained ts) := by
  have p := congrArg bytes (retained_partition ts)
  rw [bytes_append] at p
  rw [stored,←removed_extent ts co,←p]
  simp

theorem trim_bound (ts : List Token) (co : coalesced ts.reverse) :
    (scan {} ts).trailing ≤ (bytes ts).length := by
  have p := congrArg bytes (retained_partition ts)
  rw [bytes_append] at p
  rw [←removed_extent ts co,←p,List.length_append]
  omega

end ProtectedSpan
