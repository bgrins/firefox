# First query-driver execution attempt

The retained-browser baseline passed its exact 130-record comparison and restored successfully. Candidate installation passed WPT lint and full installed-file ESLint, then failed manifest lint: per-test prefs entries are not supported for a plain Mochitest manifest. No native build or direct-driver browser run occurred. The failed candidate restored source, application, installed Mochitest tree and metadata; its original receipts remain unchanged.

A fresh v2 experiment will move the two preferences into an awaited test setup and reparse the existing inline stylesheet afterward, so preference-gated declarations are parsed with the intended settings. It will preserve the native code and 208 assertion inventory. This is a test setup correction, not evidence of a Firefox defect.
