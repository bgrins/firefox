import Lean
import LFComplexStreamCounterexample

open Lean LanguageBreak LanguageBreak.LFComplexStream

def numericKind : BreakKind → Nat
  | .none => 0 | .normal => 1 | .hyphen => 2 | .emergency => 3

def main : IO Unit := do
  for units in [leadingUnits,suffix,text] do
    IO.println (Json.mkObj [("units",toJson (units.map Fin.val)),
      ("values",toJson ((segmentation units).map numericKind))]).compress
  IO.println (Json.mkObj [("whole",toJson ((glyphs whole).map numericKind)),
    ("before",toJson ((glyphs beforeLF).map numericKind)),
    ("after",toJson ((glyphs afterLF).map numericKind))]).compress
