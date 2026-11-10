import Scope
open ScopeCache
example : interpret hostReceiver (compile donor) = reference hostReceiver := by decide +kernel
