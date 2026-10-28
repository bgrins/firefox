Installer for the reviewed fix139 payload, enabled only for root-owned execution after bounded review. No native/WPT installation or live preservation check has run from this package.

The intended transaction changes two existing native files in place, preserving their file identities, and creates seven absent WPT files with exclusive ownership. The other five native candidate bodies must match their existing pins. The full signed epoch, root/nested semantic index and flags, 50 parked source bodies, 140 recovery captures and 74 pre-existing untracked project files are checked before and after. New WPTs are tracked separately from those 74; the native-untracked list remains unchanged.

The installer reuses existing ownership, file creation, process and complete-epoch helpers. Desired and restoration bodies are read into authenticated buffers before writes. Source/control claims are rechecked immediately before mutation. Browser/build groups must be absent; both the completed 32-case run and the completed line-height-only observation must have terminal preserved receipts. Only the 16 container assertions must pass; readiness outcomes remain independent observations.

Runtime OWNED changes from 57 entries to 64, installed identities from 99 to 106, with the existing entries preserved except the two cleanup hashes. ROLE remains candidate/zoom-standalone-v1 and becomes built=false. The epoch keeps the same seven modified native paths, marks compiled=false, adds seven exact WPT pins/identities and records the payload manifest. PRE/POST control and epoch snapshots are saved. A failed transaction restores owned source bytes, removes only newly owned WPTs and restores control state; the raw-index observation may be refreshed only after full original semantic/source preservation is established, with no asserted cause of raw drift.

Both completed browser observations and their actual outer exit/hash receipts are now bound. The initial disabled guard was exercised before enablement and stopped before helper loading or live state reads. An artifact-only semantic replay accepted the actual saved observations and rejected ten corruptions; process and group checks were mocked in that replay. All referenced saved hashes and source/epoch bindings passed. No successful installation, rebuild, lint or final86 test claim is made.

Root-owned command:

```
python3 -I -S -B artifacts/css-registered-zoom-fix139-install-v1/install.py MANIFEST_SHA EPOCH_SHA
```

It writes its receipt under css-registered-number-native-runtime-v1/zoom-standalone-final-payload-1. The existing build.py must then rebuild with variant zoom-standalone-v1; real WPT lint and the final86 run remain required before acceptance.

This installer does not alter the parked-prototype restoration plan. If the zoom fix is accepted, later restoration/publication must explicitly retain the accepted zoom overlay instead of overwriting it with old source snapshots. That later policy change is outside this installation.
