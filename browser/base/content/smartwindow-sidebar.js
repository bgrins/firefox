/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

"use strict";

const { topChromeWindow } = window.browsingContext;

addEventListener("load", () => {
  console.log("[Smart Window Sidebar] Loading");
  setupSmartWindowBrowser();
});

function setupSmartWindowBrowser() {
  console.log("[Smart Window Sidebar] Setting up new tab browser");
  
  const browserContainer = document.getElementById("browser-container");
  
  // Create a browser element to load about:newtab
  const browser = document.createXULElement("browser");
  
  // Set browser attributes - mark it as transparent for smart window mode
  browser.setAttribute("type", "content");
  browser.setAttribute("remote", "true");
  browser.setAttribute("maychangeremoteness", "true");
  browser.setAttribute("disableglobalhistory", "true");
  browser.setAttribute("transparent", "true"); // Enable transparency for smart window
  browser.setAttribute("src", "about:newtab");
  
  // Add browser to container
  browserContainer.appendChild(browser);
  
  // Store reference for messaging
  window.smartWindowBrowser = browser;
  
  // Get the connected tab information
  const smartWindowArgs = topChromeWindow.SidebarController._smartWindowArgs;
  const connectedTab = smartWindowArgs?.connectedTab;
  
  console.log("[Smart Window Sidebar] Smart window args:", smartWindowArgs);
  console.log("[Smart Window Sidebar] Connected tab:", connectedTab?.label, connectedTab?.linkedBrowser?.currentURI?.spec);
  
  // Send smart window state immediately after browser creation
  browser.addEventListener("DOMContentLoaded", () => {
    console.log("[Smart Window Sidebar] DOMContentLoaded fired");
    
    // Set smart-window attribute on the content document
    try {
      const contentDoc = browser.contentDocument;
      if (contentDoc && contentDoc.documentElement) {
        contentDoc.documentElement.setAttribute("smart-window", "true");
        console.log("[Smart Window Sidebar] Set smart-window attribute on content document");
      }
    } catch (e) {
      console.log("[Smart Window Sidebar] Could not access content document:", e);
    }
    
    // Try to get the actor and send smart window state
    const tryToSendMessages = (attempt = 1) => {
      console.log(`[Smart Window Sidebar] Attempt ${attempt} to send messages`);
      
      const actor = browser.browsingContext?.currentWindowGlobal?.getActor("AboutNewTab");
      console.log("[Smart Window Sidebar] Actor available:", !!actor);
      
      if (actor) {
        // First, send smart window state update
        console.log("[Smart Window Sidebar] Sending SMART_WINDOW_STATE_UPDATE");
        actor.receiveMessage({
          name: "ActivityStream:MainToContent",
          data: {
            type: "SMART_WINDOW_STATE_UPDATE",
            data: { smartWindowActive: true }
          }
        });
        
        // Then send connected tab info if available
        if (connectedTab) {
          const tabId = connectedTab.linkedBrowser?.permanentKey?.id || 
                        `tab-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
          
          console.log("[Smart Window Sidebar] Sending SmartWindow:ConnectedTab");
          actor.receiveMessage({
            name: "SmartWindow:ConnectedTab",
            data: {
              tabId: tabId,
              url: connectedTab.linkedBrowser?.currentURI?.spec || "unknown",
              title: connectedTab.label || "Untitled"
            }
          });
        }
      } else if (attempt < 5) {
        // Retry up to 5 times
        setTimeout(() => tryToSendMessages(attempt + 1), 200 * attempt);
      } else {
        console.error("[Smart Window Sidebar] Failed to get actor after 5 attempts");
      }
    };
    
    // Start trying to send messages
    tryToSendMessages();
  }, { once: true });
  
  // Clean up args after use
  if (topChromeWindow.SidebarController._smartWindowArgs) {
    delete topChromeWindow.SidebarController._smartWindowArgs;
  }
}

addEventListener("unload", () => {
  console.log("[Smart Window Sidebar] Unloading");
});