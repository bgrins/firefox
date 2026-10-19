import Std
namespace Utf16Repair

def valid (c : Nat) : Prop := c < 0x110000 ∧ (c < 0xD800 ∨ 0xDFFF < c)
def width (c : Nat) : Nat := if c <= 0xFFFF then 1 else 2
def encode (c : Nat) : List Nat :=
  if c <= 0xFFFF then [c]
  else [0xD800 + (c - 0x10000) / 1024, 0xDC00 + (c - 0x10000) % 1024]
def encodeRun (cs : List Nat) := cs.flatMap encode

theorem width_positive (c : Nat) : 0 < width c := by
  unfold width; split <;> omega

theorem encode_length (c : Nat) : (encode c).length = width c := by
  unfold encode width; split <;> simp

theorem valid_bmp_preserved (c : Nat) (h : c <= 0xFFFF) : encode c = [c] := by
  simp [encode,h]

theorem supplementary_roundtrip (c : Nat) (hlo : 0xFFFF < c) (hi : c < 0x110000) :
  let d := c - 0x10000
  0x10000 + (d / 1024) * 1024 + d % 1024 = c := by
  dsimp
  have h := Nat.mod_add_div (c - 0x10000) 1024
  omega

theorem supplementary_bounds (c : Nat) (hlo : 0xFFFF < c) (hi : c < 0x110000) :
  let d := c - 0x10000
  0xD800 <= 0xD800 + d / 1024 ∧ 0xD800 + d / 1024 <= 0xDBFF ∧
  0xDC00 <= 0xDC00 + d % 1024 ∧ 0xDC00 + d % 1024 <= 0xDFFF := by
  dsimp; omega

theorem run_length (cs : List Nat) : (encodeRun cs).length = (cs.map width).sum := by
  induction cs with
  | nil => simp [encodeRun]
  | cons c cs ih => simpa [encodeRun,encode_length] using congrArg (fun n => width c + n) ih

def seek : List Nat → Nat
 | [] => 0
 | c::cs => width c + seek cs

theorem seek_coordinates (cs : List Nat) : seek cs = (encodeRun cs).length := by
  induction cs with
  | nil => rfl
  | cons c cs ih => simp [seek,encodeRun,encode_length,ih]

theorem prefix_boundary_reached (leading trailing : List Nat) :
  seek leading = (encodeRun leading).length ∧
  (encodeRun (leading ++ trailing)).length = seek leading + (encodeRun trailing).length := by
  simp [seek_coordinates,encodeRun]

theorem strict_scalar_progress (leading : List Nat) (c : Nat) :
  seek leading < seek (leading ++ [c]) := by
  simp [seek_coordinates,encodeRun,encode_length]
  exact width_positive c

theorem ahom_representation : encode 0x11700 = [0xD805,0xDF00] ∧ width 0x11700 = 2 := by decide

theorem exact_witness_seek : seek [0x0E01,0x11700,0x0E01] = 4 := by decide
end Utf16Repair
