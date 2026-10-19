import CommentExecution
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
namespace CommentNativeBounds
open CommentScan CommentObservers CommentExecution

def sourceColumn (offset lineStart : Int) : Int := offset-lineStart+1

theorem ordinary_column (offset lineStart : Int) :
    sourceColumn (offset+1) lineStart = sourceColumn offset lineStart+1 := by unfold sourceColumn; omega

theorem continuation_column (offset lineStart : Int) :
    sourceColumn (offset+1) (lineStart+1) = sourceColumn offset lineStart := by unfold sourceColumn; omega

theorem four_intro_column (offset lineStart : Int) :
    sourceColumn (offset+1) (lineStart-1) = sourceColumn offset lineStart+2 := by unfold sourceColumn; omega

theorem newline_column (offset n : Int) : sourceColumn (offset+n) (offset+n) = 1 := by unfold sourceColumn; omega

theorem wrapping_projection (offset lineStart : Int) :
    ((offset%4294967296-lineStart%4294967296)%4294967296+1)%4294967296 =
      sourceColumn offset lineStart % 4294967296 := by
  unfold sourceColumn
  omega

theorem packed_line_decode (line block : Nat) (hb : block < 4) :
    (line*4+block)/4 = line := by omega

theorem packed_line_step (line block : Nat) (hb : block < 4) (hl : line+1 < 1073741824) :
    line*4+block+4 = (line+1)*4+block ∧ line*4+block+4 < 4294967296 := by omega

theorem step_bounds (r : RefState) (b : Byte) :
    (referenceStep r b).state.line ≤ r.state.line+1 ∧
    (referenceStep r b).state.column ≤ r.state.column+2 := by
  have hw : ∀ b : Byte, referenceWidth b ≤ 2 := by decide
  unfold referenceStep
  split
  · simp [newline] <;> omega
  · split
    · split <;> simp [newline] <;> omega
    · split
      · simp [newline] <;> omega
      · simp; exact hw b

theorem fold_bounds (xs : List Byte) (r : RefState) :
    (xs.foldl referenceStep r).state.line ≤ r.state.line+xs.length ∧
    (xs.foldl referenceStep r).state.column ≤ r.state.column+2*xs.length := by
  induction xs generalizing r with
  | nil => simp
  | cons b bs ih =>
    have hs := step_bounds r b
    have hi := ih (referenceStep r b)
    simp only [List.foldl_cons,List.length_cons]
    constructor <;> omega

theorem native_bounds (xs : List Byte) (s : State) :
    (nativeObserve xs s).line ≤ s.line+xs.length ∧
    (nativeObserve xs s).column ≤ s.column+2*xs.length := by
  rw [native_reference]
  exact fold_bounds xs ⟨s,false⟩

theorem run_endpoint (xs : List Byte) (s : State) :
    (run xs s).state.offset = s.offset+(scan xs).count := by
  rw [run_observer,consumed_offset,List.length_take,Nat.min_eq_left (consumed_bound xs)]

theorem raw_endpoint_bound (tail : List Byte) (s : State) :
    s.offset+2 ≤ (run tail (advance 2 s)).state.offset ∧
    (run tail (advance 2 s)).state.offset ≤ s.offset+2+tail.length := by
  rw [run_endpoint]
  have hb := consumed_bound tail
  simp only [advance]
  omega

theorem native_capacity (xs : List Byte) (s : State) (limit : Nat)
    (hp : s.offset+xs.length < limit)
    (hl : s.line+xs.length < 1073741824)
    (hc : s.column+2*xs.length < 4294967296) :
    (nativeObserve xs s).offset < limit ∧
    (nativeObserve xs s).line < 1073741824 ∧
    (nativeObserve xs s).column < 4294967296 := by
  have hb := native_bounds xs s
  rw [consumed_offset]
  omega
end CommentNativeBounds
