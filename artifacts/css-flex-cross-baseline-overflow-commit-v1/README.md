# Flex baseline sum: local commit queue

Discovery evidence, formal review, and corrected WPT evidence precede the two-file Gecko/WPT fix. Signing remains required. Set each recipe's expected parent only after the preceding signed commit has been verified, then use `commit-item-v2.py`. Record the resulting IDs in the main bugfix ledger.

`PACKAGING.json` verifies the accepted patch after all preceding queued native fixes on both retained bases, using temporary indexes. The resulting flex source is byte-identical to the accepted standalone snapshots. The WPT includes the reviewed numeric-range prerequisite; all 54 Gecko cases were admitted in the recorded paired run.

Acceptance covers final baseline-group sums and capped storage. Earlier subtraction, multiline accumulation, and native providers remain separate obligations. Packaging does not add browser results or establish isolated upstream runtime coverage.
