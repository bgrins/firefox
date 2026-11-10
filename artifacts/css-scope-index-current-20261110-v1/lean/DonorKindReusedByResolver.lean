import Scope
open ScopeCache
example : (interpret hostReceiver (compile donor)).map (Option.map Meaning.receiverShadowHost) = [some false] := by decide +kernel
