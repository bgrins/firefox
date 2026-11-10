import Scope
open ScopeCache
example : dispatchAll scopeDispatch (interpret hostReceiver (compile donor)) = dispatchAll scopeDispatch (reference hostReceiver) := by decide +kernel
