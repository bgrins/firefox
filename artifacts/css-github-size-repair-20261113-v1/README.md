# Repair of rejected GitHub push

The unpublished range above `fd4b301f80b0aaed9f198a978f00ab2e99300147` contained four generated `checkpoint-staged.patch` blobs larger than 50 MiB. The v41 snapshot exceeded 100 MiB and caused GitHub to reject the branch push.

Only those four raw snapshot paths were removed from history. The 255 outgoing commits retain their order and boundaries; 11 prefix commits retain their hashes, and 244 affected commits were rebuilt with the configured signing key and individually signature-verified. Independent comparisons checked every old/new tree, allowing only the four deletions, and verified author/committer identities, dates, messages and parent mapping. No Firefox source or test bytes changed in any commit. The working-tree changes and untracked files were preserved.

`COMMIT-MAP.json` translates original commit IDs to the repaired history. The bugfix ledger uses the new IDs. Immutable proof and validation receipts retain their original IDs and can be interpreted through the map; this rewrite does not claim new proof or browser-test coverage. The CSS goal remains paused and the accepted native-fix count remains 158.

The four snapshots are retained under `archives/` as deterministic gzip files, each smaller than 50 MiB. `ARCHIVES.json` records original Git object IDs, SHA-256 hashes, sizes and compressed hashes. Decompress an archive to the original path listed there when an old local signing receipt needs it. The existing raw local files were retained, and gzip round-trip hashes were checked. Do not force-add raw generated staging snapshots again; preserve a hash and path manifest instead.

The original history is retained locally at `backup-stylo-bloom-verification-2-before-size-repair-20261113`. Do not push that backup branch or use `git push --all`: the backup intentionally retains the oversized blobs. The existing remote branch tip is still an ancestor of the repaired branch. A normal explicit push is sufficient:

```sh
git push origin stylo-bloom-verification-2
```

Check the full outgoing object graph before future pushes:

```sh
python3 -I -B artifacts/stylo-bloom-tools/check-push-blob-sizes.py --base origin/stylo-bloom-verification-2
```

The checker reports all newly reachable blobs, including historical versions and files deleted at the tip. It warns above 50 MiB and fails above 100 MiB. Its regression check detects the original rejection and accepts the repaired range. No remote refs were modified by this repair.
