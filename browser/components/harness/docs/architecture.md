# Firefox Harness — Architecture Overview

An experiment in Firefox *hosting* a coding agent rather than being driven by
an external one. The agent loop comes from a pinned Codex App Server sidecar;
every command and file operation the model performs executes inside a libkrun
micro-VM. The hard invariant: **no model-generated command ever executes on
the host** — conversations fail closed if the VM is unavailable.

macOS arm64 only, pref-gated (`browser.harness.enabled`), development spike.

## System overview

```mermaid
flowchart TB
    subgraph parent["Firefox parent process"]
        UI["about:harness<br/>chat UI · settings · VM tools"]
        AS["AgentService<br/>conversations · events · approvals<br/>rendering journal"]
        CASC["CodexAppServerClient<br/>JSONL over stdio, clean env<br/>model catalog (apply_patch)"]
        BRIDGE["CodexExecBridge<br/>exec-server: routes every<br/>process/fs op into the VM"]
        HVM["HarnessVM / HarnessAgent<br/>VM lifecycle · vsock protocol"]
        IMG["HarnessImageManager<br/>kernel + rootfs delivery<br/>(build objdir or verified download)"]
        TOOLS["HarnessBrowserTools<br/>tabs · history · page content<br/>present_files"]
        PROXY["HarnessProxy<br/>deny-default egress allowlist<br/>SNI-verified CONNECT"]
        SITESRV["HarnessSite actor<br/>serves harness-site:// bytes<br/>from workspace/sites, injects CSP"]
    end

    SIDECAR["codex-app-server sidecar<br/>(pinned binary, own CODEX_HOME)"]
    PROVIDER["model provider<br/>ollama · OpenAI · OpenRouter"]

    subgraph vm["libkrun micro-VM (Alpine, ~1s boot)<br/>read-only rootfs + tmpfs overlay"]
        GA["guest-agent (static C)<br/>exec · pty · fs · stdin"]
        WS["/workspace (virtio-fs)"]
        TOOLCHAIN["bun · node · uv/python<br/>sqlite3 · rg · jq · imagemagick"]
    end

    HELPER["harness-vm-helper<br/>Seatbelt jailer · hypervisor<br/>entitlement · dlopen(libkrun)"]
    WIDGET["widget frame<br/>(file content process)"]
    SITE["published site frames/tabs<br/>harness-site://name<br/>(webIsolated process per site)"]

    UI --> AS
    AS --> CASC
    CASC <-->|stdio JSONL| SIDECAR
    SIDECAR <-->|HTTPS| PROVIDER
    SIDECAR <-->|"WebSocket (loopback,<br/>single-accept)"| BRIDGE
    BRIDGE --> HVM
    AS --> TOOLS
    HVM --> IMG
    HVM -->|spawns| HELPER
    HELPER -->|Hypervisor.framework| vm
    HVM <-->|"vsock ⇄ unix socket<br/>JSON lines"| GA
    GA -->|127.0.0.1:3128| PROXY
    PROXY -->|allowlisted hosts only| INTERNET(("network"))
    UI -->|remote browser embed| WIDGET
    UI -->|live site cards| SITE
    SITESRV --> SITE
```

The sidecar believes it is talking to a normal "exec server" environment; the
bridge impersonates that protocol and forwards every `process/*` and `fs/*`
request over vsock into the guest. The model never gets a host shell.

## Security boundaries

```mermaid
flowchart LR
    subgraph zone1["Trusted: Firefox parent"]
        A["about:harness UI<br/>AgentService · bridge · proxy"]
    end
    subgraph zone2["Semi-trusted: sidecar process"]
        B["codex-app-server<br/>explicit env only<br/>(no shell/SSH/git creds)<br/>fail-closed server requests"]
    end
    subgraph zone3["Untrusted: micro-VM"]
        C["model-directed commands<br/>page content · downloads"]
    end
    subgraph zone4["Untrusted: widget frame"]
        D["agent-generated HTML<br/>file content process"]
    end
    subgraph zone5["Untrusted: published sites"]
        E["harness-site://name<br/>one webIsolated process per site<br/>own origin, storage, CSP"]
    end

    A ---|"stdio, JSONL<br/>requests denied by default"| B
    A ---|"vsock only<br/>(no NIC, TSI disabled)"| C
    A ---|"process isolation +<br/>injected CSP (no network)"| D
    A ---|"served bytes only<br/>(content never reads the profile)"| E
```

Layered enforcement, outermost first:

1. **VM boundary** — commands run in the guest; the only channels out are
   vsock (control) and virtio-fs (`/workspace`, explicit user mounts).
   The rootfs is a host-enforced read-only virtio-fs (a per-start APFS
   clone of the template) with a whole-root tmpfs overlay in the guest, so
   every write outside `/workspace` is ephemeral and rebuilds can never
   corrupt a running VM. Guest networking is off: libkrun's
   transparent-socket mode is disabled; HTTP(S) goes through the host-side
   policy proxy (deny-default allowlist, `CONNECT` verified against the
   TLS SNI, ECH rejected; default allows only the npm/pypi registries).
2. **Helper jailer** — the VM host process Seatbelt-sandboxes itself before
   loading libkrun: only the rootfs, declared volumes, and its sockets are
   reachable; read-only mounts are enforced host-side (and again in
   virtio-fs and in the guest mount).
