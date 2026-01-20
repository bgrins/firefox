/* Any copyright is dedicated to the Public Domain.
 * http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { CapabilityProfileStore } = ChromeUtils.importESModule(
  "moz-src:///browser/components/aiwindow/services/mcp/CapabilityProfileStore.sys.mjs"
);

// Clean up after each test
function cleanup() {
  CapabilityProfileStore.clearAll();
}

// Helper to create a minimal valid profile
function createValidProfile(level = "isolated") {
  return CapabilityProfileStore.getDefaultProfile(level);
}

// ============================================================================
// Server ID Validation Tests
// ============================================================================

add_task(async function test_server_id_validation_valid() {
  cleanup();

  const validIds = [
    "server1",
    "my-server",
    "my_server",
    "Server123",
    "a",
    "A-B_C-1-2-3",
  ];

  for (const serverId of validIds) {
    const profile = createValidProfile();
    CapabilityProfileStore.save(serverId, profile);
    const loaded = CapabilityProfileStore.load(serverId);
    Assert.ok(loaded, `Should save/load profile for valid ID: ${serverId}`);
    cleanup();
  }
});

add_task(async function test_server_id_validation_invalid() {
  cleanup();

  const invalidIds = [
    "",
    null,
    undefined,
    123,
    "server.name",
    "server/name",
    "server\\name",
    "server name",
    "server:name",
    "a".repeat(101),
    "../etc/passwd",
    "server%id",
  ];

  for (const serverId of invalidIds) {
    Assert.throws(
      () => CapabilityProfileStore.save(serverId, createValidProfile()),
      /Invalid server ID/,
      `Should reject invalid server ID: ${serverId}`
    );

    const loaded = CapabilityProfileStore.load(serverId);
    Assert.equal(loaded, null, `Should return null for invalid ID: ${serverId}`);
  }
});

// ============================================================================
// Basic CRUD Operations
// ============================================================================

add_task(async function test_save_and_load() {
  cleanup();

  const profile = createValidProfile("browser-readonly");
  CapabilityProfileStore.save("test-server", profile);

  const loaded = CapabilityProfileStore.load("test-server");
  Assert.ok(loaded, "Should load saved profile");
  Assert.equal(loaded.level, "browser-readonly", "Level should match");
  Assert.equal(
    loaded.browser.tabs.read,
    true,
    "Browser tabs read should be true"
  );
  Assert.equal(
    loaded.browser.tabs.create,
    false,
    "Browser tabs create should be false"
  );

  cleanup();
});

add_task(async function test_update_existing() {
  cleanup();

  const profile1 = createValidProfile("isolated");
  CapabilityProfileStore.save("test-server", profile1);

  const loaded1 = CapabilityProfileStore.load("test-server");
  Assert.equal(loaded1.level, "isolated");

  const profile2 = createValidProfile("developer");
  CapabilityProfileStore.save("test-server", profile2);

  const loaded2 = CapabilityProfileStore.load("test-server");
  Assert.equal(loaded2.level, "developer", "Should update to new level");

  cleanup();
});

add_task(async function test_delete() {
  cleanup();

  CapabilityProfileStore.save("test-server", createValidProfile());
  Assert.ok(CapabilityProfileStore.load("test-server"), "Should exist before delete");

  const deleted = CapabilityProfileStore.delete("test-server");
  Assert.equal(deleted, true, "Delete should return true");

  const loaded = CapabilityProfileStore.load("test-server");
  Assert.equal(loaded, null, "Should return null after delete");

  cleanup();
});

add_task(async function test_delete_nonexistent() {
  cleanup();

  const deleted = CapabilityProfileStore.delete("nonexistent-server");
  Assert.equal(deleted, false, "Delete should return false for nonexistent");

  cleanup();
});

add_task(async function test_load_nonexistent() {
  cleanup();

  const loaded = CapabilityProfileStore.load("nonexistent-server");
  Assert.equal(loaded, null, "Should return null for nonexistent server");

  cleanup();
});

// ============================================================================
// Profile Validation Tests
// ============================================================================

add_task(async function test_profile_validation_missing_level() {
  cleanup();

  const invalidProfile = {
    system: { filesystem: { enabled: false } },
    browser: { tabs: { read: false } },
  };

  Assert.throws(
    () => CapabilityProfileStore.save("test-server", invalidProfile),
    /Invalid profile/,
    "Should reject profile without level"
  );

  cleanup();
});

add_task(async function test_profile_validation_missing_system() {
  cleanup();

  const invalidProfile = {
    level: "custom",
    browser: { tabs: { read: false } },
  };

  Assert.throws(
    () => CapabilityProfileStore.save("test-server", invalidProfile),
    /Invalid profile/,
    "Should reject profile without system"
  );

  cleanup();
});

add_task(async function test_profile_validation_missing_browser() {
  cleanup();

  const invalidProfile = {
    level: "custom",
    system: { filesystem: { enabled: false } },
  };

  Assert.throws(
    () => CapabilityProfileStore.save("test-server", invalidProfile),
    /Invalid profile/,
    "Should reject profile without browser"
  );

  cleanup();
});

add_task(async function test_profile_validation_invalid_filesystem_enabled() {
  cleanup();

  const invalidProfile = {
    level: "custom",
    system: {
      filesystem: { enabled: "yes" },
    },
    browser: { tabs: { read: false } },
  };

  Assert.throws(
    () => CapabilityProfileStore.save("test-server", invalidProfile),
    /Invalid profile/,
    "Should reject non-boolean filesystem.enabled"
  );

  cleanup();
});

add_task(async function test_profile_validation_invalid_filesystem_read() {
  cleanup();

  const invalidProfile = {
    level: "custom",
    system: {
      filesystem: { enabled: false, read: "not-array" },
    },
    browser: { tabs: { read: false } },
  };

  Assert.throws(
    () => CapabilityProfileStore.save("test-server", invalidProfile),
    /Invalid profile/,
    "Should reject non-array filesystem.read"
  );

  cleanup();
});

add_task(async function test_profile_validation_invalid_browser_capability() {
  cleanup();

  const invalidProfile = {
    level: "custom",
    system: { filesystem: { enabled: false } },
    browser: { tabs: { read: "yes" } },
  };

  Assert.throws(
    () => CapabilityProfileStore.save("test-server", invalidProfile),
    /Invalid profile/,
    "Should reject non-boolean browser capability"
  );

  cleanup();
});

add_task(async function test_profile_validation_invalid_allowPrivateBrowsing() {
  cleanup();

  const invalidProfile = {
    level: "custom",
    system: { filesystem: { enabled: false } },
    browser: {
      tabs: { read: false },
      allowPrivateBrowsing: "yes",
    },
  };

  Assert.throws(
    () => CapabilityProfileStore.save("test-server", invalidProfile),
    /Invalid profile/,
    "Should reject non-boolean allowPrivateBrowsing"
  );

  cleanup();
});

// ============================================================================
// Default Profile Tests
// ============================================================================

add_task(async function test_get_default_profile_isolated() {
  const profile = CapabilityProfileStore.getDefaultProfile("isolated");

  Assert.ok(profile, "Should return profile for isolated level");
  Assert.equal(profile.level, "isolated");
  Assert.equal(profile.system.filesystem.enabled, false);
  Assert.equal(profile.system.network.enabled, false);
  Assert.equal(profile.system.subprocess.enabled, false);
  Assert.equal(profile.browser.tabs.read, false);
  Assert.equal(profile.browser.tabs.create, false);
  Assert.equal(profile.browser.history.read, false);
  Assert.equal(profile.browser.cookies.read, false);
  Assert.equal(profile.browser.activeTab.executeScript, false);
  Assert.equal(profile.browser.allowPrivateBrowsing, false);
});

add_task(async function test_get_default_profile_browser_readonly() {
  const profile = CapabilityProfileStore.getDefaultProfile("browser-readonly");

  Assert.ok(profile, "Should return profile for browser-readonly level");
  Assert.equal(profile.level, "browser-readonly");
  Assert.equal(profile.system.filesystem.enabled, false);
  Assert.equal(profile.browser.tabs.read, true);
  Assert.equal(profile.browser.tabs.create, false);
  Assert.equal(profile.browser.history.read, true);
  Assert.equal(profile.browser.history.write, false);
  Assert.equal(profile.browser.bookmarks.read, true);
  Assert.equal(profile.browser.bookmarks.write, false);
  Assert.equal(profile.browser.cookies.read, false);
});

add_task(async function test_get_default_profile_browser_full() {
  const profile = CapabilityProfileStore.getDefaultProfile("browser-full");

  Assert.ok(profile, "Should return profile for browser-full level");
  Assert.equal(profile.level, "browser-full");
  Assert.equal(profile.browser.tabs.read, true);
  Assert.equal(profile.browser.tabs.create, true);
  Assert.equal(profile.browser.tabs.close, true);
  Assert.equal(profile.browser.history.write, true);
  Assert.equal(profile.browser.bookmarks.write, true);
  Assert.equal(profile.browser.downloads.initiate, true);
  Assert.equal(profile.browser.cookies.read, false, "Cookies still restricted");
  Assert.equal(
    profile.browser.activeTab.executeScript,
    false,
    "executeScript still restricted"
  );
});

add_task(async function test_get_default_profile_workspace() {
  const profile = CapabilityProfileStore.getDefaultProfile("workspace");

  Assert.ok(profile, "Should return profile for workspace level");
  Assert.equal(profile.level, "workspace");
  Assert.equal(profile.system.filesystem.enabled, true);
  Assert.equal(profile.system.clipboard.read, true);
  Assert.equal(profile.system.clipboard.write, true);
  Assert.equal(profile.browser.tabs.read, false, "No browser access");
});

add_task(async function test_get_default_profile_developer() {
  const profile = CapabilityProfileStore.getDefaultProfile("developer");

  Assert.ok(profile, "Should return profile for developer level");
  Assert.equal(profile.level, "developer");
  Assert.equal(profile.system.filesystem.enabled, true);
  Assert.equal(profile.system.network.enabled, true);
  Assert.equal(profile.system.subprocess.enabled, true);
  Assert.equal(profile.browser.tabs.read, true);
  Assert.equal(profile.browser.tabs.create, true);
  Assert.equal(profile.browser.cookies.read, false, "Cookies still restricted");
});

add_task(async function test_get_default_profile_unknown() {
  const profile = CapabilityProfileStore.getDefaultProfile("unknown-level");
  Assert.equal(profile, null, "Should return null for unknown level");
});

// ============================================================================
// Available Levels Tests
// ============================================================================

add_task(async function test_get_available_levels() {
  const levels = CapabilityProfileStore.getAvailableLevels();

  Assert.ok(Array.isArray(levels), "Should return array");
  Assert.ok(levels.includes("isolated"));
  Assert.ok(levels.includes("browser-readonly"));
  Assert.ok(levels.includes("browser-full"));
  Assert.ok(levels.includes("workspace"));
  Assert.ok(levels.includes("developer"));
  Assert.equal(levels.length, 5, "Should have 5 levels");
});

add_task(async function test_get_level_description() {
  Assert.ok(
    CapabilityProfileStore.getLevelDescription("isolated").includes("computation"),
    "Isolated description"
  );
  Assert.ok(
    CapabilityProfileStore.getLevelDescription("browser-readonly").includes("tabs"),
    "Browser-readonly description"
  );
  Assert.equal(
    CapabilityProfileStore.getLevelDescription("unknown"),
    null,
    "Unknown level returns null"
  );
});

// ============================================================================
// Custom Profile Tests
// ============================================================================

add_task(async function test_create_custom_profile_from_isolated() {
  const profile = CapabilityProfileStore.createCustomProfile("isolated", {
    browser: {
      tabs: { read: true },
    },
  });

  Assert.equal(profile.level, "custom", "Level should be custom");
  Assert.equal(profile.browser.tabs.read, true, "Customization applied");
  Assert.equal(
    profile.browser.tabs.create,
    false,
    "Non-customized values preserved"
  );
  Assert.equal(profile.system.filesystem.enabled, false, "System unchanged");
});

add_task(async function test_create_custom_profile_from_workspace() {
  const profile = CapabilityProfileStore.createCustomProfile("workspace", {
    system: {
      filesystem: { read: ["/home/user/project"] },
    },
  });

  Assert.equal(profile.level, "custom");
  Assert.equal(profile.system.filesystem.enabled, true, "Base enabled preserved");
  Assert.deepEqual(
    profile.system.filesystem.read,
    ["/home/user/project"],
    "Custom paths applied"
  );
});

add_task(async function test_create_custom_profile_unknown_level_defaults() {
  const profile = CapabilityProfileStore.createCustomProfile("unknown-level", {
    browser: { tabs: { read: true } },
  });

  Assert.equal(profile.level, "custom");
  Assert.equal(
    profile.system.filesystem.enabled,
    false,
    "Falls back to isolated"
  );
  Assert.equal(profile.browser.tabs.read, true, "Customization still applied");
});

// ============================================================================
// List Server IDs Tests
// ============================================================================

add_task(async function test_list_server_ids_empty() {
  cleanup();

  const ids = CapabilityProfileStore.listServerIds();
  Assert.deepEqual(ids, [], "Should return empty array when no profiles");

  cleanup();
});

add_task(async function test_list_server_ids_multiple() {
  cleanup();

  CapabilityProfileStore.save("server-a", createValidProfile());
  CapabilityProfileStore.save("server-b", createValidProfile());
  CapabilityProfileStore.save("server-c", createValidProfile());

  const ids = CapabilityProfileStore.listServerIds();
  Assert.equal(ids.length, 3, "Should have 3 servers");
  Assert.ok(ids.includes("server-a"));
  Assert.ok(ids.includes("server-b"));
  Assert.ok(ids.includes("server-c"));

  cleanup();
});

add_task(async function test_list_server_ids_after_delete() {
  cleanup();

  CapabilityProfileStore.save("server-a", createValidProfile());
  CapabilityProfileStore.save("server-b", createValidProfile());
  CapabilityProfileStore.delete("server-a");

  const ids = CapabilityProfileStore.listServerIds();
  Assert.equal(ids.length, 1, "Should have 1 server after delete");
  Assert.ok(ids.includes("server-b"));
  Assert.ok(!ids.includes("server-a"));

  cleanup();
});

// ============================================================================
// Version and Metadata Tests
// ============================================================================

add_task(async function test_version_and_updated_at() {
  cleanup();

  const profile = createValidProfile();
  CapabilityProfileStore.save("test-server", profile);

  const loaded = CapabilityProfileStore.load("test-server");
  Assert.equal(loaded.version, 1, "Should have schema version");
  Assert.ok(loaded.updatedAt, "Should have updatedAt timestamp");
  Assert.ok(loaded.updatedAt <= Date.now(), "Timestamp should be in past");
  Assert.ok(
    loaded.updatedAt > Date.now() - 60000,
    "Timestamp should be recent"
  );

  cleanup();
});

// ============================================================================
// Edge Cases
// ============================================================================

add_task(async function test_clear_all() {
  cleanup();

  CapabilityProfileStore.save("server-1", createValidProfile());
  CapabilityProfileStore.save("server-2", createValidProfile());
  CapabilityProfileStore.save("server-3", createValidProfile());

  Assert.equal(CapabilityProfileStore.listServerIds().length, 3);

  CapabilityProfileStore.clearAll();

  Assert.equal(CapabilityProfileStore.listServerIds().length, 0);

  cleanup();
});

add_task(async function test_profile_deep_copy() {
  // Ensure default profiles are deep copied
  const profile1 = CapabilityProfileStore.getDefaultProfile("isolated");
  const profile2 = CapabilityProfileStore.getDefaultProfile("isolated");

  profile1.system.filesystem.read.push("/modified");

  Assert.deepEqual(
    profile2.system.filesystem.read,
    [],
    "Modifying one profile should not affect another"
  );
});

add_task(async function test_minimal_valid_profile() {
  cleanup();

  const minimalProfile = {
    level: "custom",
    system: {},
    browser: {},
  };

  CapabilityProfileStore.save("test-server", minimalProfile);
  const loaded = CapabilityProfileStore.load("test-server");
  Assert.ok(loaded, "Should accept minimal valid profile");
  Assert.equal(loaded.level, "custom");

  cleanup();
});

// ============================================================================
// Integration with CapabilityGate
// ============================================================================

add_task(async function test_profile_works_with_gate() {
  cleanup();

  const { CapabilityGate } = ChromeUtils.importESModule(
    "moz-src:///browser/components/aiwindow/services/mcp/CapabilityGate.sys.mjs"
  );

  // Save a profile
  const profile = CapabilityProfileStore.createCustomProfile("workspace", {
    system: {
      filesystem: {
        read: ["/home/user/project"],
        write: ["/home/user/project"],
      },
    },
  });
  CapabilityProfileStore.save("test-server", profile);

  // Use CapabilityGate with the store
  const gate = new CapabilityGate(CapabilityProfileStore);

  // Should allow read in allowed directory
  let result = gate.checkPermission(
    "test-server",
    "system",
    "filesystem",
    "read",
    { path: "/home/user/project/file.txt" }
  );
  Assert.equal(result.allowed, true, "Should allow read in project dir");

  // Should deny read outside directory
  result = gate.checkPermission(
    "test-server",
    "system",
    "filesystem",
    "read",
    { path: "/etc/passwd" }
  );
  Assert.equal(result.allowed, false, "Should deny read outside project dir");

  cleanup();
});
