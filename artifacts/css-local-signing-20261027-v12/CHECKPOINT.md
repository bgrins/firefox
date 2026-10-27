# Signed research checkpoint

| Commit | Work |
| --- | --- |
| cedc8870ce0781d941bae1a52d97db19b622c79d | Frozen browser comparison and isolated commit tooling |
| 5f2ca219dcd0940692ab0a328d73a14857fce624 | Original/candidate evidence, failed acceptance gate, 20 passing native tests |
| 56aaa34661925da60e2c35b9a9a98e68a20b22c8 | EOF oracle correction, revised 73-target proposal and numeric spec trace |

Accepted fixes remain 136; held repair 120 is excluded. No new native bugfix is accepted at this checkpoint.

The raw attribute candidate repaired all 13 original target failures but failed one historical EOF expectation. The revised expectation has two independent spec traces and seven additional controls. The new 73-target fixture requires a fresh paired browser run before accepting the repair. The saved 66-target comparison remains failed; its 329 regression assertions and six reftests passed. All 20 selected native regression tests passed.

Unfinished implementation and test work remains in the working tree and is also stored in ../css-unfinished-work-checkpoint-20261027-v7/unfinished.patch, with an exact base, source hashes, and verified forward/reverse application. This recovery patch is not an accepted production fix. Unrelated directories, the nested Lean repository and build products are excluded.

Continue from CURRENT-EPOCH.json in this signing directory, synchronized to the raw native runtime after final signing. Source remains the compiled, unaccepted raw candidate. The live historical attr-cycle.html remains unchanged and the proposed new raw WPT is not installed. Prior runtime epochs are historical.

Next: freeze the revised 73-target comparison, rebuild and run original/candidate, then commit any accepted native repair with only cascade.rs and its two WPT files. Keep fix 137 as the explicit prerequisite.
