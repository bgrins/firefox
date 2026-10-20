import Calibration
import ModelMutants
def emit (name : String) (o : OffsetSource.Observation) : IO Unit :=
  IO.println (name ++ " " ++ String.intercalate " " ((OffsetSource.row o).map toString))
def main : IO Unit := do
  for c in Calibration.inputs do
    emit "before" (OffsetSource.observeOld c)
    emit "candidate" (OffsetSource.observe c)
    emit "auto_reserved_too" (ModelMutants.observe 1 c)
    emit "maximum_instead_of_minimum" (ModelMutants.observe 2 c)
    emit "reserve_two_units" (ModelMutants.observe 3 c)
    emit "negative_values_lost" (ModelMutants.observe 4 c)
    emit "wrong_side" (ModelMutants.observe 5 c)
