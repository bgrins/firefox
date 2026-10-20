import Witnesses

open Destruction

example : (badKeepTable sample).map (fun h => h 0) = some (some (.frame 1 true emptyTable)) := by decide
