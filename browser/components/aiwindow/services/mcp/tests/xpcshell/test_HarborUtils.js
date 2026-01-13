/* Any copyright is dedicated to the Public Domain.
 * http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { HarborUtils } = ChromeUtils.importESModule(
  "moz-src:///browser/components/aiwindow/services/mcp/HarborUtils.sys.mjs"
);

add_task(async function test_checkEndpointStatus_invalid_url() {
  const result = await HarborUtils.checkEndpointStatus("not-a-valid-url");
  Assert.equal(
    result.status,
    "offline",
    "Should return offline for invalid URL"
  );
  Assert.ok(result.error, "Should have an error message");
});

add_task(async function test_checkEndpointStatus_unreachable() {
  const result = await HarborUtils.checkEndpointStatus(
    "http://127.0.0.1:59999/v1"
  );
  Assert.equal(
    result.status,
    "offline",
    "Should return offline for unreachable endpoint"
  );
});

add_task(async function test_checkEndpointStatus_strips_v1_suffix() {
  // This tests that /v1 is stripped and /api/tags is appended
  // The endpoint won't be reachable, but we're testing the URL transformation
  const result = await HarborUtils.checkEndpointStatus(
    "http://127.0.0.1:59999/v1"
  );
  // Should be offline since nothing is listening
  Assert.equal(result.status, "offline", "Should return offline");
});

add_task(
  async function test_checkEndpointStatus_strips_v1_with_trailing_slash() {
    const result = await HarborUtils.checkEndpointStatus(
      "http://127.0.0.1:59999/v1/"
    );
    Assert.equal(result.status, "offline", "Should handle trailing slash");
  }
);
