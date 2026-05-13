const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: ".",
  testMatch: ["test-canvas-engine.js", "test-snap-manager.js"],
  timeout: 30000,
  use: {
    baseURL: "http://localhost:9876",
    headless: true,
  },
  webServer: {
    command: "python3 -m http.server 9876",
    port: 9876,
    reuseExistingServer: true,
  },
  projects: [
    { name: "chromium", use: { browserName: "chromium" } },
  ],
});
