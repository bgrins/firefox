import Witnesses
open CaptionCache
example : inlineOnly (tableInput 200) (tableInput 300) = candidate (tableInput 200) (tableInput 300) := by decide +kernel
