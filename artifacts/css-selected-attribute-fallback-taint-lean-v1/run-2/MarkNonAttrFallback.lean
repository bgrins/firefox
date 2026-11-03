import Fallback
open SelectedAttributeFallback RetainedAggregateTaint
example : evaluate absent (.fallback .other 7 "missing" (.literal clean.bytes)) = some fallbackValue := by decide
