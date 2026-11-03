# V130 research checkpoint preparation

This disabled checkpoint follows signed cancellation native commit `2409a410a2641c54a42feefd3c998cd58cbf028e`, whose sole parent is signed V129 research `e795bd155abbcf3bc6d9d861ad4ee22d610b07ad`. Its actual native receipt is `04e71056a08e9180b061cd10e5de1255937b248e315b6e182a4e4e0da83e3df8`. The separate signed standalone alternative is preserved as evidence; it did not replace the main HEAD and is not counted as another repair.

The current authority bridge is the actual completed `css-post-cancellation-raw-index-observation-v1` operation `87342e / 63689 / c65f00 / exit 0`, sealed `f0db98c0…`. Its real schema uses `BEFORE.json`, `AFTER.json`, `PRE-CURRENT-EPOCH.json`, current controls and `ROOT-TERMINAL.json`. The saved admission checks the exact native receipt and research parent, actual result/terminal, unchanged OWNED/ROLE, and the one-field epoch change from `749a79f5…` to `3e039655…`. Full before/after snapshots are equal and retain the same semantic index. The cause of the raw-index change remains unestablished; neither a failure-based authority bridge nor a different historical refresh receipt is invented.

`validate_native_raw_observation` compares whole epochs and full snapshots with typed JSON serialization, so Boolean/integer substitution is not treated as equality. It requires the exact five committed native/WPT hashes and installed identities, the unchanged cancellation publication marker, clean semantic diffs, and zero new native-fix increment. The current app is not claimed rebuilt by publication. No prior native/browser/proof suites or recursive historical validators are rerun.

The existing manifest/selection checks, private-index staging, exact staged set and blobs, configured signing, rollback and canonical transaction remain byte-identical to V129 apart from version/message labels. Capture retains the full live observer and control/source/index/lock checks; its changed authority prefix requires the exact native commit, sole signed-research parent and five-file tree change. Root owns fresh capture and any later normal signing attempt. The gate and future capture binding remain disabled/pending.

Selection records completed V129 outputs, cancellation installation/delivery/commit, standalone execution and its honest early guard failure, inventory159, tree-boundary and route-proof research, both typed-taint publisher preparations, completed cleanup evidence, and roadmap190. Exact immutable main-HEAD blobs are excluded. Nested CSSLean's 25 tracked paths remain excluded and pinned. Partial activation manifests are selected as explicit files rather than claimed complete packages. Browser binaries, caches, live native/WPT paths and future publication outcomes are excluded. `INVENTORY.json` gives the exact completed selection and exclusions.

The focused saved check authenticates selection and closure bytes, immutable native Git objects, the authority bridge, and unchanged transaction/observer code. Mutation controls exercise receipt kinds and fields, terminal/result association, raw-only epoch reconstruction, typed before/after equality, semantic state, controls, research-parent authority and disabled/pending gates. These are saved checks, not a fresh current-state observation or signing attempt.

Root capture command after preserving this preparation:

```sh
python3 -I -S -B artifacts/css-research-checkpoint-20261103-v130/capture_current.py > artifacts/css-research-checkpoint-20261103-v130-capture-root.log 2>&1
```

After actual capture binding, add its closed output/log/terminal, reseal, and run the existing `commit.py --check` before root's gate-only signing activation. The message is `No bug - Record cancellation publication and subsequent validation research. r?#firefox-style-system-reviewers`. No signing bypass, native acceptance increment or publication retry is implied by this preparation.
