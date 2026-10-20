import Lean
namespace OverflowCoordinates
def q : Int := 1073741823
def lo : Int := -2147483648
def hi : Int := 2147483647
def fits (x : Int) := lo ≤ x ∧ x ≤ hi
def place (container size block : Int) := (container - size) - block
def observe (container size physical : Int) := (container - physical) - size

theorem temporary_error (t f s b : Int) :
    observe f s (place t s b) = b + (f-t) := by
  unfold observe place; omega

theorem final_coordinate (f s b : Int) :
    observe f s (place f s b) = b := by
  unfold observe place; omega

theorem skipped_coordinate (old final size block : Int) :
    observe final size (place old size block) = block + final-old := by
  unfold observe place; omega

theorem skip_requires_equal_frame (old final size block : Int) :
    observe final size (place old size block) = block ↔ final = old := by
  unfold observe place; omega

theorem ordinary_reflow_bounds (t f oldSize newSize : Int)
    (ht : 0 ≤ t ∧ t < q) (hf : 0 ≤ f ∧ f < q)
    (ho : 0 ≤ oldSize ∧ oldSize ≤ q)
    (hn : 0 ≤ newSize ∧ newSize ≤ q) :
    fits (t-oldSize) ∧ fits (oldSize-newSize) ∧
    fits ((t-oldSize)+(oldSize-newSize)) ∧
    fits (0+newSize) ∧ fits (t-(0+newSize)) ∧
    fits (f-(t-newSize)) ∧ fits ((f-(t-newSize))-newSize) := by
  unfold fits lo hi q at *; omega

theorem resized_position_exact (t oldSize newSize : Int) :
    (t-oldSize)+(oldSize-newSize) = place t newSize 0 := by
  unfold place; omega

theorem ordinary_browser_witness :
    observe (160*60) 0 (place 0 0 0) = 160*60 ∧
    observe (80*60) 0 (place (-160*60) 0 0) = 240*60 := by decide

theorem hypothetical_skipped_resize :
    observe (81*60) 0 (place (80*60) 0 0) = 60 := by decide

def horizontalRTL (c px pw cw : Int) : Int :=
  (c-cw) - ((c-px)-pw)
theorem horizontal_rtl_container_cancels (c px pw cw : Int) :
    horizontalRTL c px pw cw = px+pw-cw := by
  unfold horizontalRTL; omega

theorem horizontal_rtl_skip_no_width_dependency (old final px pw cw : Int) :
    horizontalRTL old px pw cw = horizontalRTL final px pw cw := by
  unfold horizontalRTL; omega

theorem restored_relative_offset (old final size block rel : Int) :
    (place old size block + rel) + (final-old) =
    place final size block + rel := by
  unfold place; omega

end OverflowCoordinates
#print axioms OverflowCoordinates.temporary_error
#print axioms OverflowCoordinates.final_coordinate
#print axioms OverflowCoordinates.skipped_coordinate
#print axioms OverflowCoordinates.skip_requires_equal_frame
#print axioms OverflowCoordinates.ordinary_reflow_bounds
#print axioms OverflowCoordinates.resized_position_exact
#print axioms OverflowCoordinates.ordinary_browser_witness
#print axioms OverflowCoordinates.hypothetical_skipped_resize
#print axioms OverflowCoordinates.horizontal_rtl_container_cancels
#print axioms OverflowCoordinates.horizontal_rtl_skip_no_width_dependency
#print axioms OverflowCoordinates.restored_relative_offset
