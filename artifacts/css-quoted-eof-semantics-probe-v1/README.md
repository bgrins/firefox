# Quoted EOF semantic controls

The pinned browser produces eight failures and fourteen passes across 22 checks.
Four failures use even positive runs of terminal backslashes in an unfinished
string. Four use an escaped terminal quote. Both quote kinds are covered.

The test stores the raw string in a custom property, substitutes it into a
font-family list, and appends `serif` outside the reference. Its independent
literal reference pairs backslashes and retains an escaped terminal quote as
string content. It compares computed values; it does not require a particular
raw custom-property serialization spelling. The failures swallow the external
family suffix into the string.

The existing recovery code removes a terminal backslash without checking parity
and treats any final matching quote as a terminator without checking whether it
was escaped. These are distinct from the nested-reference endpoint crash in
the adjacent probe. Odd-backslash EOF and closed-string controls pass, as do
the closed and no-backslash unclosed fallback controls.

The oracle follows CSS Syntax's [string consumer](https://drafts.csswg.org/css-syntax-3/#consume-string-token):
backslash pairs decode to literal backslashes, an escaped quote is content,
and an escaped EOF adds nothing. Substitution must preserve that string token
before the following family separator. No raw spelling adjudication is needed.

This is finite shared-tree browser evidence, not a formal proof or a new accepted
repair. Source/configuration/resource/binary pins are stable. Separate parity
and terminal-quote repairs, proof companions and WPT commits remain planned.
