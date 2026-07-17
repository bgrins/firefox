/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * Toolbar button + panel for the MCP server (gated on browser.mcp.enabled).
 * Spike-grade UI: raw strings, no fluent.
 */

import { MCPServer } from "moz-src:///browser/components/mcp/MCPServer.sys.mjs";

const lazy = {};
ChromeUtils.defineESModuleGetters(lazy, {
  CustomizableUI:
    "moz-src:///browser/components/customizableui/CustomizableUI.sys.mjs",
});

const WIDGET_ID = "mcp-button";
const PANEL_ID = "PanelUI-mcp";
const AUTOSTART_PREF = "browser.mcp.autostart";

let initialized = false;

function populatePanel(panelview) {
  const doc = panelview.ownerDocument;
  const body = panelview.querySelector(".panel-subview-body");
  while (body.lastChild) {
    body.lastChild.remove();
  }

  const status = doc.createXULElement("description");
  status.style.cssText = "padding: 8px 16px 0; font-weight: 600;";
  status.textContent = MCPServer.running
    ? `MCP server: running (port ${MCPServer.port})`
    : "MCP server: stopped";
  body.appendChild(status);

  const endpoint = doc.createXULElement("description");
  endpoint.style.cssText =
    "padding: 0 16px 4px; font-family: monospace; font-size: 0.85em; user-select: text;";
  endpoint.textContent = MCPServer.running
    ? `http://127.0.0.1:${MCPServer.port}/mcp`
    : " ";
  body.appendChild(endpoint);

  const toggle = doc.createXULElement("toolbarbutton");
  toggle.className = "subviewbutton";
  toggle.setAttribute("label", MCPServer.running ? "Stop" : "Start");
  toggle.addEventListener("command", async () => {
    if (MCPServer.running) {
      MCPServer.stop();
    } else {
      await MCPServer.start().catch(e =>
        console.error("MCPUI: start failed", e)
      );
    }
    populatePanel(panelview);
  });
  body.appendChild(toggle);
}

export const MCPUI = {
  async init() {
    if (initialized) {
      return;
    }
    initialized = true;

    lazy.CustomizableUI.createWidget({
      id: WIDGET_ID,
      type: "view",
      viewId: PANEL_ID,
      label: "MCP Server",
      tooltiptext: "MCP Server",
      defaultArea: lazy.CustomizableUI.AREA_NAVBAR,
      onCreated(node) {
        node.setAttribute("image", "chrome://global/skin/icons/developer.svg");
      },
      onViewShowing(event) {
        populatePanel(event.target);
      },
    });

    if (Services.prefs.getBoolPref(AUTOSTART_PREF, false)) {
      await MCPServer.start().catch(e =>
        console.error("MCPUI: autostart failed", e)
      );
    }
  },

  uninit() {
    if (!initialized) {
      return;
    }
    initialized = false;
    MCPServer.stop();
    lazy.CustomizableUI.destroyWidget(WIDGET_ID);
  },
};
