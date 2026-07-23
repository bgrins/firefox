# Codex App Server integration on the harness VM stack

Reviewed version of the "Firefox prototype using a pinned Codex App Server and
VM-backed execution" handoff, adjusted to build on the working micro-VM stack
in this component instead of introducing a parallel one. The handoff's
security invariants and acceptance tests are adopted wholesale; the deltas
below are about *how*, informed by what is already implemented and verified
here.

## What already exists (do not rebuild)

| Handoff component | Existing equivalent | State |
| --- | --- | --- |
| "native VM broker helper" | `harness-vm-helper` (in-tree `Program()`, dlopens vendored libkrun) | boots Alpine in ~1s, vsock, virtio-fs, hypervisor entitlement handling |
| "sandboxd in Linux VM" | `guest/guest-agent.c` | JSON-lines over vsock: concurrent exec, streamed stdout/stderr, exit codes, env, stdin (b64), timeouts, output caps, kill-on-disconnect |
| "VmBrokerClient" | `HarnessVM.sys.mjs` + `HarnessAgent.sys.mjs` | parent-process lifecycle + exec API |
| guest transport | vsock port ⇄ unix socket (`krun_add_vsock_port2`) | verified |
| network isolation | implicit-TSI disabled by default in the helper | verified (`wget` fails in guest); gated egress design in `proxy-plan.md` |
| guest image | Alpine minirootfs template, pinned fetch in `vm/setup-deps.sh` | verified |
| smoke tests | `tests/browser/browser_harness_vm.js` | 14 asserts, ~13s incl. real boot |

## Key decisions (deltas from the handoff)

### 1. VM backend: libkrun, not Virtualization.framework + new broker

The handoff proposes a separate signed native broker owning a
Virtualization.framework VM. We already have a smaller version of exactly that
boundary: hypervisor code lives outside Firefox in `harness-vm-helper` +
vendored libkrun, spawned per-VM by the parent. Keep it.

- `PROTOTYPE_HOST_OS` = macOS arm64 (what this stack runs on today).
- Portability story is *better* than Virtualization.framework: libkrun also
  backs Linux/KVM with the same helper. Windows/HCS remains future work either
  way; the `HarnessVM` session interface is the host-neutral seam.
- Known macOS quirk already solved here: the helper needs the
  `com.apple.security.hypervisor` entitlement and local relinks drop it, so
  HarnessVM re-signs before each start. Any "signed helper" plan must keep
  this step.

### 2. Exec-server bridge lives in the Firefox parent, in JS

Codex App Server connects to `ws://127.0.0.1:<port>` speaking its exec-server
protocol. The handoff puts that bridge in the native broker. Put it in the
parent instead (`CodexExecBridge.sys.mjs`):

- Every process/filesystem operation Codex performs then passes through one
  reviewable JS chokepoint — which is precisely what §12 of the handoff needs
  for routing instrumentation, and matches the control-plane-in-the-parent
  principle the whole component follows (same reason the egress proxy is
  parent-side in `proxy-plan.md`).
- Implementation: `nsIServerSocket` on loopback, ephemeral port, accept
  exactly one connection then stop listening, hand-rolled WS handshake +
  framing (bounded, ~200 lines; RFC6455 server side with required client
  masking). Translate exec-server ops → guest-agent JSON-lines.
- Fallback if WS-in-JS fights us: a small bridge thread in the helper. Do not
  start there.

### 3. sandboxd = guest-agent, extended

Do not write a new sandboxd. Extend the existing agent's protocol with the
exec-server-required surface:

- Process ops: already covered (spawn/stream/kill/exit). PTY support is the
  one open question — if the pinned exec-server schema requires PTY output for
  shell commands, add `forkpty` to guest-agent (straightforward; the poll loop
  already generalizes). Resolve against the generated schema before coding.
