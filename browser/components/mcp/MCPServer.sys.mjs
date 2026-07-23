/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * Lifecycle for the in-browser MCP server: wires the vendored firefox-devtools-mcp
 * bundle (vendor/fdm-core.mjs) to MCPBridge and tracks running state for the UI.
 */

import { setTimeout, clearTimeout } from "resource://gre/modules/Timer.sys.mjs";
import { MCPBridge } from "moz-src:///browser/components/mcp/MCPBridge.sys.mjs";
import {
  configure,
  startMcp,
  DEFAULT_PORT,
} from "moz-src:///browser/components/mcp/vendor/fdm-core.mjs";

const PORT_PREF = "browser.mcp.port";

let configured = false;
let running = false;
let boundPort = null;

export const MCPServer = {
  get running() {
    return running;
  },

  get port() {
    return boundPort;
  },

  // True when the running server is restricted to a single tab.
  get scoped() {
    return MCPBridge.scope !== null;
  },

  async start({ port, scope } = {}) {
    if (running) {
      return boundPort;
    }
    if (!configured) {
      configure({
        bidi: MCPBridge,
        version: Services.appinfo.version,
        setTimeout,
        clearTimeout,
      });
      configured = true;
    }
    if (scope) {
      MCPBridge.setScope(scope);
    } else {
      MCPBridge.clearScope();
    }
    const requested =
      port ?? Services.prefs.getIntPref(PORT_PREF, DEFAULT_PORT);
    try {
      boundPort = await startMcp(requested);
    } catch (e) {
      MCPBridge.clearScope();
      throw e;
    }
    running = true;
    return boundPort;
  },

  stop() {
    MCPBridge.stopServer();
    MCPBridge.clearScope();
    running = false;
  },
};
