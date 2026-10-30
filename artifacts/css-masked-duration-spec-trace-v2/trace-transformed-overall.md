# trace: `WEB-ANIMATIONS-1#transformed-progress` -> `WEB-ANIMATIONS-1#overall-progress`

Max depth 9, kind `step`. Found 28 trace(s).

## Trace 1 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 1 calls `WEB-ANIMATIONS-1#directed-progress`
   > If the directed progress is unresolved, return unresolved.

2) `WEB-ANIMATIONS-1#directed-progress` step 1 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the simple iteration progress is unresolved, return unresolved.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 1 calls `WEB-ANIMATIONS-1#overall-progress`
   > If the overall progress is unresolved, return unresolved.

## Trace 2 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 1 calls `WEB-ANIMATIONS-1#directed-progress`
   > If the directed progress is unresolved, return unresolved.

2) `WEB-ANIMATIONS-1#directed-progress` step 1 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the simple iteration progress is unresolved, return unresolved.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 2 calls `WEB-ANIMATIONS-1#overall-progress`
   > If overall progress is infinity, let the simple iteration progress be iteration start % 1.0; otherwise, let the simple iteration progress be overall progress % 1.0.

## Trace 3 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 1 calls `WEB-ANIMATIONS-1#directed-progress`
   > If the directed progress is unresolved, return unresolved.

2) `WEB-ANIMATIONS-1#directed-progress` step 1 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the simple iteration progress is unresolved, return unresolved.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 2 calls `WEB-ANIMATIONS-1#overall-progress`
   > If overall progress is infinity, let the simple iteration progress be iteration start % 1.0; otherwise, let the simple iteration progress be overall progress % 1.0.

## Trace 4 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 1 calls `WEB-ANIMATIONS-1#directed-progress`
   > If the directed progress is unresolved, return unresolved.

2) `WEB-ANIMATIONS-1#directed-progress` step 2.1 calls `WEB-ANIMATIONS-1#current-iteration-index`
   - under: Calculate the current direction using the first matching condition from the following list:
   > Let d be the current iteration index.

3) `WEB-ANIMATIONS-1#current-iteration-index` step 3 calls `WEB-ANIMATIONS-1#overall-progress`
   > If the simple iteration progress is 1.0, return floor(overall progress) − 1.

## Trace 5 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 1 calls `WEB-ANIMATIONS-1#directed-progress`
   > If the directed progress is unresolved, return unresolved.

2) `WEB-ANIMATIONS-1#directed-progress` step 2.1 calls `WEB-ANIMATIONS-1#current-iteration-index`
   - under: Calculate the current direction using the first matching condition from the following list:
   > Let d be the current iteration index.

3) `WEB-ANIMATIONS-1#current-iteration-index` step 4 calls `WEB-ANIMATIONS-1#overall-progress`
   > Otherwise, return floor(overall progress).

## Trace 6 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 1 calls `WEB-ANIMATIONS-1#directed-progress`
   > If the directed progress is unresolved, return unresolved.

2) `WEB-ANIMATIONS-1#directed-progress` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the current direction is forwards then return the simple iteration progress. Otherwise, return 1.0 − simple iteration progress.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 1 calls `WEB-ANIMATIONS-1#overall-progress`
   > If the overall progress is unresolved, return unresolved.

## Trace 7 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 1 calls `WEB-ANIMATIONS-1#directed-progress`
   > If the directed progress is unresolved, return unresolved.

2) `WEB-ANIMATIONS-1#directed-progress` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the current direction is forwards then return the simple iteration progress. Otherwise, return 1.0 − simple iteration progress.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 2 calls `WEB-ANIMATIONS-1#overall-progress`
   > If overall progress is infinity, let the simple iteration progress be iteration start % 1.0; otherwise, let the simple iteration progress be overall progress % 1.0.

## Trace 8 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 1 calls `WEB-ANIMATIONS-1#directed-progress`
   > If the directed progress is unresolved, return unresolved.

2) `WEB-ANIMATIONS-1#directed-progress` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the current direction is forwards then return the simple iteration progress. Otherwise, return 1.0 − simple iteration progress.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 2 calls `WEB-ANIMATIONS-1#overall-progress`
   > If overall progress is infinity, let the simple iteration progress be iteration start % 1.0; otherwise, let the simple iteration progress be overall progress % 1.0.