- File ops (`read/write/list/mkdir/stat/canonicalize/remove/copy`): add as
  guest-agent ops executed **inside the guest**, not as host-side IOUtils on
  the shared workspace. This matters: path/symlink semantics must be evaluated
  in the *guest* namespace. A model-created symlink `/task/work/x -> /etc/foo`
  must resolve to the guest's `/etc`, never the host's — host-side fs handling
  of a guest-writable tree is a sandbox escape shaped exactly like the routing
  bugs §12 worries about, just on our side of the boundary.
- Path policy in guest-agent: canonicalize first, then require the result
  under `/task`; reject traversal, reject writes outside `/task/work` and
  `/task/output`. Deny-by-default on unknown ops (already the case).

### 4. Task filesystem: virtio-fs with discipline, not RPC-only

The handoff forbids host mounts entirely and moves all bytes via
putFile/getFile RPC. Amended position:

- Mount a **dedicated per-task host directory** (`profile/harness/tasks/<id>/`
  with `input/`, `work/`, `output/`) into the guest as `/task` via virtio-fs.
  This is not a profile/home/arbitrary mount; it is a directory that exists
  only for the task. Staging inputs = parent `IOUtils` writes; retrieving
  outputs = parent reads. This is already proven in both directions here and
  removes an entire RPC surface.
- Rules that make it safe:
  - Host-side code never resolves symlinks inside the task dir (write inputs
    before task start; read outputs with nofollow semantics; treat symlinks in
    `output/` as errors).
  - `input/` is exported read-only to task commands (guest-side `mount -o ro`
    bind or chmod; verify in tests).
  - The task dir is deleted when the task ends.
- Pure tmpfs + RPC remains the stricter fallback if virtio-fs symlink review
  finds anything uncomfortable; the bridge API shape doesn't change.

### 5. One long-lived VM first; per-task sessions are a follow-up

To be clear about granularity: nothing here proposes a VM per bash command.
The handoff wanted a fresh VM per *conversation/task*; even that is deferred.
The first slices reuse the existing long-lived `HarnessVM` singleton and its
`/workspace` mount — simplest possible end-to-end, and boot (~1s) + rootfs
clone (~130ms) mean sessionizing later is cheap when isolation-between-tasks
starts to matter. Follow-up shape when it does:

- `HarnessVM.createSession({taskDir, mem, cpus})` → fresh rootfs clone, fresh
  vsock socket; `session.destroy()` deletes rootfs + task dir; startup sweep
  reconciles orphans after a crash. The about:harness fiddle becomes one
  long-lived session.

### 6. Guest image additions

Alpine minirootfs (busybox) already covers sh/coreutils/sed/awk/grep/tar/
unzip/file. The guest has no network, so add the rest at template-build time:
`vm/setup-deps.sh` fetches pinned `.apk` packages (bash, jq, sqlite,
ripgrep — apks are tarballs; extract into the template) with sha256 pins, same
pattern as everything else in that script. Run task commands as an
unprivileged user: create `task` (uid 1000) in the template; guest-agent
setuids for exec ops (keep root for the agent itself).

## Codex sidecar (adopted from the handoff, with notes)

The Codex-side plan is adopted as written — pinned binary manifest + sha256
verification (reuse the setup-deps pinning pattern; store under a versioned
dir in `~/.mozbuild/harness/codex/` or dist, never committed), generated
schema checked in and version-coupled, JSONL client over `Subprocess` with
size limits and pending-request rejection on exit, narrow `AgentService` API,
allowlisted methods only, no `thread/shellCommand`/`process/spawn`/host `fs/*`.

Notes:

- `Subprocess.call` with an explicit `environment` (not `environmentAppend`)
  gives the clean env the handoff requires; set dedicated `CODEX_HOME`/`HOME`/
  `TMPDIR` under `profile/harness/codex/`. Distinction worth keeping sharp:
  CODEX_HOME (credentials) is host-side sidecar state — it may live under the
  profile; it must never be readable from the guest or referenced in prompts.
