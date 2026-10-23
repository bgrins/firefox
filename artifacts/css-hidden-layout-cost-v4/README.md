# Hidden-layout cost v4: early updater guard

**Source-only additive launcher; no browser run. Next invocation is restricted to the root-owned local build, never installed Firefox.** The only execution delta from sealed cost-v3 adds child environment MOZ_DISABLE_UPDATE_PROCESSING=1 and records that value in STARTUP-ENV/SPAWN/RESULT. All other five execution inputs are byte-identical to v3. Safe-mode controls, progress markers, workload, validator and strict cleanup remain unchanged.

The direct source guard is ShouldNotProcessUpdates in toolkit/xre/nsAppRunner.cpp: the named environment variable excludes early ProcessUpdates before preferences are available. This addresses the concrete updater-entry risk exposed by the rejected release diagnostic. It is not a universal later-update-service disable or no-relaunch proof.

No inert app.update.disabledForTesting preference, dangerous automation preference, Marionette listener or nonlocal-connection environment change is added. Later UpdateServiceStub suppression requires conditions absent from this bare fresh-profile launcher. Keep that boundary explicit and preserve the stop on any uncertain/escaped cleanup or profile removal failure. No user-global profile or installed application may be mutated by this proposal.

Every compared variant must use the same controlled environment and exact six execution inputs. Only presence of an inherited MOZ_SAFE_MODE_RESTART is recorded; its value is removed from the child. The parent should additionally require MOZ_DISABLE_UPDATE_PROCESSING=='1' in all startup receipts. The local runtime driver fixes the browser path to objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox.

The full cost-v3 measurement/progress/cleanup limitations are retained in PREDECESSOR-README.md. This v4 does not make the previously failed release cleanup successful or permit new installed-release runs. Mock startup-environment and HTTP-handler checks run without browser/process launch. The tiny source delta is for root/independent review before execution.
