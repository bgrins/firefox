import Language
open LanguageContext
example : (query (fun _ => some false) (some (7, true)) 7).1 = some false := by decide