- The JSONL client is a near-clone of `HarnessAgent.sys.mjs` (same buffering,
  id-correlation, timeout shape) minus the latin1/vsock quirks; factor the
  line-protocol core out rather than duplicating it.
- Host canary test from §12: put canaries in `$HOME` and CWD of the sidecar
  and assert exec-bridge logs show zero host fallbacks while the guest ops
  succeed. This drops naturally out of decision 2 — there is no code path for
  a guest op that does not cross the bridge.

## Revised architecture

```
sidebar / about:harness (chrome page)
        │  narrow service API + events
        ▼
AgentService.sys.mjs (parent)
  ├─ CodexBinaryManager.sys.mjs      pinned manifest, sha256, version check
  ├─ CodexAppServerClient.sys.mjs    JSONL over stdio (Subprocess)
  ├─ CodexExecBridge.sys.mjs         loopback WS server, single-accept,
  │                                  op translation + routing audit log
  ├─ TaskWorkspaceManager.sys.mjs    stage input/, retrieve output/
  └─ HarnessVM session               (existing stack)
        │ spawns
        ▼
harness-vm-helper ── libkrun ──► guest
        vsock ⇄ unix socket          guest-agent (exec + fs ops, /task policy)
        virtio-fs                    /task {input ro, work rw, output rw}
```

Codex never talks to the guest directly; the guest never sees credentials or
the network; every operation crosses `CodexExecBridge`, which is also the
instrumentation point.

## Locked plan (2026-07-23)

Decisions settled with the project owner:

- **UI**: conversation panel in about:harness. Sidebar is later packaging.
- **Codex binary**: pinned download with sha256 verification via a setup
  script, exactly the libkrunfw pattern — never committed, never fetched
  "latest" at runtime, dev-setup only.
- **Models**: multi-model from day one via Codex's provider configuration in
  our dedicated `CODEX_HOME/config.toml`. Primary spike path is a local
  OpenAI-compatible endpoint (ollama, e.g. gemma) — free, no credentials, no
  network questions. OpenAI proper uses a developer-preauthenticated
  `CODEX_HOME` when wanted; no auth UI.
- **VM granularity**: reuse the existing long-lived VM + `/workspace`
  (decision 5). No sessionization in the first slices.
- **PTY**: pipes-first; `forkpty` only if the pinned schema demands it.
- **Protocol**: schema generated from the pinned binary is step 0; no
  protocol structures written from memory. Golden transcript captured for
  tests.
- **Guest fs policy**: default-deny outside `/task`→(`/workspace` for now);
  read-only allowlist entries added only when transcripts prove the pinned
  build needs them.

### Slices (in order, each lands with tests)

1. **Pin + probe**: release manifest (version/url/sha256), `setup-codex.sh`,
   schema generation + digest; handshake the real binary over stdio; verify an
   ollama-backed chat turn works headlessly.
2. **Client**: factor the JSON-lines core out of `HarnessAgent`;
   `CodexAppServerClient.sys.mjs` (Subprocess, clean env, dedicated
   CODEX_HOME/HOME/TMPDIR, id correlation, size limits, exit rejection,
   orderly + forced shutdown). Test against the real pinned binary
   (initialize/shutdown needs no model); skips when the binary is absent, same
   pattern as the VM mochitest.
3. **Chat end-to-end**: `AgentService.sys.mjs` narrow API
   (createConversation / sendMessage / interrupt / events) + about:harness
   chat panel streaming deltas. Method allowlist; no host-exec methods
   reachable.
4. **Exec bridge**: `CodexExecBridge.sys.mjs` loopback WS server
   (single-accept, ephemeral port) translating exec-server ops onto
   `HarnessAgent`; `environment/add` wiring; audit log of every routed op;
   host-canary + routing-proof mochitests (§12 of the handoff).
5. **Guest fs ops** in guest-agent as the bridge's fs backend (guest-namespace
   canonicalization + `/task` policy), sized by what the schema/transcript
   actually require.

### Follow-ups (explicitly deferred)

