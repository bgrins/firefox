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
  MCPAuth: "moz-src:///browser/components/mcp/MCPAuth.sys.mjs",
  MCPSessions: "moz-src:///browser/components/mcp/MCPSessions.sys.mjs",
  NavigableManager: "chrome://remote/content/shared/NavigableManager.sys.mjs",
});

const WIDGET_ID = "mcp-button";
const PANEL_ID = "PanelUI-mcp";
const MENUITEM_ID = "context_mcpHandoff";
const STYLE_ID = "mcp-handoff-style";
const AUTOSTART_PREF = "browser.mcp.autostart";
const AUTH_PREF = "browser.mcp.auth";
const HANDOFF_ATTR = "mcp-handoff";
const HAND_OFF_LABEL = "Hand Off Tab to Agent";
const REVOKE_LABEL = "Revoke Agent Access to Tab";

let initialized = false;
let handoffTab = null;
// Tab preselected for the next OAuth consent (set from the context menu).
let preferredTab = null;

function onHandoffTabClose(event) {
  if (event.target === handoffTab) {
    revoke();
  }
}

function badgeTab(tab) {
  unbadgeTab();
  handoffTab = tab;
  tab.setAttribute(HANDOFF_ATTR, "true");
  tab.addEventListener("TabClose", onHandoffTabClose);
}

function unbadgeTab() {
  if (handoffTab) {
    handoffTab.removeAttribute(HANDOFF_ATTR);
    handoffTab.removeEventListener("TabClose", onHandoffTabClose);
    handoffTab = null;
  }
}

function tabForNavigableId(id) {
  for (const win of Services.wm.getEnumerator("navigator:browser")) {
    for (const tab of win.gBrowser?.tabs ?? []) {
      if (lazy.NavigableManager.getIdForBrowser(tab.linkedBrowser) === id) {
        return tab;
      }
    }
  }
  return null;
}

// Badge state follows the session registry so grants made through the OAuth
// consent flow badge the tab exactly like menu-initiated handoffs.
function onSessionEvent(type, session) {
  if (type === "created") {
    unbadgeTab();
    if (session.scope) {
      const tab = tabForNavigableId(session.scope);
      if (tab) {
        badgeTab(tab);
      }
    }
  } else if (type === "updated" && session.state === "revoked") {
    unbadgeTab();
  }
}

// Surface incoming authorization requests by opening the management panel in
// the most recent browser window.
function onAuthEvent(type) {
  if (type !== "pending") {
    return;
  }
  const win = Services.wm.getMostRecentBrowserWindow();
  if (!win) {
    return;
  }
  try {
    const node = lazy.CustomizableUI.getWidget(WIDGET_ID)?.forWindow(win)?.node;
    if (node) {
      win.PanelUI.showSubView(PANEL_ID, node);
    }
  } catch (e) {
    console.error("MCPUI: failed to open panel for auth request", e);
  }
}

function revoke() {
  unbadgeTab();
  if (MCPServer.authMode === "oauth" && MCPServer.running) {
    // Keep the server up: the client gets 401 and can re-run the OAuth flow.
    MCPServer.revokeSession();
  } else {
    MCPServer.stop();
  }
}

