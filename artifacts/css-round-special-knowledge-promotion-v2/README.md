Enabled, unexecuted successor for the explicit-null absence guard.

Promotion-v1 stopped before mutation or runtime creation: the new WPT was absent, but its canonical pin was null rather than omitted. This successor permits only an absent or null pin, still requires the file and ownership/identity entries to be absent, and keeps tracked-index/HEAD and parent ownership checks. The temporary null entry is removed only from the copied candidate epoch immediately before the existing exclusive-new-entry updater. Original epoch/control bytes, including the null pin, remain the rollback preimage.

Build/evidence/local phase are byte-identical to reviewed promotion-v1. Source, WPT, eleven accepted claims, paired evidence and final-validation requirements are unchanged. No agent execution, native acceptance or ID allocation. Historical failed package/log are preserved.
