# CSS verification continuation 173

Continue the full objective and [continuation172](../css-continuation-roadmap-20261103-v172/PLAN.md). Previous goal turn made progress by completing native61 validation and launching its raw-index refresh. This turn completed that refresh, prepared and checked the research checkpoint, and diagnosed a private-staging failure before signing. No new commit exists. HEAD remains e86b64866cdc with 157 committed fixes; the two taint fixes and newly validated font-unit fix remain queued.

## Current state and next action

There is no active root process. Native61, its audit, raw refresh, V123 capture/checks, failed commit attempt, recovery and staging diagnostic are all terminal. Current canonical epoch is `b4bb653fbac1f4b16dedb2bbe5713a36f2dad9b50b15258d761ba6f25430fa0c`; real raw index is `c1d5743411f801baba1c8202ed20f829ca80fcee9e93d37450299c6f5fa86fe8`. OWNED594bb5ef and ROLE14d0f2bb remain unchanged. The operation lock is absent. Source/application remain the restored original state recorded in172.

Agent typed_demand_review is preparing fresh disabled V124, preserving failed V123. The correction excludes exactly25 files already committed in the separate CSS Lean repository from Firefox's selection, while retaining their byte hashes/nested-commit evidence and the existing full-current nested-state checks. No source or signing guard is to be weakened. Root must authenticate the proposal, obtain fresh V124 capture, run saved/live checks and explicitly verify the corrected final private staged set before the next normal configured commit attempt. No memo adapter is used. Commit the validated taint work before further native experiments.

## Completed raw refresh and V123 preparation

Raw refresh34832b/session70533/0cf99b exited0. Root d7e636 independently proved exactly raw_index_observation.current changed, PRE=POST, actual canonical EPOCH equality, unchanged OWNED/ROLE/HEAD, matching real raw index and absent lock. Runtime `css-keyframe-font-unit-raw-index-refresh-runtime-1` FILES is `974a7c3134878b9e875445ff6cf1255360509e765a07a6f52b6c257e9cc31372`; RESULT is `136fe4ef65f822025454c3f3332803833458acb2875730506bd894324fb617a2`; ROOT-TERMINAL is `0d9ed382704ceba1c919c8794d4a1a7ebb01c1b020c7fc9a9c31e435f89e1ce6`. It joins prior f83/083f to b4bb/c1d without a native-fix increment.

Selection addition `css-v123-native61-selection-addition-v1`, FILES77568146, was root-authenticated in ed7a25:816 paths,41 closures, with53 root-HEAD dependencies and552 already-selected inputs reused. This proposal failed to distinguish25 nested-repository dependencies, as diagnosed below. Its original evidence is preserved rather than rewritten.

Root f664ad preserved the original V123 preparation in `css-research-checkpoint-20261103-v123-root-prebinding-v1`, manifest5314d8cc. Root6619c6/acf53e merged completed evidence and actual refresh bindings. Fresh capture **a49299/session62798/4e404c/exit0** produced `css-research-checkpoint-20261103-v123-current.json`, SHA `45b6e4348e67941ca8effc65863ae35872f53effc4ae723f7ad9e00f9add33f6`; its root terminal is bad997b4. Root7298e9 rechecked controls and completed admission.

Saved check **875c77/session81418/c8665e/exit0** authenticated3592 selected paths/264,051,954 bytes/129 closures, four refresh negatives, eleven admission negatives and unchanged signing tail. Disabled final V123 FILES79f71a0b had13 self payloads. Live preflight **595a14/session77899/bc8d1e/exit0** verified3606 total files, no already-tracked root paths and full current state. Root03f250 preserved disabled commit.py/FILES in `css-research-checkpoint-20261103-v123-root-activation-v1`, flipped only the execution literal and resealed active FILES `6c5b6f443c6458afcf9c161c871f7e75de2ed6b586aca8a6f7a0b00225d2563b`.

## Failed attempt and exact diagnosis

Attempt **04c546/session99447/0d66f2/exit1** stopped at private-index staged path equality, before creating signing.log or invoking the signer. Do not describe this as a signing-helper failure or infer signer availability. Root442bd8 verified HEAD, real-index bytes, all controls and all3606 selected bytes unchanged. No casefold duplicates or root-tracked case aliases existed (9688fa/0b5c89).

Independent recovery **c23b02/session12072/d4d7b3/exit0** verified the complete current snapshot equals the capture. It removed only the exact empty owned lock directory [16777230,281861545]. V123/result.json now records the actual failed pre-signing stage, unchanged state and completed recovery; SHA `869cd58fb648e2223e120eff01df36a2d41b874d7520f6f95e757c7e358ad4fa`. Root terminal is `css-research-checkpoint-20261103-v123-root-terminal.json`. Failed V123 must not be retried or used as signature authority.

Diagnostic **05486c/session12343/cdf720/exit0** recreated staging in a disposable private index without signing or changing HEAD/real index/canonical epoch. Default diff, explicit HEAD/no-renames/NUL diff and newly indexed paths all showed3581 files: exactly25 CSS Lean paths missing, no extras. Its owned temporary directory was removed. Frozen diagnostic `css-research-v123-staging-mismatch-v1` FILES is `7891dd8048a82901c7bd23e5a071b3bc4018ac60d52e135ea1493177ac70d76c` (de4e24).

Independent review12cc70 confirms all25 paths belong to `artifacts/css-spec-lean`, a separate clean Git repository at **162b20fb7c53a0ab89b20875a965baee98fb66bb**. Every current file matches its nested HEAD blob and the selected SHA256. Git omitted those embedded-repository files from Firefox staging; they are already committed dependencies, not lost work. V124 must retain this distinction and exact staged-path checking.

## Memo work, separate from publication

Saved-only memo replay **a0a08e/session17182/4cfe8a/exit0** completed in55.02 seconds:795 inputs, all11 binding negatives,14 stream negatives, two staging lanes and real inode rejection/cleanup preserved. Each of seven wrapped functions executed eight times (56 total), with106 hits. Root1e1e8f authenticated all40 final payloads and actual success. `css-saved-authority-replay-memo-v1` FILES is `09af5159ed2c0ab28a33062d57e48973ea3373654c276cabb9c9c155b7f88f32`; execution and deployment are disabled. Failed run1 remains preserved. No live owner used the optimization.

Independent review01bf64/621ec5/7e3f61 and implementation check68edd1 found V123's checkpoint lineage is linear and never enters those seven memoized capture functions. Root stopped the proposed adapter. Verified949ebd: no adapter directory, draft files, replay or deployment existed. V123/V124 use their unchanged checkpoint lifecycle; the successful memo prototype remains for its demonstrated saved-validator scope.

All earlier CSS/Stylo formal milestones, retained archives, recovery-backed WPTs and validated but unpublished repairs remain active. No pushes, Try jobs or external reports were made.
