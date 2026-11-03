# Combined taint repair validation

The cumulative candidate passes all82 assertions over seven pages. Relative to the separately validated typed-recascade candidate, exactly11 selected-fallback and two composition failures become PASS; all69 previous PASS signatures and all seven page-ending signatures are identical. These are two pending repairs, not13 separate bugs.

The actual native build compiled Stylo/geckoservo and linked Gecko. Browser build20261102235513 used combined custom-properties sourcebdb3. The executed source was temporary: the owner restored originalbb13 source and application, then removed its1,008,605,176-byte backup. A separate unchanged audit replayed all raw results and independently verified source/application/binaries/index/flags/control restoration and process/temp cleanup.

Actual owner e92cbf/session97438/4dee11 exited0. Independent audit544791/session77516/3ba158 exited0. Comparison505411 exited0. VALIDATION.json binds all evidence. The Git index changed only its raw cache representation (3af76ac0 to083f1ae2), with semantic contents unchanged; canonical raw-index observation still needs an explicit refresh before the next live admission.

Publication remains pending normal signing and separate standalone commits. The first repair is explicit taint through typed recascade; the second is selected attr() fallback taint, rebased onto the first. No accepted-count increment or commit is asserted here. The build log retains nonfatal Mach export-monitor KeyError traces alongside successful compiler/linker completion and exit0.
