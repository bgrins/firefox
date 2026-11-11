import Std
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
namespace NumericDigits
abbrev Byte := Fin 256

def digit (b : Byte) : Bool := 48 ≤ b.val && b.val ≤ 57

def referenceDigit (b : Byte) : Bool :=
  "0123456789".toList.any (fun c => c.toNat == b.val)

theorem classifier : ∀ b : Byte, digit b = referenceDigit b := by decide

theorem digit_ascii (b : Byte) (h : digit b = true) : b.val < 128 := by
  simp [digit] at h
  omega

structure Scan where
  digits : List Byte
  rest : List Byte
  reads : List Nat
  deriving DecidableEq, Repr

def scan : List Byte → Scan
  | [] => ⟨[],[],[]⟩
  | b::bs =>
    if digit b then
      let r := scan bs
      ⟨b::r.digits,r.rest,0::r.reads.map (·+1)⟩
    else ⟨[],b::bs,[0]⟩

def reference (xs : List Byte) : List Byte × List Byte :=
  (xs.takeWhile referenceDigit,xs.dropWhile referenceDigit)

theorem scan_reference (xs : List Byte) (impossible : False) :
    ((scan xs).digits,(scan xs).rest) = reference xs := False.elim impossible

end NumericDigits
