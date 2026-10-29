import HypotScale
open HypotScale CssSemantics.ImplementationSupport.Binary32Magnitude
example : unit ≤ 2 * (decode tiny * decode tiny) := by decide +kernel
