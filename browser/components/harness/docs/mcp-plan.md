# MCP support: findings and product plan

How MCP (Model Context Protocol) works in the pinned codex (rust-v0.145.0)
and how the harness could let users configure MCP servers. All codex
citations were verified against the rust-v0.145.0 tag; local citations are
from this branch. Status: research + plan, nothing implemented yet.

**Headline finding:** at this tag, codex MCP servers carry an
`environment_id` field that resolves through the *same* exec-server
`EnvironmentManager` our `environment/add` call already populates. A stdio
MCP server configured with `environment_id = "harness-vm"` is spawned
**through CodexExecBridge into the micro-VM**, not on the host. Guest-side
MCP is a first-class codex mechanism, not a hack — and it is the
recommended product shape.

## How codex MCP works at rust-v0.145.0

### Config format (`[mcp_servers.<name>]` in config.toml)

Parsed as `HashMap<String, McpServerConfig>`
(`codex-rs/config/src/config_toml.rs:264-265`). The raw shape is
`RawMcpServerConfig` (`codex-rs/config/src/mcp_types.rs:246-304`);
transport is chosen untagged by which keys are present, with strict
mutual-exclusion validation (`mcp_types.rs:347-392`):

- **stdio** (`command` present): `command`, `args`, `env` (literal map),
  `env_vars` (names forwarded from environment; each entry may set
  `source = "local" | "remote"`, `mcp_types.rs:63-101`), `cwd`.
  `url`/`bearer_token*`/`http_headers`/`oauth*`/`auth` are rejected for
  stdio (`mcp_types.rs:354-366`).
