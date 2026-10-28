# Untracked files after linear guard promotion

Read-only repeated inventory at signed HEAD b1cae69: 564 root paths, comprising 69 project files and 495 unrelated names. The only addition relative to the committed prior audit is the exact new linear crash WPT. All 68 prior project bodies, modes and device/inode identities still match. All 75 recovery-source bodies match both the recorded hashes and committed working copies. Nested status remains only its recorded .DS_Store; staging is empty.

The audit reads unrelated names only. No file was staged, removed or altered. After the new WPT is included in the exact two-file native commit, the expected list is 563 paths, 68 project and 495 unrelated; that future state must be verified by the signing checkpoint, not inferred as already complete. Replay audit.py before signing only; it intentionally binds this HEAD and current untracked state.
