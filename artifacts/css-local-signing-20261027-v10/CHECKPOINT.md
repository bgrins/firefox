# CSS verification signing checkpoint

The Lean attribute guard model and its independent replay, build-metadata-bound browser comparison harness, and upstream fallback repair variants are signed as separate research commits. The accepted bugfix count remains 135.

The Lean replay passed 13 general laws and 23 kernel examples, with nine false claims rejected. It models normalized substitution and guard behavior; it does not prove the Rust implementation correct. Harness assessment and build-identity controls passed without running a browser. The upstream variants have exact patch transport and Rust syntax checks, but have not been built or browser-tested.

All 132 source bodies in the existing signed unfinished-work snapshot still match the working tree, including the 129 unfinished paths. The recovery patch remains in `artifacts/css-unfinished-work-checkpoint-20261027-v5`, committed as `c658aea9918cc81f60af0bbf46877530b6bfed64`. The later full native build, 20 selected GTests, and ordinary WPT results are preserved in the preceding validation commits. Unfinished source changes remain in the working tree for continued development; no unrelated files were staged.

Next, run the original browser comparison, apply and build the reviewed fallback repair, then require all 34 candidate assertions and unchanged regression results before accepting a native-plus-WPT fix. Refresh the native runtime's continuation epoch from this signing checkpoint before execution. No native repair was applied or accepted during this signing checkpoint.
