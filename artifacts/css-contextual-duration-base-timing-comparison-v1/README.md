# Pre-own-effect timing trial: observed separation from descendant completion

The four-source trial built successfully but failed its authored comparison: actual 29079/6c7cd1/1 has 2 PASS, 5 FAIL, 3 OK and seven complete calibrated records. Original 61482/249ad8/0 has 1 PASS, 6 FAIL, 3 OK. The masked callback changed to PASS; the same-element acyclic and all four descendant first-read callbacks still FAIL. The feedback callback remains PASS because its contextual endpoint is diagnostic. None of these counts is a new accepted native fix.

Saved replay 002853/0 authenticates the frozen runtime, reproduces the strict original/candidate raw assessments, seven private records and calibration, and joins the actual four source postimages. It projects historical records from the earlier three-source candidate and all three Chrome fixtures. Literal trajectories are exactly equal across the applicable runs; all depth initial snapshots also agree. Recorded animation/effect identities remain current, and detailed values before/after membership reads agree. Historical browsers were not rerun.

Each list below is the first getter followed by three passive-frame getters. Detailed CSS/effect timing is read later, not atomically with the first getter.

| Case | Firefox original seven-case run | Earlier three-source candidate | New four-source timing candidate | Chrome 156 |
| --- | --- | --- | --- | --- |
| Same-element acyclic opacity | .75,.75,.75,.75 | .545455,.545455,.545455,.545455 | .75,.75,.75,.75 | .75,.75,.75,.75 |
| Stepped self-feedback font(px) | 32,32,32,32 | 16,16,16,16 | 32,32,32,32 | 32,32,32,32 |
| Masked-font opacity | .75,.75,.75,.75 | Not tested | .375,.375,.375,.375 | .375,.375,.375,.375 |
| Descendant depth 1 (expected 1) | 0,0,0,0 | 0,1,1,1 | 0,1,1,1 | 1,1,1,1 |
| Descendant depth 2 (expected 0) | 1,1,1,1 | 1,0,0,0 | 1,0,0,0 | 0,0,0,0 |
| Descendant depth 4 (expected 0) | 1,1,1,1 | 1,1,0,0 | 1,1,0,0 | 0,0,0,0 |
| Descendant depth 8 (expected 0) | 1,1,1,1 | 1,1,1,1 | 1,1,1,1 | 0,0,0,0 |

The new timing input restores the sampled same-element rendered/effect behavior seen in original Firefox and Chrome. In the acyclic case, later applied opacity duration is 1000ms in original/new/Chrome, versus 1375ms in the earlier candidate. Firefox original/new still expose computed CSS `2s, 1.375s`, while Chrome exposes `2s, 1s`. Thus the trial changes the manager input without making computed CSS serialization match Chrome. The authored .545455 expectation remains tentative and must not turn agreement with Chrome into an alleged regression.

The stepped feedback later snapshot has applied 500ms/progress 1/time 750ms in all four runs. Original/new/Chrome render 32px; the earlier candidate renders 16px. Firefox original/new computed CSS is 1s, Chrome and earlier candidate .5s. No alternation, fixed point, hang or general cycle policy is established by these four observations.

Masked-font final correctness is less ambiguous: authored and animated font are both 32px after mutation. Original Firefox's applied timing stays 1000ms/.75 despite computed CSS `2s, 2s`; the new candidate and Chrome reach 2000ms/.375 from the first sample. Initial applied timing remains 1000ms/.75. Firefox original/new initial computed CSS is already `2s, 2s`, whereas Chrome's is `2s, 1s`. This demonstrates a repair in the combined trial, not that all four changed sources are necessary or that unconditional update admission is safe. Root’s specification readout supports the final equal-input arithmetic but leaves the complete normative first-getter algorithm trace inconclusive; this comparison does not close that trace. The isolated normal-admission patch and standalone final-only WPT remain unexecuted.

The depth sample trajectories are exactly those of the earlier three-source candidate. Depths 1/2 become correct at frame 1, depth 4 at frame 2, and depth 8 remains old through frame 3. Its later detail snapshot has stage 8 font 16px despite CSS/effect duration 1000ms and progress 1; timing equality is not evidence of fresh composition. Sequential getters and frames do not identify native traversal counts or prove eventual recovery beyond the sampled window. Chrome's first-read PASS remains the concrete descendant gap. Pre-own timing did not complete arbitrary descendant dependencies in this trial.

Root verifier 36669/0dd20f/0 independently verified all four source/app restorations, replayed records and removed the owned 1,008,605,176-byte backup. Frozen runtime 6c308f53 and its ROOT-TERMINAL preserve the comparison failure. Only the raw-index observation changed af90→256349; epoch is e1cc8caa. Accepted native fixes remain 149. The parent task/publication prototypes are not in this build and provide no additional runtime claim.

Next: isolate the masked repair with unrelated-restyle, API-ownership and performance controls; implement and test the actual parent publication/composition/child-release boundary; bridge selected timing inputs and native dependency evaluation to the models. Publish completed research before the already validated min/max and logarithm native commits. Do not weaken first-read assertions or add a fixed traversal budget.