## Trace 9 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 1 calls `WEB-ANIMATIONS-1#directed-progress`
   > If the directed progress is unresolved, return unresolved.

2) `WEB-ANIMATIONS-1#directed-progress` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the current direction is forwards then return the simple iteration progress. Otherwise, return 1.0 − simple iteration progress.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 1 calls `WEB-ANIMATIONS-1#overall-progress`
   > If the overall progress is unresolved, return unresolved.

## Trace 10 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 1 calls `WEB-ANIMATIONS-1#directed-progress`
   > If the directed progress is unresolved, return unresolved.

2) `WEB-ANIMATIONS-1#directed-progress` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the current direction is forwards then return the simple iteration progress. Otherwise, return 1.0 − simple iteration progress.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 2 calls `WEB-ANIMATIONS-1#overall-progress`
   > If overall progress is infinity, let the simple iteration progress be iteration start % 1.0; otherwise, let the simple iteration progress be overall progress % 1.0.

## Trace 11 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 1 calls `WEB-ANIMATIONS-1#directed-progress`
   > If the directed progress is unresolved, return unresolved.

2) `WEB-ANIMATIONS-1#directed-progress` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the current direction is forwards then return the simple iteration progress. Otherwise, return 1.0 − simple iteration progress.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 2 calls `WEB-ANIMATIONS-1#overall-progress`
   > If overall progress is infinity, let the simple iteration progress be iteration start % 1.0; otherwise, let the simple iteration progress be overall progress % 1.0.

## Trace 12 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 3 calls `WEB-ANIMATIONS-1#directed-progress`
   > Return the result of evaluating the effect easing function passing directed progress as the input progress value and before flag as the before flag.

2) `WEB-ANIMATIONS-1#directed-progress` step 1 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the simple iteration progress is unresolved, return unresolved.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 1 calls `WEB-ANIMATIONS-1#overall-progress`
   > If the overall progress is unresolved, return unresolved.

## Trace 13 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 3 calls `WEB-ANIMATIONS-1#directed-progress`
   > Return the result of evaluating the effect easing function passing directed progress as the input progress value and before flag as the before flag.

2) `WEB-ANIMATIONS-1#directed-progress` step 1 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the simple iteration progress is unresolved, return unresolved.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 2 calls `WEB-ANIMATIONS-1#overall-progress`
   > If overall progress is infinity, let the simple iteration progress be iteration start % 1.0; otherwise, let the simple iteration progress be overall progress % 1.0.

## Trace 14 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 3 calls `WEB-ANIMATIONS-1#directed-progress`
   > Return the result of evaluating the effect easing function passing directed progress as the input progress value and before flag as the before flag.

2) `WEB-ANIMATIONS-1#directed-progress` step 1 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the simple iteration progress is unresolved, return unresolved.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 2 calls `WEB-ANIMATIONS-1#overall-progress`
   > If overall progress is infinity, let the simple iteration progress be iteration start % 1.0; otherwise, let the simple iteration progress be overall progress % 1.0.

## Trace 15 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 3 calls `WEB-ANIMATIONS-1#directed-progress`
   > Return the result of evaluating the effect easing function passing directed progress as the input progress value and before flag as the before flag.

2) `WEB-ANIMATIONS-1#directed-progress` step 2.1 calls `WEB-ANIMATIONS-1#current-iteration-index`
   - under: Calculate the current direction using the first matching condition from the following list:
   > Let d be the current iteration index.

3) `WEB-ANIMATIONS-1#current-iteration-index` step 3 calls `WEB-ANIMATIONS-1#overall-progress`
   > If the simple iteration progress is 1.0, return floor(overall progress) − 1.

## Trace 16 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 3 calls `WEB-ANIMATIONS-1#directed-progress`
   > Return the result of evaluating the effect easing function passing directed progress as the input progress value and before flag as the before flag.

2) `WEB-ANIMATIONS-1#directed-progress` step 2.1 calls `WEB-ANIMATIONS-1#current-iteration-index`
   - under: Calculate the current direction using the first matching condition from the following list:
   > Let d be the current iteration index.

