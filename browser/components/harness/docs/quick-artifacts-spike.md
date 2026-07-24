# Quick-style hosting for agent artifacts (research spike)

Status: research only. Question: could harness artifacts be hosted the way
Shopify's Quick (shopify.engineering/quick) hosts internal sites — and if
so, who runs the service, how do sites deploy and talk to it, and is the
concept even right versus plain HTML files or agent-run servers?

## What Quick actually is

- Static folders deployed via a trivial CLI (`quick deploy`, an rsync
  wrapper) to GCS; nginx serves them from a single $200/month VM;
  Identity-Aware Proxy gates everything to employees.
- Every site gets an origin: `mysite.quick.shopify.io` maps to a folder.
- The differentiator is a client-side SDK of shared platform APIs: database
  (collections + realtime), file uploads, AI (LLM/image calls with
  server-held keys), BigQuery, websockets, identity. Sites are static but
  feel like apps.
- Stated motivation matches ours: LLM agents can scaffold a working site
  from a prompt; Quick removes every deployment/config step after that.
  50k+ sites, half the company has made one.

The transferable insight: **static files + a curated capability SDK covers
most of what LLM-generated apps need, without letting the model run server
code**. Distribution (the other half of Quick's value) mostly doesn't
transpose to a single-user browser — what transposes is persistence,
stable origins, and capabilities.

## What we have today (for contrast)

Widgets are single HTML files: CSP-injected staged copies rendered inline
in a remote browser (file content process, all network blocked). Great
containment, but: no persistence (no meaningful origin → no storage), no
multi-file sites, no assets, no APIs, no stable URL to iterate against.
Artifacts are one-shot outputs, not things you keep.

## Who would run the "core Quick service"?

Three candidate operators:

1. **Firefox itself (recommended)** — the harness registers a protocol
   handler or local server and *is* the Quick service. Deploy = the agent
   writing files; no infrastructure, private by default, lifecycle owned by
   the browser. Quick's nginx+GCS+IAP stack collapses to "a folder in the
   profile plus an origin scheme" because there is exactly one user.
2. **A local daemon** (sidecar-style `quickd` serving on loopback) — only
   wins if non-Firefox clients need to reach the sites; otherwise it's an
   extra process, an extra port, and an extra attack surface.
3. **Mozilla-hosted multi-user Quick** — the real analog (share an artifact
   with anyone / your team). A different product with auth, abuse, and
   privacy surfaces; explicitly out of scope for the harness, but worth
   naming as the future "share this artifact" story.

## Origin strategy (the crux)

| Option | How | Pros | Cons |
| --- | --- | --- | --- |
| Custom scheme `harness-site://<name>/` | protocol handler, like `moz-extension://` | no TCP at all (nothing for other local apps or drive-by web pages to hit); per-site origin for free; storage/secure-context flags settable per scheme; fits our existing frame containment | not URL-openable outside Firefox; some web APIs assume http(s) |
| `<site>.localhost:<port>` server | loopback HTTP server; Firefox resolves `*.localhost` to loopback per RFC 6761 | real http origins — service workers, storage, everything just works; other local tools can hit it | classic localhost-server problems: any local process can connect, any website can CSRF it (needs token auth); port lifetime management |
| `mysite.firefox-internal.com` mapping | PAC/proxy or DNS override to loopback | "real looking" URLs | HTTPS needs certificates we'd have to mint (local CA — a huge foot-gun); interferes with real proxy/DNS config. Avoid. |

Recommendation: **custom scheme first** — it inherits the security posture
we already built for widgets (isolated process, no network unless granted),
just with a persistent origin per site instead of a throwaway staged file.
The loopback server is the later compatibility hatch if sites need to be
reachable by other tools.

## Deploy and communicate

- **Deploy**: the agent writes a folder under `/workspace/sites/<name>/`
  and calls a `publish_site` tool (or we auto-detect). The harness copies
  it into `profile/harness/sites/<name>/` (versioned, same stamp pattern as
  the rootfs), registers the origin, and the chat shows a live card
  linking/embedding it. Iterating = rewrite + republish; the origin stays
  stable so storage survives.
- **Platform APIs**: Quick's SDK maps onto a JS shim served at a well-known
  path inside every site, bridged to the parent via a JSWindowActor —
  the same pattern smart window uses for its chat transcript:
  - `db` → per-site KV/collection store (profile-backed sqlite or
    IndexedDB on the site origin — the origin alone may be enough for v1).
  - `files` → scoped read/write into the site's own folder.
  - `ai` → routed through AgentService to the configured provider, with
    explicit user consent and budget; keys never touch site code (exactly
    Quick's server-held-keys property).
  - `identity` → trivial locally; interesting only in a future shared mode.
  - `browser data` → the differentiator Quick can't have: curated
    read-only views of the user's own snapshots (places, tabs) with the
    same audit/consent story as the existing browser tools.
- **Network**: default-deny stays; a site that wants remote data asks the
  *user* (allowlist entry) or asks the *agent* to fetch it into the site
  folder from inside the VM.

## Does the concept make sense?

Against the two alternatives:

- **Vanilla HTML files (today)**: right for one-shot artifacts ("show me a
  chart"). Falls over exactly where Quick's users started: the moment an
  artifact is worth *keeping* — a dashboard you reopen, a tracker with
  state, a tool you refine over days. No origin means no storage, no
  identity for the thing itself.
- **Agent-run servers in the VM**: maximal power (any stack, real
  backends), and we're one vsock port-forward away from supporting it. But
  it couples artifact lifetime to VM lifetime, burns VM resources per
  site, and means model-authored code servicing requests — a much worse
  default posture. Shopify's data point cuts the same way: static + shared
  APIs covered 50k sites without user-run servers.

Honest assessment: the concept is sound and composes unusually well with
what's already built (widget containment → same frames; named volumes →
site persistence; browser tools → capability SDK; AGENTS.md → teach the
agent to build sites). But it's a *keep-your-artifacts* feature — it earns
its complexity only once people actually want to return to artifacts. The
staged path if/when we do:

1. Scheme + static serving + persistent per-site origin (storage works).
2. `publish_site` tool + site cards in chat + management UI (list/delete).
3. Capability SDK: storage first, browser-data views second, `ai` last
   (consent + budget design needed).
4. Escape hatch: vsock port-forward for agent-run servers in the VM.
5. Far future: hosted sharing (the actual Quick), or peer-to-tab handoff.

### How "real" can scheme origins be? (checked in-tree)

Custom-scheme sites can behave like real origins to a much greater degree
than file://:

- **Storage**: each `harness-site://<name>/` is a distinct origin
  (scheme+host), and content principals on custom schemes get
  localStorage/IndexedDB/CacheStorage through the normal quota manager —
  this is exactly how `moz-extension://<uuid>` pages store data today.
  file:// never gets this; it's the main reason artifacts can't persist
  state now.
- **Secure-context APIs**: schemes can declare
  `URI_IS_POTENTIALLY_TRUSTWORTHY` (`nsIProtocolHandler.idl:252`), which
  unlocks crypto.subtle and other https-gated APIs.
- **fetch()**: same-origin fetch of the site's own resources works (unlike
  file://, where fetch is crippled); ES modules load normally.
  Cross-origin fetch is whatever our policy says — default-deny via CSP,
  with the capability SDK as the sanctioned data path.
- **Service workers** are the one real gap: Gecko gates SW registration on
  https (moz-extension SWs exist but behind their own flag and plumbing).
  Probably acceptable to punt; sites that need SW-grade behavior are the
  signal to offer the loopback-server hatch.

So the design stance is: register the scheme with content principals, per-
host origins, and the trustworthy flag — sites are "real" web origins for
storage, APIs, and modules, with networking as the one deliberately
policy-shaped surface.

## Open questions

- Scheme registration ergonomics: `moz-extension` gets origins via the
  extensions framework; a lighter-weight per-site substitution scheme
  (`harness-site://<name>/` → folder) needs a look at
  `nsISubstitutingProtocolHandler` to confirm the registration surface.
- Should sites be readable/writable by the agent after publish (live
  iteration) or snapshot-on-publish (reproducibility)? Quick is rsync-
  overwrite; snapshotting fits our stamp pattern better.
- Quota/lifecycle: sites accumulate in the profile; need caps + a
  management surface (same problem class as VM sessions, solved the same
  way).
- Does the `ai` capability create a prompt-injection loop (site content →
  agent)? Needs the same untrusted-data framing as page extraction.
