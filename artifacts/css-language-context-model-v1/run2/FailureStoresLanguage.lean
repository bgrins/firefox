import Language
open LanguageContext
example : recordedLanguage 7 none = recordedLanguage 7 (some false) := by decide