3) `WEB-ANIMATIONS-1#current-iteration-index` step 4 calls `WEB-ANIMATIONS-1#overall-progress`
   > Otherwise, return floor(overall progress).

## Trace 17 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 3 calls `WEB-ANIMATIONS-1#directed-progress`
   > Return the result of evaluating the effect easing function passing directed progress as the input progress value and before flag as the before flag.

2) `WEB-ANIMATIONS-1#directed-progress` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the current direction is forwards then return the simple iteration progress. Otherwise, return 1.0 − simple iteration progress.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 1 calls `WEB-ANIMATIONS-1#overall-progress`
   > If the overall progress is unresolved, return unresolved.

## Trace 18 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 3 calls `WEB-ANIMATIONS-1#directed-progress`
   > Return the result of evaluating the effect easing function passing directed progress as the input progress value and before flag as the before flag.

2) `WEB-ANIMATIONS-1#directed-progress` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the current direction is forwards then return the simple iteration progress. Otherwise, return 1.0 − simple iteration progress.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 2 calls `WEB-ANIMATIONS-1#overall-progress`
   > If overall progress is infinity, let the simple iteration progress be iteration start % 1.0; otherwise, let the simple iteration progress be overall progress % 1.0.

## Trace 19 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 3 calls `WEB-ANIMATIONS-1#directed-progress`
   > Return the result of evaluating the effect easing function passing directed progress as the input progress value and before flag as the before flag.

2) `WEB-ANIMATIONS-1#directed-progress` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the current direction is forwards then return the simple iteration progress. Otherwise, return 1.0 − simple iteration progress.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 2 calls `WEB-ANIMATIONS-1#overall-progress`
   > If overall progress is infinity, let the simple iteration progress be iteration start % 1.0; otherwise, let the simple iteration progress be overall progress % 1.0.

## Trace 20 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 3 calls `WEB-ANIMATIONS-1#directed-progress`
   > Return the result of evaluating the effect easing function passing directed progress as the input progress value and before flag as the before flag.

2) `WEB-ANIMATIONS-1#directed-progress` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the current direction is forwards then return the simple iteration progress. Otherwise, return 1.0 − simple iteration progress.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 1 calls `WEB-ANIMATIONS-1#overall-progress`
   > If the overall progress is unresolved, return unresolved.

## Trace 21 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 3 calls `WEB-ANIMATIONS-1#directed-progress`
   > Return the result of evaluating the effect easing function passing directed progress as the input progress value and before flag as the before flag.

2) `WEB-ANIMATIONS-1#directed-progress` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the current direction is forwards then return the simple iteration progress. Otherwise, return 1.0 − simple iteration progress.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 2 calls `WEB-ANIMATIONS-1#overall-progress`
   > If overall progress is infinity, let the simple iteration progress be iteration start % 1.0; otherwise, let the simple iteration progress be overall progress % 1.0.

## Trace 22 (3 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 3 calls `WEB-ANIMATIONS-1#directed-progress`
   > Return the result of evaluating the effect easing function passing directed progress as the input progress value and before flag as the before flag.

2) `WEB-ANIMATIONS-1#directed-progress` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the current direction is forwards then return the simple iteration progress. Otherwise, return 1.0 − simple iteration progress.

3) `WEB-ANIMATIONS-1#simple-iteration-progress` step 2 calls `WEB-ANIMATIONS-1#overall-progress`
   > If overall progress is infinity, let the simple iteration progress be iteration start % 1.0; otherwise, let the simple iteration progress be overall progress % 1.0.

## Trace 23 (4 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 1 calls `WEB-ANIMATIONS-1#directed-progress`
   > If the directed progress is unresolved, return unresolved.

2) `WEB-ANIMATIONS-1#directed-progress` step 2.1 calls `WEB-ANIMATIONS-1#current-iteration-index`
   - under: Calculate the current direction using the first matching condition from the following list:
   > Let d be the current iteration index.

3) `WEB-ANIMATIONS-1#current-iteration-index` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the simple iteration progress is 1.0, return floor(overall progress) − 1.

4) `WEB-ANIMATIONS-1#simple-iteration-progress` step 1 calls `WEB-ANIMATIONS-1#overall-progress`
   > If the overall progress is unresolved, return unresolved.

## Trace 24 (4 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 1 calls `WEB-ANIMATIONS-1#directed-progress`
   > If the directed progress is unresolved, return unresolved.

