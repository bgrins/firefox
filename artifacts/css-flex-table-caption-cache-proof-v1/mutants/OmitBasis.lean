import Witnesses
open CaptionCache
example : candidate (tableInput 200) (tableInput 300) = original (tableInput 200) (tableInput 300) := by decide +kernel
