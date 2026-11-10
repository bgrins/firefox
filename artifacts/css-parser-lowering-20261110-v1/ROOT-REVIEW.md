# Root review and acceptance

Clean source-only replay passed from 36 inputs: 229 theorem audits (18 new),
28 observations and nine controls. `ROOT-ORIGINS.json` independently compares
19 unchanged dependencies and three specification inputs with committed origin
`650d15ca41e8`. No generated Lean objects remain from the replay.

`lowering_correct` is quantified over every typed parser and initial modeled
state. It preserves successful values and final state exactly, and returns the
initial state on failure. Here the entire modeled state means unread scalar
input and the error flag. The transaction proof restores both fields, including
earlier consumption before a failed right-hand parser. Optional parsing relies
on that proved child contract. The maximal scanner uses the actual remaining
input length and existing scanner equivalence laws.

The runtime lowering and target interpreter do not call `ParserIR.run` or the
number reference implementation as an oracle. The source AST is data-only; the
target effect representation contains generated Lean continuations. The number
instance composes the generic proof with an unchanged numeric projection and
reference relation. The projection itself is not lowered, and `StartsNumber`
remains a caller premise.

The independent source review in
`../css-parser-lowering-review-20261110-v1/REPORT.md` found no blocking issue.
Root accepts this reusable lowering theorem at its stated boundary. The manual
CSS prose interpretation, shared primitive meanings, unchecked interchange
emission, machine floating point, and native/browser refinement remain separate.
This adds no browser repair and does not change the standalone library.
