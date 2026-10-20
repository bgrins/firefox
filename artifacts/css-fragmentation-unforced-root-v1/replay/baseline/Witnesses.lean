import Emergency
namespace Fragmentation

def box (id extent : Nat) : Atom := ⟨.box id, extent⟩
def atA (cut : Nat) : Opportunity := { cut, kind := .a, controls := [.auto, .auto] }
def three : Input :=
  { types := {page := true}, content := [box 0 1, box 1 1, box 2 1],
    opportunities := [atA 1, atA 2], capacity := 2 }
def sevenLines : List Atom := (List.range 7).map (fun n => ⟨.line 8 n, 1⟩)
def linePoint (cut : Nat) : Opportunity :=
  { cut, kind := .b 8, orphans := 3, widows := 2 }
def lineInput : Input :=
  { types := {page := true}, content := sevenLines,
    opportunities := [linePoint 2, linePoint 3, linePoint 4, linePoint 6], capacity := 2 }
def avoidInput : Input :=
  { three with opportunities := [{ (atA 1) with controls := [.avoid] }] }
def decorationsInput (cap : Nat) (cloned : Bool) : Input :=
  { types := {page := true}, content := [box 0 2, box 1 2],
    opportunities := [atA 1], decorations := [⟨1, 2, cloned⟩], capacity := cap }
def graphic : Input :=
  { types := {page := true}, content := [⟨.graphic 7, 5⟩], opportunities := [], capacity := 2 }
def regionInput : Input :=
  { types := {page := true}, content := [box 0 4, box 1 1],
    opportunities := [atA 1], capacity := 2 }
def zeroInput : Input :=
  { types := {page := true}, content := [box 0 1, box 1 0, box 2 1],
    opportunities := [atA 1, atA 2], capacity := 1 }

theorem typed_avoidance_witness :
    rules .strict {page := true} [] { (atA 1) with controls := [.avoidColumn] } = true ∧
    rules .strict {page := true, column := true} []
      { (atA 1) with controls := [.avoidColumn] } = false := by decide

theorem common_ancestor_witness :
    rules .strict three.types three.content
      { (atA 1) with commonAncestors := [.avoid] } = false ∧
    rules .strict three.types three.content
      { (atA 1) with controls := [.avoidColumn], commonAncestors := [.avoid] } = true := by decide

theorem line_counts_witness :
    (List.map (rules .strict {page := true} sevenLines) [linePoint 2, linePoint 3, linePoint 4, linePoint 5, linePoint 6]) =
      [false, true, true, true, false] ∧ lineCount 99 sevenLines = 0 := by decide

theorem strict_inhabited : scan three stages = some (.strict, .cut (atA 1)) := by decide

theorem lines_inhabited : scan lineInput stages = some (.lines, .cut (linePoint 2)) := by decide

theorem avoidance_not_dropped_with_lines :
    evaluate .lines avoidInput = none ∧ scan avoidInput stages =
      some (.avoid, .cut { (atA 1) with controls := [.avoid] }) := by decide

theorem end_clone_inhabited : scan (decorationsInput 3 true) stages = some (.endClone, .cut (atA 1)) := by decide

theorem both_clone_inhabited : scan (decorationsInput 2 true) stages = some (.bothClone, .cut (atA 1)) := by decide

theorem ordinary_decoration_control : scan (decorationsInput 2 false) stages = none := by decide

theorem allowed_but_not_fitting :
    rules .strict three.types three.content (atA 2) = true ∧
    evaluate .strict {three with capacity := 1, opportunities := [atA 2]} = none := by decide

theorem emergency_inhabited : graphicSlice graphic [] = some 2 := by decide

theorem emergency_region_competition :
    emergencyGuard regionInput [] = true ∧ emergencyGuard regionInput [atA 1] = false ∧
    RegionCandidateAdmitted regionInput [] ∧ RegionCandidateAdmitted regionInput [atA 1] := by decide

theorem zero_prefix_is_still_at_top :
    noBelowTop {zeroInput with content := [box 0 0, box 1 5]} [atA 1] = true := by decide

theorem no_empty_emergency : graphicSlice {graphic with capacity := 0} [] = none := by decide

theorem zero_box_earlier_side : evaluate .strict zeroInput = some (.cut (atA 2)) := by decide

theorem forced_delegation_control :
    rules .strict three.types three.content { (atA 1) with controls := [.force, .avoid] } = true ∧
    ordinary .strict three.types three.content { (atA 1) with controls := [.force, .avoid] } = false := by decide

end Fragmentation
