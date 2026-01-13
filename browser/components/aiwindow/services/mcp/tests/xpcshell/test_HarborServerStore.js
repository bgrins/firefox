/* Any copyright is dedicated to the Public Domain.
 * http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { HarborServerStore } = ChromeUtils.importESModule(
  "moz-src:///browser/components/aiwindow/services/mcp/HarborServerStore.sys.mjs"
);

const SERVERS_PREF = "browser.aiwindow.harbor.servers";

add_setup(function () {
  Services.prefs.setStringPref(SERVERS_PREF, "[]");
});

registerCleanupFunction(function () {
  Services.prefs.clearUserPref(SERVERS_PREF);
});

add_task(async function test_load_empty_servers() {
  Services.prefs.setStringPref(SERVERS_PREF, "[]");

  const servers = HarborServerStore.loadServers();
  Assert.ok(Array.isArray(servers), "Should return an array");
  Assert.equal(servers.length, 0, "Should be empty");
});

add_task(async function test_load_malformed_pref() {
  Services.prefs.setStringPref(SERVERS_PREF, "not valid json");

  const servers = HarborServerStore.loadServers();
  Assert.ok(Array.isArray(servers), "Should return empty array on error");
  Assert.equal(servers.length, 0, "Should be empty on error");

  Services.prefs.setStringPref(SERVERS_PREF, "[]");
});

add_task(async function test_load_non_array_pref() {
  Services.prefs.setStringPref(SERVERS_PREF, '{"not": "an array"}');

  const servers = HarborServerStore.loadServers();
  Assert.ok(Array.isArray(servers), "Should return empty array for non-array");
  Assert.equal(servers.length, 0, "Should be empty for non-array");

  Services.prefs.setStringPref(SERVERS_PREF, "[]");
});

add_task(async function test_save_sandbox_server() {
  HarborServerStore.clearAll();

  const config = {
    name: "Test Server",
    type: "sandbox",
    code: 'globalThis.handleMessage = function() {}',
    enabled: true,
  };

  const saved = HarborServerStore.saveServer(config);

  Assert.ok(saved.id, "Should generate an ID");
  Assert.equal(saved.name, "Test Server", "Should save name");
  Assert.equal(saved.type, "sandbox", "Should save type");
  Assert.equal(saved.code, config.code, "Should save code");
  Assert.equal(saved.enabled, true, "Should save enabled state");
  Assert.ok(saved.createdAt, "Should have createdAt timestamp");
  Assert.ok(saved.updatedAt, "Should have updatedAt timestamp");

  const servers = HarborServerStore.loadServers();
  Assert.equal(servers.length, 1, "Should have one server");
  Assert.equal(servers[0].id, saved.id, "ID should match");
});

add_task(async function test_save_http_server() {
  HarborServerStore.clearAll();

  const config = {
    name: "HTTP Server",
    type: "http",
    url: "http://localhost:3000/mcp",
  };

  const saved = HarborServerStore.saveServer(config);

  Assert.ok(saved.id, "Should generate an ID");
  Assert.equal(saved.type, "http", "Should save type");
  Assert.equal(saved.url, config.url, "Should save URL");
  Assert.equal(saved.code, null, "Code should be null for HTTP servers");
});

add_task(async function test_save_requires_name_and_type() {
  HarborServerStore.clearAll();

  Assert.throws(
    () => HarborServerStore.saveServer({ type: "sandbox", code: "test" }),
    /name and type are required/,
    "Should require name"
  );

  Assert.throws(
    () => HarborServerStore.saveServer({ name: "Test" }),
    /name and type are required/,
    "Should require type"
  );
});

add_task(async function test_save_sandbox_requires_code() {
  HarborServerStore.clearAll();

  Assert.throws(
    () => HarborServerStore.saveServer({ name: "Test", type: "sandbox" }),
    /Sandbox servers require code/,
    "Sandbox servers should require code"
  );
});

add_task(async function test_save_http_requires_url() {
  HarborServerStore.clearAll();

  Assert.throws(
    () => HarborServerStore.saveServer({ name: "Test", type: "http" }),
    /HTTP servers require a URL/,
    "HTTP servers should require URL"
  );
});

add_task(async function test_update_existing_server() {
  HarborServerStore.clearAll();

  const initial = HarborServerStore.saveServer({
    name: "Original Name",
    type: "sandbox",
    code: "original code",
  });

  const originalCreatedAt = initial.createdAt;

  // Wait a bit to ensure updatedAt changes
  await new Promise(resolve => do_timeout(10, resolve));

  const updated = HarborServerStore.saveServer({
    id: initial.id,
    name: "Updated Name",
    type: "sandbox",
    code: "updated code",
  });

  Assert.equal(updated.id, initial.id, "ID should remain the same");
  Assert.equal(updated.name, "Updated Name", "Name should be updated");
  Assert.equal(updated.code, "updated code", "Code should be updated");
  Assert.equal(
    updated.createdAt,
    originalCreatedAt,
    "createdAt should be preserved"
  );
  Assert.ok(
    updated.updatedAt >= originalCreatedAt,
    "updatedAt should be updated"
  );

  const servers = HarborServerStore.loadServers();
  Assert.equal(servers.length, 1, "Should still have only one server");
});

add_task(async function test_get_server() {
  HarborServerStore.clearAll();

  const saved = HarborServerStore.saveServer({
    name: "Find Me",
    type: "sandbox",
    code: "test",
  });

  const found = HarborServerStore.getServer(saved.id);
  Assert.ok(found, "Should find the server");
  Assert.equal(found.name, "Find Me", "Should have correct name");

  const notFound = HarborServerStore.getServer("nonexistent-id");
  Assert.equal(notFound, null, "Should return null for nonexistent server");
});

add_task(async function test_delete_server() {
  HarborServerStore.clearAll();

  const server1 = HarborServerStore.saveServer({
    name: "Server 1",
    type: "sandbox",
    code: "test1",
  });

  const server2 = HarborServerStore.saveServer({
    name: "Server 2",
    type: "sandbox",
    code: "test2",
  });

  Assert.equal(HarborServerStore.loadServers().length, 2, "Should have 2 servers");

  const deleted = HarborServerStore.deleteServer(server1.id);
  Assert.ok(deleted, "Should return true when deleting");

  const servers = HarborServerStore.loadServers();
  Assert.equal(servers.length, 1, "Should have 1 server after delete");
  Assert.equal(servers[0].id, server2.id, "Remaining server should be server2");

  const deletedAgain = HarborServerStore.deleteServer(server1.id);
  Assert.ok(!deletedAgain, "Should return false for nonexistent server");
});

add_task(async function test_set_server_enabled() {
  HarborServerStore.clearAll();

  const server = HarborServerStore.saveServer({
    name: "Toggle Me",
    type: "sandbox",
    code: "test",
    enabled: true,
  });

  Assert.equal(
    HarborServerStore.getServer(server.id).enabled,
    true,
    "Should start enabled"
  );

  const disabled = HarborServerStore.setServerEnabled(server.id, false);
  Assert.ok(disabled, "Should return true");
  Assert.equal(
    HarborServerStore.getServer(server.id).enabled,
    false,
    "Should be disabled"
  );

  const enabled = HarborServerStore.setServerEnabled(server.id, true);
  Assert.ok(enabled, "Should return true");
  Assert.equal(
    HarborServerStore.getServer(server.id).enabled,
    true,
    "Should be enabled"
  );

  const nonexistent = HarborServerStore.setServerEnabled("fake-id", true);
  Assert.ok(!nonexistent, "Should return false for nonexistent server");
});

add_task(async function test_export_configs() {
  HarborServerStore.clearAll();

  HarborServerStore.saveServer({
    name: "Export Server 1",
    type: "sandbox",
    code: "test1",
  });

  HarborServerStore.saveServer({
    name: "Export Server 2",
    type: "http",
    url: "http://localhost:3000",
  });

  const exported = HarborServerStore.exportConfigs();
  const parsed = JSON.parse(exported);

  Assert.ok(Array.isArray(parsed), "Export should be valid JSON array");
  Assert.equal(parsed.length, 2, "Should export 2 servers");
  Assert.equal(parsed[0].name, "Export Server 1", "First server name correct");
  Assert.equal(parsed[1].name, "Export Server 2", "Second server name correct");
});

add_task(async function test_import_configs() {
  HarborServerStore.clearAll();

  const toImport = JSON.stringify([
    { name: "Imported 1", type: "sandbox", code: "imported code 1" },
    { name: "Imported 2", type: "sandbox", code: "imported code 2" },
    { invalid: "missing required fields" },
  ]);

  const count = HarborServerStore.importConfigs(toImport);
  Assert.equal(count, 2, "Should import 2 valid servers");

  const servers = HarborServerStore.loadServers();
  Assert.equal(servers.length, 2, "Should have 2 servers");
});

add_task(async function test_import_invalid_json() {
  HarborServerStore.clearAll();

  Assert.throws(
    () => HarborServerStore.importConfigs("not json"),
    /.*/, // JSON.parse error
    "Should throw on invalid JSON"
  );

  Assert.throws(
    () => HarborServerStore.importConfigs('{"not": "array"}'),
    /Import data must be an array/,
    "Should throw for non-array"
  );
});

add_task(async function test_clear_all() {
  HarborServerStore.saveServer({
    name: "To Clear",
    type: "sandbox",
    code: "test",
  });

  Assert.ok(
    HarborServerStore.loadServers().length > 0,
    "Should have servers before clear"
  );

  HarborServerStore.clearAll();

  Assert.equal(
    HarborServerStore.loadServers().length,
    0,
    "Should have no servers after clear"
  );
});

add_task(async function test_multiple_servers() {
  HarborServerStore.clearAll();

  for (let i = 1; i <= 5; i++) {
    HarborServerStore.saveServer({
      name: `Server ${i}`,
      type: "sandbox",
      code: `code ${i}`,
    });
  }

  const servers = HarborServerStore.loadServers();
  Assert.equal(servers.length, 5, "Should have 5 servers");

  for (let i = 1; i <= 5; i++) {
    const server = servers.find(s => s.name === `Server ${i}`);
    Assert.ok(server, `Server ${i} should exist`);
    Assert.equal(server.code, `code ${i}`, `Server ${i} code should match`);
  }
});
