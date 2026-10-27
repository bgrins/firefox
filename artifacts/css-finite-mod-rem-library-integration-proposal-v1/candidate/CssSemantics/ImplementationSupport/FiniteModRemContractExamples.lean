import CssSemantics.ImplementationSupport.FiniteModRemContract

namespace CssSemantics.ImplementationSupport.FiniteModRemContractExamples
open CssSemantics.ImplementationSupport.FiniteModRemContract
open CssSemantics.ImplementationSupport.ModRemInfinity

example : adjust ((-17 : Int).tmod 3) 3 = 1 := by decide +kernel
example : adjust ((17 : Int).tmod (-3)) (-3) = -1 := by decide +kernel
example : candidate .mod (fun _ => 999) true false 0 3 = .zero false := by decide +kernel
example : candidate .rem (fun _ => 999) true false 0 3 = .zero true := by decide +kernel
example : candidateGrid .rem (fun _ => 999) 2 3 = 2 := by decide +kernel
example : candidate .mod (fun _ => 0) false true 1 (-3) = .zero true := by decide +kernel
example : candidateGrid .mod (fun _ => 33554432) (-1) 33554432 = 33554432 := by decide +kernel
example : NearestProjection 33554431 33554432 := endpoint_projection

def checks : List (String × Bool) := [
  ("finite ModRem contract positive divisor adjustment", decide (adjust ((-17 : Int).tmod 3) 3 = 1)),
  ("finite ModRem contract negative divisor adjustment", decide (adjust ((17 : Int).tmod (-3)) (-3) = -1)),
  ("finite ModRem contract Mod divisor zero sign", decide (candidate .mod (fun _ => 999) true false 0 3 = .zero false)),
  ("finite ModRem contract Rem dividend zero sign", decide (candidate .rem (fun _ => 999) true false 0 3 = .zero true)),
  ("finite ModRem contract Rem ignores addition", decide (candidateGrid .rem (fun _ => 999) 2 3 = 2)),
  ("finite ModRem contract projected zero sign", decide (candidate .mod (fun _ => 0) false true 1 (-3) = .zero true)),
  ("finite ModRem contract projected divisor endpoint", decide (candidateGrid .mod (fun _ => 33554432) (-1) 33554432 = 33554432)),
  ("finite ModRem contract rejects omitted adjustment", decide (adjust ((-17 : Int).tmod 3) 3 = -2)),
  ("finite ModRem contract rejects divisor added to zero", decide (candidateGrid .mod (fun x => x) 0 3 = 3)),
  ("finite ModRem contract rejects Mod dividend zero sign", decide (candidate .mod (fun x => x) true false 0 3 = .zero true)),
  ("finite ModRem contract rejects Rem divisor zero sign", decide (candidate .rem (fun x => x) true false 0 3 = .zero false)),
  ("finite ModRem contract rejects strict endpoint", decide ((33554432 : Int) < 33554432)),
  ("finite ModRem contract rejects omitted remainder premise", decide (candidateGrid .rem (fun x => x) 0 3 = (33554432 : Int).tmod 3))]

end CssSemantics.ImplementationSupport.FiniteModRemContractExamples