2) `WEB-ANIMATIONS-1#directed-progress` step 2.1 calls `WEB-ANIMATIONS-1#current-iteration-index`
   - under: Calculate the current direction using the first matching condition from the following list:
   > Let d be the current iteration index.

3) `WEB-ANIMATIONS-1#current-iteration-index` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the simple iteration progress is 1.0, return floor(overall progress) − 1.

4) `WEB-ANIMATIONS-1#simple-iteration-progress` step 2 calls `WEB-ANIMATIONS-1#overall-progress`
   > If overall progress is infinity, let the simple iteration progress be iteration start % 1.0; otherwise, let the simple iteration progress be overall progress % 1.0.

## Trace 25 (4 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 1 calls `WEB-ANIMATIONS-1#directed-progress`
   > If the directed progress is unresolved, return unresolved.

2) `WEB-ANIMATIONS-1#directed-progress` step 2.1 calls `WEB-ANIMATIONS-1#current-iteration-index`
   - under: Calculate the current direction using the first matching condition from the following list:
   > Let d be the current iteration index.

3) `WEB-ANIMATIONS-1#current-iteration-index` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the simple iteration progress is 1.0, return floor(overall progress) − 1.

4) `WEB-ANIMATIONS-1#simple-iteration-progress` step 2 calls `WEB-ANIMATIONS-1#overall-progress`
   > If overall progress is infinity, let the simple iteration progress be iteration start % 1.0; otherwise, let the simple iteration progress be overall progress % 1.0.

## Trace 26 (4 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 3 calls `WEB-ANIMATIONS-1#directed-progress`
   > Return the result of evaluating the effect easing function passing directed progress as the input progress value and before flag as the before flag.

2) `WEB-ANIMATIONS-1#directed-progress` step 2.1 calls `WEB-ANIMATIONS-1#current-iteration-index`
   - under: Calculate the current direction using the first matching condition from the following list:
   > Let d be the current iteration index.

3) `WEB-ANIMATIONS-1#current-iteration-index` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the simple iteration progress is 1.0, return floor(overall progress) − 1.

4) `WEB-ANIMATIONS-1#simple-iteration-progress` step 1 calls `WEB-ANIMATIONS-1#overall-progress`
   > If the overall progress is unresolved, return unresolved.

## Trace 27 (4 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 3 calls `WEB-ANIMATIONS-1#directed-progress`
   > Return the result of evaluating the effect easing function passing directed progress as the input progress value and before flag as the before flag.

2) `WEB-ANIMATIONS-1#directed-progress` step 2.1 calls `WEB-ANIMATIONS-1#current-iteration-index`
   - under: Calculate the current direction using the first matching condition from the following list:
   > Let d be the current iteration index.

3) `WEB-ANIMATIONS-1#current-iteration-index` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the simple iteration progress is 1.0, return floor(overall progress) − 1.

4) `WEB-ANIMATIONS-1#simple-iteration-progress` step 2 calls `WEB-ANIMATIONS-1#overall-progress`
   > If overall progress is infinity, let the simple iteration progress be iteration start % 1.0; otherwise, let the simple iteration progress be overall progress % 1.0.

## Trace 28 (4 hop(s))

1) `WEB-ANIMATIONS-1#transformed-progress` step 3 calls `WEB-ANIMATIONS-1#directed-progress`
   > Return the result of evaluating the effect easing function passing directed progress as the input progress value and before flag as the before flag.

2) `WEB-ANIMATIONS-1#directed-progress` step 2.1 calls `WEB-ANIMATIONS-1#current-iteration-index`
   - under: Calculate the current direction using the first matching condition from the following list:
   > Let d be the current iteration index.

3) `WEB-ANIMATIONS-1#current-iteration-index` step 3 calls `WEB-ANIMATIONS-1#simple-iteration-progress`
   > If the simple iteration progress is 1.0, return floor(overall progress) − 1.

4) `WEB-ANIMATIONS-1#simple-iteration-progress` step 2 calls `WEB-ANIMATIONS-1#overall-progress`
   > If overall progress is infinity, let the simple iteration progress be iteration start % 1.0; otherwise, let the simple iteration progress be overall progress % 1.0.

