# Compact post-v46 untracked audit summary

Root audit session 44101 completed with exit 0 (440230); root compact read 856f6f. The source report hash is preserved in SUMMARY.json without copying its full 563-name inventory again. It records 563 expected untracked paths: 68 project files with signed recovery copies and 495 unrelated names checked without reading their contents. No unexpected or unsaved project path was reported; staging was empty. The only tracked dirty file remained the held custom_properties.rs provider. HEAD and recovery signatures were verified, and the recovery commit was an ancestor.

This is the completed post-v46 audit, before the follow-up candidate run. It does not claim the live prototype files are tracked or that the worktree is clean. The historical recovery manifest has 75 entries; the current untracked project set has 68. No fresh audit or live-state mutation was performed while archiving this compact summary.
