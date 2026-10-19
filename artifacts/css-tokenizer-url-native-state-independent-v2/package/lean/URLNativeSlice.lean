import URLNativeBadState
import URLTrace
set_option maxHeartbeats 2000000
namespace URLNativeSlice
open URLNativeState URLNativeBad
abbrev Byte := CommentScan.Byte

def slice (source : List Byte) (start finish : Nat) : List Byte :=
 (source.drop start).take (finish-start)

theorem close_le_count (xs : List Byte) (s : State) :
 (if (run xs s).closed then 1 else 0)≤(run xs s).count := by
 obtain ⟨hp,he,hb⟩ := positions xs s
 omega

theorem captured_range (before copied xs : List Byte) (s : State)
 (position : s.position=before.length+copied.length) :
 before.length≤(run xs s).rawEnd ∧
 (run xs s).rawEnd≤(before++copied++xs).length := by
 obtain ⟨hp,he,hb⟩ := positions xs s
 have bound := consumed_bound xs s
 simp only [List.length_append]
 omega

theorem captured_slice (before copied xs : List Byte) (s : State)
 (position : s.position=before.length+copied.length) :
 slice (before++copied++xs) before.length (run xs s).rawEnd =
 copied++xs.take ((BadURL.native xs).count-(if (BadURL.native xs).closed then 1 else 0)) := by
 have close := close_le_count xs s
 obtain ⟨hcount,hclosed⟩ := boundary xs s
 rw [hcount,hclosed] at close
 have endpoint := raw_endpoint xs s
 rw [position] at endpoint
 have length : (run xs s).rawEnd-before.length = copied.length+
   ((BadURL.native xs).count-(if (BadURL.native xs).closed then 1 else 0)) := by omega
 simp only [slice,List.append_assoc,List.drop_left,length,List.take_add,List.take_left,List.drop_left]

theorem prior_raw_model (xs : List Byte) :
 URLTrace.rawPayload (URLTrace.bad xs)=
 xs.take ((BadURL.native xs).count-(if (BadURL.native xs).closed then 1 else 0)) := by
 have bound := BadURL.bounded xs
 simp [URLTrace.rawPayload,URLTrace.bad,List.length_take,Nat.min_eq_left bound,List.take_take,Nat.min_eq_left (Nat.sub_le (BadURL.native xs).count _)]
 rfl

theorem captured_prior_raw (before copied xs : List Byte) (s : State)
 (position : s.position=before.length+copied.length) :
 slice (before++copied++xs) before.length (run xs s).rawEnd =
 copied++URLTrace.rawPayload (URLTrace.bad xs) := by
 rw [captured_slice before copied xs s position,prior_raw_model]

theorem escaped_close_eof :
 let result := run [92,41] ⟨0,0,0⟩
 result.state.position=2 ∧ result.rawEnd=2 ∧ result.closed=false ∧
 slice [92,41] 0 result.rawEnd=[92,41] := by
 simp [run,add,advance,slice]

theorem genuine_close :
 let result := run [92,41,41] ⟨0,0,0⟩
 result.state.position=3 ∧ result.rawEnd=2 ∧ result.closed=true ∧
 slice [92,41,41] 0 result.rawEnd=[92,41] := by
 simp [run,add,advance,slice]
end URLNativeSlice
