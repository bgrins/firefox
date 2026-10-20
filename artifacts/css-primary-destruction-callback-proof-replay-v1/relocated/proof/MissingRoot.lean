import Witnesses

open Destruction

example : (badOmitRoot sample).map (fun h => h 30) = some none := by decide