3. **Bridge path policy** — exec-server fs ops are restricted to
   `/workspace` and `/mnt/<tag>`; writes to read-only mounts denied; every
   call audit-logged.
4. **Sidecar hygiene** — launched with a fully explicit environment
   (dedicated `CODEX_HOME`, no inherited shell state); unknown server→client
   requests are denied by default. Provider API keys live host-side only and
   are never guest-visible.
5. **Widget containment** — agent-authored HTML renders in a separate
   content process with an injected CSP that blocks all network, so
   presented artifacts cannot exfiltrate data the agent had access to.
   (about:harness is allowlisted for remote frames in `nsFrameLoader`,
   following the `aiWindow.html` precedent.)
6. **Site containment** — published sites (`harness-site://<name>/`) get
   real per-site origins in origin-keyed (`webIsolated`) content processes
   with a serve-time CSP; content processes never read the profile — a
   JSWindowActor serves the bytes. Web pages cannot link to or fetch the
   scheme (`URI_DANGEROUS_TO_LOAD`).
7. **Browser tools** — read-only (tabs, history, extracted page text);
   private windows excluded; page content is staged into the sandbox as
   files marked untrusted, never inlined into model context.
8. **Image delivery** — remote kernel/rootfs installs are https-only,
   sha256-verified, staged-then-renamed, with manifest path components
   validated; offline falls back to the newest installed image.

## Anatomy of a turn

```mermaid
sequenceDiagram
    actor User
    participant UI as about:harness
    participant AS as AgentService
    participant CX as codex-app-server
    participant BR as CodexExecBridge
    participant VM as micro-VM guest

    User->>UI: "chart my browsing by hour"
    UI->>AS: sendMessage()
    AS->>CX: turn/start (thread bound to VM environment)
    CX->>BR: process/start (ws)
    BR->>VM: exec over vsock
    VM-->>BR: streamed output
    BR-->>CX: chunks
    Note over CX,VM: model iterates: query places snapshot,<br/>bun/d3 script writes chart to /workspace
    CX->>AS: item/tool/call present_files
    AS->>UI: presentFiles event
    UI->>UI: stage CSP-injected copy,<br/>embed in remote browser frame
    CX-->>AS: agent message + turn/completed
    AS-->>UI: streamed deltas → markdown
```

## Design decisions worth knowing

- **Sidecar, not SDK**: the agent loop is a pinned external binary speaking
  a versioned JSONL protocol — swappable, updateable, crash-isolated.
- **Codex persists chats** (rollout files in our dedicated `CODEX_HOME`);
  the only host-side chat state is a per-conversation rendering journal,
  because codex's resume drops command output and presented artifacts.
  Temporary mode = ephemeral threads, never journaled.
- **Native edits via apply_patch**: a generated model catalog maps our
  OpenRouter slugs onto codex's bundled model metadata, which unlocks
  codex's built-in apply_patch tool — structured diffs routed through the
  exec-server fs bridge into the VM (no echo-append file building).
- **Publish by writing**: anything under `/workspace/sites/<name>/` with
  an `index.html` is live at `harness-site://<name>/` — no deploy step, a
  reload shows edits, IndexedDB/localStorage persist per site across
  restarts. Cards embed the live origin in the chat.
- **Profile data is shared by snapshot, not by mount**: live SQLite (WAL)
  and virtio-fs don't compose; `Sqlite.sys.mjs` online-backup copies
  places.sqlite into `/workspace` for the guest's sqlite3.
- **JS-first guest toolchain**: bun runs TS and auto-installs npm deps
  without a package.json; charts are produced as SVG (matplotlib has no
  musl-arm64 wheels — a good example of the guest being a real, opinionated
  environment).
- **Sessions are cheap**: rootfs copies are APFS clones; per-conversation
  VMs are a pref away (`browser.harness.sessionPerConversation`). A
  template stamp auto-refreshes stale rootfs copies when baked-in tooling
  changes.
- **GPL hygiene**: libkrun (Apache-2.0) is vendored and shippable; the
  guest kernel (libkrunfw) and Alpine rootfs are pinned downloads —
  `HarnessImageManager` is the runtime-fetch path (GMP-style manifest,
  sha256, staged installs) that production needs before any distribution
  (see [image-download-plan](image-download-plan.md)).

## Where things live

| Layer | Code |
| --- | --- |
| UI | `content/aboutHarness.{html,mjs,css}` |
| Agent orchestration | `codex/AgentService.sys.mjs`, `codex/CodexAppServerClient.sys.mjs` |
| VM routing | `codex/CodexExecBridge.sys.mjs`, `codex/WebSocketServer.sys.mjs` |
| VM substrate | `HarnessVM.sys.mjs`, `HarnessAgent.sys.mjs`, `helper/`, `guest/` |
| Image delivery | `HarnessImageManager.sys.mjs` |
| Published sites | `HarnessSiteProtocol.sys.mjs`, `actors/HarnessSite{Parent,Child}.sys.mjs` |
| Egress policy | `HarnessProxy.sys.mjs` |
| Browser tools | `HarnessBrowserTools.sys.mjs` |
| Image build | `vm/setup-deps.sh`, `vm/setup-codex.sh` |

Deeper reading: [README](../README.md) (setup, dev gotchas),
[codex-integration-plan](codex-integration-plan.md) (decisions + follow-ups),
[proxy-plan](proxy-plan.md), [model-providers-spike](model-providers-spike.md).
