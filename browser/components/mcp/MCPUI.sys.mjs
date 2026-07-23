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
  MCPSessions: "moz-src:///browser/components/mcp/MCPSessions.sys.mjs",
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

async function handOffTab(tab) {
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

  const session = MCPServer.session;
  const running = MCPServer.running && !!session;
  const scoped = running && MCPServer.scoped;
  let state = "stopped";
  if (running) {
    state = session.state === "paused" ? "paused" : "active";
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
      handOffTab(doc.defaultView.gBrowser.selectedTab).catch(e =>
        console.error("MCPUI: handoff failed", e)
      )
    );
    addButton("Start (full browser)", () =>
      MCPServer.start().catch(e => console.error("MCPUI: start failed", e))
    );
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

  addLabel("Connection");
  addValue(`http://127.0.0.1:${MCPServer.port}/mcp`, "mcp-value mcp-mono");
  addValue(`Bearer ${session.token.slice(0, 8)}…`, "mcp-value mcp-mono");
  addButton(
    "Copy connection details",
    btn => {
      copyString(
        `http://127.0.0.1:${MCPServer.port}/mcp\nAuthorization: Bearer ${session.token}`
      );
      btn.setAttribute("label", "Copied");
      doc.defaultView.setTimeout(
        () => btn.setAttribute("label", "Copy connection details"),
        1500
      );
    },
    { repopulate: false }
  );

  addSeparator();

  if (state === "paused") {
    addButton("Resume", () => lazy.MCPSessions.resume(session));
  } else {
    addButton("Pause", () => lazy.MCPSessions.pause(session));
  }
  addButton(scoped ? "Revoke tab access" : "Stop server", () => revoke());
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
        // Repaint on session updates (client connect, activity, pause) while
        // the panel stays open.
        const listener = () => populatePanel(panelview);
        lazy.MCPSessions.addListener(listener);
        panelview.addEventListener(
          "ViewHiding",
          () => lazy.MCPSessions.removeListener(listener),
          { once: true }
        );
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
