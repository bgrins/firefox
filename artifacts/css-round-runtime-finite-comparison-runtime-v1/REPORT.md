# Independent Round repair comparisons

Root session 27331 exited 0. All five phases complete 1,484 assertions, 35 OK harnesses and eight passing rendering references. The installed 159 mandatory assertions pass in every phase. Four native builds succeed; their logs retain pre-existing build-monitor export callback exceptions. Underlying WPT exits are 1 because known failing assertions remain; the comparison itself passes.

| Phase | PASS | Retained FAIL | Required repairs |
| --- | ---: | ---: | ---: |
| Installed baseline | 1408 | 76 | 0 |
| Runtime NaN priority only | 1416 | 68 | 8 |
| Finite negative-zero bound only | 1412 | 72 | 4 |
| Both repairs | 1420 | 64 | 12 |
| Restored original stack | 1408 | 76 | 0 |

The two single phases change only their own enumerated failures to PASS. All other status, diagnostic and metadata tuples are exact. Composition preserves both singles, permitting only the other family's remaining repairs. The restored phase reproduces every original outcome. The deferred-value parse guard is excluded, and the two nonnormative integer-policy observations remain unchanged.

Both candidates have separate two-path Gecko/WPT patches in the data capsule. Each independently applies to the committed HEAD90 generic calc body. Static dependency review finds no dependence on the pending raw-length or integer patches; the actual browser comparison uses the installed working stack, not a clean HEAD90 build. Native/runtime refinement remains unproved.

All 605 preservation roles, 72 guarded source bodies, 21 installed identities, 925 staged payloads and the 42-path original native inventory pass final checks. Six temporary fixtures are removed by body/inode identity; all WPT process-group cleanup records are clean. Original source is restored and freshly rebuilt binaries are recorded in restored-BINARIES and FINAL-PINS. No candidate remains installed. Independent terminal review and fix acceptance are pending at sealing.
