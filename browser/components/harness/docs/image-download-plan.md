# Runtime download of the sandbox image (research)

Status: research only, no implementation. Why this exists: the guest kernel
(libkrunfw, GPL-2.0) and the Alpine rootfs (GPL components) must never be
bundled into the Firefox installer, so before this feature could ride any
release train the image has to become a runtime-downloaded component. This
doc surveys how Firefox delivers downloaded components today and what the
harness flow would look like in development and production.

## What ships vs what downloads

| Artifact | License | Size (now) | Compressed | Delivery |
| --- | --- | --- | --- | --- |
| `libkrun.dylib` (VMM) | Apache-2.0 | 3.8 MB | — | ships in the app (vendored, built by mach) |
| `harness-vm-helper` | MPL (ours) | tiny | — | ships in the app |
| `libkrunfw.5.dylib` (guest kernel) | **GPL-2.0** | 23 MB | ~9 MB | **runtime download** |
| rootfs template (Alpine + toolchain) | mixed, incl. GPL | 334 MB | **123 MB (gzip)** | **runtime download** |

One-time download on first use: **~130 MB** (zstd would trim further; the
rootfs dominates). Comparable in scale to Firefox Translations model sets
and smaller than typical local-ML models.

## Existing mechanisms surveyed

### GMP / Balrog (how OpenH264 arrives today)
The closest precedent for *downloaded native code that gets loaded into a
process*. Update check hits Balrog (`media.gmp-manager.url`,
`modules/libpref/init/all.js:3475`); the update.xml response is
content-signature verified (`GMPInstallManager.sys.mjs:308`), and the
downloaded zip is hash-verified against the manifest
(`ProductAddonChecker.sys.mjs:519`). Installs per-profile
(`<profile>/gmp-gmpopenh264/<version>`), checks are throttled to daily and
forced on buildID change, and dev overrides exist (`MOZ_GMP_PATH`,
`media.gmp-manager.url.override`). Operationally this means a Balrog
product entry and release engineering involvement per artifact update.

### Remote Settings attachments (how Translations models arrive)
`client.attachments.download(record)` (`services/settings/Attachments.sys.mjs:319`)
from the `firefox-settings-attachments` CDN. Integrity is equivalent to GMP
in structure: the *records* are content-signature verified at sync, and
attachment bytes are verified against the record's `hash` and `size`
(`Attachments.sys.mjs:561`). Translations downloads language models
on-demand with concurrency control and cleans up stale attachments on sync;
no hard size limit is encoded in-tree. Records give us versioning,
channel/filtering (`filter_expression`), staged rollout, and a preview
environment for testing. Caching is IndexedDB-oriented but a no-cache
downloader exists (`UnstoredDownloader`) for writing to our own directory.

### ML ModelHub (how local AI models arrive)
Downloads from `model-hub.mozilla.org` with host allowlisting, OPFS +
IndexedDB storage, cache-size caps, and rich progress callbacks — built for
multi-GB blobs. Notably it does **not** hash-verify content (host trust
only), which rules it out for the kernel dylib on its own. Its progress
plumbing is the UX bar we should match.

### Recommendation
**Remote Settings for both artifacts.** Rationale:

- Integrity properties match GMP (signed metadata + per-file sha256), which
  is the review bar for downloaded native code.
- One mechanism for both the dylib and the rootfs; records map naturally
  onto our existing `.rootfs-stamp` versioning.
- Staged rollout/preview built in; no new Balrog product.
- The rootfs could be split into layered attachments later (base / node /
  python / bun) for partial updates; start with one tarball for simplicity.

Balrog/GMP remains the fallback if security review prefers the established
"product addon" pipeline for the kernel specifically — `ProductAddonChecker`
is reusable outside GMP.

## What it looks like in practice

### Production flow
1. User opens about:harness and sends the first message (or presses a
   "set up sandbox" button — first paint should show the download cost
   up front: "one-time ~130 MB").
2. AgentService asks an `HarnessImageManager` for the image. It syncs the
   `harness-image` Remote Settings collection, picks the record matching
   the app version/platform, downloads the attachments with progress
   surfaced as chat meta-lines, verifies hashes, and unpacks into
   `<profile>/harness/image/<version>/` (kernel dylib + rootfs template +
   the stamp file).
3. `HarnessVM` resolves the kernel/template from that directory instead of
   GreD. The existing stamp logic already handles "template changed →
   refresh profile rootfs copies".
4. Updates: on RS sync (push-driven) a new record version marks the local
   image stale; download happens in the background or on next VM start;
   old versions are deleted after the swap (Translations does the same
   stale-attachment cleanup).
5. Kill switches: our own pref, plus Remote Settings is already covered by
   the `DisableRemoteSettingsAndAcceptSecurityConsequences` enterprise
   policy; a dedicated harness policy would follow the EME policy pattern.

