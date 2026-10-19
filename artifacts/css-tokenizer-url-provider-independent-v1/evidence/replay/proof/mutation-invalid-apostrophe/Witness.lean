import BadURL
import Escape
set_option maxRecDepth 4096
set_option maxHeartbeats 4000000
namespace Mutation
abbrev Byte := BadURL.Byte
inductive Action where
 | copy | close | invalid | space | nul | escape
 deriving DecidableEq, Repr
inductive Kind where
 | url | bad
 deriving DecidableEq, Repr
structure Value where
 kind : Kind
 output : List Byte
 count : Nat
 deriving DecidableEq, Repr

def nativeWhitespace (b : Byte) : Bool := b == 32 || b == 9 || b == 10 || b == 12 || b == 13
def referenceWhitespace (b : Byte) : Bool := ([9,10,12,13,32] : List Byte).contains b

def nativeClass (b : Byte) : Action :=
 if nativeWhitespace b then .space
 else if b == 41 then .close
 else if (1 ≤ b.val ∧ b.val ≤ 8) ∨ b.val = 11 ∨ (14 ≤ b.val ∧ b.val ≤ 31) ∨
     b.val = 127 ∨ b.val = 34 ∨ b.val = 39 ∨ b.val = 40 then .invalid
 else if b == 92 then .escape else if b == 0 then .nul else .copy

def referenceClass (b : Byte) : Action :=
 if referenceWhitespace b then .space
 else if ([34,40] : List Byte).contains b ∨ b.val ∈ [1,2,3,4,5,6,7,8,11,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,127] then .invalid
 else if b == 0 then .nul else if b == 41 then .close else if b == 92 then .escape else .copy


example : nativeClass 39 ≠ referenceClass 39 := by decide
end Mutation
