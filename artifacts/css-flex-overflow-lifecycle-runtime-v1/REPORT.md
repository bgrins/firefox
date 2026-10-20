# Overflow continuation lifecycle diagnostic

Eight paired browser stages exercise ordinary-item80→81→80 changes, same-size invalidation, the first item's80→320→80 transition, and removal/reinsertion of two tall descendants. All independent references calibrate the expected logical[i*100,0,100,160] rectangles. Seven baseline stages have misplaced descendants; all eight candidate stages match the references. The shortened chain control stays correct. Parent flex fragment counts remain equal between builds: five during the320px first-item stage and four otherwise.

Only the standalone final-size overflow-container retiming patch was applied. This run does not include branch instrumentation. Browser rectangles exercise observable lifecycle behavior without proving which exact frame-list operations or skip guards occurred. Both builds and browser runs exit0; candidate/restoration build logs retain the known mach monitor exception and report zero compiler warnings. Source and browser build are restored, and HEAD and the staged binary diff are unchanged.

The candidate remains unaccepted pending skipped-child reachability/geometry review, broader focused regression gates, formatting/lint, and the formal/native review. The patch is separate from exact cumulative arithmetic work.
