# Cancellation installation rollback verification

Actual corrected-publisher installation 46d940/session76828/54df8c exited1 when its second new WPT attempted exclusive creation of the existing CREATED.json journal. The first source/test writes had occurred; this was not a pre-write rejection. The production rollback removed both newly created tests and restored the three source preimages, retaining their identities. INSTALL-FAILURE reports rollback_verified=true and manual_recovery_required=false.

Root independent audit d73758/session89017/71f98d/0 checks actual HEAD, clean tracked and staged diffs, restored source hashes/inodes, absent tests/lock, unchanged ownership/role, and full current source/browser/research/index state against the saved pre-install snapshot. Only a changed raw-index observation is allowed in the restored epoch; REPORT records the actual old/new hashes. This audit does not claim the cancellation patch was installed or committed. Current primary count remains158.

Fix the two-file creation journal in a new publisher version with genuine two-file and failure-path tests. Preserve the failed generated owner/runtime/log unchanged, use new destination names and authenticate the next signed research receipt. Do not retry the completed owner.
