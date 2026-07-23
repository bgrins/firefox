# Third-party model providers (OpenRouter) spike

How the harness should connect the pinned `codex-app-server` (0.145.0) to
OpenAI-compatible providers such as OpenRouter. Research notes, 2026-07-23.

Verification caveat: network access and sidecar execution were unavailable in
the research session, so codex mechanics below are verified from the pinned
binary itself (`strings` on `dist/bin/harness/codex/codex-app-server`, which
embeds the serde field/variant tables and validation messages) plus the
earlier live-probe notes in `codex-integration-plan.md`. Items marked
**verify** need the empirical probe described at the end before coding.

## Codex config mechanics at rust-v0.145.0

Source of truth upstream: `codex-rs/core/src/model_provider_info.rs` and
`codex-rs/core/src/config/mod.rs` at tag `rust-v0.145.0`.

`[model_providers.<id>]` entries deserialize into `ModelProviderInfo` with
these fields (recovered verbatim from the binary's serde metadata): `name`,
`base_url`, `env_key`, `env_key_instructions`, `experimental_bearer_token`,
`wire_api`, `query_params`, `http_headers`, `env_http_headers`,
`request_max_retries`, `stream_max_retries`, `stream_idle_timeout_ms`,
`websocket_connect_timeout_ms`, `requires_openai_auth`,
`supports_websockets`, `auth`, `aws`. The `auth` subtable
(`ModelProviderAuthInfo`) is `{ command, args, cwd, timeout_ms,
refresh_interval_ms }`: an external command the sidecar runs to obtain a
bearer token, with periodic refresh.

Confirmed properties:

- **`wire_api` has exactly one variant: `responses`.** The `chat` variant is
  gone (the binary carries a migration error: "`ollama-chat` is no longer
  supported ... replace `ollama-chat` with `ollama`"). There is no
  chat-completions fallback path in 0.145.0; every provider must speak the
  OpenAI Responses API at `<base_url>/responses`.
- **Reserved built-in provider ids: `openai`, `amazon-bedrock`, `ollama`,
  `lmstudio`.** Redefining one fails config validation: "model_providers
  contains reserved built-in provider IDs: ... Built-in providers cannot be
  overridden. Rename your custom provider (for example, `openai-custom`)."
  This is the collision that already bit us with `ollama` (the built-in
  defaults to 127.0.0.1:11434; `CODEX_OSS_BASE_URL`/`CODEX_OSS_PORT` override
  it).
- **Custom providers are field-restricted.** A validation message states a
  `model_providers.<id>` entry "only supports changing `base_url`, `auth`,
  `http_headers`, `aws.profile`, and `aws.region`; other non-default provider
  fields are not supported". **Verify** whether `env_key` counts as a
  rejected "non-default field": the struct still deserializes it and request
  telemetry includes `auth.env_provider_key_name`/`auth.env_provider_key_present`,
  so it may remain functional. If `env_key` is rejected, the supported
  equivalent is `auth = { command = "/usr/bin/printenv", args =
  ["OPENROUTER_API_KEY"] }` — same effect (token read from the launch
  environment we control; `/usr/bin` is already on the sidecar's PATH).
- Token supply paths, best to worst: `env_key = "VAR"` (sidecar reads env at
  request time), `auth.command` (prints a token; supports refresh),
  `experimental_bearer_token` (token literal inside config.toml — never use).

## OpenRouter compatibility

Because 0.145.0 is responses-only, OpenRouter works iff it serves the
Responses API. As of writing, OpenRouter documents a **beta**
`POST https://openrouter.ai/api/v1/responses` endpoint (OpenAI Responses
schema; historically stateless — server-side `store`/`previous_response_id`
state not persisted). **Verify** against
`https://openrouter.ai/docs/api-reference/responses-api` before shipping:
streaming event coverage, tool/function calls, and reasoning items are the
areas most likely to diverge in a beta. Auth is a standard
`Authorization: Bearer <key>` header, exactly what `env_key` produces.

If the beta proves insufficient there is no in-codex fallback; the options
are waiting, restricting the feature to providers with native Responses
support, or a host-side translation proxy — all out of scope for this spike.

## Firefox infrastructure reuse verdict

- `browser/components/genai` (`GenAI.sys.mjs`): `browser.ml.chat.provider`
  is a *URL of a chatbot web UI* rendered in the sidebar; the provider
  registry is website metadata (name, max length, icons). No API clients, no
  tokens. Irrelevant to a codex sidecar.
- `browser/components/aiwindow` (`models/openAIEngine.sys.mjs`): in-process
  fetch client against a Mozilla-hosted LiteLLM endpoint authenticated with
  FxA OAuth tokens; a dev-oriented custom-endpoint path stores an API key in
  the **plaintext pref** `browser.smartwindow.apiKey`. The machinery (401
  retry, token stream parsing) is specific to its own fetch loop — codex is
  its own HTTP client, so none of it applies. The plaintext-pref key is the
  anti-pattern to avoid, not a foundation.
- `toolkit/modules/OSKeyStore.sys.mjs` (used by credit-card autofill): the
  one piece worth using. `await OSKeyStore.encrypt(plainText)` → opaque
  ciphertext string; `await OSKeyStore.decrypt(cipherText, trigger, reauth)`
  → plaintext. Backed by `nsIOSKeyStore` with an OS-keychain secret labeled
  "<App> Encrypted Storage"; callers persist the ciphertext wherever they
  like. Wart: `decrypt()` records the Glean `creditcard.osKeystoreDecrypt`
  metric keyed by the caller-supplied `trigger` string.

Verdict: integrate with nothing in genai/aiwindow; use OSKeyStore directly.

## Token storage design

Store the OpenRouter key as OSKeyStore ciphertext in a pref
(`browser.harness.codex.openrouter.tokenCipher`). Rejected alternatives:

- Plaintext pref: readable by anything that can read prefs.js; shows up in
  pref dumps and support artifacts.
- Plaintext file in CODEX_HOME: honest to note codex's own `auth.json`
  (ChatGPT tokens) is already plaintext there, but we should not add to that
  baseline for credentials *we* manage, and config.toml is regenerated (and
  readable) — a token must never appear in it.

Flow invariants:

- The decrypted token exists only transiently in the parent process and is
  handed to the sidecar solely via the explicit `environment` object of
  `Subprocess.call` in `CodexAppServerClient.start()` (we already construct
  it fully; nothing is inherited).
- Never written into config.toml; config references it only by env var name.
- Never visible to the guest VM: the guest env is whatever the exec bridge
  sets per exec op; the sidecar's host env does not propagate.
- Decrypt with `reauth = false` at sidecar start (no OS auth prompt for a
  background start); surface decryption failure in settings UI.

## Implementation sketch

1. Prefs: `browser.harness.codex.provider` gains `"openrouter"` (and later a
   generic `"custom"` with `browser.harness.codex.customBaseUrl`); model pref
   unchanged.
2. `CodexAppServerClient.configFromPrefs()` emits, for openrouter:

   ```toml
   model_provider = "openrouter"
   model = "<pref>"
   [model_providers.openrouter]
   name = "OpenRouter"
   base_url = "https://openrouter.ai/api/v1"
   env_key = "OPENROUTER_API_KEY"   # or auth.command printenv fallback
   ```

   Sanitize interpolated pref values as done for `model` today. Probably
   also `model_context_window` (codex has no metadata for third-party model
   slugs — same as ollama; **verify** the warning behavior).
3. `AgentService` gains `setProviderToken(token)` /
   `clearProviderToken()` / `hasProviderToken` (encrypt via OSKeyStore, store
   ciphertext pref) and decrypts in `#ensureClient()` before constructing the
   client; `CodexAppServerClient` takes an `extraEnvironment` option merged
   into the `Subprocess.call` env — the client stays storage-agnostic.
4. about:harness settings: OpenRouter radio + password-type token field
   showing set/unset state (never the token); save encrypts and uses the
   existing restart-on-next-message flow. Keep token strings out of logs.
5. `thread/start` already accepts per-thread `model`/`modelProvider` (plumbed
   in `AgentService.createConversation`), so multi-provider selection per
   conversation is available later without config changes.

## Verified against the pinned binary (0.145.0, live key)

- End-to-end works: `auth = { command = "/usr/bin/printenv", args =
  ["OPENROUTER_API_KEY"] }` on a custom `openrouter` provider, key injected
  into the sidecar environment, `model = "openai/gpt-5-mini"` — turn
  completed with a streamed reply. `env_key = "OPENROUTER_API_KEY"` also
  attaches the header; the "only supports changing base_url/auth/..."
  restriction is Bedrock-only, custom providers pass through unfiltered.
  We keep the `auth.command` form because command-backed auth also opts the
  provider into codex's model-catalog refresh (avoids "Unknown model"
  warnings for OpenRouter slugs).
- Two traps that made all of this look broken during probing:
  - OpenRouter's 401 `"Missing Authentication header"` actually means the
    Bearer header WAS sent but the key is invalid. A request with no
    Authorization header at all gets `"No cookie auth credentials found"`.
    Fake-key probes therefore read as "header not attached" when the
    mechanism was working the whole time.
  - Credential-derived auth (env_key, auth.command, env_http_headers,
    experimental_bearer_token) is only attached over https. Probing against
    a plain-http localhost dump server shows no Authorization header even
    when the config is correct. Static `http_headers` values are attached
    unconditionally (they go through `to_api_provider`, not the auth path),
    which is what finally disambiguated the two.
- OpenRouter's `/api/v1/responses` handles codex streaming turns fine
  (agentMessage deltas, turn/completed).

## Open questions

- Context-window handling for arbitrary OpenRouter models (pref? per-model
  table? accept codex's fallback metadata warning?).
- Whether to file a follow-up to generalize the Glean trigger story before
  shipping OSKeyStore use from harness code (metric lives in the
  `creditcard` category).
