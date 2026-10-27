# Third explicit historical oracle correction

The first two raw-nested corrections remain exactly those documented by the sealed version 1 proposal. This version additionally changes the case whose declaration is `--x: attr(data-foo type(*), abc)` and attribute data-foo contains `attr(data-foo`.

Old expectation: `abc`.
New expectation: the CSS string `"attr(data-foo"`.

The missing closing parenthesis is handled by the CSS Syntax function consumer's EOF branch. The nested bare attribute read returns before typed substitution-context guarding and retrieves the original DOM string, including the missing parenthesis. No closing parenthesis is inserted inside that string. See `css-attr-raw-eof-oracle-audit-v1/SPEC-TRACE.md` and the independently sealed EOF trace, both bound in REFERENCES.json.

The existing comment now describes implicit EOF closure. No other helper call changes relative to version 1. The historical baseline's pass and candidate's failure under the old expectation are retained in the audit; acceptance requires rerunning both phases with the new immutable oracle and additional controls.

The added controls preserve genuine typed self-cycles even when one or both closing parentheses are omitted. They also separate universal syntax accepting a trailing identifier from string syntax rejecting it, and rejection of an unmatched closing token. These expectations are spec-derived predictions awaiting browser comparison.
