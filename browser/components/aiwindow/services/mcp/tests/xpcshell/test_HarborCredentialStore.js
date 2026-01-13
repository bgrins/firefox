/* Any copyright is dedicated to the Public Domain.
 * http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { HarborCredentialStore } = ChromeUtils.importESModule(
  "moz-src:///browser/components/aiwindow/services/mcp/HarborCredentialStore.sys.mjs"
);

const TEST_SERVER_ID = "test-server-123";
const TEST_TOKEN = "test-bearer-token-abc";

function run_test() {
  do_get_profile();
  run_next_test();
}

add_setup(async function () {
  await HarborCredentialStore.removeAllCredentials();
});

registerCleanupFunction(async function () {
  await HarborCredentialStore.removeAllCredentials();
});

add_task(async function test_store_and_retrieve_token() {
  await HarborCredentialStore.storeBearerToken(TEST_SERVER_ID, TEST_TOKEN);

  const retrieved = HarborCredentialStore.getBearerToken(TEST_SERVER_ID);
  Assert.equal(retrieved, TEST_TOKEN, "Should retrieve stored token");
});

add_task(async function test_has_bearer_token() {
  await HarborCredentialStore.removeAllCredentials();

  Assert.ok(
    !HarborCredentialStore.hasBearerToken(TEST_SERVER_ID),
    "Should return false when no token exists"
  );

  await HarborCredentialStore.storeBearerToken(TEST_SERVER_ID, TEST_TOKEN);

  Assert.ok(
    HarborCredentialStore.hasBearerToken(TEST_SERVER_ID),
    "Should return true when token exists"
  );
});

add_task(async function test_remove_bearer_token() {
  await HarborCredentialStore.storeBearerToken(TEST_SERVER_ID, TEST_TOKEN);
  Assert.ok(
    HarborCredentialStore.hasBearerToken(TEST_SERVER_ID),
    "Token should exist before removal"
  );

  await HarborCredentialStore.removeBearerToken(TEST_SERVER_ID);

  Assert.ok(
    !HarborCredentialStore.hasBearerToken(TEST_SERVER_ID),
    "Token should not exist after removal"
  );
  Assert.equal(
    HarborCredentialStore.getBearerToken(TEST_SERVER_ID),
    null,
    "getBearerToken should return null after removal"
  );
});

add_task(async function test_update_existing_token() {
  const newToken = "new-token-xyz";

  await HarborCredentialStore.storeBearerToken(TEST_SERVER_ID, TEST_TOKEN);
  await HarborCredentialStore.storeBearerToken(TEST_SERVER_ID, newToken);

  const retrieved = HarborCredentialStore.getBearerToken(TEST_SERVER_ID);
  Assert.equal(retrieved, newToken, "Should update to new token");
});

add_task(async function test_multiple_servers() {
  await HarborCredentialStore.removeAllCredentials();

  const server1 = "server-1";
  const server2 = "server-2";
  const token1 = "token-for-server-1";
  const token2 = "token-for-server-2";

  await HarborCredentialStore.storeBearerToken(server1, token1);
  await HarborCredentialStore.storeBearerToken(server2, token2);

  Assert.equal(
    HarborCredentialStore.getBearerToken(server1),
    token1,
    "Should retrieve correct token for server1"
  );
  Assert.equal(
    HarborCredentialStore.getBearerToken(server2),
    token2,
    "Should retrieve correct token for server2"
  );

  await HarborCredentialStore.removeBearerToken(server1);

  Assert.equal(
    HarborCredentialStore.getBearerToken(server1),
    null,
    "Server1 token should be removed"
  );
  Assert.equal(
    HarborCredentialStore.getBearerToken(server2),
    token2,
    "Server2 token should still exist"
  );
});

add_task(async function test_get_nonexistent_token() {
  await HarborCredentialStore.removeAllCredentials();

  const result = HarborCredentialStore.getBearerToken("nonexistent-server");
  Assert.equal(result, null, "Should return null for nonexistent server");
});

add_task(async function test_get_token_with_null_serverid() {
  const result = HarborCredentialStore.getBearerToken(null);
  Assert.equal(result, null, "Should return null for null serverId");
});

add_task(async function test_store_token_requires_params() {
  await Assert.rejects(
    HarborCredentialStore.storeBearerToken(null, TEST_TOKEN),
    /serverId and bearerToken are required/,
    "Should throw when serverId is null"
  );

  await Assert.rejects(
    HarborCredentialStore.storeBearerToken(TEST_SERVER_ID, null),
    /serverId and bearerToken are required/,
    "Should throw when bearerToken is null"
  );

  await Assert.rejects(
    HarborCredentialStore.storeBearerToken("", TEST_TOKEN),
    /serverId and bearerToken are required/,
    "Should throw when serverId is empty"
  );
});

add_task(async function test_remove_all_credentials() {
  await HarborCredentialStore.storeBearerToken("server-a", "token-a");
  await HarborCredentialStore.storeBearerToken("server-b", "token-b");

  await HarborCredentialStore.removeAllCredentials();

  Assert.equal(
    HarborCredentialStore.getBearerToken("server-a"),
    null,
    "server-a token should be removed"
  );
  Assert.equal(
    HarborCredentialStore.getBearerToken("server-b"),
    null,
    "server-b token should be removed"
  );
});
