# Quoted EOF endpoint browser pair

The unchanged 38-case WPT crashes before the repair and passes every check after
rebuilding style, geckoservo and XUL. The other 34 outcomes are identical,
including eight deliberately separate string-content failures and three known
expected escaped-EOF spelling failures. The aggregate WPT exit remains 1 because
of the separate string-content failures; it is not a wholly green suite.

The new WPT covers both quotes, odd terminal backslash runs, missing var/env/attr
providers, nested fallbacks, an earlier sibling, custom-property storage, an
unused fallback, UTF-8, escaped newline and closed/no-backslash controls. Its
oracle compares computed font families against independently closed literals.
It does not depend on installed fonts or raw CSS serialization spelling.

Source/configuration/test and executable hashes are checked before and after
both runs. Only custom_properties.rs and the rebuilt executable/XUL differ.
Runtime validation is on the shared local tree. Root separately checks that the
two-file native/WPT patch applies and reverses exactly at upstream base.

The first lint invocation used the unavailable wpt-lint mach command; the
correct mach lint --linter wpt invocation passed with no findings. The build
printed export-tier progress-monitor callback errors, then completed style/XUL
compilation and linking successfully with exit zero. Its complete log is kept.
