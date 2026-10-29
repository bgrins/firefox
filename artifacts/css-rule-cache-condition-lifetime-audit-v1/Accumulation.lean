import Std

namespace CacheExclusion

inductive Read where
  | covered
  | untracked
  deriving DecidableEq

def collect : Bool → List Read → Bool
  | blocked, [] => blocked
  | blocked, .covered :: rest => collect blocked rest
  | _, .untracked :: rest => collect true rest

theorem blocked_survives (reads : List Read) : collect true reads = true := by
  induction reads with
  | nil => rfl
  | cons read rest ih => cases read <;> simpa [collect] using ih

theorem append_composes (blocked : Bool) (a b : List Read) :
    collect blocked (a ++ b) = collect (collect blocked a) b := by
  induction a generalizing blocked with
  | nil => rfl
  | cons read rest ih => cases read <;> simp [collect, ih]

theorem untracked_blocks (reads : List Read) (blocked : Bool)
    (h : Read.untracked ∈ reads) : collect blocked reads = true := by
  induction reads generalizing blocked with
  | nil => simp at h
  | cons read rest ih =>
    cases read with
    | covered =>
      simp only [List.mem_cons] at h
      rcases h with impossible | member
      · cases impossible
      · exact ih blocked member
    | untracked => exact blocked_survives rest

theorem admission_requires_coverage (reads : List Read)
    (h : collect false reads = false) : Read.untracked ∉ reads := by
  intro missing
  have blocked := untracked_blocks reads false missing
  simp [h] at blocked

theorem no_later_read_reopens (earlier later : List Read)
    (h : collect false earlier = true) : collect false (earlier ++ later) = true := by
  rw [append_composes, h]
  exact blocked_survives later

end CacheExclusion
