# Branch baseline execution and restoration review

PASS for the frozen baseline experiment at ec467c0219d3d5daf70f42fcc53677cf8a262173, input manifest 4f33634170317b4c78026e253e01953e0d7324d3e79da83187a6f48c3a953904. This is independent execution/result review; the parent authored the wrapper and executed it. No native repair was installed.

The raw lifecycle contains exactly four callbacks and one OK harness ending. Plain WAAPI preserves its specified variable expressions (PASS). Replaced CSS keyframes fail the getter array assertion: expected var(--source)/var(--other), got 12px/24px. Detached and plain-Animation-transferred CSS effects each fail the frame-count assertion: expected one specified frame, got two. These are intended getter assertions, not setup failures. Later assertions after each failure remain unexecuted; the successful candidate must reach them.

Lint exits zero; WPT exits one for these three unannotated failures, while the baseline wrapper exits zero after matching its explicit expected vector. Raw messages and expected classifications agree with TEST-RESULTS.json. No build ran.

The independent live audit verifies all 9378 application entries, three extras, source and test pins, sampled binary/configuration hashes, HEAD and index, clean tracked files, absent temporary fixture/metadata/backups/lock, and terminated owned process groups. REVIEW.json and review.py retain the checks; process-snapshot.txt records the process audit. The parent's live hold was released after these checks passed. This establishes the sampled baseline and restoration, not a fix or universal getter correctness.
