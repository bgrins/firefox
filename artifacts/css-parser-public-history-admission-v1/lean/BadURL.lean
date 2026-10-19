import CommentScan
namespace BadURL
abbrev Byte := CommentScan.Byte
structure End where
  count : Nat
  closed : Bool
  deriving DecidableEq, Repr

def add (n : Nat) (r : End) : End := ⟨n+r.count,r.closed⟩

def native : List Byte → End
  | [] => ⟨0,false⟩
  | b::bs =>
    if b == 41 then ⟨1,true⟩
    else if b == 92 && (bs.head? == some 41 || bs.head? == some 92) then
      add 2 (native bs.tail)
    else add 1 (native bs)
termination_by xs => xs.length

-- The reference labels each source byte with the parity of its preceding slash run.
def labels : Bool → List Byte → List Bool
  | _, [] => []
  | escaped, b::bs => (b == 41 && !escaped) :: labels (b == 92 && !escaped) bs

def reference (xs : List Byte) : End :=
  let position := (labels false xs).findIdx id
  ⟨if position < xs.length then position+1 else position, position < xs.length⟩

def scan : Bool → List Byte → End
  | _, [] => ⟨0,false⟩
  | escaped, b::bs =>
    if b == 41 && !escaped then ⟨1,true⟩
    else add 1 (scan (b == 92 && !escaped) bs)

theorem labels_length (escaped) (xs : List Byte) : (labels escaped xs).length = xs.length := by
  induction xs generalizing escaped with
  | nil => rfl
  | cons b bs ih => simp [labels,ih]

theorem index_bound (escaped) (xs : List Byte) : (labels escaped xs).findIdx id ≤ xs.length := by
  simpa [labels_length] using List.findIdx_le_length (p:=id) (xs:=labels escaped xs)

theorem scan_index (escaped) (xs : List Byte) :
    scan escaped xs = let n := (labels escaped xs).findIdx id
      End.mk (if n < xs.length then n+1 else n) (n < xs.length) := by
  induction xs generalizing escaped with
  | nil => simp [scan,labels]
  | cons b bs ih =>
    by_cases h : (b == 41 && !escaped) = true
    · simp [scan,labels,h,List.findIdx_cons]
    · have hf : (b == 41 && !escaped) = false := by simpa using h
      simp only [scan,h,↓reduceIte,ih,labels,List.findIdx_cons,hf,↓reduceIte,List.length_cons]
      have hb := index_bound (b == 92 && !escaped) bs
      by_cases hn : (labels (b == 92 && !escaped) bs).findIdx id < bs.length
      · simp [add,hn,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]
      · have he : (labels (b == 92 && !escaped) bs).findIdx id = bs.length := by omega
        simp [he,add,Nat.add_comm]

theorem native_scan (xs : List Byte) : native xs = scan false xs := by
  induction xs using native.induct with
  | case1 => simp [native,scan]
  | case2 b bs h => simp [native,scan,h]
  | case3 b bs h pair ih =>
    cases bs with
    | nil => simp at pair
    | cons c cs =>
      simp only [Bool.and_eq_true,beq_iff_eq,List.head?_cons,Bool.or_eq_true,Option.some.injEq] at pair
      obtain ⟨rfl,hc⟩ := pair
      rcases hc with rfl | rfl <;> simp only [List.tail_cons] at ih <;>
        simp [native,scan,ih,add,← Nat.add_assoc]
  | case4 b bs h pair ih =>
    by_cases slash : b = 92
    · subst b
      cases bs with
      | nil => simp [native,scan,add]
      | cons c cs =>
        have hc : c ≠ 41 ∧ c ≠ 92 := by simpa using pair
        have hc92 : (c == 92) = false := by simpa using hc.2
        simp [scan,hc,hc92,add] at ih ⊢
        simp [native,hc,hc92,ih,add,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]
    · have hs : (b == 92) = false := by simpa using slash
      simp [native,h,pair,scan,hs,ih]

theorem native_reference (xs : List Byte) : native xs = reference xs := by
  rw [native_scan,scan_index]
  rfl

theorem bounded (xs : List Byte) : (native xs).count ≤ xs.length := by
  rw [native_reference]
  have h := index_bound false xs
  simp only [reference]
  split <;> omega

theorem positive (b : Byte) (bs : List Byte) : 0 < (native (b::bs)).count := by
  simp only [native]
  split
  · decide
  · split <;> simp [add] <;> omega


end BadURL
