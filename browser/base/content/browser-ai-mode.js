/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

"use strict";

/**
 * Firefox AI Mode Implementation
 * This module provides the AI Mode interface matching the Figma design
 */
var AIMode = {
  _initialized: false,
  _aiModeActive: false,
  _sidebarWasOpen: false,
  _sidebarCommand: null,
  SESSION_STORE_KEY: "ai-mode-active",
  
  /**
   * Initialize AI Mode functionality
   */
  init() {
    if (this._initialized) {
      return;
    }
    
    this._initialized = true;
    
    // Enable AI Mode feature
    document.documentElement.setAttribute("ai-mode-enabled", "true");
    
    // Initialize toggle button
    this.initToggleButton();
    
    // Initialize AI Mode interface
    this.initAIModeInterface();
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Restore AI Mode state from session storage
    this.restoreState();
    
    console.log("AI Mode initialized");
  },
  
  /**
   * Save AI Mode state to session storage
   */
  saveState() {
    try {
      // SessionStore is available as a global from browser.js
      console.log(`[AI Mode] Saving state: ${this._aiModeActive}`);
      SessionStore.setCustomWindowValue(window, this.SESSION_STORE_KEY, String(this._aiModeActive));
      
      // Verify it was saved
      const verifyState = SessionStore.getCustomWindowValue(window, this.SESSION_STORE_KEY);
      console.log(`[AI Mode] Verified saved state: ${verifyState}`);
    } catch (e) {
      console.error("[AI Mode] Failed to save state:", e);
    }
  },
  
  /**
   * Restore AI Mode state from session storage
   */
  restoreState() {
    try {
      console.log("[AI Mode] Attempting to restore state...");
      
      // SessionStore is available as a global from browser.js
      const savedState = SessionStore.getCustomWindowValue(window, this.SESSION_STORE_KEY);
      console.log(`[AI Mode] Found saved state: "${savedState}"`);
      
      if (savedState === "true") {
        // Restore AI Mode if it was previously active
        console.log("[AI Mode] Restoring AI Mode from session storage");
        this.toggleAIMode(true); // Pass true to skip saving during restore
      } else {
        console.log("[AI Mode] No active state to restore");
      }
    } catch (e) {
      // It's normal for this to fail if there's no saved state
      console.log("[AI Mode] Error during restore:", e.message);
    }
  },
  
  /**
   * Initialize the toggle button in the tab bar
   */
  initToggleButton() {
    const tabsToolbar = document.getElementById("TabsToolbar");
    const toggleButton = document.getElementById("ai-mode-toggle");
    
    if (!toggleButton && tabsToolbar) {
      // Button should already be included via the .inc.xhtml file
      // but if not, we could create it dynamically here
    }
  },
  
  /**
   * Initialize the AI Mode search interface
   */
  initAIModeInterface() {
    const container = document.getElementById("ai-mode-container");
    if (!container) {
      console.error("AI Mode container not found");
      return;
    }
    
    // Initially hidden
    container.style.display = "none";
  },
  
  /**
   * Set up all event listeners
   */
  setupEventListeners() {
    // Toggle button
    const toggleButton = document.getElementById("ai-mode-toggle");
    if (toggleButton) {
      toggleButton.addEventListener("click", () => this.toggleAIMode());
    }
    
    // Search input
    const searchInput = document.getElementById("ai-mode-input");
    if (searchInput) {
      searchInput.addEventListener("keydown", (e) => this.handleSearchInput(e));
      searchInput.addEventListener("focus", () => this.handleInputFocus());
    }
    
    // Ask button
    const askButton = document.getElementById("ai-mode-ask-button");
    if (askButton) {
      askButton.addEventListener("click", () => this.handleAskButton());
    }
    
    // Mic button
    const micButton = document.getElementById("ai-mode-mic");
    if (micButton) {
      micButton.addEventListener("click", () => this.handleMicButton());
    }
    
    // Add button
    const addButton = document.getElementById("ai-mode-add-button");
    if (addButton) {
      addButton.addEventListener("click", () => this.handleAddButton());
    }
    
    // Suggestion buttons
    const suggestions = document.querySelectorAll(".ai-mode-suggestion");
    suggestions.forEach(suggestion => {
      suggestion.addEventListener("click", (e) => this.handleSuggestion(e));
    });
    
    // Listen for tab switches to manage sidebar visibility
    if (gBrowser) {
      gBrowser.tabContainer.addEventListener("TabSelect", (e) => this.handleTabSwitch(e));
    }
  },
  
  /**
   * Handle tab switch events
   */
  handleTabSwitch(event) {
    if (!this._aiModeActive) {
      return;
    }
    
    const selectedTab = event.target;
    const isFirefoxView = selectedTab === FirefoxViewHandler?.tab;
    const container = document.getElementById("ai-mode-container");
    const navBar = document.getElementById("nav-bar");
    
    if (isFirefoxView) {
      // Switching to Firefox View - show AI Mode UI and close sidebar
      if (container) {
        container.style.display = "flex";
      }
      
      // Hide normal URL bar
      if (navBar) {
        navBar.style.display = "none";
      }
      
      // Close sidebar for Firefox View
      this.saveSidebarState();
      this.closeSidebar();
      
      // Focus the AI Mode input
      const input = document.getElementById("ai-mode-input");
      if (input) {
        setTimeout(() => input.focus(), 100);
      }
      
      console.log("[AI Mode] Switched to Firefox View - AI Mode UI shown, sidebar closed");
    } else {
      // Switching to regular tab - hide AI Mode UI and restore normal UI
      if (container) {
        container.style.display = "none";
      }
      
      // Restore normal toolbar
      if (navBar) {
        navBar.style.display = "";
      }
      
      // Restore sidebar if it was open
      this.restoreSidebarState();
      
      console.log("[AI Mode] Switched to regular tab - AI Mode UI hidden, normal UI restored");
    }
  },
  
  /**
   * Toggle AI Mode on/off
   * @param {boolean} skipSave - Skip saving state (used during restore)
   */
  toggleAIMode(skipSave = false) {
    this._aiModeActive = !this._aiModeActive;
    
    const root = document.documentElement;
    const container = document.getElementById("ai-mode-container");
    const toggleButton = document.getElementById("ai-mode-toggle");
    
    if (this._aiModeActive) {
      // Activate AI Mode
      root.setAttribute("ai-mode", "true");
      toggleButton?.setAttribute("checked", "true");
      
      // Show AI Mode interface
      if (container) {
        container.style.display = "flex";
      }
      
      // Hide the normal toolbar
      const navBar = document.getElementById("nav-bar");
      if (navBar) {
        navBar.style.display = "none";
      }
      
      // Open Firefox View
      this.openFirefoxView();
      
      // Focus the AI Mode input
      const input = document.getElementById("ai-mode-input");
      if (input) {
        setTimeout(() => input.focus(), 100);
      }
      
      console.log("AI Mode activated");
      
      // Save the state unless we're restoring
      if (!skipSave) {
        this.saveState();
      }
    } else {
      // Deactivate AI Mode using the dedicated exit method
      this.exitAIMode();
      
      // Skip saving if we're restoring (exitAIMode already saves)
      if (skipSave) {
        // Restore the saved state flag since exitAIMode would have saved
        this._aiModeActive = false;
      }
    }
  },
  
  /**
   * Open Firefox View tab
   */
  openFirefoxView() {
    // Save sidebar state before closing
    this.saveSidebarState();
    
    // Use FirefoxViewHandler to open Firefox View properly
    if (typeof FirefoxViewHandler !== "undefined") {
      // Check if Firefox View tab already exists
      if (FirefoxViewHandler.tab) {
        // Switch to existing Firefox View tab
        gBrowser.selectedTab = FirefoxViewHandler.tab;
      } else {
        // Open Firefox View using the handler
        FirefoxViewHandler.openTab();
      }
    } else {
      // Fallback: click the Firefox View button
      const firefoxViewButton = document.getElementById("firefox-view-button");
      if (firefoxViewButton) {
        firefoxViewButton.click();
      }
    }
    
    // Close sidebar when in Firefox View
    this.closeSidebar();
  },
  
  /**
   * Save the current sidebar state
   */
  saveSidebarState() {
    if (typeof SidebarController !== "undefined" && SidebarController.isOpen) {
      this._sidebarWasOpen = true;
      this._sidebarCommand = SidebarController.currentID;
      console.log(`[AI Mode] Saved sidebar state: ${this._sidebarCommand}`);
    } else {
      this._sidebarWasOpen = false;
      this._sidebarCommand = null;
    }
  },
  
  /**
   * Close the sidebar
   */
  closeSidebar() {
    if (typeof SidebarController !== "undefined" && SidebarController.isOpen) {
      SidebarController.hide();
      console.log("[AI Mode] Closed sidebar for Firefox View");
    }
  },
  
  /**
   * Restore the sidebar state
   */
  restoreSidebarState() {
    if (this._sidebarWasOpen && this._sidebarCommand && typeof SidebarController !== "undefined") {
      console.log(`[AI Mode] Restoring sidebar: ${this._sidebarCommand}`);
      SidebarController.show(this._sidebarCommand);
      this._sidebarWasOpen = false;
      this._sidebarCommand = null;
    }
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
      this.toggleAIMode();
    }
  },
  
  /**
   * Handle input focus
   */
  handleInputFocus() {
    const container = document.getElementById("ai-mode-searchbar");
    if (container) {
      container.classList.add("focused");
    }
  },
  
  /**
   * Handle Ask button click
   */
  handleAskButton() {
    this.performSearch();
  },
  
  /**
   * Perform the AI search/query
   */
  performSearch() {
    const input = document.getElementById("ai-mode-input");
    const query = input?.value?.trim();
    
    if (!query) {
      return;
    }
    
    console.log("AI Mode search:", query);
    
    // Store the query for the sidebar to use
    this._currentQuery = query;
    
    // Exit AI Mode first to restore normal Firefox UI
    // This will restore the URL bar and toolbar
    if (this._aiModeActive) {
      this.exitAIMode();
    }
    
    // Open a new tab (regular new tab, not Firefox View)
    const newTab = gBrowser.addTrustedTab("about:newtab");
    gBrowser.selectedTab = newTab;
    
    // Open the sidebar after a short delay to ensure the tab is ready
    setTimeout(() => {
      this.openAISidebar(query);
    }, 100);
  },
  
  /**
   * Exit AI Mode and restore normal UI
   */
  exitAIMode() {
    if (!this._aiModeActive) {
      return;
    }
    
    const root = document.documentElement;
    const container = document.getElementById("ai-mode-container");
    const toggleButton = document.getElementById("ai-mode-toggle");
    
    // Mark as inactive
    this._aiModeActive = false;
    
    // Remove AI Mode attributes
    root.removeAttribute("ai-mode");
    toggleButton?.removeAttribute("checked");
    
    // Hide AI Mode interface
    if (container) {
      container.style.display = "none";
    }
    
    // Restore the normal toolbar
    const navBar = document.getElementById("nav-bar");
    if (navBar) {
      navBar.style.display = "";
    }
    
    console.log("AI Mode exited, UI restored");
    
    // Save the state
    this.saveState();
  },
  
  /**
   * Open the AI sidebar with the query
   */
  openAISidebar(query) {
    try {
      // Try to open the AI chat sidebar
      console.log(`[AI Mode] Opening sidebar with query: "${query}"`);
      
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
            const event = new sidebar.contentWindow.CustomEvent("ai-mode-query", {
              detail: { 
                query: query,
                source: "ai-mode"
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
        console.error("[AI Mode] SidebarController not available");
      }
    } catch (e) {
      console.error("[AI Mode] Error opening sidebar:", e);
      // Fallback: open bookmarks sidebar
      try {
        SidebarController.toggle("viewBookmarksSidebar");
      } catch (fallbackError) {
        console.error("[AI Mode] Fallback sidebar also failed:", fallbackError);
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
    const text = button.querySelector(".ai-mode-suggestion-text")?.textContent;
    
    console.log("Suggestion clicked:", action, text);
    
    // Set the input value to the suggestion text
    const input = document.getElementById("ai-mode-input");
    if (input && text) {
      input.value = text;
      input.focus();
      
      // Optionally auto-submit
      setTimeout(() => this.performSearch(), 100);
    }
  },
  
  /**
   * Shutdown AI Mode
   */
  shutdown() {
    // Save state before shutdown
    this.saveState();
    
    // Clean up event listeners
    if (gBrowser) {
      gBrowser.tabContainer.removeEventListener("TabSelect", (e) => this.handleTabSwitch(e));
    }
    
    // Restore sidebar if needed
    this.restoreSidebarState();
    
    // Clean up and restore original state
    this._aiModeActive = false;
    document.documentElement.removeAttribute("ai-mode");
    document.documentElement.removeAttribute("ai-mode-enabled");
    
    const container = document.getElementById("ai-mode-container");
    if (container) {
      container.style.display = "none";
    }
    
    console.log("AI Mode shutdown");
  }
};

// Initialize when the browser window loads
window.addEventListener("load", () => {
  // Delay initialization slightly to ensure all elements are ready
  setTimeout(() => AIMode.init(), 500);
});

// Save state when window is closing
window.addEventListener("unload", () => {
  AIMode.shutdown();
});

// Export for use in other modules if needed
if (typeof module !== "undefined") {
  module.exports = AIMode;
}