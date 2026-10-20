import Std
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
namespace CommentScan
abbrev Byte := Fin 256
structure Result where
  body : List Byte
  count : Nat
  closed : Bool
  deriving DecidableEq, Repr

def stop (b : Byte) (bs : List Byte) : Bool := b == 42 && bs.head? == some 47

def scan : List Byte → Result
  | [] => ⟨[],0,false⟩
  | b::bs =>
    if stop b bs then ⟨[],2,true⟩
    else let r := scan bs; ⟨b::r.body,r.count+1,r.closed⟩

def marks (xs : List Byte) : List Bool :=
  xs.zipWith (fun b n => b == 42 && n == some 47) (xs.tail.map some ++ [none])
def index (xs : List Byte) : Nat := (marks xs).findIdx id

theorem marks_cons (b : Byte) (bs : List Byte) : marks (b::bs) = stop b bs :: marks bs := by
  cases bs <;> simp [marks,stop]

theorem index_cons (b : Byte) (bs : List Byte) :
    index (b::bs) = if stop b bs then 0 else index bs + 1 := by
  simp [index,marks_cons,List.findIdx_cons]

theorem marks_length (xs : List Byte) : (marks xs).length = xs.length := by
  induction xs with
  | nil => rfl
  | cons b bs ih => simp [marks_cons,ih]

theorem index_bound (xs : List Byte) : index xs ≤ xs.length := by
  have h := List.findIdx_le_length (p := id) (xs := marks xs)
  simpa [index,marks_length] using h

def reference (xs : List Byte) : Result :=
  let n := index xs
  ⟨xs.take n, if n < xs.length then n+2 else n, n < xs.length⟩

theorem scan_reference (xs : List Byte) : scan xs = reference xs := by
  induction xs with
  | nil => rfl
  | cons b bs ih =>
    by_cases h : stop b bs = true
    · simp [scan,h,reference,index_cons,h]
    · have hf : stop b bs = false := by simp [Bool.eq_false_iff,h]
      rw [scan,if_neg h,ih]
      simp only [reference,index_cons,hf,Bool.false_eq_true,↓reduceIte,List.length_cons]
      by_cases hn : index bs < bs.length
      · simp [hn, Nat.add_lt_add_iff_right, Nat.add_assoc]
      · have he : index bs = bs.length := by have := index_bound bs; omega
        simp [he]

theorem stop_tail (b : Byte) (bs : List Byte) (h : stop b bs = true) : ∃ tail, b = 42 ∧ bs = 47::tail := by
  cases bs with
  | nil => simp [stop] at h
  | cons c cs =>
    simp [stop] at h
    exact ⟨cs,h.1,by simp [h.2]⟩

theorem consumed_bound (xs : List Byte) : (scan xs).count ≤ xs.length := by
  induction xs with
  | nil => simp [scan]
  | cons b bs ih =>
    by_cases h : stop b bs = true
    · obtain ⟨tail,rfl,rfl⟩ := stop_tail b bs h
      simp [scan,stop]
    · simp [scan,h]; omega

theorem body_count (xs : List Byte) :
    (scan xs).body.length + (if (scan xs).closed then 2 else 0) = (scan xs).count := by
  induction xs with
  | nil => rfl
  | cons b bs ih =>
    by_cases h : stop b bs = true
    · simp [scan,h]
    · simp [scan,h]
      omega

theorem exact_body (xs : List Byte) : (scan xs).body = xs.take (index xs) := by
  rw [scan_reference]; rfl

theorem remainder_decomposition (xs : List Byte) :
    xs.take (scan xs).count ++ xs.drop (scan xs).count = xs := List.take_append_drop _ _

def grouped : List Byte → Result
  | [] => ⟨[],0,false⟩
  | b::bs =>
    if stop b bs then ⟨[],2,true⟩
    else if b == 13 && bs.head? == some 10 then
      let r := grouped bs.tail; ⟨b::10::r.body,r.count+2,r.closed⟩
    else let r := grouped bs; ⟨b::r.body,r.count+1,r.closed⟩
termination_by xs => xs.length

theorem grouped_scan (xs : List Byte) : grouped xs = scan xs := by
  induction xs using grouped.induct with
  | case1 => simp [grouped,scan]
  | case2 b bs h => simp [grouped,h,scan]
  | case3 b bs h hcr ih =>
    cases bs with
    | nil => simp at hcr
    | cons c cs =>
      simp at hcr
      obtain ⟨rfl,rfl⟩ := hcr
      simp only [List.tail_cons] at ih
      simp [grouped,stop,ih,scan,Nat.add_assoc]
  | case4 b bs h hcr ih => simp [grouped,h,hcr,scan,ih]
end CommentScan
