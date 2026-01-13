/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

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

// Helper to create a filesystem-enabled profile
function createFilesystemProfile(
  readPaths = [],
  writePaths = [],
  denyPaths = []
) {
  return {
    level: "custom",
    system: {
      filesystem: {
        enabled: true,
        read: readPaths,
        write: writePaths,
        deny: denyPaths,
      },
      network: { enabled: false },
      subprocess: { enabled: false },
      clipboard: { read: false, write: false },
      notifications: { enabled: false },
    },
    browser: {
      tabs: { read: false },
      history: { read: false },
      bookmarks: { read: false },
      allowPrivateBrowsing: false,
    },
  };
}

// Helper to create a network-enabled profile
function createNetworkProfile(allowedHosts = [], denyPrivate = true) {
  return {
    level: "custom",
    system: {
      filesystem: { enabled: false },
      network: {
        enabled: true,
        allowedHosts,
        denyPrivate,
      },
      subprocess: { enabled: false },
      clipboard: { read: false, write: false },
      notifications: { enabled: false },
    },
    browser: {
      tabs: { read: false },
      history: { read: false },
      bookmarks: { read: false },
      allowPrivateBrowsing: false,
    },
  };
}

// ============================================================================
// Default Deny Tests
// ============================================================================

add_task(async function test_default_deny_no_profile() {
  const gate = new CapabilityGate(new MockProfileStore());

  // Without any profile, everything should be denied
  let result = gate.checkPermission(
    "test-server",
    "system",
    "filesystem",
    "read",
    {
      path: "/some/path",
    }
  );
  Assert.equal(result.allowed, false, "Filesystem read denied by default");

  result = gate.checkPermission("test-server", "system", "network", "fetch", {
    url: "https://example.com",
  });
  Assert.equal(result.allowed, false, "Network fetch denied by default");

  result = gate.checkPermission("test-server", "browser", "tabs", "read", {});
  Assert.equal(result.allowed, false, "Browser tabs denied by default");
});

add_task(async function test_default_deny_patterns() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  // Create profile that allows reading everything
  store.save("test-server", createFilesystemProfile(["/**"]));

  // These should still be denied due to default deny patterns
  const denyPaths = [
    "/home/user/.env",
    "/home/user/.env.local",
    "/home/user/secret.key",
    "/home/user/server.pem",
    "/home/user/credentials.json",
    "/home/user/.ssh/id_rsa",
    "/home/user/.gnupg/secring.gpg",
    "/home/user/.aws/credentials",
  ];

  for (const path of denyPaths) {
    const result = gate.checkPermission(
      "test-server",
      "system",
      "filesystem",
      "read",
      { path }
    );
    Assert.equal(result.allowed, false, `Should deny access to ${path}`);
  }
});

// ============================================================================
// Server ID Validation Tests
// ============================================================================

add_task(async function test_server_id_validation() {
  const gate = new CapabilityGate(new MockProfileStore());

  // Valid server IDs
  const validIds = ["server1", "my-server", "my_server", "Server123", "a"];
  for (const id of validIds) {
    const result = gate.checkPermission(id, "system", "filesystem", "read", {
      path: "/",
    });
    Assert.notEqual(
      result.reason,
      "Invalid server ID",
      `Should accept server ID: ${id}`
    );
  }

  // Invalid server IDs
  const invalidIds = [
    "",
    null,
    undefined,
    "server.with.dots",
    "server/with/slash",
    "server\\backslash",
    "a".repeat(200), // Too long
    "server with space",
    "server\0null",
  ];

  for (const id of invalidIds) {
    const result = gate.checkPermission(id, "system", "filesystem", "read", {
      path: "/",
    });
    Assert.equal(
      result.allowed,
      false,
      `Should reject invalid server ID: ${id}`
    );
    Assert.equal(
      result.reason,
      "Invalid server ID",
      `Reason should be invalid ID for: ${id}`
    );
  }
});

// ============================================================================
// Filesystem Permission Tests
// ============================================================================

