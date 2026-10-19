import Std

namespace TaintRanges

structure Span where
  start : Nat
  finish : Nat
deriving DecidableEq, Repr

def contains (r : Span) (byte : Nat) : Prop := r.start ≤ byte ∧ byte < r.finish

def overlaps (a b : Span) : Bool :=
  decide (max a.start b.start < min a.finish b.finish)

def originalOverlaps (a b : Span) : Bool :=
  decide (a.start ≤ b.finish ∧ a.finish ≥ b.start)

def blocked (taints : List Span) (url : Span) : Bool :=
  taints.any (fun taint => overlaps taint url)

theorem overlaps_iff_shared_byte (a b : Span) :
    overlaps a b = true ↔ ∃ byte, contains a byte ∧ contains b byte := by
  simp only [overlaps, decide_eq_true_eq, contains]
  constructor
  · intro h
    exact ⟨max a.start b.start, by omega⟩
  · rintro ⟨byte, ha, hb⟩
    omega

theorem symmetry (a b : Span) : overlaps a b = overlaps b a := by
  simp [overlaps, Nat.max_comm, Nat.min_comm]

theorem empty_left (point : Nat) (b : Span) :
    overlaps ⟨point,point⟩ b = false := by
  simp only [overlaps, decide_eq_false_iff_not]
  omega

theorem empty_right (a : Span) (point : Nat) :
    overlaps a ⟨point,point⟩ = false := by
  rw [symmetry, empty_left]

theorem separated (a b : Span) (h : a.finish ≤ b.start) :
    overlaps a b = false := by
  simp only [overlaps, decide_eq_false_iff_not]
  omega

theorem touching (a b : Span) (h : a.finish = b.start) :
    overlaps a b = false := separated a b (by omega)

theorem contained_nonempty (outer inner : Span)
    (lower : outer.start ≤ inner.start) (upper : inner.finish ≤ outer.finish)
    (nonempty : inner.start < inner.finish) : overlaps outer inner = true := by
  rw [overlaps_iff_shared_byte]
  exact ⟨inner.start, by simp only [contains]; omega⟩

theorem blocked_iff_shared_byte (taints : List Span) (url : Span) :
    blocked taints url = true ↔
      ∃ taint ∈ taints, ∃ byte, contains taint byte ∧ contains url byte := by
  simp only [blocked, List.any_eq_true, overlaps_iff_shared_byte]

theorem no_taint (url : Span) : blocked [] url = false := rfl

theorem append_taints (xs ys : List Span) (url : Span) :
    blocked (xs ++ ys) url = (blocked xs url || blocked ys url) := by
  simp [blocked]

theorem shift_preserves (a b : Span) (offset : Nat) :
    overlaps ⟨a.start + offset,a.finish + offset⟩
      ⟨b.start + offset,b.finish + offset⟩ = overlaps a b := by
  simp only [overlaps]
  congr 1
  apply propext
  omega

theorem original_touching_false_positive :
    originalOverlaps ⟨10,20⟩ ⟨0,10⟩ = true ∧
    overlaps ⟨10,20⟩ ⟨0,10⟩ = false := by decide

theorem original_empty_false_positive :
    originalOverlaps ⟨5,5⟩ ⟨0,10⟩ = true ∧
    overlaps ⟨5,5⟩ ⟨0,10⟩ = false := by decide

theorem strict_pairwise_empty_false_positive :
    (5 < (10 : Nat) ∧ 5 > (0 : Nat)) ∧ overlaps ⟨5,5⟩ ⟨0,10⟩ = false := by decide

end TaintRanges
