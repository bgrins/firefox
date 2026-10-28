# Untracked work audit after Round experiment

At signed HEAD `995e0d2df8d7439fbd1a38f6d6fc46af247034e1`, all **563 untracked paths** match the prior signed checkpoint: **68 project files** (53 WPT, 11 layout, 3 Servo, 1 DOM) and **495 unrelated paths**. Unexpected paths within this comparison: **0**. Unsaved project files within this comparison: **0**.

Each of the 68 project files has the same body hash, size, permissions, device and inode as the prior post-rename inventory. Every body also exactly matches both its local recovery copy and that copy’s Git blob in the signed current HEAD. The recovery manifest contains 75 historical entries; 68 are currently untracked. Both the recovery commit’s ancestry/signature and current HEAD signature were checked. These are archived unfinished prototypes, not accepted fixes or permission to delete their live copies.

The 495 unrelated path names are unchanged. Their current type/size/mode/identity were inspected using lstat only. No unrelated contents, secret values, or content hashes were read. The prior inventory did not pin those types or bodies, so historical type/content equality is **not** claimed.

The sole tracked working change is `servo/components/style/custom_properties.rs`, exactly matching the canonical held, unaccepted provider candidate. Staging is empty. The nested Lean repository still reports only its recorded untracked `.DS_Store`. No source, Git index, runtime control or nested repository mutation was performed. The census and HEAD were checked again at the end.

Reproduce read-only from this checkout:

```sh
python3 -I -S -B artifacts/css-untracked-audit-post-round-20261028-v1/audit.py
```

The script emits JSON and requires the expected historical/current state; after later changes it may intentionally fail rather than certify a different tree. It uses `git --no-optional-locks -c core.fsmonitor=false ls-files --others --exclude-standard -z`, without collapsed directories. The saved inventory records all names, project hashes and metadata; unrelated metadata is observation only. Verification passed e3c140→e480e0 and the final explicit HEAD-signature/schema check passed 7cb388→8d1188. No browser, build, staging, deletion or signing ran.
