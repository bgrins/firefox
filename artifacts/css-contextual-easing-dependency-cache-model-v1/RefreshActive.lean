import Dependency
open ContextualEasing
example :
    let started := advance countSteps { context := before, captured := none } .start
    let changed := advance countSteps started (.contextChanged after)
    changed.captured = some (evaluate countSteps changed.context) := by decide
