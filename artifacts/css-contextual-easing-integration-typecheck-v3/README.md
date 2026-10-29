# Configured contextual easing typecheck retry

Enabled after actual raw-index refresh 85459/913aaf -> 4ee28b/0 and root review. The preceding configured
check exited 101 with serde trait errors, then restored all six sources and
passed full preservation checks. That failure remains unchanged in runtime 2.
This successor uses the sealed v2 candidate, which removes two unnecessary
serde derives. The other five candidates and all six bases are unchanged.

The runner authenticates two exact manifests: the new candidate and the original
six-source handoff. Each capture must be an exact path/hash entry in one of
those manifests. Relative-path, symlink, body-hash and signed-HEAD base checks
remain required. `RUN-DELTA.patch` shows the sole code change. Source captures
are referenced without duplication; arbitrary capture roots are not permitted.

The existing configured Gecko Cargo `check --offline -j2`, objdir target,
30 GiB admission/15 GiB running stop, timeout, ownership and source restoration
are unchanged. The prior failed compiler and caffeinate groups must also be
absent. Only accepted 143's specified easing source may be overlaid; generic
145, other accepted files and the held provider remain fixed. Full epoch
verification stays in memory. No canonical publication or full epoch copies
occur during the check.

Successful Gecko compilation would not establish Servo cfg support, selected
rule scope transport, dependency/lifecycle correctness, browser behavior or
activation readiness. Parser guards remain closed. No compiler or source
overlay was executed by this preparation.

Root-only command:
`/Users/bgrins/venvs/firefox/bin/python -I -S -B artifacts/css-contextual-easing-integration-typecheck-v3/run.py --run FILES_SHA256`.
