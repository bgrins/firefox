import Escape
namespace Name
open HexPrefix Escape
set_option maxRecDepth 4096
set_option maxHeartbeats 3000000

def simple (b : Byte) : Bool :=
  (97 ≤ b.val && b.val ≤ 122) || (65 ≤ b.val && b.val ≤ 90) ||
  (48 ≤ b.val && b.val ≤ 57) || b.val == 95 || b.val == 45 || (192 ≤ b.val && b.val ≤ 239)

def continuation (b : Byte) : Bool := 128 ≤ b.val && b.val ≤ 191
def fourIntro (b : Byte) : Bool := 240 ≤ b.val && b.val ≤ 255
def ordinary (b : Byte) : Bool := simple b || continuation b || fourIntro b

def referenceOrdinary (b : Byte) : Bool :=
  "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-".toList.any (fun c => c.toNat == b.val)
    || 128 ≤ b.val

theorem ordinary_classification : ∀ b : Byte, ordinary b = referenceOrdinary b := by decide

theorem nonordinary_ascii (b : Byte) (h : ordinary b = false) : b.val < 128 := by
  have hb := b.isLt
  simp [ordinary,simple,continuation,fourIntro] at h
  omega

def newlineAfter (bs : List Byte) : Bool :=
  match bs with
  | [] => false
  | b::_ => b.val == 10 || b.val == 12 || b.val == 13

structure Result where
  output : List Byte
  count : Nat
  rest : List Byte
  owned : Bool
  deriving DecidableEq, Repr

def run (owned : Bool) (xs : List Byte) : Result :=
  match xs with
  | [] => ⟨[],0,[],owned⟩
  | b::bs =>
    if ordinary b then
      let r := run owned bs
      ⟨b::r.output,r.count+1,r.rest,r.owned⟩
    else if b.val = 0 then
      let r := run true bs
      ⟨encode 65533 ++ r.output,r.count+1,r.rest,r.owned⟩
    else if b.val = 92 then
      if newlineAfter bs then ⟨[],0,b::bs,true⟩
      else
        let e := Escape.native bs
        let r := run true (bs.drop e.count)
        ⟨e.output ++ r.output,1+e.count+r.count,r.rest,r.owned⟩
    else ⟨[],0,b::bs,owned⟩
termination_by xs.length
decreasing_by all_goals simp_wf <;> omega

theorem ordinary_prefix (owned : Bool) (pre suffix : List Byte)
    (h : ∀ b ∈ pre, ordinary b = true) :
    run owned (pre ++ suffix) =
      let r := run owned suffix
      ⟨pre ++ r.output, pre.length + r.count, r.rest, r.owned⟩ := by
  induction pre with
  | nil => simp
  | cons b bs ih =>
    have hb := h b (by simp)
    have ht : ∀ c ∈ bs, ordinary c = true := by intro c hc; exact h c (by simp [hc])
    simp [run,hb,ih ht,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]

theorem simple_ordinary (b : Byte) (h : simple b = true) : ordinary b = true := by
  simp [ordinary,h]

theorem fast_prefix (owned : Bool) (pre suffix : List Byte)
    (h : ∀ b ∈ pre, simple b = true) :
    run owned (pre ++ suffix) =
      let r := run owned suffix
      ⟨pre ++ r.output, pre.length + r.count, r.rest, r.owned⟩ :=
  ordinary_prefix owned pre suffix (fun b hb => simple_ordinary b (h b hb))

theorem native_fast_chunk (owned : Bool) (xs : List Byte) :
    run owned xs =
      let pre := xs.takeWhile simple
      let r := run owned (xs.dropWhile simple)
      ⟨pre ++ r.output, pre.length+r.count,r.rest,r.owned⟩ := by
  have h : ∀ b ∈ xs.takeWhile simple, simple b = true := by
    induction xs with
    | nil => simp
    | cons b bs ih =>
      cases hb : simple b <;> simp_all [hb]
  have result := fast_prefix owned (xs.takeWhile simple) (xs.dropWhile simple) h
  simpa using result

