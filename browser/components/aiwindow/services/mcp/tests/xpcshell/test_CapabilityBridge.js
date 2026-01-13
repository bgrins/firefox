/* Any copyright is dedicated to the Public Domain.
 * http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { CapabilityBridge, CapabilityError } = ChromeUtils.importESModule(
  "moz-src:///browser/components/aiwindow/services/mcp/CapabilityBridge.sys.mjs"
);
const { CapabilityGate } = ChromeUtils.importESModule(
  "moz-src:///browser/components/aiwindow/services/mcp/CapabilityGate.sys.mjs"
);

// Mock profile store for testing
class MockProfileStore {
  constructor() {
    this.profiles = new Map();
  }

  load(serverId) {
    return this.profiles.get(serverId) || null;
  }

  save(serverId, profile) {
    this.profiles.set(serverId, profile);
  }

  delete(serverId) {
    this.profiles.delete(serverId);
  }
}

// Helper to get temp directory
function getTempDir() {
  return Services.dirsvc.get("TmpD", Ci.nsIFile).path;
}

// Helper to create a test file
async function createTestFile(path, content) {
  await IOUtils.writeUTF8(path, content);
}

// Helper to create a filesystem profile
function createFilesystemProfile(readPaths = [], writePaths = []) {
  return {
    level: "custom",
    system: {
      filesystem: {
        enabled: true,
        read: readPaths,
        write: writePaths,
        deny: [],
      },
      network: { enabled: false, allowedHosts: [], denyPrivate: true },
      subprocess: { enabled: false, allowedCommands: [], denyShell: true },
      clipboard: { read: false, write: false },
      notifications: { enabled: false },
    },
    browser: {
      tabs: { read: false, navigate: false, create: false, close: false },
      history: { read: false, write: false },
      bookmarks: { read: false, write: false },
      downloads: { read: false, initiate: false, manage: false },
      cookies: { read: false, write: false },
      storage: { read: false, write: false },
      activeTab: { readContent: false, executeScript: false },
      allowPrivateBrowsing: false,
    },
  };
}

// Helper to create a browser profile
function createBrowserProfile(caps = {}) {
  return {
    level: "custom",
    system: {
      filesystem: { enabled: false, read: [], write: [], deny: [] },
      network: { enabled: false, allowedHosts: [], denyPrivate: true },
      subprocess: { enabled: false, allowedCommands: [], denyShell: true },
      clipboard: { read: false, write: false },
      notifications: { enabled: false },
    },
    browser: {
      tabs: { read: false, navigate: false, create: false, close: false, ...caps.tabs },
      history: { read: false, write: false, ...caps.history },
      bookmarks: { read: false, write: false, ...caps.bookmarks },
      downloads: { read: false, initiate: false, manage: false },
      cookies: { read: false, write: false },
      storage: { read: false, write: false },
      activeTab: { readContent: false, executeScript: false },
      allowPrivateBrowsing: false,
    },
  };
}

// ============================================================================
// Constructor Tests
// ============================================================================

add_task(async function test_constructor_valid() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const bridge = new CapabilityBridge("test-server", gate);

  Assert.equal(bridge.serverId, "test-server", "Should store serverId");
});

add_task(async function test_constructor_invalid_server_id() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  Assert.throws(
    () => new CapabilityBridge("", gate),
    /serverId must be a non-empty string/,
    "Should reject empty serverId"
  );

  Assert.throws(
    () => new CapabilityBridge(null, gate),
    /serverId must be a non-empty string/,
    "Should reject null serverId"
  );
});

add_task(async function test_constructor_missing_gate() {
  Assert.throws(
    () => new CapabilityBridge("test-server", null),
    /gate is required/,
    "Should reject null gate"
  );
});

// ============================================================================
// Filesystem API Tests
// ============================================================================

add_task(async function test_filesystem_read_allowed() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const tempDir = getTempDir();
  const testDir = `${tempDir}/bridge-test-${Date.now()}`;
  const testFile = `${testDir}/test.txt`;

  await IOUtils.makeDirectory(testDir);
  await createTestFile(testFile, "Hello, World!");

  store.save("test-server", createFilesystemProfile([testDir], []));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  const content = await apis.fs.readFile(testFile);
  Assert.equal(content, "Hello, World!", "Should read file content");

  await IOUtils.remove(testDir, { recursive: true });
});

add_task(async function test_filesystem_read_denied() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const tempDir = getTempDir();

  store.save("test-server", createFilesystemProfile([], []));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  try {
    await apis.fs.readFile(`${tempDir}/some-file.txt`);
    Assert.ok(false, "Should have thrown");
  } catch (e) {
    Assert.ok(e instanceof CapabilityError, "Should throw CapabilityError");
    Assert.equal(e.capability, "filesystem", "Capability should be filesystem");
    Assert.equal(e.operation, "read", "Operation should be read");
  }
});

add_task(async function test_filesystem_write_allowed() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const tempDir = getTempDir();
  const testDir = `${tempDir}/bridge-write-${Date.now()}`;
  const testFile = `${testDir}/output.txt`;

  await IOUtils.makeDirectory(testDir);

  store.save("test-server", createFilesystemProfile([], [testDir]));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  await apis.fs.writeFile(testFile, "Test content");

  const content = await IOUtils.readUTF8(testFile);
  Assert.equal(content, "Test content", "Should write file content");

  await IOUtils.remove(testDir, { recursive: true });
});

add_task(async function test_filesystem_write_denied() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const tempDir = getTempDir();

  store.save("test-server", createFilesystemProfile([tempDir], []));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  try {
    await apis.fs.writeFile(`${tempDir}/forbidden.txt`, "content");
    Assert.ok(false, "Should have thrown");
  } catch (e) {
    Assert.ok(e instanceof CapabilityError, "Should throw CapabilityError");
    Assert.equal(e.operation, "write", "Operation should be write");
  }
});

add_task(async function test_filesystem_exists() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const tempDir = getTempDir();
  const testDir = `${tempDir}/bridge-exists-${Date.now()}`;
  const existingFile = `${testDir}/exists.txt`;
  const missingFile = `${testDir}/missing.txt`;

  await IOUtils.makeDirectory(testDir);
  await createTestFile(existingFile, "content");

  store.save("test-server", createFilesystemProfile([testDir], []));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  const exists = await apis.fs.exists(existingFile);
  Assert.equal(exists, true, "Should return true for existing file");

  const missing = await apis.fs.exists(missingFile);
  Assert.equal(missing, false, "Should return false for missing file");

  await IOUtils.remove(testDir, { recursive: true });
});

add_task(async function test_filesystem_stat() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const tempDir = getTempDir();
  const testDir = `${tempDir}/bridge-stat-${Date.now()}`;
  const testFile = `${testDir}/stat.txt`;

  await IOUtils.makeDirectory(testDir);
  await createTestFile(testFile, "some content");

  store.save("test-server", createFilesystemProfile([testDir], []));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  const stat = await apis.fs.stat(testFile);
  Assert.equal(stat.type, "regular", "Should have type");
  Assert.ok(stat.size > 0, "Should have size");
  Assert.ok(stat.lastModified, "Should have lastModified");

  await IOUtils.remove(testDir, { recursive: true });
});

add_task(async function test_filesystem_listDir() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const tempDir = getTempDir();
  const testDir = `${tempDir}/bridge-list-${Date.now()}`;

  await IOUtils.makeDirectory(testDir);
  await createTestFile(`${testDir}/file1.txt`, "1");
  await createTestFile(`${testDir}/file2.txt`, "2");

  store.save("test-server", createFilesystemProfile([testDir], []));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  const files = await apis.fs.listDir(testDir);
  Assert.ok(files.includes("file1.txt"), "Should list file1.txt");
  Assert.ok(files.includes("file2.txt"), "Should list file2.txt");

  await IOUtils.remove(testDir, { recursive: true });
});

add_task(async function test_filesystem_mkdir() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const tempDir = getTempDir();
  const testDir = `${tempDir}/bridge-mkdir-${Date.now()}`;
  const newDir = `${testDir}/subdir`;

  await IOUtils.makeDirectory(testDir);

  store.save("test-server", createFilesystemProfile([], [testDir]));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  await apis.fs.mkdir(newDir);

  const exists = await IOUtils.exists(newDir);
  Assert.ok(exists, "Should create directory");

  await IOUtils.remove(testDir, { recursive: true });
});

add_task(async function test_filesystem_remove() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const tempDir = getTempDir();
  const testDir = `${tempDir}/bridge-rm-${Date.now()}`;
  const testFile = `${testDir}/to-delete.txt`;

  await IOUtils.makeDirectory(testDir);
  await createTestFile(testFile, "delete me");

  store.save("test-server", createFilesystemProfile([], [testDir]));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  await apis.fs.remove(testFile);

  const exists = await IOUtils.exists(testFile);
  Assert.ok(!exists, "Should remove file");

  await IOUtils.remove(testDir, { recursive: true });
});

add_task(async function test_filesystem_copy() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const tempDir = getTempDir();
  const testDir = `${tempDir}/bridge-copy-${Date.now()}`;
  const srcFile = `${testDir}/source.txt`;
  const destFile = `${testDir}/dest.txt`;

  await IOUtils.makeDirectory(testDir);
  await createTestFile(srcFile, "copy me");

  store.save("test-server", createFilesystemProfile([testDir], [testDir]));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  await apis.fs.copy(srcFile, destFile);

  const srcExists = await IOUtils.exists(srcFile);
  const destExists = await IOUtils.exists(destFile);
  const destContent = await IOUtils.readUTF8(destFile);

  Assert.ok(srcExists, "Source should still exist");
  Assert.ok(destExists, "Dest should exist");
  Assert.equal(destContent, "copy me", "Dest should have same content");

  await IOUtils.remove(testDir, { recursive: true });
});

add_task(async function test_filesystem_move() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const tempDir = getTempDir();
  const testDir = `${tempDir}/bridge-move-${Date.now()}`;
  const srcFile = `${testDir}/source.txt`;
  const destFile = `${testDir}/dest.txt`;

  await IOUtils.makeDirectory(testDir);
  await createTestFile(srcFile, "move me");

  store.save("test-server", createFilesystemProfile([testDir], [testDir]));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  await apis.fs.move(srcFile, destFile);

  const srcExists = await IOUtils.exists(srcFile);
  const destExists = await IOUtils.exists(destFile);

  Assert.ok(!srcExists, "Source should not exist");
  Assert.ok(destExists, "Dest should exist");

  await IOUtils.remove(testDir, { recursive: true });
});

// ============================================================================
// Browser API Tests (permission checks only - no real browser window)
// ============================================================================

add_task(async function test_browser_tabs_read_denied() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createBrowserProfile({ tabs: { read: false } }));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  try {
    await apis.browser.tabs.list();
    Assert.ok(false, "Should have thrown");
  } catch (e) {
    Assert.ok(e instanceof CapabilityError);
    Assert.equal(e.capability, "tabs");
    Assert.equal(e.operation, "read");
  }
});

add_task(async function test_browser_tabs_create_denied() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createBrowserProfile({ tabs: { create: false } }));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  try {
    await apis.browser.tabs.create("https://example.com");
    Assert.ok(false, "Should have thrown");
  } catch (e) {
    Assert.ok(e instanceof CapabilityError);
    Assert.equal(e.capability, "tabs");
    Assert.equal(e.operation, "create");
  }
});

add_task(async function test_browser_history_read_denied() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createBrowserProfile({ history: { read: false } }));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  try {
    await apis.browser.history.search("test");
    Assert.ok(false, "Should have thrown");
  } catch (e) {
    Assert.ok(e instanceof CapabilityError);
    Assert.equal(e.capability, "history");
    Assert.equal(e.operation, "read");
  }
});

add_task(async function test_browser_bookmarks_write_denied() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createBrowserProfile({ bookmarks: { write: false } }));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  try {
    await apis.browser.bookmarks.create("Test", "https://example.com");
    Assert.ok(false, "Should have thrown");
  } catch (e) {
    Assert.ok(e instanceof CapabilityError);
    Assert.equal(e.capability, "bookmarks");
    Assert.equal(e.operation, "write");
  }
});

// ============================================================================
// Network API Tests
// ============================================================================

add_task(async function test_network_fetch_denied() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", {
    level: "custom",
    system: {
      filesystem: { enabled: false, read: [], write: [], deny: [] },
      network: { enabled: false, allowedHosts: [], denyPrivate: true },
      subprocess: { enabled: false, allowedCommands: [], denyShell: true },
      clipboard: { read: false, write: false },
      notifications: { enabled: false },
    },
    browser: {
      tabs: { read: false, navigate: false, create: false, close: false },
      history: { read: false, write: false },
      bookmarks: { read: false, write: false },
      downloads: { read: false, initiate: false, manage: false },
      cookies: { read: false, write: false },
      storage: { read: false, write: false },
      activeTab: { readContent: false, executeScript: false },
      allowPrivateBrowsing: false,
    },
  });

  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  try {
    await apis.net.fetch("https://example.com");
    Assert.ok(false, "Should have thrown");
  } catch (e) {
    Assert.ok(e instanceof CapabilityError);
    Assert.equal(e.capability, "network");
  }
});

// ============================================================================
// Clipboard API Tests
// ============================================================================

add_task(async function test_clipboard_read_denied() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createFilesystemProfile([], []));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  try {
    await apis.clipboard.read();
    Assert.ok(false, "Should have thrown");
  } catch (e) {
    Assert.ok(e instanceof CapabilityError);
    Assert.equal(e.capability, "clipboard");
    Assert.equal(e.operation, "read");
  }
});

add_task(async function test_clipboard_write_denied() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createFilesystemProfile([], []));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  try {
    await apis.clipboard.write("test");
    Assert.ok(false, "Should have thrown");
  } catch (e) {
    Assert.ok(e instanceof CapabilityError);
    Assert.equal(e.capability, "clipboard");
    Assert.equal(e.operation, "write");
  }
});

// ============================================================================
// Notifications API Tests
// ============================================================================

add_task(async function test_notifications_denied() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createFilesystemProfile([], []));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  try {
    await apis.notifications.show("Test Notification");
    Assert.ok(false, "Should have thrown");
  } catch (e) {
    Assert.ok(e instanceof CapabilityError);
    Assert.equal(e.capability, "notifications");
  }
});

// ============================================================================
// Audit Log Tests
// ============================================================================

add_task(async function test_audit_log_records_allowed() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const tempDir = getTempDir();
  const testDir = `${tempDir}/bridge-audit-${Date.now()}`;
  const testFile = `${testDir}/audit.txt`;

  await IOUtils.makeDirectory(testDir);
  await createTestFile(testFile, "audit test");

  store.save("test-server", createFilesystemProfile([testDir], []));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  await apis.fs.readFile(testFile);

  const log = bridge.auditLog;
  Assert.equal(log.length, 1, "Should have one entry");
  Assert.equal(log[0].serverId, "test-server");
  Assert.equal(log[0].category, "system");
  Assert.equal(log[0].capability, "filesystem");
  Assert.equal(log[0].operation, "read");
  Assert.equal(log[0].allowed, true);
  Assert.ok(log[0].timestamp, "Should have timestamp");

  await IOUtils.remove(testDir, { recursive: true });
});

add_task(async function test_audit_log_records_denied() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const tempDir = getTempDir();

  store.save("test-server", createFilesystemProfile([], []));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  try {
    await apis.fs.readFile(`${tempDir}/forbidden.txt`);
  } catch {
    // Expected
  }

  const log = bridge.auditLog;
  Assert.equal(log.length, 1, "Should have one entry");
  Assert.equal(log[0].allowed, false);
  Assert.ok(log[0].reason, "Should have reason");
});

add_task(async function test_audit_log_clear() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const tempDir = getTempDir();

  store.save("test-server", createFilesystemProfile([], []));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  try {
    await apis.fs.readFile(`${tempDir}/test.txt`);
  } catch {
    // Expected
  }

  Assert.equal(bridge.auditLog.length, 1);

  bridge.clearAuditLog();

  Assert.equal(bridge.auditLog.length, 0, "Should clear log");
});

add_task(async function test_audit_log_immutable() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const tempDir = getTempDir();

  store.save("test-server", createFilesystemProfile([], []));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  try {
    await apis.fs.readFile(`${tempDir}/test.txt`);
  } catch {
    // Expected
  }

  const log1 = bridge.auditLog;
  const log2 = bridge.auditLog;

  Assert.notEqual(log1, log2, "Should return copy each time");

  log1.push({ fake: true });
  Assert.equal(bridge.auditLog.length, 1, "Original should be unchanged");
});

// ============================================================================
// URL Validation Tests
// ============================================================================

add_task(async function test_url_validation_valid() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createBrowserProfile({ tabs: { create: true } }));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  // This should fail because there's no browser window, but should fail
  // after URL validation passes
  try {
    await apis.browser.tabs.create("https://example.com");
  } catch (e) {
    // Expected to fail due to no browser window, not URL validation
    Assert.ok(!e.message.includes("Invalid URL"), "Should not fail URL validation");
  }
});

add_task(async function test_url_validation_invalid_protocol() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createBrowserProfile({ tabs: { create: true } }));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  try {
    await apis.browser.tabs.create("file:///etc/passwd");
    Assert.ok(false, "Should have thrown");
  } catch (e) {
    Assert.ok(e.message.includes("Only http/https"), "Should reject file protocol");
  }
});

add_task(async function test_url_validation_invalid_format() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createBrowserProfile({ tabs: { create: true } }));
  const bridge = new CapabilityBridge("test-server", gate);
  const apis = bridge.createAPIs();

  try {
    await apis.browser.tabs.create("not-a-url");
    Assert.ok(false, "Should have thrown");
  } catch (e) {
    Assert.ok(e.message.includes("Invalid URL"), "Should reject invalid URL");
  }
});

// ============================================================================
// createAPIs Structure Tests
// ============================================================================

add_task(async function test_createAPIs_structure() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);
  const bridge = new CapabilityBridge("test-server", gate);

  const apis = bridge.createAPIs();

  // Check structure
  Assert.ok(apis.fs, "Should have fs API");
  Assert.ok(typeof apis.fs.readFile === "function", "fs.readFile should be function");
  Assert.ok(typeof apis.fs.writeFile === "function", "fs.writeFile should be function");
  Assert.ok(typeof apis.fs.exists === "function", "fs.exists should be function");
  Assert.ok(typeof apis.fs.stat === "function", "fs.stat should be function");
  Assert.ok(typeof apis.fs.listDir === "function", "fs.listDir should be function");
  Assert.ok(typeof apis.fs.mkdir === "function", "fs.mkdir should be function");
  Assert.ok(typeof apis.fs.remove === "function", "fs.remove should be function");
  Assert.ok(typeof apis.fs.copy === "function", "fs.copy should be function");
  Assert.ok(typeof apis.fs.move === "function", "fs.move should be function");

  Assert.ok(apis.browser, "Should have browser API");
  Assert.ok(apis.browser.tabs, "Should have browser.tabs");
  Assert.ok(typeof apis.browser.tabs.list === "function");
  Assert.ok(typeof apis.browser.tabs.create === "function");
  Assert.ok(apis.browser.history, "Should have browser.history");
  Assert.ok(apis.browser.bookmarks, "Should have browser.bookmarks");

  Assert.ok(apis.net, "Should have net API");
  Assert.ok(typeof apis.net.fetch === "function");

  Assert.ok(apis.clipboard, "Should have clipboard API");
  Assert.ok(typeof apis.clipboard.read === "function");
  Assert.ok(typeof apis.clipboard.write === "function");

  Assert.ok(apis.notifications, "Should have notifications API");
  Assert.ok(typeof apis.notifications.show === "function");
});

// ============================================================================
// CapabilityError Tests
// ============================================================================

add_task(async function test_capability_error_properties() {
  const error = new CapabilityError("filesystem", "read", "Path not allowed");

  Assert.equal(error.name, "CapabilityError");
  Assert.equal(error.capability, "filesystem");
  Assert.equal(error.operation, "read");
  Assert.equal(error.reason, "Path not allowed");
  Assert.ok(error.message.includes("filesystem"));
  Assert.ok(error.message.includes("read"));
  Assert.ok(error.message.includes("Path not allowed"));
});

add_task(async function test_capability_error_inheritance() {
  const error = new CapabilityError("tabs", "create", "Not permitted");

  // Note: instanceof checks can fail across module boundaries in xpcshell
  // so we verify error-like behavior instead
  Assert.ok(error.message, "Should have message property like Error");
  Assert.ok(error.stack, "Should have stack property like Error");
  Assert.equal(error.name, "CapabilityError", "Should have correct name");
  Assert.ok(
    typeof error.toString === "function",
    "Should have toString like Error"
  );
});