Failure modes to design for: offline first-run (clear message + retry),
partial download (resume or restart; attachments API retries 3x), disk
pressure (image is ~360 MB unpacked per profile — see open questions).

### Development flow
- `setup-deps.sh` stays exactly as-is: pinned upstream fetches into the
  objdir, which local builds resolve via GreD. A pref
  (`browser.harness.image.source = "build" | "remote"`) defaults to
  `build` in local/unofficial builds — the GMP `MOZ_GMP_PATH` analog.
- Testing the download path uses the Remote Settings dev/preview
  environment (standard `services.settings.server` override) or a local
  attachment server in mochitests — both are established patterns in
  Translations tests.
- CI keeps using the objdir image; only dedicated tests exercise the
  remote path.

## macOS signing implications (production)

Two entitlement problems, both with precedent but neither free:

1. **Library validation**: hardened-runtime binaries cannot dlopen a
   downloaded (non-Apple, non-team-ID) dylib unless they carry
   `com.apple.security.cs.disable-library-validation`. In production
   signing, `plugin-container` deliberately does *not* have it — CDMs run
   in the separately-entitled `media-plugin-helper`
   (`security/mac/hardenedruntime/production/media-plugin-helper.xml`).
   `harness-vm-helper` should follow that model: its own hardened-runtime
   entitlement file with library validation disabled, scoped to the one
   process that is already Seatbelt-jailed.
2. **Hypervisor**: no entitlement in `security/mac/hardenedruntime/`
   mentions hypervisor today. `com.apple.security.hypervisor` works with
   Developer ID signing (and even ad-hoc, which is how dev builds run), but
   adding it to release signing is new territory for RelEng and will need
   its own conversation.

Gatekeeper is not an issue: files fetched by necko don't get quarantine
attributes (this is the same reason downloaded GMP plugins load).

## GPL compliance notes

Both artifacts are unmodified upstream builds, so compliance is
straightforward: host the exact source tarballs (libkrunfw + Alpine package
sources) next to the binaries or link to upstream, and state the offer in
about:license. This mirrors how OpenH264's BSD+GPL-ish distribution is
handled outside the installer. Building libkrunfw ourselves (rather than
trusting upstream GitHub release binaries) is required for production
anyway — provenance for a guest *kernel* should be Mozilla CI, not a
third-party release page.

## Open questions

- **Per-profile vs shared storage**: GMP installs per-profile (simple
  permissions, N× disk for N profiles). 360 MB unpacked per profile argues
  for a shared cache (`~/Library/Caches/Mozilla/` style) with per-profile
  hardlinks/clones — APFS clones make this nearly free on macOS, but it's
  a divergence from precedent.
- **Progress UX**: RS attachments lack progress callbacks (ModelHub has
  them). Either fetch manually with the record supplying URL+hash, or add
  a progress hook upstream.
- **Rootfs granularity**: single tarball first; layered attachments
  (base/toolchain) if update size matters later.
- **Windows/Linux**: this plan is macOS-shaped (libkrun/HVF). KVM/Linux is
  plausible with the same delivery; Windows would be a different substrate
  entirely (WSL2/Hyper-V) — delivery mechanism still applies.

## Implementation review (2026-07-25)

A severity-ranked review of HarnessImageManager against GMPInstallManager
and Remote Settings attachment patterns. Fixed immediately:

- **Manifest `version` was unvalidated** and flowed into
  `PathUtils.join` + a recursive delete: `version: "../.."` would have
  recursively deleted the profile. Both `version` and file `name` now
  require plain-filename shape (and reject `.`/`..`).
- **http URLs refused** (`browser.harness.image.allowInsecure` pref for
  the test server): the payload is a dylib the helper dlopens, so plain
  http was native-code-execution-via-MITM.
- **Single-flight resolve()**: concurrent VM starts previously raced the
  same `.tmp` stage dir (mutual deletion, torn installs); now they share
  one install promise.

Known gaps, deliberately deferred (severity order):

1. No content signing — the sha256s come from the same unauthenticated
   manifest; integrity only, zero authenticity. This is the ship-blocker
   the RS plan addresses; pointless to interim-fix at spike stage.
2. Downloads buffer fully in memory (~250 MB transient); should stream to
   a temp file like ProductAddonChecker, and the manifest should carry
   `size` to enforce a cap.
3. Offline hard-fails even with a valid installed image (manifest fetch
   precedes the `.complete` check); should fall back to the newest
   installed version and throttle checks GMP-style (daily + buildID).
4. No retry/backoff/timeout on fetches; a stalled connection hangs VM
   start indefinitely.
5. Tar extraction trusts /usr/bin/tar's default traversal refusals; add a
   hostile-tarball test before this matters.
6. Install failures emit no imageProgress event (UI sees the error via
   the VM error path only).
