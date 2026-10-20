import Chunks

namespace VariableOrigin

def takeBytes : Nat → List Char → List Char
  | _, [] => []
  | n, c :: cs => if c.utf8Size ≤ n then c :: takeBytes (n - c.utf8Size) cs else []

def dropBytes : Nat → List Char → List Char
  | _, [] => []
  | n, c :: cs => if c.utf8Size ≤ n then dropBytes (n - c.utf8Size) cs else c :: cs

@[simp] theorem takeBytes_zero (s : List Char) : takeBytes 0 s = [] := by
  cases s with
  | nil => rfl
  | cons c cs => have h := Char.utf8Size_pos c; simp [takeBytes,show ¬ c.utf8Size ≤ 0 by omega]

@[simp] theorem dropBytes_zero (s : List Char) : dropBytes 0 s = s := by
  cases s with
  | nil => rfl
  | cons c cs => have h := Char.utf8Size_pos c; simp [dropBytes,show ¬ c.utf8Size ≤ 0 by omega]

theorem takeBytes_prefix (a b : List Char) : takeBytes (byteLength a) (a ++ b) = a := by
  induction a with
  | nil => simp
  | cons c cs ih => simp [byteLength,takeBytes,ih]

theorem dropBytes_prefix (a b : List Char) : dropBytes (byteLength a) (a ++ b) = b := by
  induction a with
  | nil => simp
  | cons c cs ih => simp [byteLength,dropBytes,ih]

def byteSlice (s : List Char) (start stop : Nat) := takeBytes (stop-start) (dropBytes start s)

theorem slice_exact (before inside after : List Char) :
    byteSlice (before ++ inside ++ after) (byteLength before)
      (byteLength (before ++ inside)) = inside := by
  simp only [byteSlice,byteLength_append,Nat.add_sub_cancel_left,List.append_assoc]
  rw [dropBytes_prefix, takeBytes_prefix]

theorem safe_slice_decomposition (text : List Char) (start stop : Nat)
    (h : SliceWitness text start stop) :
    ∃ before after, text = before ++ byteSlice text start stop ++ after ∧
      byteLength before = start ∧ byteLength (byteSlice text start stop) = stop-start := by
  obtain ⟨before,inside,after,rfl,rfl,rfl⟩ := h
  rw [slice_exact]
  exact ⟨before,after,rfl,rfl,by simp⟩

end VariableOrigin
