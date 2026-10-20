# Triage addendum: fixes 81–87

The branch now has 87 committed native/WPT fixes. This adds the seven newest
commits to the [first 80-fix triage](../css-bugfix-triage-20261019/README.md).
Review order is a recommendation, not assigned Mozilla severity. All seven
commits are ancestors of the recorded HEAD and contain WPT changes.

## First: demonstrated crashes

| Fix | Native commit | Impact | Evidence limits |
| --- | --- | --- | --- |
| 83 | `ad608a212bd8d7f77a2f0b9df62df18d33c12b96` | Leading-whitespace reference offsets can trigger a content-process bounds panic. | Script-free reproduction in installed Firefox 158; patched build passes 26 new cases. Memory corruption or exploitability is not established. |

## Next: rendering and API correctness

| Fix | Native commit | Impact | Evidence limits |
| --- | --- | --- | --- |
| 81 | `34e4e755cb81332819e56457f5fb68b9b305c394` | Registered custom property serialization loses token boundaries, changing downstream interpretation. | 37-case WPT: ten baseline failures become passes; no release or isolated upstream runtime claim. |
| 82 | `d63735091bf8dc469d900ddba56e8a43bcac26d7` | Animation publication replaces guaranteed-invalid registered values with initial values, changing required fallback/inheritance behavior. | Ten reproduced failures improve in a 343-check matrix; two pre-existing expected failures remain. Six final controls are candidate-only. |
| 84 | `bccea9c1fffc59e41a9f9bef16fcaf0056ff1f10` | Trimming stored whitespace leaves trailing token metadata inconsistent with the actual bytes. | 28 baseline failures become passes in a 40-case WPT. General serialization correctness remains outside the proof. |
| 87 | `2db94380203863bced9e3a7147505beabaaf7599` | Deleting an initially duplicated view-transition type leaves native selector membership behind. | Five baseline failures become passes; all 21 candidate cases pass. The separate cached-style invalidation repair is not counted yet. |

## Later: narrower syntax triggers

| Fix | Native commit | Impact | Evidence limits |
| --- | --- | --- | --- |
| 85 | `fff2d758ef6bb39b4465cb072767bc5db6d5e09f` | Trimming escaped trailing whitespace changes identifier contents. | 16 failures become passes in a 20-case WPT; escaped space/tab inputs are required. |
| 86 | `246f1ff43250ec24e177f03cde923c9d11ee86e9` | Removing a newline after a backslash delimiter turns an invalid animation name into an identifier. | 30 final cases pass against a baseline subset with 16 failures; no release reproduction claimed. |

The attribute-taint review remains in its existing security-review group. This
addendum establishes no additional security defect. Fix 83 is the new first-priority
item because it has a minimal, script-free release crash reproduction. Use the
[commit ledger](../stylo-bloom-tools/CURRENT-COMMITS.json) for standalone alternatives
and exact preceding evidence commits.
