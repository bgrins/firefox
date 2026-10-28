# Round nonfinite classification diagnostic

Unexecuted observation function: `observeRoundNonfiniteClassification()` from observe.js. The 14 operand pairs, four existing strategies and four font phases produce 224 snapshots. No unsupported case counts as a pass. The function removes its owned iframe and returns JSON-detached values.

The outer encoding distinguishes NaN (0), negative (.25), zero (.5), and positive (.75). Each row retains authored CSSOM, repeated computed values, resolved-operand CSS, literal expected encoding and independent font/difference/sign calibration. Finite arithmetic cases use only exact unit steps; this does not test the separate quotient-precision repair. Signed zero is intentionally not distinguished. The newer line-width strategy is outside scope.

CSS Values 4 Editor’s Draft dated 24 August 2026, freshly read 28 October: [argument ranges](https://drafts.csswg.org/css-values-4/#round-func) require NaN for a zero step or both infinite operands; infinite value with finite nonzero step remains that infinity. Finite value with infinite step selects signed zero or an infinity according to strategy and sign. [Top-level calculation rules](https://drafts.csswg.org/css-values-4/#calc-ieee) censor NaN to zero only at the outer boundary. The probe applies these rules after resolving the contextual sign; it does not use browser results as its numerical oracle.

Source discovery and the prior paired observation prompted this diagnostic. No new browser execution, native acceptance, full IEEE proof, or bug count is claimed.

This follows the known open boundary recorded in css-round-special-knowledge-repair-v2 and css-round-four-phase-terminal-review-v1; the latest paired run is a new observation of that existing lead, not discovery. The resolved-operand browser controls may share parse-time defects and remain diagnostic, not prerequisites that erase a target result. Counter bounded setup review 6e89bf/0 is clear; JavaScript syntax fa654f/0 passed. No callbacks have been executed by this agent.