add_task(async function test_filesystem_basic_read() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  // Use paths that exist on the test system
  const tempDir = Services.dirsvc.get("TmpD", Ci.nsIFile).path;
  const testDir = tempDir + "/test-project";
  const testFile = testDir + "/file.txt";
  const otherFile = tempDir + "/other/file.txt";

  store.save("test-server", createFilesystemProfile([testDir]));

  // Should allow read within allowed path
  let result = gate.checkPermission(
    "test-server",
    "system",
    "filesystem",
    "read",
    {
      path: testFile,
    }
  );
  info(`Testing path: ${testFile}, allowed dir: ${testDir}`);
  info(`Result: allowed=${result.allowed}, reason=${result.reason}`);
  Assert.equal(result.allowed, true, "Should allow read in allowed directory");

  // Should allow read of the directory itself
  result = gate.checkPermission("test-server", "system", "filesystem", "read", {
    path: testDir,
  });
  Assert.equal(
    result.allowed,
    true,
    "Should allow read of allowed directory itself"
  );

  // Should deny read outside allowed path
  result = gate.checkPermission("test-server", "system", "filesystem", "read", {
    path: otherFile,
  });
  Assert.equal(
    result.allowed,
    false,
    "Should deny read outside allowed directory"
  );
});

add_task(async function test_filesystem_write_separate_from_read() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  // Read allowed, but no write paths
  store.save(
    "test-server",
    createFilesystemProfile(["/home/user/project"], [])
  );

  // Should allow read
  let result = gate.checkPermission(
    "test-server",
    "system",
    "filesystem",
    "read",
    {
      path: "/home/user/project/file.txt",
    }
  );
  Assert.equal(result.allowed, true, "Should allow read");

  // Should deny write (no write paths configured)
  result = gate.checkPermission(
    "test-server",
    "system",
    "filesystem",
    "write",
    {
      path: "/home/user/project/file.txt",
    }
  );
  Assert.equal(result.allowed, false, "Should deny write when no write paths");
});

add_task(async function test_filesystem_glob_patterns() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save(
    "test-server",
    createFilesystemProfile(["/home/user/project/**/*.js"])
  );

  // Should match .js files
  let result = gate.checkPermission(
    "test-server",
    "system",
    "filesystem",
    "read",
    {
      path: "/home/user/project/src/index.js",
    }
  );
  Assert.equal(result.allowed, true, "Should allow .js files");

  // Should not match .ts files
  result = gate.checkPermission("test-server", "system", "filesystem", "read", {
    path: "/home/user/project/src/index.ts",
  });
  Assert.equal(result.allowed, false, "Should deny .ts files");
});

add_task(async function test_filesystem_custom_deny_patterns() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  // Allow everything but deny **/secret/**
  store.save(
    "test-server",
    createFilesystemProfile(["/**"], [], ["**/secret/**"])
  );

  // Should allow normal files
  let result = gate.checkPermission(
    "test-server",
    "system",
    "filesystem",
    "read",
    {
      path: "/home/user/public/file.txt",
    }
  );
  Assert.equal(result.allowed, true, "Should allow non-secret files");

  // Should deny secret directory
  result = gate.checkPermission("test-server", "system", "filesystem", "read", {
    path: "/home/user/secret/password.txt",
  });
  Assert.equal(result.allowed, false, "Should deny secret directory");
});

add_task(async function test_filesystem_path_traversal() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createFilesystemProfile(["/home/user/project"]));

  // Path traversal attempts should be blocked
  const traversalPaths = [
    "/home/user/project/../../../etc/passwd",
    "/home/user/project/./../../etc/passwd",
  ];

  for (const path of traversalPaths) {
    const result = gate.checkPermission(
      "test-server",
      "system",
      "filesystem",
      "read",
      { path }
    );
    Assert.equal(result.allowed, false, `Should block path traversal: ${path}`);
  }
});

add_task(async function test_filesystem_null_byte() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createFilesystemProfile(["/home/user/project"]));

  // Null byte injection should be blocked
  const result = gate.checkPermission(
    "test-server",
    "system",
    "filesystem",
    "read",
    {
      path: "/home/user/project/file.txt\0.jpg",
    }
  );
  Assert.equal(result.allowed, false, "Should block null byte injection");
  Assert.ok(result.reason.includes("null byte"), "Should mention null byte");
});

