# Harness gated egress: allowlist proxy plan

## Goal

Give the sandboxed guest *selective* network access (package installs, git
fetches from known hosts) without granting general egress, with every request
observable and enforced in the Firefox parent process. Replace the current
all-or-nothing `browser.harness.allownet` (TSI) escape hatch as the way agents
get network.

Non-goals: making exfiltration impossible through allowed hosts (an allowed
`github.com` is already a write channel); supporting non-HTTP protocols;
IP-literal or raw-socket traffic.

## Threat model

Assume the guest is fully adversarial (it runs agent-authored code). The guest
must not be able to:
- reach arbitrary hosts (default-deny),
- use DNS as a resolver/exfil channel (guest never resolves names),
- reach non-allowlisted hosts via domain fronting on shared CDN edges
  (SNI must match the CONNECT target),
- reach the host's local network / localhost services through the proxy
  (block RFC1918/loopback resolutions unless explicitly allowed).

Accepted residual risk: data exfiltration *through* allowed hosts, and
correlation of activity by allowed hosts. Mitigation is a small allowlist and
the audit log, not technical prevention.

## Architecture

```
guest process (wget/git/npm, http_proxy=http://127.0.0.1:3128)
  └─ guest-agent proxy listener on 127.0.0.1:3128 (plain TCP forward)
       └─ vsock port 1025            (krun_add_vsock_port, guest-initiated)
            └─ unix socket /tmp/harness-proxy-<id>.sock (helper/libkrun)
                 └─ HarnessProxy.sys.mjs in Firefox parent
                      ├─ parses CONNECT host:443 / absolute-form GET
                      ├─ policy check (allowlist, ports, SNI peek)
                      ├─ host-side DNS + connect via nsISocketTransport
                      └─ audit log → about:harness network panel
```

Key properties: the guest still has **no NIC and no TSI** — the only route out
is this byte stream, and the parent terminates and polices it. DNS happens on
the host, so the allowlist is evaluated against the name the tunnel actually
connects to.

## Components

### 1. guest-agent: local forwarder (~60 lines C)
- New listener on `127.0.0.1:3128` (guest loopback exists; `lo` is up by
  default in libkrun guests — verify, else `ip link set lo up` in boot cmd).
- Each accepted connection opens `AF_VSOCK` to `(VMADDR_CID_HOST, 1025)` and
  splices bytes both ways (integrate into the existing poll loop; reuse the
  job fd bookkeeping shape, no protocol awareness in the guest).
- Exec default env gains `http_proxy`/`https_proxy`/`HTTP_PROXY`/`HTTPS_PROXY`
  pointing at it (git, curl, wget, npm, pip all honor these).

### 2. harness-vm-helper
- Second mapping: `--vsock-out 1025:<unix-path>` → `krun_add_vsock_port(ctx,
  1025, path)` (guest-initiated direction, `listen=false` variant). Multiple
  ports on the one vsock device are supported; we already create the device
  explicitly with TSI off.
- libkrun *connects to* this unix socket per guest connection, so the host
  side must be listening before boot.

### 3. HarnessProxy.sys.mjs (parent)
- Listens on the unix socket via `nsIServerSocket` (supports unix domain
  paths). One connection per guest TCP connection.
- Request parsing (only two shapes):
  - `CONNECT host:port HTTP/1.1` → policy check → if allowed and port==443,
    peek the first client bytes for a TLS ClientHello and extract SNI;
    require SNI == CONNECT host and no ECH extension → open
    `nsISocketTransport` to host:port → `220 Connection established` → splice.
  - absolute-form `GET http://host/... HTTP/1.1` (plain HTTP) → policy check,
    port 80 only → forward.
  - Anything else → `403` + log.
- DNS: implicit via nsISocketTransport (host-side). Add a resolution check
  that rejects loopback/RFC1918/link-local answers for non-allowlisted-private
  hosts (DNS rebinding guard); nsIDNSService lookup first, connect by IP.
- Policy:
  - `browser.harness.proxy.allowlist` — JSON array of hostnames; supports
    leading `*.` wildcard per entry. Exact match otherwise. Empty = deny all.
  - Ports fixed: 443 (CONNECT), 80 (plain). No other CONNECT ports.
  - Starter set for a coding agent (commented default, still opt-in):
    `registry.npmjs.org`, `pypi.org`, `files.pythonhosted.org`, `crates.io`,
    `static.crates.io`, `index.crates.io`, `dl-cdn.alpinelinux.org`,
    `github.com`, `codeload.github.com`, `objects.githubusercontent.com`.
- Audit log: ring buffer of `{time, host, port, verdict, bytesUp, bytesDown}`;
  emitted as HarnessVM-style events so about:harness can render a network
  panel; also logConsole.
- Optional phase 2: interactive grants — a blocked request surfaces a
  notification in about:harness with "allow once / allow for session".

### 4. SNI verification details
- Parse only the ClientHello: record header (0x16, TLS version), handshake
  type 0x01, walk extensions for `server_name` (0) and `encrypted_client_hello`
  (0xfe0d). Buffer up to 4KB before deciding; malformed/absent SNI → reject.
- Reject ECH: with ECH the outer SNI is decoy, so name-based policy is blind.
  (Guests wanting ECH are exactly the case we want to block.)
- This is ~150 lines of careful JS; test it with fixture ClientHello buffers.

## Implementation steps

1. Helper: `--vsock-out` flag (trivial, mirrors `--vsock`).
2. HarnessProxy.sys.mjs: unix server socket + CONNECT/absolute-form parsing +
   allowlist + splice, no SNI peek yet. Wire into HarnessVM start/stop.
3. guest-agent: loopback forwarder + proxy env defaults for exec.
4. SNI/ECH verification + private-address guard.
5. about:harness network panel (verdict log), allowlist pref UI.
6. Mochitest: local `httpd.js` server + `localhost` allowlist entry proves
   allow path end-to-end; wget to non-allowlisted host proves deny; unit-style
   tests for the ClientHello parser.

Steps 1–3 give functioning gated egress; 4 closes the fronting hole and must
land before calling it a security boundary.

## Open questions

- Does the libkrun guest bring up `lo` automatically? (Affects step 3; easy
  boot-cmd fallback.)
- Per-exec vs per-VM policy: does an agent Bash tool want to pass a narrower
  allowlist for a specific command? (Protocol allows adding `allowlist` to
  exec requests later; start per-VM.)
- HTTP/1.0 clients and keep-alive edge cases in absolute-form parsing — may
  be simpler to force `Connection: close` on plain HTTP.
- Should allowed-host TLS also verify the *certificate* host-side (full MITM
  with a local CA) instead of SNI-peek? Much heavier (cert generation, guest
  trust store); SNI-peek is the right cost/benefit for now.