- **streamable_http** (`url` present): `url`, `bearer_token_env_var`
  (secret read from the *sidecar's* environment), `http_headers`
  (literal), `env_http_headers` (values read from sidecar env)
  (`mcp_types.rs:448-462`). `args`/`env`/`env_vars`/`cwd` rejected
  (`mcp_types.rs:378-389`). SSE-only transport does not exist; it's stdio
  or streamable HTTP.
- **shared**: `enabled` (default true; false = server skipped,
  `mcp_types.rs:168-170`), `required` (fail startup if it can't init),
  `environment_id` (default `"local"`, `mcp_types.rs:17,394-395`),
  `auth = "oauth" | "chatgpt"`, `startup_timeout_sec` (default 30s) /
  `tool_timeout_sec` (default 300s), `enabled_tools`/`disabled_tools`
  allow/deny lists, per-tool `tools.<name>.approval_mode` +
  `default_tools_approval_mode` (`auto|prompt|writes|approve`), `scopes`,
  `oauth.client_id`, `oauth_resource`, `supports_parallel_tool_calls`.

### Launch and environment resolution

Per thread, a `McpConnectionManager` owns one rmcp client per enabled
server (`codex-rs/core/src/session/mcp.rs:424-435`). Each server's
environment is resolved via `McpRuntimeContext::resolve_server_environment`
(`codex-rs/codex-mcp/src/runtime.rs:90-118`):

- `environment_id` found in the `EnvironmentManager` registry: use it.
- `"local"` + stdio with no local environment: **error** ("local stdio MCP
  server requires a local environment", `runtime.rs:105-111`).
- `"local"` + streamable HTTP: host-side reqwest.
- unknown id: error.

Launch paths (`codex-rs/codex-mcp/src/rmcp_client.rs:1016-1102`,
`codex-rs/rmcp-client/src/stdio_server_launcher.rs`):

- **Local stdio** — child of the sidecar. Environment = sanitized
  whitelist `DEFAULT_ENV_VARS` (HOME, PATH, TMPDIR, SHELL, LANG, TZ, ...)
  read from the sidecar's env, plus config `env` literals, plus
  `env_vars`-named vars copied from the sidecar env
  (`codex-rs/rmcp-client/src/utils.rs:12-25,130-142`).
- **Executor stdio (non-local environment)** —
  `ExecutorStdioServerLauncher` calls `ExecBackend::start(ExecParams{
  argv, cwd, env, tty:false, pipe_stdin:true, ... })`
  (`stdio_server_launcher.rs:449-533`), i.e. the *exact* `process/start`
  RPC our bridge already serves for shell commands. Requires an explicit
  `cwd` in config. Env: only config `env` literals plus explicitly named
  `env_vars` are forwarded; PATH/HOME come from the executor side.
- **Streamable HTTP** — uses the environment's HTTP capability: for a
  remote environment, HTTP requests are forwarded over the exec-server
  connection as `http/request` RPCs with `http/request/bodyDelta`
  streaming (`codex-rs/exec-server/src/environment.rs:657-675,799-801`).
  For local, host reqwest.

The app-server builds one shared `EnvironmentManager` at startup from
`CODEX_HOME/environments.toml` or legacy `CODEX_EXEC_SERVER_URL`
(`codex-rs/app-server/src/lib.rs:479-490`); **`environment/add` upserts
into that same manager**, and threads resolve MCP environments from it.
With neither present — our situation — the default provider sets
`include_local = true` (`codex-rs/exec-server/src/environment_provider.rs:69`),
so **a host "local" environment exists in our sidecar today** and host
stdio MCP would work out of the box if configured.

### Tool namespacing

Tools are namespaced by sanitized server name; names are deduplicated with
hash suffixes and capped at 64 bytes; the legacy `mcp__` prefix is only
added when `prefix_mcp_tool_names = true`
(`codex-rs/codex-mcp/src/tools.rs:22,105-180`). Per-server
`enabled_tools`/`disabled_tools` filter before advertisement; tools with
UI-only visibility metadata are hidden from the model.

### App-server protocol surface (all rides our JSONL connection)

Client→server requests (`app-server-protocol/src/protocol/common.rs:984-1013`),
none experimental-gated:

- `mcpServer/oauth/login` → `{ authorizationUrl }` (params `name`,
  optional `threadId`, `scopes`, `timeoutSecs`)
- `config/mcpServer/reload` — re-read config and refresh servers
- `mcpServerStatus/list` — paginated `{ name, serverInfo, tools,
  resources, resourceTemplates, authStatus }`
- `mcpServer/resource/read`, `mcpServer/tool/call` — client-initiated

Server→client request: `mcpServer/elicitation/request` (`common.rs:1505`).
Server notifications: `mcpServer/oauthLogin/completed`,
`mcpServer/startupStatus/updated` (payload `{ threadId, name, status:
starting|ready|failed|cancelled, error, failureReason }`), plus
`item/mcpToolCall/progress`.

**OAuth flow** (HTTP servers only): request returns an `authorizationUrl`
the client opens in a browser; the sidecar runs a loopback callback
listener; completion arrives as `mcpServer/oauthLogin/completed`. Tokens
stored per `mcp_oauth_credentials_store_mode` (default: OS keyring with
fallback to `CODEX_HOME/.credentials.json`). The token exchange itself
goes through the server's *resolved environment HTTP client*
(`app-server/src/request_processors/mcp_processor.rs:169-173`).

**Elicitation**: with `approvalPolicy = "never"` (our default),
elicitations are rejected by codex policy before ever reaching the client
(`codex-rs/codex-mcp/src/elicitation.rs:316-323`). If a request does reach
the client and the client replies with an error — our fail-closed
default — the app-server maps it to a graceful `Decline`
(`app-server/src/bespoke_event_handling.rs:1711-1748`). Our current
posture degrades safely.

**CLI-only**: `codex mcp add/list/login` just edits config.toml —
irrelevant to us since we regenerate config.toml from prefs on every start.

## Security analysis for our architecture

**Host stdio MCP (default config) violates the invariant directly.** A
`command = ...` server is a child of the semi-trusted sidecar, running as
the user on the host, receiving *model-controlled tool arguments* every
call. Our clean sidecar env reduces ambient secrets but is not a sandbox:
the process has full user-level filesystem/network/exec. Two concrete
exfiltration paths even from "benign" config:

- `env_vars = ["OPENROUTER_API_KEY"]` copies our injected API key into any
  host stdio server.
- With `HOME` = CODEX_HOME, a host server can trivially read `auth.json` /
  `.credentials.json`.

**Host streamable HTTP is network-only but egress-uncontrolled**: requests
go out via host reqwest — bypassing the HarnessProxy allowlist entirely.
`bearer_token_env_var` / `env_http_headers` read the sidecar env, so a
config entry can attach the API key as a header to an arbitrary URL. A
settings UI must never expose free-form env-var names.

**Guest-side stdio MCP preserves the invariant with codex's own
plumbing.** `environment_id = "harness-vm"` resolves to the environment we
register via `environment/add`, the launcher uses the audited
`process/start`/`process/read`/`process/write` bridge RPCs with `cwd`
constrained to `/workspace` or `/mnt/*`, and the server process inherits
the guest's `http_proxy` so all egress rides the user allowlist. Blast
radius = the VM, same as any model shell command.

**Gaps in the guest path:**

1. In-guest **streamable HTTP** needs `http/request` (+ bodyDelta)
   implemented in CodexExecBridge; today unknown methods are denied, so an
   HTTP MCP bound to `harness-vm` fails cleanly at startup.
2. The bridge ignores the launcher's `env_policy`, so
   `env_vars source = "remote"` isn't filtered per spec (document it).
3. `browser.harness.sessionPerConversation = true` registers environments
   as `harness-vm-<sessionId>`, which a static `environment_id =
   "harness-vm"` won't match. Fix by additionally upserting the stable id
   per conversation (upsert replaces).
4. **Fail-closed hardening regardless of option:** write
   `CODEX_HOME/environments.toml` with `include_local = false`
   (`codex-rs/exec-server/src/environment_toml.rs:73`) so a host "local"
   environment never exists — any stdio MCP config missing
   `environment_id = "harness-vm"` then fails at startup instead of
   running on the host. Needs a smoke test that thread exec via
   `environment/add` still works.

## Product options

**(a) Raw config passthrough (host execution) — reject.** Arbitrary
`[mcp_servers.*]` blocks mean model-influenced code execution on the
host — the exact thing the harness exists to prevent. No consent dialog
meaningfully conveys "this npm package runs unsandboxed as you, driven by
model output".

**(b) Network-only MCP (url-based, host-side client).** Small codex
surface, OAuth works, but host reqwest bypasses HarnessProxy; forcing
proxy env vars on the sidecar would also proxy model-provider traffic.
Must hard-block `bearer_token_env_var`/`env_http_headers`. Acceptable
follow-up, weaker than (c) for egress control.

**(c) Guest-side MCP via `environment_id` — recommended.** Codex natively
supports it; our bridge already implements the required RPCs; egress is
allowlisted; audit logging is free. The guest has `bunx` and `uvx`, so the
npm and PyPI MCP ecosystems work, and package downloads already flow
through the allowlist. Remote/url servers can work today via an in-guest
`bunx mcp-remote <url>` stdio shim (HTTP rides the guest proxy) — limited
to token/no-auth in v1 since mcp-remote's localhost OAuth callback isn't
reachable from the user's browser. Native in-guest streamable HTTP +
codex-driven OAuth is the phase-2 build.

Degradation under (c): stdio OAuth doesn't exist in codex (HTTP-only) —
fine; elicitations auto-decline gracefully; startup failures surface as
`mcpServer/startupStatus/updated` notifications we currently drop —
needs UI.

## Integration checklist (option c, v1 = guest stdio only)

1. **Config generation** (`CodexAppServerClient.configFromPrefs`): new
   pref (e.g. `browser.harness.codex.mcpServers`, JSON) serialized into
   `[mcp_servers.<name>]` blocks. Generator **forces**
   `environment_id = "harness-vm"` and `cwd = "/workspace"`, and emits
   only `command`/`args`/`env` (literal)/`enabled`/tool
   allowlists/timeouts. Never emit `env_vars`, `bearer_token_env_var`,
   `env_http_headers`, or `url` (v1). Sanitize names (TOML keys become
   model-visible tool namespaces).
2. **Fail-closed hardening**: write `environments.toml` with
   `include_local = false` into CODEX_HOME on every start; regression-test
   exec through `environment/add` environments.
3. **sessionPerConversation**: also upsert the stable `"harness-vm"` id
   pointing at the per-conversation bridge.
4. **Bridge**: no changes required for stdio (verify `pipe_stdin` framing
   under load). Optionally honor/log `env_policy`.
5. **Notifications**: handle `mcpServer/startupStatus/updated` → surface
   ready/failed in the UI; ignore-list `mcpServer/oauthLogin/completed`
   until phase 2.
6. **Server requests**: add `mcpServer/elicitation/request` to the
   known-but-declined set with an explicit `{ action: "decline" }`
   response; consider routing through the approval UI later.
7. **Settings UI**: MCP server list (name, command, args, enabled toggle)
   plus a status readout via `mcpServerStatus/list`; reuse the existing
   applySettings restart flow.
8. **Guest brief**: one line telling the model configured MCP tools exist
   and run inside the sandbox.
9. **Tests**: browser test with a trivial in-guest stdio MCP server (bun
   script) — tool listed, callable, audit-logged; and a config with no
   `environment_id` fails startup rather than spawning host-side.

## Open questions / prototype needs

1. **Does executor-stdio MCP work end-to-end through our bridge?**
   Highest-value spike: `[mcp_servers.echo] command="bun"
   args=["run","/workspace/mcp-echo.ts"] environment_id="harness-vm"
   cwd="/workspace"`, watch `mcpServer/startupStatus/updated`. Risks: 30s
   startup timeout vs guest cold start; framing through the base64
   process/read path.
2. **`include_local = false` side effects** — confirm nothing else we use
   (fs/commandExec processors, fuzzy search) needs the local environment.
3. **MCP lifecycle per thread**: N conversations = N in-guest server
   processes. Measure guest memory; use `enabled_tools` to keep tool
   counts sane.
4. **Capability-root discovery over the bridge**: connection setup may
   issue discovery RPCs our bridge denies — confirm they fail soft.
5. **Phase-2 HTTP**: implement `http/request` (+ bodyDelta) in
   CodexExecBridge — decide host-side fetch under HarnessProxy policy vs
   forwarding into the guest; unlocks url-based MCP **and** codex-native
   OAuth.