add_task(async function test_filesystem_invalid_paths() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createFilesystemProfile(["/home/user/project"]));

  // Invalid path types should be rejected
  const invalidPaths = [null, undefined, "", 123, {}, []];

  for (const path of invalidPaths) {
    const result = gate.checkPermission(
      "test-server",
      "system",
      "filesystem",
      "read",
      { path }
    );
    Assert.equal(result.allowed, false, `Should reject invalid path: ${path}`);
  }
});

// ============================================================================
// Network Permission Tests
// ============================================================================

add_task(async function test_network_basic() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createNetworkProfile(["api.example.com"]));

  // Should allow configured host
  let result = gate.checkPermission(
    "test-server",
    "system",
    "network",
    "fetch",
    {
      url: "https://api.example.com/data",
    }
  );
  Assert.equal(result.allowed, true, "Should allow configured host");

  // Should deny other hosts
  result = gate.checkPermission("test-server", "system", "network", "fetch", {
    url: "https://evil.com/steal",
  });
  Assert.equal(result.allowed, false, "Should deny unconfigured host");
});

add_task(async function test_network_wildcard_subdomain() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createNetworkProfile(["*.example.com"]));

  // Should allow subdomains
  let result = gate.checkPermission(
    "test-server",
    "system",
    "network",
    "fetch",
    {
      url: "https://api.example.com/data",
    }
  );
  Assert.equal(result.allowed, true, "Should allow subdomain");

  // Should also allow base domain
  result = gate.checkPermission("test-server", "system", "network", "fetch", {
    url: "https://example.com/data",
  });
  Assert.equal(result.allowed, true, "Should allow base domain");

  // Should deny different domain
  result = gate.checkPermission("test-server", "system", "network", "fetch", {
    url: "https://example.org/data",
  });
  Assert.equal(result.allowed, false, "Should deny different domain");
});

add_task(async function test_network_deny_private() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  // Allow everything but deny private (default)
  store.save("test-server", createNetworkProfile(["*"], true));

  // Should deny localhost
  let result = gate.checkPermission(
    "test-server",
    "system",
    "network",
    "fetch",
    {
      url: "http://localhost:3000/api",
    }
  );
  Assert.equal(result.allowed, false, "Should deny localhost");

  // Should deny 127.0.0.1
  result = gate.checkPermission("test-server", "system", "network", "fetch", {
    url: "http://127.0.0.1:3000/api",
  });
  Assert.equal(result.allowed, false, "Should deny 127.0.0.1");

  // Should deny private IP ranges
  const privateIPs = ["10.0.0.1", "172.16.0.1", "192.168.1.1", "169.254.1.1"];
  for (const ip of privateIPs) {
    result = gate.checkPermission("test-server", "system", "network", "fetch", {
      url: `http://${ip}/api`,
    });
    Assert.equal(result.allowed, false, `Should deny private IP: ${ip}`);
  }

  // Should deny .local domains
  result = gate.checkPermission("test-server", "system", "network", "fetch", {
    url: "http://myserver.local/api",
  });
  Assert.equal(result.allowed, false, "Should deny .local domain");
});

add_task(async function test_network_allow_private_explicit() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  // Explicitly allow private networks
  store.save(
    "test-server",
    createNetworkProfile(["localhost", "127.0.0.1"], false)
  );

  // Should allow localhost when explicitly permitted
  let result = gate.checkPermission(
    "test-server",
    "system",
    "network",
    "fetch",
    {
      url: "http://localhost:3000/api",
    }
  );
  Assert.equal(result.allowed, true, "Should allow localhost when permitted");
});

add_task(async function test_network_protocol_restriction() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createNetworkProfile(["example.com"]));

  // Should deny non-http(s) protocols
  const invalidUrls = [
    "file:///etc/passwd",
    "javascript:alert(1)",
    "ftp://example.com/file",
    "data:text/html,<h1>Hi</h1>",
  ];

  for (const url of invalidUrls) {
    const result = gate.checkPermission(
      "test-server",
      "system",
      "network",
      "fetch",
      { url }
    );
    Assert.equal(result.allowed, false, `Should deny protocol in: ${url}`);
  }
});

