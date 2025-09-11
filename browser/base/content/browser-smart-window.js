/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

"use strict";

/**
 * Firefox Smart Window Implementation
 * This module provides the Smart Window interface
 */
var SmartWindow = {
  _initialized: false,
  _smartWindowActive: false,
  _sidebarWasOpen: false,
  _sidebarCommand: null,
  SESSION_STORE_KEY: "smart-window-active",
  
  /**
   * Initialize Smart Window functionality
   */
  init() {
    if (this._initialized) {
      return;
    }
    
    this._initialized = true;
    
    // Initialize toggle button
    this.initToggleButton();
    
    // Initialize Smart Window interface
    this.initSmartWindowInterface();
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Check if this window was opened with Smart Window active from parent window
    let shouldActivateSmartWindow = false;
    
    // Debug logging
    console.log("[Smart Window] Checking window.arguments for Smart Window state");
    console.log("[Smart Window] window.arguments:", window.arguments);
    console.log("[Smart Window] window.arguments length:", window.arguments?.length);
    
    // Check window.arguments[1] for extraOptions property bag
    if (window.arguments && window.arguments.length >= 2 && window.arguments[1]) {
      try {
        const extraOptions = window.arguments[1];
        console.log("[Smart Window] extraOptions:", extraOptions);
        console.log("[Smart Window] extraOptions type:", typeof extraOptions);
        console.log("[Smart Window] Is nsIPropertyBag2?", extraOptions instanceof Ci.nsIPropertyBag2);
        
        // Check if it's a property bag with our Smart Window flag
        if (extraOptions instanceof Ci.nsIPropertyBag2) {
          console.log("[Smart Window] Checking for smartWindowActive key...");
          if (extraOptions.hasKey("smartWindowActive")) {
            const smartWindowActive = extraOptions.getPropertyAsBool("smartWindowActive");
            console.log("[Smart Window] smartWindowActive value:", smartWindowActive);
            if (smartWindowActive) {
              console.log("[Smart Window] New window opened with Smart Window active from parent");
              shouldActivateSmartWindow = true;
            }
          } else {
            console.log("[Smart Window] No smartWindowActive key found in extraOptions");
          }
        }
      } catch (e) {
        console.log("[Smart Window] Error checking window arguments:", e);
      }
    } else {
      console.log("[Smart Window] No extraOptions found in window.arguments[1]");
    }
    
    if (shouldActivateSmartWindow) {
      // Activate Smart Window immediately for proper state
      this._smartWindowActive = true;
      document.documentElement.setAttribute("smart-window", "true");
      
      // Update UI elements
      const toggleButton = document.getElementById("smart-window-toggle");
      toggleButton?.setAttribute("checked", "true");
      
      // Open Firefox View
      this.openFirefoxView();
      
      // Notify all tabs and Firefox View after a brief delay to ensure they're ready
      requestAnimationFrame(() => {
        this.updateNewTabsSmartWindowState(true);
        this.notifyFirefoxViewOfModeChange(true);
        
        // Focus the Smart Window input
        const input = document.getElementById("smart-window-input");
        if (input) {
          setTimeout(() => input.focus(), 100);
        }
      });
      
      console.log("[Smart Window] New window Smart Window activated");
    } else {
      // Otherwise restore Smart Window state from session storage
      this.restoreState();
    }
    
    console.log("Smart Window initialized");
  },
  
  /**
   * Save Smart Window state to session storage
   */
  saveState() {
    try {
      // Check if window is ready for SessionStore
      if (!window.__SSi || !SessionStore) {
        console.log("[Smart Window] SessionStore not ready, skipping save");
        return;
      }
      
      console.log(`[Smart Window] Saving state: ${this._smartWindowActive}`);
      SessionStore.setCustomWindowValue(window, this.SESSION_STORE_KEY, String(this._smartWindowActive));
      
      // Verify it was saved
      const verifyState = SessionStore.getCustomWindowValue(window, this.SESSION_STORE_KEY);
      console.log(`[Smart Window] Verified saved state: ${verifyState}`);
    } catch (e) {
      console.error("[Smart Window] Failed to save state:", e);
    }
  },
  
  /**
   * Restore Smart Window state from session storage
   */
  restoreState() {
    try {
      // Check if SessionStore is ready
      if (!window.__SSi || !SessionStore) {
        console.log("[Smart Window] SessionStore not ready for restore");
        return;
      }
      
      console.log("[Smart Window] Attempting to restore state...");
      
      const savedState = SessionStore.getCustomWindowValue(window, this.SESSION_STORE_KEY);
      console.log(`[Smart Window] Found saved state: "${savedState}"`);
      
      if (savedState === "true") {
        // Restore Smart Window if it was previously active
        console.log("[Smart Window] Restoring Smart Window from session storage");
        this.toggleSmartWindow(true); // Pass true to skip saving during restore
      } else {
        console.log("[Smart Window] No active state to restore");
      }
    } catch (e) {
      // It's normal for this to fail if there's no saved state
      console.log("[Smart Window] Error during restore:", e.message);
    }
  },
  
  /**
   * Initialize the toggle button in the tab bar
   */
  initToggleButton() {
    const tabsToolbar = document.getElementById("TabsToolbar");
    const toggleButton = document.getElementById("smart-window-toggle");
    
    if (toggleButton) {
      // Add click event listener to avoid inline handlers
      toggleButton.addEventListener("command", () => {
        this.toggleSmartWindow();
      });
    }
    
    if (!toggleButton && tabsToolbar) {
      // Button should already be included via the .inc.xhtml file
      // but if not, we could create it dynamically here
    }
  },
  
  /**
   * Initialize the Smart Window search interface
   */
  initSmartWindowInterface() {
    const container = document.getElementById("smart-window-container");
    if (!container) {
      console.error("Smart Window container not found");
      return;
    }
    
    // Initially hidden
    container.style.display = "none";
  },
  
  
  /**
   * Set up all event listeners
   */
  setupEventListeners() {
    // Toggle button is handled by navigator-toolbox.js command event
    
    // Search input
    const searchInput = document.getElementById("smart-window-input");
    if (searchInput) {
      searchInput.addEventListener("keydown", (e) => this.handleSearchInput(e));
      searchInput.addEventListener("focus", () => this.handleInputFocus());
    }
    
    // Ask button
    const askButton = document.getElementById("smart-window-ask-button");
    if (askButton) {
      askButton.addEventListener("click", () => this.handleAskButton());
    }
    
    // Mic button
    const micButton = document.getElementById("smart-window-mic");
    if (micButton) {
      micButton.addEventListener("click", () => this.handleMicButton());
    }
    
    // Add button
    const addButton = document.getElementById("smart-window-add-button");
    if (addButton) {
      addButton.addEventListener("click", () => this.handleAddButton());
    }
    
    // Suggestion buttons
    const suggestions = document.querySelectorAll(".smart-window-suggestion");
    suggestions.forEach(suggestion => {
      suggestion.addEventListener("click", (e) => this.handleSuggestion(e));
    });
    
    // Listen for tab switches to manage sidebar visibility
    if (gBrowser) {
      gBrowser.tabContainer.addEventListener("TabSelect", (e) => this.handleTabSwitch(e));
      
      // Listen for new tabs being opened to update their Smart Window state
      gBrowser.tabContainer.addEventListener("TabOpen", (e) => {
        if (this._smartWindowActive) {
          // Give the tab a moment to load, then update its state
          setTimeout(() => {
            const tab = e.target;
            if (tab.linkedBrowser && tab.linkedBrowser.currentURI) {
              const uri = tab.linkedBrowser.currentURI.spec;
              if (uri.startsWith("about:newtab") || uri.startsWith("about:home")) {
                console.log("[Smart Window] New tab opened, updating state");
                try {
                  const actor = tab.linkedBrowser.browsingContext?.currentWindowGlobal?.getActor("AboutNewTab");
                  if (actor) {
                    actor.sendAsyncMessage("UpdateSmartWindowState", { 
                      smartWindowActive: true 
                    });
                  }
                } catch (e) {
                  console.log("[Smart Window] Error updating new tab:", e);
                }
              }
            }
          }, 100);
        }
      });
    }
  },
  
  /**
   * Handle tab switch events
   */
  handleTabSwitch(event) {
    // No longer manipulating UI on tab switches
    // All browser chrome remains visible at all times
  },
  
  /**
   * Toggle Smart Window on/off
   * @param {boolean} skipSave - Skip saving state (used during restore)
   */
  toggleSmartWindow(skipSave = false) {
    console.log(`[Smart Window] toggleSmartWindow called, current state: ${this._smartWindowActive}, skipSave: ${skipSave}`);
    
    const root = document.documentElement;
    const container = document.getElementById("smart-window-container");
    const toggleButton = document.getElementById("smart-window-toggle");
    
    if (!this._smartWindowActive) {
      // Activate Smart Window
      this._smartWindowActive = true;
      root.setAttribute("smart-window", "true");
      toggleButton?.setAttribute("checked", "true");
      
      // Notify all new tabs about Smart Window state change
      this.updateNewTabsSmartWindowState(true);
      
      // Notify Firefox View to update its content
      this.notifyFirefoxViewOfModeChange(true);
      
      // Show Smart Window interface (though we removed it from the chrome)
      if (container) {
        container.style.display = "flex";
      }
      
      // Don't open Firefox View automatically - let user navigate normally
      
      console.log("Smart Window activated");
      
      // Save the state unless we're restoring
      if (!skipSave) {
        this.saveState();
      }
    } else {
      // Deactivate Smart Window
      this._smartWindowActive = false;
      root.removeAttribute("smart-window");
      toggleButton?.removeAttribute("checked");
      
      // Notify all new tabs about Smart Window state change
      this.updateNewTabsSmartWindowState(false);
      
      // Hide Smart Window interface (though we removed it from the chrome)
      if (container) {
        container.style.display = "none";
      }
      
      // Notify Firefox View to update its content
      this.notifyFirefoxViewOfModeChange(false);
      
      console.log("Smart Window deactivated");
      
      // Save the state unless we're restoring
      if (!skipSave) {
        this.saveState();
      }
    }
  },
  
  /**
   * Open Firefox View tab
   */
  openFirefoxView() {
    // No longer automatically opening Firefox View
    // Users can navigate to it manually if they want
  },
  
  /**
   * Save the current sidebar state
   */
  saveSidebarState() {
    // No longer manipulating sidebar
  },
  
  /**
   * Close the sidebar
   */
  closeSidebar() {
    // No longer manipulating sidebar
  },
  
  /**
   * Restore the sidebar state
   */
  restoreSidebarState() {
    // No longer manipulating sidebar
  },
  
  /**
   * Handle search input keyboard events
   */
  handleSearchInput(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      this.performSearch();
    } else if (event.key === "Escape") {
      event.preventDefault();
      this.toggleSmartWindow();
    }
  },
  
  /**
   * Handle input focus
   */
  handleInputFocus() {
    const container = document.getElementById("smart-window-searchbar");
    if (container) {
      container.classList.add("focused");
    }
  },
  
  /**
   * Handle Ask button click
   */
  handleAskButton() {
    this.performAskAction();
  },
  
  /**
   * Perform the AI search/query from Enter key
   */
  performSearch() {
    const input = document.getElementById("smart-window-input");
    const query = input?.value?.trim();
    
    if (!query) {
      return;
    }
    
    console.log("Smart Window search:", query);
    
    // For now, just log the search - don't exit Smart Window
    // TODO: Implement actual search functionality within Smart Window
  },
  
  /**
   * Handle Ask button - opens new tab with sidebar
   */
  performAskAction() {
    const input = document.getElementById("smart-window-input");
    const query = input?.value?.trim();
    
    if (!query) {
      return;
    }
    
    console.log("Smart Window Ask action:", query);
    
    // Store the query for the sidebar to use
    this._currentQuery = query;
    
    // Open a new tab (will inherit Smart Window state)
    const newTab = gBrowser.addTrustedTab("about:newtab");
    gBrowser.selectedTab = newTab;
    
    // Open the sidebar after a short delay to ensure the tab is ready
    setTimeout(() => {
      this.openAISidebar(query);
    }, 100);
  },
  
  /**
   * Exit Smart Window and restore normal UI
   */
  exitSmartWindow() {
    const root = document.documentElement;
    const container = document.getElementById("smart-window-container");
    const toggleButton = document.getElementById("smart-window-toggle");
    
    // Mark as inactive
    this._smartWindowActive = false;
    
    // Remove Smart Window attributes
    root.removeAttribute("smart-window");
    toggleButton?.removeAttribute("checked");
    
    // Notify all new tabs about Smart Window state change
    this.updateNewTabsSmartWindowState(false);
    
    // Hide Smart Window interface (though we removed it from the chrome)
    if (container) {
      container.style.display = "none";
    }
    
    // Don't need to restore toolbar since we're not hiding it anymore
    
    // Notify Firefox View to update its content
    this.notifyFirefoxViewOfModeChange(false);
    
    console.log("Smart Window exited, UI restored");
    
    // Save the state
    this.saveState();
  },
  
  /**
   * Open the AI sidebar with the query
   */
  openAISidebar(query) {
    try {
      // Try to open the AI chat sidebar
      console.log(`[Smart Window] Opening sidebar with query: "${query}"`);
      
      // Ensure the sidebar is ready
      if (typeof SidebarController !== "undefined") {
        // Open the GenAI chat sidebar
        SidebarController.toggle("viewGenaiChatSidebar");
        
        // Wait for sidebar to load, then pass the query
        setTimeout(() => {
          const sidebar = document.getElementById("sidebar");
          if (sidebar && sidebar.contentWindow) {
            // Try to pass the query to the sidebar
            // The sidebar might listen for this event to populate the input
            const event = new sidebar.contentWindow.CustomEvent("smart-window-query", {
              detail: { 
                query: query,
                source: "smart-window"
              }
            });
            sidebar.contentWindow.dispatchEvent(event);
            
            // Also try to set the value directly if there's an input field
            const inputField = sidebar.contentDocument?.querySelector('input[type="text"], textarea');
            if (inputField) {
              inputField.value = query;
              inputField.dispatchEvent(new Event('input', { bubbles: true }));
            }
          }
        }, 500);
      } else {
        console.error("[Smart Window] SidebarController not available");
      }
    } catch (e) {
      console.error("[Smart Window] Error opening sidebar:", e);
      // Fallback: open bookmarks sidebar
      try {
        SidebarController.toggle("viewBookmarksSidebar");
      } catch (fallbackError) {
        console.error("[Smart Window] Fallback sidebar also failed:", fallbackError);
      }
    }
  },
  
  /**
   * Handle microphone button click
   */
  handleMicButton() {
    console.log("Microphone input requested");
    // Here you would implement voice input functionality
    // This would require WebRTC permissions and speech recognition
  },
  
  /**
   * Handle add button click
   */
  handleAddButton() {
    console.log("Add content requested");
    // Here you would implement file/image/tab addition functionality
    const input = document.createElement("input");
    input.type = "file";
    input.multiple = true;
    input.accept = "image/*,application/pdf,.txt,.doc,.docx";
    input.onchange = (e) => {
      const files = e.target.files;
      console.log("Files selected:", files);
      // Process selected files
    };
    input.click();
  },
  
  /**
   * Handle suggestion button clicks
   */
  handleSuggestion(event) {
    const button = event.currentTarget;
    const action = button.dataset.action;
    const text = button.querySelector(".smart-window-suggestion-text")?.textContent;
    
    console.log("Suggestion clicked:", action, text);
    
    // Set the input value to the suggestion text
    const input = document.getElementById("smart-window-input");
    if (input && text) {
      input.value = text;
      input.focus();
      
      // Optionally auto-submit
      setTimeout(() => this.performSearch(), 100);
    }
  },
  
  /**
   * Notify Firefox View of Smart Window state change
   */
  notifyFirefoxViewOfModeChange(smartWindowActive) {
    // Find the Firefox View tab
    if (FirefoxViewHandler?.tab?.linkedBrowser) {
      try {
        const browser = FirefoxViewHandler.tab.linkedBrowser;
        // Send a message to Firefox View's content
        browser.contentWindow.postMessage({
          type: "smart-window-changed",
          smartWindowActive: smartWindowActive
        }, "*");
        console.log(`[Smart Window] Notified Firefox View of mode change: ${smartWindowActive}`);
      } catch (e) {
        console.error("[Smart Window] Failed to notify Firefox View:", e);
      }
    }
  },
  
  /**
   * Update all new tabs with Smart Window state
   */
  updateNewTabsSmartWindowState(smartWindowActive) {
    console.log(`[Smart Window] Broadcasting Smart Window state to new tabs: ${smartWindowActive}`);
    
    // Send message through the actor system
    for (let tab of gBrowser.tabs) {
      if (tab.linkedBrowser && tab.linkedBrowser.currentURI) {
        const uri = tab.linkedBrowser.currentURI.spec;
        
        // Check for new tab pages (might be about:newtab or about:home)
        if (uri.startsWith("about:newtab") || uri.startsWith("about:home")) {
          console.log(`[Smart Window] Found new tab to update: ${uri}`);
          try {
            // Get the actor for this tab
            const actor = tab.linkedBrowser.browsingContext?.currentWindowGlobal?.getActor("AboutNewTab");
            if (actor) {
              // Send message through the actor
              actor.sendAsyncMessage("UpdateSmartWindowState", { 
                smartWindowActive 
              });
              console.log("[Smart Window] Sent UpdateSmartWindowState message to tab actor");
            } else {
              console.log("[Smart Window] No AboutNewTab actor found for tab");
            }
          } catch (e) {
            console.log("[Smart Window] Error updating tab:", e);
          }
        }
      }
    }
  },
  
  /**
   * Shutdown Smart Window
   */
  shutdown() {
    // Save state before shutdown
    this.saveState();
    
    // Clean up event listeners
    if (gBrowser) {
      gBrowser.tabContainer.removeEventListener("TabSelect", (e) => this.handleTabSwitch(e));
    }
    
    // Restore OpenBrowserWindow if we overrode it
    if (window.OpenBrowserWindow && window.OpenBrowserWindow.originalFunction) {
      window.OpenBrowserWindow = window.OpenBrowserWindow.originalFunction;
    }
    
    // Restore sidebar if needed
    this.restoreSidebarState();
    
    // Clean up and restore original state
    this._smartWindowActive = false;
    document.documentElement.removeAttribute("smart-window");
    
    const container = document.getElementById("smart-window-container");
    if (container) {
      container.style.display = "none";
    }
    
    console.log("Smart Window shutdown");
  }
};

// Initialize when the browser window loads
window.addEventListener("load", () => {
  // Delay initialization slightly to ensure all elements are ready
  setTimeout(() => SmartWindow.init(), 500);
});

// Save state when window is closing
window.addEventListener("unload", () => {
  SmartWindow.shutdown();
});

// Export for use in other modules if needed
if (typeof module !== "undefined") {
  module.exports = SmartWindow;
}