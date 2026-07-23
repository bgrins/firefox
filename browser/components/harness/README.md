# Firefox Harness (about:harness)

An experiment in Firefox *hosting* a coding agent, rather than being driven by
an external one: a Codex App Server sidecar provides the agent loop, and every
command or file operation the model performs executes inside a libkrun
micro-VM — never on the host.

macOS arm64 only. Pref-gated behind `browser.harness.enabled`.

## System architecture

```
┌─ Firefox parent process ────────────────────────────────────────────────┐
│                                                                         │
│  about:harness (chrome page)                                            │
│    chat UI · history/resume · temporary mode · settings · VM tools      │
│        │                                                                │
│        ▼                                                                │
│  AgentService.sys.mjs          narrow conversation API + events         │
│    ├── CodexAppServerClient    JSONL over stdio; clean env; fail-closed │
│    │        │                  server requests; approvals surfaced      │
│    │        ▼                                                           │
│    │   codex-app-server ───────────► model provider                     │
│    │   (pinned sidecar,             (local ollama, or OpenAI via        │
│    │    dedicated CODEX_HOME)        ChatGPT login)                     │
│    │        │                                                           │
│    │        │ WebSocket (loopback, single-accept)                       │
│    │        ▼                                                           │
│    ├── CodexExecBridge.sys.mjs exec-server impersonation: routes every  │
│    │        │                  process/fs op into the VM; audit log;    │
│    │        │                  /workspace path policy                   │
│    │        ▼                                                           │
│    └── HarnessVM.sys.mjs       VM lifecycle + exec API                  │
│         │      └── HarnessAgent.sys.mjs   JSON-lines over vsock         │
│         │ spawns                                                        │
└─────────┼───────────────────────────────────────────────────────────────┘
          ▼
   harness-vm-helper (in-tree Program)
     · Seatbelt-sandboxed (jailer): only rootfs/volumes/socket reachable
     · com.apple.security.hypervisor entitlement (re-signed each start)
     · dlopens vendored libkrun ──► Hypervisor.framework
          │
          ▼
   Alpine micro-VM guest (~1s boot)
     · guest-agent (static C): concurrent exec, streamed output, fs ops
     · /workspace  ⇄  profile/harness/workspace (virtio-fs)
     · AGENTS.md seeded with sandbox context; sqlite3 available
     · no network (TSI disabled); vsock is the only channel out
```

Key modules:

| Piece | Role |
| --- | --- |
| `HarnessVM.sys.mjs` | VM lifecycle, exec API, places-DB snapshotting |
| `HarnessAgent.sys.mjs` | JSON-lines client for the guest agent (vsock⇄unix socket) |
| `guest/guest-agent.c` | in-guest daemon: exec jobs, stdin/env, kill, output streaming |
| `helper/harness-vm-helper.c` | boots libkrun; Seatbelt jailer; entitlement holder |
| `codex/CodexAppServerClient.sys.mjs` | pinned sidecar process + JSONL protocol |
| `codex/AgentService.sys.mjs` | conversations, approvals, environment wiring, login |
| `codex/CodexExecBridge.sys.mjs` | loopback WS exec-server; the routing chokepoint + audit log |
| `codex/WebSocketServer.sys.mjs` | minimal RFC6455 server used by the bridge |
| `JsonLines.sys.mjs` | shared line-splitting + request-correlation core |
| `third_party/libkrun` | vendored VMM (Apache-2.0), built by setup script |

## Security model (invariants)

1. Model-generated commands never run on the host. Conversations *require*
   the VM: the environment is registered before `thread/start`, and creation
   fails closed if the VM can't run.
2. The guest sees only its rootfs copy and explicit virtio-fs mounts —
   never the profile, home, or credentials. No network (TSI disabled).
3. Every Codex process/fs operation crosses `CodexExecBridge`: deny-by-default
   methods, `/workspace`-only paths, full audit log.
4. The helper is Seatbelt-sandboxed before parsing any guest-controlled data,
   so a hypothetical VMM escape lands in a deny-by-default sandbox
   (`--seatbelt-selftest <path>` demonstrates the confinement).
5. Server→client requests from the sidecar are denied unless explicitly
   surfaced (approvals go to the UI; unanswered ones decline after 120s).

Deeper documents: `docs/codex-integration-plan.md` (plan, decisions, security
boundary assessment, follow-ups), `docs/proxy-plan.md` (future gated egress).

## Development setup

```sh
# one-time: VM runtime deps (builds vendored libkrun; fetches pinned
# guest kernel + Alpine rootfs + apks; cross-compiles guest-agent)
./browser/components/harness/vm/setup-deps.sh

# one-time: pinned codex-app-server sidecar
./browser/components/harness/vm/setup-codex.sh

./mach build
./mach run    # set browser.harness.enabled=true, open about:harness
```

For free/local model turns, run [ollama](https://ollama.com) with the model
from `codex/ollama-codex-home/config.toml` pulled (default `gemma4:latest`).
OpenAI accounts: Settings → OpenAI account → Sign in to ChatGPT.

### Codesigning (why the VM works in an unsigned local build)

Hypervisor.framework requires the `com.apple.security.hypervisor`
entitlement. Local mach builds are only ad-hoc signed — but that entitlement
is honored on ad-hoc signatures, so `HarnessVM` re-signs
`harness-vm-helper` (with `helper/harness-vm-helper.entitlements.xml`)
before every VM start. This is needed each time because relinking during
`./mach build` resets the binary to a plain ad-hoc signature. Production
signing would instead add the entitlement to the release signing config
(`taskcluster/config.yml` hardened-sign-config).

### Shared folder mounts and macOS privacy (TCC)

User-selected folders (Settings → Shared folders) mount at `/mnt/<tag>` with
three-layer read-only enforcement when requested (libkrun virtio-fs
`read_only`, a read-only Seatbelt grant in the helper, and guest `-o ro`).
Caveat: TCC-protected folders (Downloads, Desktop, Documents) require the
*helper process* to pass macOS privacy checks; if denied, the VM refuses to
start with a clear error rather than mounting silently empty. Non-protected
paths are unaffected. Fallbacks under consideration: copy-in staging, or an
fd-based virtio-fs root upstreamed to libkrun.

### Dev-loop gotchas

- Changed `.sys.mjs` files can be served stale from a profile's startup
  cache; relaunch with `MOZ_PURGE_CACHES=1` when in doubt.
- `setup-deps.sh` writes into `dist/bin`; run `./mach build faster`
  afterwards so the `Nightly.app` bundle mirror (what `mach run` and
  mochitests use) picks the artifacts up.
- Tests: `./mach mochitest --headless browser/components/harness/tests/browser`
  — they skip gracefully when setup artifacts or ollama are missing.
