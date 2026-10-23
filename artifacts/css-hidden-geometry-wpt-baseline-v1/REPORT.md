# Initial hidden-flex WPT baseline

The unchanged48-case release-derived WPT executed locally in the real WPT harness:
40 PASS,8 FAIL, file statusOK. The eight failures are hidden shrink insertion for
direct items and nested descendants, append/prepend, bounding/offset. Direct items
return0×0 rather than50×32; descendants retain100×32. The WPT captures five stages
and three reads before assertions, but a failing subtest reports its first failure.
These are eight failing subtests, not a recount of every failing stage.

BEFORE pins the25 relevant native sources, executable/XUL, test and harness.
All pins remained unchanged after execution. This run uses the restored shared
working-tree build, including existing prototypes. The subsequent four-variant
experiment uses exact committed native sources to remove those prototypes.
No repair was installed by this run. Exit1 reflects expected baseline failures.