- **User-selected additional volume mounts**: let the user attach chosen host
  directories into the guest (helper already supports multiple `--volume`
  host:tag pairs; needs UI for picking a directory + read-only/read-write
  choice, guest-side mount wiring, and extending the exec-bridge path policy
  beyond `/workspace` to the mounted roots). Never offer profile/home
  wholesale; per-directory opt-in only.
  - UI shape: `nsIFilePicker` in `modeGetFolder` from the settings panel
    (e.g. "add folder..." → Downloads), rows with tag + RO/RW toggle +
    remove; persisted as a JSON pref (`browser.harness.mounts`:
    `[{path, tag, readOnly}]`). Mount changes require a VM restart; the
    settings panel should say so and offer the restart.
  - Each mount extends: helper argv (`--volume path:tag`), the guest boot
    line (`mount -t virtiofs tag /mnt/tag`, `-o ro` when read-only), the
    exec-bridge path allowlist (`/mnt/tag`, write-denied when RO), and the
    host-side symlink discipline rules from decision 4.
- **Profile-data snapshots for the agent** (places.sqlite pattern, landed
  2026-07-23): never mount live SQLite DBs — WAL + shm + virtio-fs locking
  don't compose. Instead use the `Sqlite.sys.mjs` online-backup API to write
  a consistent snapshot into the workspace and query the copy with the
  guest's sqlite CLI (`HarnessVM.snapshotPlacesToWorkspace()`). Same pattern
  extends to cookies.sqlite, formhistory.sqlite, etc. — one generic
  "share profile DB snapshot" API with an explicit allowlist of DBs is the
  follow-up.
- **Multi-VM sessions (per-conversation VMs)** — expanded plan:
  - Sessions: `HarnessVM.createSession({taskDir, mem, cpus, mounts})` → each
    session owns a rootfs clone, vsock socket, HarnessAgent connection, and
    exec-bridge instance; `AgentService` maps conversationId → session and
    registers one `environment/add` per session.
  - Disk usage: rootfs copies are APFS `clonefile` clones (`cp -c`), so a new
    VM costs only metadata up front; blocks are copy-on-write, meaning disk
    grows with what each guest actually modifies (typically MBs). Guest
    writes to its rootfs persist for the session's lifetime; destroying the
    session reclaims them.
  - Persisting image changes: a session's modified rootfs can be "promoted"
    (rename into a named-images dir) to become the template for future
    sessions — cheap snapshot/restore without any overlayfs work. True
    RO-base + tmpfs overlay stays the later hardening step for
    no-persistence guarantees.
  - Named volumes: reusable host dirs (profile/harness/volumes/<name>)
    mounted into any session via virtio-fs — survive VM destruction, shared
    state between sessions when wanted.
  - Management UI: a VM panel in about:harness listing sessions (conversation,
    helper pid, uptime, rootfs size via `du`, workspace path) with
    kill/destroy per row; plus startup reconciliation that sweeps orphaned
    helper processes and session dirs after a crash.
- **Connect additional tools to the agent**: beyond the exec-server surface —
  e.g. exposing browser-side capabilities (page content, screenshots,
  downloads) as tools the model can call. Options: register as MCP servers in
  the sidecar's config (Codex supports MCP; currently disabled by our
  fail-closed posture) or stage data into `/task/input` via
  TaskWorkspaceManager and reference guest paths. Requires a per-tool
  allowlist and the same audit-log treatment as exec.

- Per-task ephemeral VM sessions + task-dir lifecycle + crash reconciliation.
- Read-only base image + tmpfs overlay; unprivileged `task` user for exec.
- Guest image: standard developer tooling baked into the rootfs template at
  setup time (pinned apk/static-binary fetches, since the guest has no
  network): bash, node, uv/python, rg, jq, yq, sqlite, git, plus an image
  toolchain for screenshots coming from web pages (imagemagick or
  libvips/vipsthumbnail for convert/resize/compare, pngcrush/oxipng
  optional). Alpine apks are plain tarballs, so setup-deps.sh can extract
  them into the template without apk itself; prefer static builds where the
  dependency tree gets deep (node, uv publish musl-static artifacts).
