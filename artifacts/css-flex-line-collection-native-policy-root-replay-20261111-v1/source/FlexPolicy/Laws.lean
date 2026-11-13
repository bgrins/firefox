import FlexPolicy.Helpers

namespace FlexPolicy

variable {α : Type} (size : α → Rat) (threshold gap limit : Rat)

theorem ready_oversized_singleton {current : List α} (h : Ready size threshold gap current)
    (hover : threshold < FlexCollect.span size gap current) :
    ∃ x, current = [x] ∧ threshold < size x := by
  rcases h.2 with hbig | hfit
  · exact hbig
  · exact False.elim (Rat.not_le.mpr hover (prefixes_span size threshold gap hfit h.1))

theorem next_total (current : List α) (x : α) (hne : current ≠ []) :
    FlexCollect.span size gap (current ++ [x]) =
      FlexCollect.span size gap current + size x + gap := by
  rw [FlexCollect.span_snoc size gap current x hne]
  ac_rfl

theorem loop_refines (input current : List α) (hlimit : threshold < limit)
    (hready : Ready size threshold gap current) :
    loop size gap (patchedBreak threshold limit) current (FlexCollect.span size gap current) input =
      FlexCollect.collect size threshold gap (current ++ input) := by
  induction input generalizing current with
  | nil =>
    rw [loop_nil size gap _ _ hready.1,
      FlexCollect.collect_step size threshold gap (next_of_ready size threshold gap hready (rest := []) trivial)]
    rw [FlexCollect.collect]
  | cons x xs ih =>
    rw [loop_step size gap _ _ x xs hready.1]
    by_cases hc : patchedBreak threshold limit (FlexCollect.span size gap current)
        (FlexCollect.span size gap current + size x + gap) = true
    · rw [ite_eq_left hc]
      have hcut := (patchedBreak_iff threshold limit _ _ hlimit).mp hc
      rw [← next_total size gap current x hready.1] at hcut
      rw [FlexCollect.collect_step size threshold gap
        (next_of_break size threshold gap x xs hready hcut)]
      exact congrArg (List.cons current) (ih [x] (singleton_ready size threshold gap x))
    · rw [ite_eq_right hc]
      have hn : ¬(threshold < FlexCollect.span size gap current ∨
          threshold < FlexCollect.span size gap current + size x + gap) :=
        fun bad => hc ((patchedBreak_iff threshold limit _ _ hlimit).mpr bad)
      have hbound : FlexCollect.span size gap current ≤ threshold :=
        Rat.not_lt.mp (fun bad => hn (Or.inl bad))
      have hnext : FlexCollect.span size gap (current ++ [x]) ≤ threshold := by
        rw [next_total size gap current x hready.1]
        exact Rat.not_lt.mp (fun bad => hn (Or.inr bad))
      have hnextReady : Ready size threshold gap (current ++ [x]) :=
        ⟨by simp, Or.inr (prefixes_snoc size threshold gap hready.1 x
          (ready_bounded size threshold gap hready hbound) hnext)⟩
      rw [← next_total size gap current x hready.1]
      simpa only [List.append_assoc, List.singleton_append] using ih (current ++ [x]) hnextReady

theorem worker : WorkerTarget := by
  intro α size threshold gap limit current total input hlimit hready htotal
  subst total
  exact loop_refines size threshold gap limit input current hlimit hready

theorem patched_refines (input : List α) (hlimit : threshold < limit) :
    patched size threshold gap limit input = FlexCollect.collect size threshold gap input := by
  cases input with
  | nil => simp [patched, loop, FlexCollect.collect]
  | cons x xs =>
    rw [patched, loop_start size gap]
    exact loop_refines size threshold gap limit xs [x] hlimit (singleton_ready size threshold gap x)

theorem patched_collected (input : List α) (hlimit : threshold < limit) :
    FlexCollect.Collected size threshold gap input (patched size threshold gap limit input) := by
  rw [patched_refines size threshold gap limit input hlimit]
  exact FlexCollect.collect_sound size threshold gap input

theorem patched_partition (input : List α) (hlimit : threshold < limit) :
    (patched size threshold gap limit input).flatten = input := by
  rw [patched_refines size threshold gap limit input hlimit]
  exact FlexCollect.collect_flatten size threshold gap input

theorem universal : UniversalTarget := by
  intro α size threshold gap limit input
  exact patched_refines size threshold gap limit input

end FlexPolicy