async function handOffTab(tab) {
  const scope = lazy.NavigableManager.getIdForBrowser(tab.linkedBrowser);
  if (!scope) {
    console.error("MCPUI: could not resolve navigable id for tab");
    return;
  }
  if (MCPServer.authMode === "oauth") {
    preferredTab = tab;
    if (!MCPServer.running) {
      await MCPServer.start({ scope }).catch(e =>
        console.error("MCPUI: start failed", e)
      );
      return;
    }
    const [request] = lazy.MCPAuth.pendingRequests;
    if (request) {
      lazy.MCPAuth.approve(request.id, scope);
    }
    return;
  }
  if (MCPServer.running) {
    MCPServer.stop();
  }
  try {
    await MCPServer.start({ scope });
  } catch (e) {
    console.error("MCPUI: handoff failed", e);
    MCPServer.stop();
  }
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
    }
    #${PANEL_ID} {
      min-width: 300px;
    }
    #${PANEL_ID} .panel-subview-body {
      padding-block: 6px 4px;
    }
    .mcp-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 16px;
    }
    .mcp-title {
      font-weight: 600;
    }
    .mcp-status {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.8em;
      font-weight: 600;
      padding: 2px 10px;
      border-radius: 12px;
      background: color-mix(in srgb, currentColor 8%, transparent);
    }
    .mcp-status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: color-mix(in srgb, currentColor 40%, transparent);
    }
    .mcp-status[data-state="active"] .mcp-status-dot {
      background-color: light-dark(#017a40, #4dbc87);
    }
    .mcp-status[data-state="paused"] .mcp-status-dot {
      background-color: light-dark(#c46a00, #ffbd4f);
    }
    .mcp-section-label {
      padding: 8px 16px 2px;
      font-size: 0.72em;
      font-weight: 600;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      opacity: 0.65;
    }
    .mcp-value {
      padding: 0 16px 4px;
      margin: 0;
    }
    .mcp-mono {
      font-family: monospace;
      font-size: 0.85em;
      user-select: text;
    }
    .mcp-dim {
      opacity: 0.65;
      font-style: italic;
    }
    .mcp-tab-row {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .mcp-tab-row > img {
      width: 16px;
      height: 16px;
      flex-shrink: 0;
    }
    .mcp-tab-row > span {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
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

function relativeTime(ts) {
  const seconds = Math.max(0, Math.round((Date.now() - ts) / 1000));
  return seconds < 60 ? `${seconds}s ago` : `${Math.round(seconds / 60)}m ago`;
}

function copyString(text) {
  Cc["@mozilla.org/widget/clipboardhelper;1"]
    .getService(Ci.nsIClipboardHelper)
    .copyString(text);
}

function populatePanel(panelview) {
  const doc = panelview.ownerDocument;
  const body = panelview.querySelector(".panel-subview-body");
  while (body.lastChild) {
    body.lastChild.remove();
  }

  const addSeparator = () =>
    body.appendChild(doc.createXULElement("toolbarseparator"));
  const addLabel = text => {
    const el = doc.createElement("div");
    el.className = "mcp-section-label";
    el.textContent = text;
    body.appendChild(el);
  };
  const addValue = (text, className = "mcp-value") => {
    const el = doc.createXULElement("description");
    el.className = className;
    el.textContent = text;
    body.appendChild(el);
  };
  const addButton = (label, command, { repopulate = true } = {}) => {
    const btn = doc.createXULElement("toolbarbutton");
    btn.className = "subviewbutton";
    btn.setAttribute("label", label);
    btn.addEventListener("command", async () => {
      await command(btn);
      if (repopulate) {
        populatePanel(panelview);
      }
    });
    body.appendChild(btn);
    return btn;
  };

  const addEndpoint = () => {
    addLabel("Connection");
    addValue(`http://127.0.0.1:${MCPServer.port}/mcp`, "mcp-value mcp-mono");
    if (MCPServer.authMode === "oauth") {
      addValue(
        "Clients authenticate via OAuth — approve requests here.",
        "mcp-value mcp-dim"
      );
    } else {
      addValue("Authentication disabled.", "mcp-value mcp-dim");
    }
    addButton(
      "Copy endpoint",
      btn => {
        copyString(`http://127.0.0.1:${MCPServer.port}/mcp`);
        btn.setAttribute("label", "Copied");
        doc.defaultView.setTimeout(
          () => btn.setAttribute("label", "Copy endpoint"),
          1500
        );
      },
      { repopulate: false }
    );
  };

  const session = MCPServer.session;
  const running = MCPServer.running;
  const scoped = running && MCPServer.scoped;
  let state = "stopped";
  if (running) {
    if (!session) {
      state = "waiting";
    } else {
      state = session.state === "paused" ? "paused" : "active";
    }
  }

  const header = doc.createElement("div");
  header.className = "mcp-header";
  const title = doc.createElement("span");
  title.className = "mcp-title";
  title.textContent = "MCP Server";
  const status = doc.createElement("span");
  status.className = "mcp-status";
  status.dataset.state = state;
  const dot = doc.createElement("span");
  dot.className = "mcp-status-dot";
  const stateText = doc.createElement("span");
  stateText.textContent = {
    stopped: "Stopped",
    waiting: "Waiting",
    paused: "Paused",
    active: "Active",
  }[state];
  status.append(dot, stateText);
  header.append(title, status);
  body.appendChild(header);

  if (!running) {
    addValue(
      "Hand off the current tab, or expose the full browser to a local MCP agent.",
      "mcp-value mcp-dim"
    );
    addSeparator();
    addButton("Start (this tab)", () =>
      handOffTab(doc.defaultView.gBrowser.selectedTab)
    );
    addButton("Start (full browser)", () =>
      MCPServer.start().catch(e => console.error("MCPUI: start failed", e))
    );
    addSeparator();
    const check = doc.createXULElement("checkbox");
    check.className = "mcp-value";
    check.setAttribute("label", "Require authorization (OAuth)");
    check.setAttribute("checked", MCPServer.authMode === "oauth");
    check.addEventListener("command", () => {
      Services.prefs.setCharPref(AUTH_PREF, check.checked ? "oauth" : "none");
    });
    body.appendChild(check);
    return;
  }

  const [request] = lazy.MCPAuth.pendingRequests;
  if (request) {
    addSeparator();
    addLabel("Authorization request");
    addValue(`"${request.clientName}" wants to control Firefox`);
    const win = doc.defaultView;
    const target =
      preferredTab && preferredTab.isConnected
        ? preferredTab
        : win.gBrowser.selectedTab;
    addButton(`Grant one tab: ${target.label.slice(0, 40)}`, () =>
      lazy.MCPAuth.approve(
        request.id,
        lazy.NavigableManager.getIdForBrowser(target.linkedBrowser)
      )
    );
    addButton("Grant full browser", () =>
      lazy.MCPAuth.approve(request.id, null)
    );
    addButton("Deny", () => lazy.MCPAuth.deny(request.id));
  }

  if (!session) {
    addSeparator();
    addValue(
      "Waiting for an agent to connect and request access.",
      "mcp-value mcp-dim"
    );
    addSeparator();
    addEndpoint();
    addSeparator();
    addButton("Stop server", () => MCPServer.stop());
    return;
  }

  addSeparator();

  addLabel("Agent");
  const client = session.clientInfo;
  if (client) {
    addValue(`${client.title || client.name} ${client.version}`.trim());
  } else {
    addValue("Waiting for a client to connect", "mcp-value mcp-dim");
  }

  addLabel("Access");
  if (scoped && handoffTab) {
    const row = doc.createElement("div");
    row.className = "mcp-value mcp-tab-row";
    const icon = doc.createElement("img");
    icon.src =
      handoffTab.getAttribute("image") ||
      "chrome://global/skin/icons/defaultFavicon.svg";
    const label = doc.createElement("span");
    label.textContent = handoffTab.label;
    row.append(icon, label);
    body.appendChild(row);
  } else {
    addValue("Full browser");
  }

  addLabel("Last activity");
  const last = session.activity.at(-1);
  if (last) {
    addValue(`${last.label} · ${relativeTime(last.ts)}`);
  } else {
    addValue("None yet", "mcp-value mcp-dim");
  }

  addSeparator();
  addEndpoint();
  addSeparator();

  if (state === "paused") {
    addButton("Resume", () => lazy.MCPSessions.resume(session));
  } else {
    addButton("Pause", () => lazy.MCPSessions.pause(session));
  }
  addButton(scoped ? "Revoke tab access" : "Revoke access", () => revoke());
  if (MCPServer.authMode === "oauth") {
    addButton("Stop server", () => MCPServer.stop());
  }
}

export const MCPUI = {
  handOffTab,
  revoke,

  get handoffTab() {
    return handoffTab;
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
        const panelview = event.target;
        populatePanel(panelview);
        // Repaint on session/auth updates (client connect, activity, pause,
        // consent requests) while the panel stays open.
        const listener = () => populatePanel(panelview);
        lazy.MCPSessions.addListener(listener);
        lazy.MCPAuth.addListener(listener);
        panelview.addEventListener(
          "ViewHiding",
          () => {
            lazy.MCPSessions.removeListener(listener);
            lazy.MCPAuth.removeListener(listener);
          },
          { once: true }
        );
      },
    });

    lazy.EveryWindow.registerCallback(MENUITEM_ID, initWindow, uninitWindow);
    lazy.MCPSessions.addListener(onSessionEvent);
    lazy.MCPAuth.addListener(onAuthEvent);

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
    unbadgeTab();
    preferredTab = null;
    MCPServer.stop();
    lazy.MCPSessions.removeListener(onSessionEvent);
    lazy.MCPAuth.removeListener(onAuthEvent);
    lazy.EveryWindow.unregisterCallback(MENUITEM_ID);
    lazy.CustomizableUI.destroyWidget(WIDGET_ID);
  },
};
