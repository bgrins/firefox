# Escaped-quote browser pair

The same 18-case WPT and relevant source/configuration/resources are pinned in
both runs. Four failures become passes; all 18 cases pass. The broader diagnostic
now passes 22 checks, while all 18 parity and 38 endpoint checks remain passing.
Compare keyed outcomes, not execution order: there are exactly eight expected
status transitions among 111 records, including the four duplicate diagnostic
cases. The command exits zero with no unexpected results; three known expected
syntax failures remain unchanged. See PAIR-RESULT.json and root acceptance.
