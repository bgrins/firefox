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

end Fragmentation