- Gated egress proxy (`proxy-plan.md`) — guest stays offline until then.
- virtio-fs symlink/`..` adversarial review + tests — required before calling
  the workspace mount a *security boundary* rather than a dev prototype.
- Sidebar UI, approval-flow UX, concurrent conversations, other host OSes.

## Probe results (2026-07-23, pinned 0.145.0)

Verified live against the pinned `codex-app-server` binary over stdio with the
in-tree `codex/ollama-codex-home/config.toml` (gemma via local ollama, no
credentials):

- Pin: `codex-app-server` 0.145.0 from `rust-v0.145.0`
  (dedicated app-server asset, sha256 in `vm/setup-codex.sh`).
- Schema: generated JSON schemas are checked into the codex repo at the tag
  under `codex-rs/app-server-protocol/schema/json/v2/` — no generation step
  needed; the dedicated binary has no `generate-json-schema` subcommand.
- Protocol (v2, JSON-RPC-ish JSONL): `initialize` → `initialized` →
  `thread/start` → `turn/start {threadId, input:[{type:"text",text}]}`.
  Streaming arrives as notifications: `turn/started`,
  `item/started`/`item/agentMessage/delta`/`item/completed`,
  `thread/status/changed`, `thread/tokenUsage/updated`, `turn/completed`.
  `turn/interrupt` exists.
- Multi-model: `thread/start` accepts per-thread `model` and `modelProvider`.
  `ollama` is a reserved built-in provider in 0.145.0 (must not be redefined;
  `wire_api = "chat"` was removed in favor of `responses`).
- Default sandbox on a fresh thread is `{type:"readOnly", networkAccess:false}`
  with `approvalPolicy:"on-request"` — fail-closed defaults.
- Hygiene confirmed empirically: launch with a neutral cwd (a `.codex/` dir in
  cwd triggers project-config probing) and an explicit env allowlist.

## Persistence model

- **Settings** (provider, model, future mounts/allowlists): Firefox prefs
  (`browser.harness.codex.*`), surfaced in the about:harness Settings panel;
  `config.toml` is regenerated from prefs on every sidecar start. Caveat:
  anything Codex itself writes into config.toml (trusted projects) is
  clobbered by the regeneration — switch to a merge or a managed-config layer
  when persistent trust starts mattering.
- **Chats**: Codex app-server persists them itself — non-ephemeral threads
  are written as rollout files under `CODEX_HOME/sessions` (which lives in
  the profile), and `thread/list` + `thread/resume` enumerate/reopen them in
  Codex's own format. We deliberately keep no chat store of our own;
  `createConversation({persist: false})` opts out. UI for listing/resuming
  past conversations is a follow-up.
- **Credentials**: `auth.json` in CODEX_HOME, written by the sidecar's
  `account/login/start` ChatGPT OAuth flow (settings panel), never read by
  us, never visible to the guest.

## Resolved / remaining questions

- ~~PTY~~ → pipes-first (locked; revisit only on schema evidence).
- ~~Auth~~ → ollama for spikes; preauth CODEX_HOME for OpenAI.
- ~~UI surface~~ → about:harness panel.
- ~~Binary distribution~~ → pinned download, libkrun pattern.
- Remaining: exact experimental shapes (`environment/add`, sandbox policy,
  per-thread model/provider selection) — answered by slice 1's schema +
  transcript; whether app-server allows per-thread provider override or only
  per-CODEX_HOME config (affects how "many models" surfaces in the UI);
  virtio-fs review (deferred, listed above).

## Non-goals

Unchanged from the handoff: no Codex source vendoring, no TUI, no MCP/plugins,
no guest networking (gated egress is separate — `proxy-plan.md`), no
concurrent-VM pooling, no Windows/Linux backends in the first slice, no
production auth/packaging/telemetry.
