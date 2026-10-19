import CommentScan
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
namespace CommentObservers
open CommentScan
structure State where
  offset : Nat
  line : Nat
  column : Nat
  deriving DecidableEq, Repr

def advance (n : Nat) (s : State) : State := ⟨s.offset+n,s.line,s.column+n⟩
def newline (n : Nat) (s : State) : State := ⟨s.offset+n,s.line+1,1⟩
def nativeWidth (b : Byte) : Nat :=
  if 128 ≤ b.val ∧ b.val ≤ 191 then 0 else if 240 ≤ b.val then 2 else 1

def referenceWidth (b : Byte) : Nat :=
  if b.val < 128 then 1 else if b.val < 192 then 0 else if b.val < 240 then 1 else 2

theorem width_classification : ∀ b : Byte, nativeWidth b = referenceWidth b := by decide

def ordinary (b : Byte) (s : State) : State := ⟨s.offset+1,s.line,s.column+nativeWidth b⟩
def isNewline (b : Byte) : Bool := b == 10 || b == 12 || b == 13

def nativeObserve : List Byte → State → State
  | [], s => s
  | b::bs, s =>
    if isNewline b then
      if b == 13 && bs.head? == some 10 then nativeObserve bs.tail (newline 2 s)
      else nativeObserve bs (newline 1 s)
    else nativeObserve bs (ordinary b s)
termination_by xs => xs.length

structure RefState where
  state : State
  afterCR : Bool

def referenceStep (r : RefState) (b : Byte) : RefState :=
  if b == 13 then ⟨newline 1 r.state,true⟩
  else if b == 10 then
    if r.afterCR then ⟨⟨r.state.offset+1,r.state.line,1⟩,false⟩
    else ⟨newline 1 r.state,false⟩
  else if b == 12 then ⟨newline 1 r.state,false⟩
  else ⟨⟨r.state.offset+1,r.state.line,r.state.column+referenceWidth b⟩,false⟩

def referenceObserve (xs : List Byte) (s : State) : State :=
  (xs.foldl referenceStep ⟨s,false⟩).state

theorem irrelevant_pending (xs : List Byte) (s : State) (h : xs.head? ≠ some 10) :
    (xs.foldl referenceStep ⟨s,true⟩).state = referenceObserve xs s := by
  cases xs with
  | nil => rfl
  | cons b bs =>
    have hb : b ≠ 10 := by simpa using h
    simp only [List.foldl_cons,referenceObserve,referenceStep]
    by_cases h13 : b = 13
    · simp [h13]
    · simp [h13,hb]

theorem native_reference (xs : List Byte) (s : State) :
    nativeObserve xs s = referenceObserve xs s := by
  induction xs, s using nativeObserve.induct with
  | case1 s => simp [nativeObserve,referenceObserve]
  | case2 b bs s hn hc ih =>
    cases bs with
    | nil => simp at hc
    | cons c cs =>
      simp at hc
      obtain ⟨rfl,rfl⟩ := hc
      simpa [nativeObserve,isNewline,referenceObserve,referenceStep,newline,Nat.add_assoc] using ih
  | case3 b bs s hn hc ih =>
    simp only [isNewline,Bool.or_eq_true,beq_iff_eq] at hn
    rcases hn with (rfl | rfl) | rfl
    · simpa [nativeObserve,isNewline,referenceObserve,referenceStep] using ih
    · simpa [nativeObserve,isNewline,referenceObserve,referenceStep] using ih
    · have htail : bs.head? ≠ some 10 := by simpa using hc
      rw [nativeObserve]
      simp only [isNewline,beq_self_eq_true,Bool.or_true,↓reduceIte,hc]
      rw [ih]
      simpa [referenceObserve,referenceStep,htail] using (irrelevant_pending bs (newline 1 s) htail).symm
  | case4 b bs s hn ih =>
    have h10 : b ≠ 10 := by intro h; subst b; simp [isNewline] at hn
    have h12 : b ≠ 12 := by intro h; subst b; simp [isNewline] at hn
    have h13 : b ≠ 13 := by intro h; subst b; simp [isNewline] at hn
    simpa [nativeObserve,hn,referenceObserve,referenceStep,h10,h12,h13,ordinary,width_classification] using ih

theorem reference_offset (xs : List Byte) (r : RefState) :
    (xs.foldl referenceStep r).state.offset = r.state.offset + xs.length := by
  induction xs generalizing r with
  | nil => simp
  | cons b bs ih =>
    rw [List.foldl_cons,ih]
    have step : (referenceStep r b).state.offset = r.state.offset+1 := by
      simp only [referenceStep]
      split
      · rfl
      · split
        · split <;> rfl
        · split <;> rfl
    simp [step,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]

theorem consumed_offset (xs : List Byte) (s : State) :
    (nativeObserve xs s).offset = s.offset+xs.length := by
  rw [native_reference]
  exact reference_offset xs ⟨s,false⟩
end CommentObservers