add_task(async function test_network_invalid_url() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", createNetworkProfile(["example.com"]));

  // Invalid URLs should be rejected
  const invalidUrls = [null, undefined, "", "not a url", "://missing-protocol"];

  for (const url of invalidUrls) {
    const result = gate.checkPermission(
      "test-server",
      "system",
      "network",
      "fetch",
      { url }
    );
    Assert.equal(result.allowed, false, `Should reject invalid URL: ${url}`);
  }
});

// ============================================================================
// Subprocess Permission Tests
// ============================================================================

add_task(async function test_subprocess_basic() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", {
    level: "custom",
    system: {
      filesystem: { enabled: false },
      network: { enabled: false },
      subprocess: {
        enabled: true,
        allowedCommands: ["git", "npm"],
        denyShell: true,
      },
      clipboard: { read: false, write: false },
      notifications: { enabled: false },
    },
    browser: {},
  });

  // Should allow git
  let result = gate.checkPermission(
    "test-server",
    "system",
    "subprocess",
    "execute",
    {
      command: "git status",
    }
  );
  Assert.equal(result.allowed, true, "Should allow git");

  // Should allow npm
  result = gate.checkPermission(
    "test-server",
    "system",
    "subprocess",
    "execute",
    {
      command: "npm install",
    }
  );
  Assert.equal(result.allowed, true, "Should allow npm");

  // Should deny unlisted command
  result = gate.checkPermission(
    "test-server",
    "system",
    "subprocess",
    "execute",
    {
      command: "curl evil.com",
    }
  );
  Assert.equal(result.allowed, false, "Should deny unlisted command");
});

add_task(async function test_subprocess_deny_shell() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", {
    level: "custom",
    system: {
      filesystem: { enabled: false },
      network: { enabled: false },
      subprocess: {
        enabled: true,
        allowedCommands: ["bash", "sh"], // Even if in allowlist
        denyShell: true,
      },
      clipboard: { read: false, write: false },
      notifications: { enabled: false },
    },
    browser: {},
  });

  // Shells should be denied even if in allowlist
  const shells = ["bash", "sh", "zsh", "fish", "cmd", "powershell", "pwsh"];
  for (const shell of shells) {
    const result = gate.checkPermission(
      "test-server",
      "system",
      "subprocess",
      "execute",
      {
        command: `${shell} -c "echo hi"`,
      }
    );
    Assert.equal(result.allowed, false, `Should deny shell: ${shell}`);
  }
});

// ============================================================================
// Browser Capability Tests
// ============================================================================

add_task(async function test_browser_tabs_permission() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", {
    level: "custom",
    system: {
      filesystem: { enabled: false },
      network: { enabled: false },
      subprocess: { enabled: false },
      clipboard: { read: false, write: false },
      notifications: { enabled: false },
    },
    browser: {
      tabs: { read: true, navigate: false, create: false, close: false },
      history: { read: false },
      bookmarks: { read: false },
      allowPrivateBrowsing: false,
    },
  });

  // Should allow tabs.read
  let result = gate.checkPermission(
    "test-server",
    "browser",
    "tabs",
    "read",
    {}
  );
  Assert.equal(result.allowed, true, "Should allow tabs.read");

  // Should deny tabs.navigate
  result = gate.checkPermission(
    "test-server",
    "browser",
    "tabs",
    "navigate",
    {}
  );
  Assert.equal(result.allowed, false, "Should deny tabs.navigate");

  // Should deny tabs.create
  result = gate.checkPermission("test-server", "browser", "tabs", "create", {});
  Assert.equal(result.allowed, false, "Should deny tabs.create");
});

