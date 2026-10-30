# Same-element diagnostic on the restored build

Actual owner session 55405, terminal 658b02/0. WPT itself exited 1: one failing acyclic callback, one passing observation/calibration callback, and one OK page ending. Both complete observation records were posted before assertions. The restored Nightly build is 20261029165244; this is not a release-browser or candidate-comparison result.

| Trajectory | First value | Next three frame samples | Final computed CSS duration | Final effect duration |
| --- | ---: | --- | --- | --- |
| Acyclic contextual opacity | 0.75 | 0.75, 0.75, 0.75 | Font 2s; opacity 1.375s | Font 2000ms; opacity 1000ms |
| Acyclic literal opacity | 0.545455 | 0.545455, 0.545455, 0.545455 | Font 2s; opacity 1.375s | Font 2000ms; opacity 1375ms |
| Self-dependent stepped font | 32px | 32px, 32px, 32px | 1s | 500ms |
| Literal 500ms stepped font | 32px | 32px, 32px, 32px | 0.5s | 500ms |
| Literal 1000ms stepped font | 16px | 16px, 16px, 16px | 1s | 1000ms |

In the acyclic trajectory, seeking the fixed 2000ms font animation from 0 to 750ms changes the font from 16px to 22px. The independent opacity animation remains paused at 750ms. Its computed CSS duration becomes 1375ms, but its effect retains 1000ms; both before and after a membership query, the opacity is 0.75. The expected acyclic value is 750/1375 = 6/11. The literal trajectory calibrates that value with otherwise identical timing and font inputs. Animation/effect identities remain retained in every recorded trajectory.

This is an additional reproducer in the contextual-duration investigation, not a separately accepted bug or a demonstrated regression caused by the candidate. It makes a blanket once-per-element completion rule unsuitable without a more specific dependency argument. The samples do not identify a particular native event or prove that repeated processing is the correct implementation.

The self-dependent trajectory terminates and remains at 32px in these four samples. Its CSS duration and effect duration differ, but there is no normative endpoint oracle for that trajectory here. No actual oscillation or hang was observed. The conditional arithmetic example in README does not describe the measured browser sequence.

PRE and POST records are identical for branch/HEAD, staged state, status/diff/index digests, canonical controls, held provider and application/executable hashes. The owned process group was removed and its temporary directory cleaned up. No native overlays or builds were performed. Runtime manifest: `44135eb8194ce2ef7fdae519d6bcd28c65c96975cf17099e54ed22654d24df0b`.

The first attempt (session 61311, terminal e2b902/0) ran zero tests because the minimal runner omitted an explicit include. Its WPT exit was 64 and it produced no browser evidence. That runtime is retained unchanged. The corrected runner supplies the exact test include, inherited metadata (including typed-arithmetic prefs), and a strict two-callback/one-ending/two-record completion check. WPT failure is preserved even though the owner completed cleanup successfully.

[Raw assessment](../css-contextual-duration-feedback-browser-runtime-2/ASSESSMENT.json), [observations](../css-contextual-duration-feedback-browser-runtime-2/records/same-element-acyclic.json), [terminal](../css-contextual-duration-feedback-browser-runtime-2/ROOT-TERMINAL.json), [fixture](../css-contextual-duration-same-element-dependency-probe-v1/README.md).