def advanceSafe (b : Byte) : Bool :=
  (b.val < 128 || (b.val &&& 240 != 240 && b.val &&& 192 != 128)) &&
    b.val != 10 && b.val != 12 && b.val != 13

theorem fast_chunk_advance_domain : ∀ b : Byte, simple b = true → advanceSafe b = true := by decide

theorem consumed_bound (owned : Bool) (xs : List Byte) : (run owned xs).count ≤ xs.length := by
  induction owned, xs using run.induct with
  | case1 owned => simp_all [run]
  | case2 owned b bs h ih => simp_all [run] <;> omega
  | case3 owned b bs h hz ih => simp_all [run] <;> omega
  | case4 owned b bs h hz hb hn => simp_all [run]
  | case5 owned b bs h hz hb hn e ih =>
      have he := Escape.consumption_bound bs
      dsimp [e] at ih
      simp [run, h, hz, hb, hn]
      simp only [List.length_drop] at ih
      omega
  | case6 owned b bs h hz hb => simp_all [run]

theorem exact_remainder (owned : Bool) (xs : List Byte) :
    (run owned xs).rest = xs.drop (run owned xs).count := by
  induction owned, xs using run.induct with
  | case1 owned => simp [run]
  | case2 owned b bs h ih => simpa [run,h] using ih
  | case3 owned b bs h hz ih => simpa [run,h,hz] using ih
  | case4 owned b bs h hz hb hn => simp [run,h,hz,hb,hn]
  | case5 owned b bs h hz hb hn e ih =>
      dsimp [e] at ih
      simp only [run, h, Bool.false_eq_true, ↓reduceIte, hz, hb, hn]
      rw [show 1 + (Escape.native bs).count + (run true (bs.drop (Escape.native bs).count)).count =
          ((Escape.native bs).count + (run true (bs.drop (Escape.native bs).count)).count) + 1 by omega]
      simpa [List.drop_drop] using ih
  | case6 owned b bs h hz hb => simp [run,h,hz,hb]

theorem positive_ordinary (owned : Bool) (b : Byte) (bs : List Byte)
    (h : ordinary b = true) : 0 < (run owned (b::bs)).count := by
  simp [run,h]

theorem positive_nul (owned : Bool) (b : Byte) (bs : List Byte)
    (h : b.val = 0) : 0 < (run owned (b::bs)).count := by
  simp [run,ordinary,simple,continuation,fourIntro,h]

theorem positive_escape (owned : Bool) (b : Byte) (bs : List Byte)
    (h : b.val = 92) (hn : newlineAfter bs = false) : 0 < (run owned (b::bs)).count := by
  simp [run,ordinary,simple,continuation,fourIntro,h,hn]
  omega

def boundary (xs : List Byte) : Prop := xs = [] ∨ ∃ b bs, xs = b::bs ∧ b.val < 128

theorem return_boundary (owned : Bool) (xs : List Byte) : boundary (run owned xs).rest := by
  induction owned, xs using run.induct with
  | case1 owned => simp [run,boundary]
  | case2 owned b bs h ih => simpa [run,h] using ih
  | case3 owned b bs h hz ih => simpa [run,h,hz] using ih
  | case4 owned b bs h hz hb hn => simp [run,h,hz,hb,hn,boundary]
  | case5 owned b bs h hz hb hn e ih => simpa [run, h, hz, hb, hn] using ih
  | case6 owned b bs h hz hb =>
      have ha : b.val < 128 := nonordinary_ascii b (by simpa using h)
      simp [run,h,hz,hb,boundary,ha]

#print axioms native_fast_chunk
#print axioms fast_chunk_advance_domain
#print axioms positive_ordinary
#print axioms positive_nul
#print axioms positive_escape
#print axioms ordinary_prefix
#print axioms fast_prefix
#print axioms exact_remainder
#print axioms ordinary_classification
#print axioms nonordinary_ascii
#print axioms consumed_bound
#print axioms return_boundary
end Name
