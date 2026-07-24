# microsandbox.dev (research spike)

Status: research only. Question: microsandbox appears to wrap libkrun —
pros/cons/differences vs our direct integration, is it battle-tested and
license-compliant, and how would it change the OS image download/caching
story?

## What it actually is

First correction to the premise: microsandbox does not *wrap* libkrun — it
**hard-forked it**. The `msb_krun` crates (crates.io, 26 releases since
2026-03) are their own maintained lineage of the libkrun VMM, plus a forked
`libkrunfw` kernel (superradcompany/libkrunfw, git submodule). The README
credits libkrun and smoltcp as ancestry, not dependencies.

Facts (GitHub, checked 2026-07-24):

- Apache-2.0, created 2024-10, ~7k stars, actively developed (pushed
  today), v0.6.6 current; maintained by one small company
  ("superradcompany").
- Components: `msb` CLI, a sandbox server with Python/JS/Rust SDKs, an MCP
  server (Claude-style clients can drive it directly), their own guest
  agent (`agentd`), an OCI image crate, user-space networking on smoltcp,
  snapshot/fork/restore.
- **Platforms: Linux (KVM), macOS (Apple Silicon/HVF), and Windows (WHP)**
  — the Windows Hypervisor Platform port is theirs; upstream libkrun has
  no Windows support. Release assets ship prebuilt
  `libkrunfw-{darwin,linux,windows}-*` kernels plus agentd binaries.
- Sandboxes are defined Docker-style: `msb pull python`, image cache with
  `msb image ls/rm`, volumes, per-project config. OS images come from
  Docker Hub / GHCR / any OCI registry and are cached locally.

## Differences vs our stack

| Dimension | harness (today) | microsandbox |
| --- | --- | --- |
| VMM | upstream libkrun (vendored, built by mach), dlopened by a ~small in-tree helper | `msb_krun` fork, embedded in their Rust runtime |
| Integration | in-process modules; VM helper is a child process we own end to end | a daemon Firefox would talk to (like our codex sidecar), or vendoring their crates |
| Guest agent | our ~single-file C agent (exec/pty/fs/proxy) | their `agentd` (richer, theirs) |
| Networking | none by default; host-side SNI-verified allowlist proxy over vsock | smoltcp user-space netstack, configurable, TLS secret injection |
| Images | one Alpine template we compose in `setup-deps.sh`, pinned sha256s | any OCI image, pulled from public registries, layer-cached |
| Extras | places snapshots, browser tools, widget containment (Firefox-specific) | snapshot/fork/restore, SDKs, MCP server |
| Platforms | macOS arm64 | macOS arm64, Linux KVM, **Windows WHP** |

## Pros (what they have that we'd want)

- **Windows support.** The single most strategically interesting artifact.
  Their WHP port of the libkrun lineage is an existence proof that the
  harness could be cross-platform without switching substrates.
- **OCI images**: the entire container ecosystem becomes the toolchain
  source; digest-pinned, content-addressed layer caching with dedup and
  partial updates — strictly nicer mechanics than our monolithic tarball.
- Snapshot/fork/restore maps directly onto our named-volumes /
  rootfs-promotion burndown items.
- Maintained guest agent + SDKs + MCP server we wouldn't have to write.

## Cons / risks

- **Battle-tested: no.** <2 years old, single small-company maintainer
  (bus factor ~1), no publicly documented large production deployments,
  and — most importantly — a fork that has diverged from upstream libkrun,
  so it no longer inherits Red Hat's security lineage (upstream libkrun
  ships inside podman machine and RamaLama; that provenance matters for a
  browser vendor). Do their forks track upstream CVE fixes? Unverified.
- **Audit surface**: adopting it means security-reviewing their VMM fork,
  netstack, agentd, image handling, and server — versus our current
  posture of a thin in-tree helper over an upstream project. Our helper +
  guest agent are small enough to actually read.
- **Architecture mismatch**: it's daemon-shaped (projects, server, config
  files) where we're browser-embedded. We'd either run yet another
  sidecar or vendor a large Rust workspace into the tree.
- Their networking model (guest gets a netstack with egress policies)
  is more permissive than ours (no NIC at all; host-side proxy is the only
  path). Ours is easier to defend in review.
- Registry pulls from docker.io/GHCR are the default image path — a
  mutable-by-tag, third-party-operated source. Fine for developers,
  wrong trust model for a browser feature (see below).

## License compliance

Their core is Apache-2.0 (like libkrun itself) — clean. The kernel fork
remains **GPL-2.0** (it's Linux), and they distribute prebuilt kernel
binaries in GitHub releases with the fork repo as corresponding source —
compliant for them. Crucially, **adopting microsandbox changes nothing
about our GPL constraint**: the kernel and any Linux rootfs still cannot
ship in the Firefox installer; the runtime-download plan
(image-download-plan.md) applies identically, just with their artifacts in
place of upstream's. There is no licensing shortcut here.

## Impact on OS download/caching

If we adopted their model wholesale: images arrive as OCI layers from a
registry, cached content-addressed (`msb pull`), digest-pinned. Genuinely
better mechanics than our single 123 MB tarball — dedup, partial updates,
and "the toolchain image" becomes composable.

But a browser pulling from Docker Hub is the wrong trust and privacy
posture (third-party operator, tag mutability, enterprise egress rules).
Making it right means Mozilla hosting/mirroring a registry — at which
point we've rebuilt the Remote Settings plan with a heavier protocol. The
right takeaway is to **steal the layer idea, not the dependency**: our RS
attachments can be content-addressed layers (base / node / python / bun)
assembled locally, which the stamp mechanism already accommodates.

## Recommendation

Don't adopt as a dependency now. Concretely:

1. Keep upstream libkrun + our thin helper — smaller audit surface, Red
   Hat-adjacent provenance, and our tighter no-NIC network posture.
2. Track microsandbox as **prior art and a feasibility proof**,
   especially the WHP/Windows port — if the harness ever needs Windows,
   evaluating their `msb_krun` fork (or upstreaming pressure on libkrun)
   is the starting point.
3. Adopt the layered/content-addressed image idea within the existing
   Remote Settings download plan.
4. Revisit in 6-12 months: if it accrues real production users, tracks
   upstream security fixes, and gains contributors beyond one company,
   the calculus changes — their agentd/SDK/MCP layer would then be worth
   weighing against what we've built.
