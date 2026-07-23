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

### 5. Per-task ephemeral sessions

Current `HarnessVM` is a singleton with a persistent rootfs (right for the
about:harness fiddle, wrong for tasks). Refactor to sessions:

- `HarnessVM.createSession({taskDir, mem, cpus})` → fresh rootfs copy
  (~130ms, APFS clone), fresh vsock socket, boot, agent connect; `session.destroy()`
  kills the VM and deletes rootfs + task dir. The about:harness fiddle becomes
  one long-lived session.
- Fresh rootfs copy per task satisfies "no persistent guest state" for the
  prototype; true read-only base + tmpfs overlay is a later hardening step
  (virtio-fs RO root via `krun_add_virtiofs3` flags + guest-side overlay
  mount).
- Startup reconciliation: kill orphaned `harness-vm-helper` processes and
  sweep `profile/harness/tasks/` on init (browser-crash recovery).

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

## Work items (ordered)

1. HarnessVM sessionization + task dir lifecycle + startup reconciliation.
2. guest-agent: fs ops with guest-namespace path policy; unprivileged exec
   user; (PTY if schema demands).
3. Guest image: pinned apk additions (bash, jq, sqlite, ripgrep), `task` user.
4. Codex pinning: manifest, fetch/verify script, schema generation + digest.
5. `CodexAppServerClient` (factor shared JSON-lines core with HarnessAgent).
6. `CodexExecBridge`: WS server + op translation + audit events.
7. `AgentService` + sidebar/about page conversation UI.
8. Tests: extend the existing mochitest harness — routing-proof suite (§12 ops
   each asserted through bridge logs), host canary, isolation, cleanup, plus
   the acceptance list from the handoff.

Items 1–3 are pure harness work with no Codex dependency and are useful for
any agent backend; they can land first.

## Open questions

- PTY requirement in the pinned exec-server schema (drives guest-agent work).
- Exact `environment/add` / sandbox-policy shapes — generate the schema from
  the pinned binary before writing any protocol code.
- Auth path for the prototype: developer-preauthenticated CODEX_HOME is the
  least machinery; confirm acceptable.
- Whether Codex requires any fs ops outside `/task` (e.g. reading its own
  config through the exec server) — if so, explicit guest-system allowlist,
  read-only.
- libkrun virtio-fs symlink/`..` handling review (decision 4 depends on it;
  fallback is tmpfs + RPC).

## Non-goals

Unchanged from the handoff: no Codex source vendoring, no TUI, no MCP/plugins,
no guest networking (gated egress is separate — `proxy-plan.md`), no
concurrent-VM pooling, no Windows/Linux backends in the first slice, no
production auth/packaging/telemetry.
