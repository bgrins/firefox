# MXC backend spike: host-sandboxed execution instead of the micro-VM

Branch `harness-mxc`. Evaluates [microsoft/mxc](https://github.com/microsoft/mxc)
(Microsoft eXecution Container, pinned at `32a4c44a`) as an execution
backend replacing libkrun. On macOS, MXC's only backend is **Seatbelt**:
`mxc-exec-mac` reads a JSON policy config, generates a TinyScheme profile,
applies it via `sandbox_init()` in `pre_exec`, and execs `/bin/sh -c
<command>` — a sandboxed process **on the host**. No Alpine, no Linux, no
VM.

Status: working end to end. `browser_harness_mxc.js` covers the substrate
(exec, stdio, env, containment, interactive stdin, places snapshot), and
the full agent E2E suite (`browser_agent_service.js`, real codex turns via
ollama) passes with `browser.harness.backend=mxc`.

## What changed

- `vm/setup-mxc.sh` — fetches the pinned source, builds `mxc_darwin`
  (outside the Firefox tree: cargo walks parents for `.cargo/config.toml`
  and the tree's crates-io source replacement breaks the mxc graph),
  installs `dist/bin/harness/mxc/mxc-exec-mac`.
- `HarnessMxc.sys.mjs` — `MxcSession`/`MxcAgent` implementing the
  HarnessSession/HarnessAgent surfaces over one-shot `mxc-exec-mac`
  spawns. Policy per exec: read-write `workspace` + a dedicated fake
  `HOME` + `TMPDIR`; read-only `/opt/homebrew`; network blocked;
  `nestedPty` on.
- `browser.harness.backend` pref ("vm" | "mxc") switches the default
  session class; the bridge asks the agent for its `workspaceRoot` instead
  of assuming `/workspace`; the sandbox brief describes the host
  environment honestly under mxc.
- `PlacesSnapshot.sys.mjs` — snapshot/refresh extracted so both backends
  share it.

## Why "one-shot only" is not a blocker

MXC's state-aware lifecycle (provision once/exec many) is Windows-only,
but the Seatbelt backend is *process-scoped by design* — there is nothing
to provision or tear down. Our architecture already treats every command
as an independent exec against a persistent workspace; each bridge
`process/start` maps to one wrapper spawn that lives exactly as long as
the process. Boot cost drops from ~1s (VM) to plain process spawn.

## Measured behavior

- stdio passthrough is clean (no wrapper noise), exit codes propagate,
  stderr stays separate, stdin round-trips — the wrapper is a drop-in
  process substrate for the agent surface.
- Containment held in tests: writes outside granted roots and reads of
  profile files (prefs.js) are denied; outbound network is blocked;
  `whoami` can't even resolve the username (directory services denied).
- The workspace is a plain host directory — no virtio-fs layer, no path
  illusion. Codex sees real host paths (cwd advertised by the bridge).

## Security posture: materially weaker than the VM

This is the headline tradeoff, not a footnote:

1. **Model commands execute on the host.** The harness invariant "no
   model-generated command ever executes on the host" does not survive
   this backend; the boundary shrinks from a hypervisor to a kernel
   sandbox policy.
2. **MXC says so itself**: "no MXC profiles should be treated as security
   boundaries currently" (README warning, early preview).
3. **Network policy is weaker.** Seatbelt cannot enforce host allowlists
   (`allowedHosts` degrades to allow-all outbound), and the cooperative
   proxy (`HTTP_PROXY` env) is bypassable by raw-socket clients. The spike
   blocks the network outright; wiring HarnessProxy would need a TCP
   loopback listener plus `allowLocalNetwork`, which also exposes every
   other loopback service on the machine.
4. **The kernel attack surface is the macOS kernel**, reachable from
   sandboxed code; with the VM, escaping requires a hypervisor bug.
5. Baseline reads: the generated profile allows `/System`/`/Library`
   reads, so fingerprinting the machine is easier than from Alpine.

What the host backend buys in exchange: no ~130MB runtime image (and no
GPL kernel download), no VM boot, native performance, Rosetta-free x86
support, host toolchain (real macOS binaries), and a plausible
cross-platform story (the same MXC config drives ProcessContainer on
Windows and Bubblewrap on Linux — the part libkrun cannot give us).

## Gaps deliberately left in the spike

- No host pty allocation (`tty:` requests run without one; `nestedPty`
  still lets inner commands allocate their own).
- Network fully blocked: no HarnessProxy integration (see above).
- User mounts (`/mnt/<tag>`) are not mapped into policies.
- `sessionPerConversation` still constructs VM sessions.
- Toolchain is whatever the host has: bun/uv come from Homebrew if
  installed; the brief no longer promises them.
- The wrapper binary is built by script, not vendored; production would
  vendor to third_party/ with moz.yaml.

## Verdict so far

The integration is small (one module, one pref, one bridge getter) because
the session/agent abstraction held. Whether to pursue it is a product
question, not a technical one: MXC trades the harness's strongest property
(host isolation by hypervisor) for zero-boot host execution and a
cross-platform path. A plausible landing: keep the VM as the default
boundary on macOS, and treat MXC as the Windows/Linux bring-up vehicle
where we have no libkrun story at all.
