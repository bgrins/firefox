/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * Toolbar button + panel for the MCP server (gated on browser.mcp.enabled),
 * plus the tab handoff flow: a tab context menu item that starts the server
 * scoped to a single tab, badges that tab, and supports revocation.
 * Spike-grade UI: raw strings, no fluent.
 */

import { MCPServer } from "moz-src:///browser/components/mcp/MCPServer.sys.mjs";

const lazy = {};
ChromeUtils.defineESModuleGetters(lazy, {
  CustomizableUI:
    "moz-src:///browser/components/customizableui/CustomizableUI.sys.mjs",
  EveryWindow: "resource:///modules/EveryWindow.sys.mjs",
  NavigableManager: "chrome://remote/content/shared/NavigableManager.sys.mjs",
});

const WIDGET_ID = "mcp-button";
const PANEL_ID = "PanelUI-mcp";
const MENUITEM_ID = "context_mcpHandoff";
const STYLE_ID = "mcp-handoff-style";
const AUTOSTART_PREF = "browser.mcp.autostart";
const HANDOFF_ATTR = "mcp-handoff";
const HAND_OFF_LABEL = "Hand Off Tab to Agent";
const REVOKE_LABEL = "Revoke Agent Access to Tab";

let initialized = false;
let handoffTab = null;

function onHandoffTabClose(event) {
  if (event.target === handoffTab) {
    revoke();
  }
}

function revoke() {
  if (handoffTab) {
    handoffTab.removeAttribute(HANDOFF_ATTR);
    handoffTab.removeEventListener("TabClose", onHandoffTabClose);
    handoffTab = null;
  }
  MCPServer.stop();
}

let confirmHandoff = tab =>
  Services.prompt.confirm(
    tab.ownerGlobal,
    "Hand off tab to agent",
    `Allow a local MCP agent to read and control "${tab.label}"?\n\n` +
      "The agent will only see this tab, but it can act as you on any site " +
      "the tab is logged into, until you revoke access from the tab context " +
      "menu or the MCP toolbar panel."
  );

async function handOffTab(tab) {
  if (!confirmHandoff(tab)) {
    return;
  }
  if (handoffTab) {
    revoke();
  } else if (MCPServer.running) {
    MCPServer.stop();
  }
  const scope = lazy.NavigableManager.getIdForBrowser(tab.linkedBrowser);
  if (!scope) {
    console.error("MCPUI: could not resolve navigable id for tab");
    return;
  }
  try {
    await MCPServer.start({ scope });
  } catch (e) {
    console.error("MCPUI: handoff failed", e);
    MCPServer.stop();
    return;
  }
  handoffTab = tab;
  tab.setAttribute(HANDOFF_ATTR, "true");
  tab.addEventListener("TabClose", onHandoffTabClose);
}

function onTabContextShowing(event) {
  const menu = event.currentTarget;
  if (event.target !== menu) {
    return;
  }
  const doc = menu.ownerDocument;
  const item = doc.getElementById(MENUITEM_ID);
  const tab = doc.defaultView.TabContextMenu?.contextTab;
  if (!item || !tab) {
    return;
  }
  item.setAttribute(
    "label",
    tab === handoffTab ? REVOKE_LABEL : HAND_OFF_LABEL
  );
}

function initWindow(win) {
  const doc = win.document;
  const menu = doc.getElementById("tabContextMenu");
  if (!menu || doc.getElementById(MENUITEM_ID)) {
    return;
  }
  const item = doc.createXULElement("menuitem");
  item.id = MENUITEM_ID;
  item.setAttribute("label", HAND_OFF_LABEL);
  item.addEventListener("command", () => {
    const tab = win.TabContextMenu?.contextTab;
    if (!tab) {
      return;
    }
    if (tab === handoffTab) {
      revoke();
    } else {
      handOffTab(tab);
    }
  });
  menu.appendChild(item);
  menu.addEventListener("popupshowing", onTabContextShowing);

  const style = doc.createElement("style");
  style.id = STYLE_ID;
  style.textContent = `
    tab[${HANDOFF_ATTR}] .tab-background {
      outline: 2px dashed var(--focus-outline-color, #0060df);
      outline-offset: -4px;
    }`;
  doc.head.appendChild(style);
}

function uninitWindow(win) {
  const doc = win.document;
  doc.getElementById(MENUITEM_ID)?.remove();
  doc.getElementById(STYLE_ID)?.remove();
  doc
    .getElementById("tabContextMenu")
    ?.removeEventListener("popupshowing", onTabContextShowing);
}

function populatePanel(panelview) {
  const doc = panelview.ownerDocument;
  const body = panelview.querySelector(".panel-subview-body");
  while (body.lastChild) {
    body.lastChild.remove();
  }

  const scoped = MCPServer.running && MCPServer.scoped;

  const status = doc.createXULElement("description");
  status.style.cssText = "padding: 8px 16px 0; font-weight: 600;";
  status.textContent = MCPServer.running
    ? `MCP server: running (port ${MCPServer.port})${scoped ? " — single tab" : " — full browser"}`
    : "MCP server: stopped";
  body.appendChild(status);

  if (scoped && handoffTab) {
    const tabInfo = doc.createXULElement("description");
    tabInfo.style.cssText = "padding: 0 16px;";
    tabInfo.textContent = `Handed off: ${handoffTab.label}`;
    body.appendChild(tabInfo);
  }

  const endpoint = doc.createXULElement("description");
  endpoint.style.cssText =
    "padding: 0 16px 4px; font-family: monospace; font-size: 0.85em; user-select: text;";
  endpoint.textContent = MCPServer.running
    ? `http://127.0.0.1:${MCPServer.port}/mcp`
    : " ";
  body.appendChild(endpoint);

  const toggle = doc.createXULElement("toolbarbutton");
  toggle.className = "subviewbutton";
  let label = "Start (full browser)";
  if (MCPServer.running) {
    label = scoped ? "Revoke tab access" : "Stop";
  }
  toggle.setAttribute("label", label);
  toggle.addEventListener("command", async () => {
    if (MCPServer.running) {
      revoke();
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
  handOffTab,
  revoke,

  get handoffTab() {
    return handoffTab;
  },

  setConfirmForTests(fn) {
    confirmHandoff = fn;
  },

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

    lazy.EveryWindow.registerCallback(MENUITEM_ID, initWindow, uninitWindow);

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
    revoke();
    lazy.EveryWindow.unregisterCallback(MENUITEM_ID);
    lazy.CustomizableUI.destroyWidget(WIDGET_ID);
  },
};