add_task(async function test_browser_private_browsing_isolation() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", {
    level: "custom",
    system: {
      filesystem: { enabled: false },
      network: { enabled: false },
      subprocess: { enabled: false },
      clipboard: { read: false, write: false },
      notifications: { enabled: false },
    },
    browser: {
      tabs: { read: true },
      history: { read: true },
      bookmarks: { read: true },
      allowPrivateBrowsing: false, // Explicitly denied
    },
  });

  // Should allow regular tab access
  let result = gate.checkPermission("test-server", "browser", "tabs", "read", {
    isPrivate: false,
  });
  Assert.equal(result.allowed, true, "Should allow regular tab access");

  // Should deny private tab access
  result = gate.checkPermission("test-server", "browser", "tabs", "read", {
    isPrivate: true,
  });
  Assert.equal(result.allowed, false, "Should deny private tab access");
  Assert.ok(
    result.reason.includes("Private browsing"),
    "Should mention private browsing"
  );
});

add_task(async function test_browser_private_browsing_allowed() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  store.save("test-server", {
    level: "custom",
    system: {
      filesystem: { enabled: false },
      network: { enabled: false },
      subprocess: { enabled: false },
      clipboard: { read: false, write: false },
      notifications: { enabled: false },
    },
    browser: {
      tabs: { read: true },
      history: { read: true },
      bookmarks: { read: true },
      allowPrivateBrowsing: true, // Explicitly allowed
    },
  });

  // Should allow private tab access when permitted
  const result = gate.checkPermission(
    "test-server",
    "browser",
    "tabs",
    "read",
    {
      isPrivate: true,
    }
  );
  Assert.equal(
    result.allowed,
    true,
    "Should allow private tab access when permitted"
  );
});

// ============================================================================
// Cache Tests
// ============================================================================

add_task(async function test_profile_caching() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  // Save initial profile
  store.save("test-server", createFilesystemProfile(["/home/user/v1"]));

  // First check should load and cache
  let result = gate.checkPermission(
    "test-server",
    "system",
    "filesystem",
    "read",
    {
      path: "/home/user/v1/file.txt",
    }
  );
  Assert.equal(result.allowed, true, "Should allow with initial profile");

  // Update profile in store
  store.save("test-server", createFilesystemProfile(["/home/user/v2"]));

  // Should still use cached profile
  result = gate.checkPermission("test-server", "system", "filesystem", "read", {
    path: "/home/user/v1/file.txt",
  });
  Assert.equal(result.allowed, true, "Should still use cached profile");

  // After invalidation, should use new profile
  gate.invalidateCache("test-server");

  result = gate.checkPermission("test-server", "system", "filesystem", "read", {
    path: "/home/user/v1/file.txt",
  });
  Assert.equal(
    result.allowed,
    false,
    "Should deny with new profile after invalidation"
  );

  result = gate.checkPermission("test-server", "system", "filesystem", "read", {
    path: "/home/user/v2/file.txt",
  });
  Assert.equal(
    result.allowed,
    true,
    "Should allow new path after invalidation"
  );
});

// ============================================================================
// Edge Case Tests
// ============================================================================

add_task(async function test_unknown_capability_category() {
  const gate = new CapabilityGate(new MockProfileStore());

  const result = gate.checkPermission(
    "test-server",
    "unknown",
    "something",
    "read",
    {}
  );
  Assert.equal(result.allowed, false, "Should deny unknown category");
  Assert.ok(
    result.reason.includes("Unknown"),
    "Should mention unknown category"
  );
});

add_task(async function test_unknown_system_capability() {
  const gate = new CapabilityGate(new MockProfileStore());

  const result = gate.checkPermission(
    "test-server",
    "system",
    "unknown_cap",
    "read",
    {}
  );
  Assert.equal(result.allowed, false, "Should deny unknown capability");
});

add_task(async function test_glob_pattern_complexity_limit() {
  const store = new MockProfileStore();
  const gate = new CapabilityGate(store);

  // Create profile with complex glob pattern (should be rejected internally)
  const complexPattern = "/**" + "/*".repeat(50);
  store.save("test-server", createFilesystemProfile([complexPattern]));

  // Should handle gracefully (pattern rejected as too complex)
  const result = gate.checkPermission(
    "test-server",
    "system",
    "filesystem",
    "read",
    {
      path: "/some/very/long/nested/path/file.txt",
    }
  );
  // The complex pattern should fail to match, so access should be denied
  Assert.equal(
    result.allowed,
    false,
    "Should handle complex patterns gracefully"
  );
});
