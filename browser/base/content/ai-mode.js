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
  _originalUrlbar: null,
  
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
    
    console.log("AI Mode initialized");
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
  },
  
  /**
   * Toggle AI Mode on/off
   */
  toggleAIMode() {
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
      
      // Hide the normal URL bar
      const navBar = document.getElementById("nav-bar");
      if (navBar) {
        this._originalUrlbar = navBar.style.cssText;
        navBar.style.display = "none";
      }
      
      // If on new tab page, make it transparent
      this.transformNewTabPage(true);
      
      // Open a new tab if not already on one
      const currentTab = gBrowser.selectedTab;
      const currentURI = currentTab.linkedBrowser.currentURI.spec;
      if (!currentURI.startsWith("about:newtab") && !currentURI.startsWith("about:blank")) {
        // Open a new tab to show the AI Mode interface
        gBrowser.selectedTab = gBrowser.addTrustedTab("about:newtab");
      }
      
      // Focus the AI Mode input
      const input = document.getElementById("ai-mode-input");
      if (input) {
        setTimeout(() => input.focus(), 100);
      }
      
      console.log("AI Mode activated");
    } else {
      // Deactivate AI Mode
      root.removeAttribute("ai-mode");
      toggleButton?.removeAttribute("checked");
      
      // Hide AI Mode interface
      if (container) {
        container.style.display = "none";
      }
      
      // Restore the normal URL bar
      const navBar = document.getElementById("nav-bar");
      if (navBar && this._originalUrlbar !== null) {
        navBar.style.cssText = this._originalUrlbar;
      }
      
      // Restore new tab page
      this.transformNewTabPage(false);
      
      console.log("AI Mode deactivated");
    }
  },
  
  /**
   * Transform the new tab page for AI Mode
   */
  transformNewTabPage(enable) {
    // Inject CSS into all new tab pages
    const browsers = gBrowser.browsers;
    browsers.forEach(browser => {
      const uri = browser.currentURI.spec;
      if (uri.startsWith("about:newtab") || uri.startsWith("about:blank")) {
        if (enable) {
          // Inject style to make new tab transparent
          browser.messageManager.loadFrameScript(
            `data:text/javascript,
            content.document.documentElement.style.background = 'transparent';
            content.document.body.style.background = 'transparent';
            const style = content.document.createElement('style');
            style.textContent = \`
              body, html { background: transparent !important; }
              .outer-wrapper { display: none !important; }
              main { display: none !important; }
            \`;
            content.document.head.appendChild(style);
            `,
            false
          );
        } else {
          // Restore new tab page
          browser.messageManager.loadFrameScript(
            `data:text/javascript,
            content.document.documentElement.style.background = '';
            content.document.body.style.background = '';
            const styles = content.document.querySelectorAll('style');
            styles.forEach(style => {
              if (style.textContent.includes('background: transparent !important')) {
                style.remove();
              }
            });
            `,
            false
          );
        }
      }
    });
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
    
    // Here you would integrate with the actual AI backend
    // For now, we'll just perform a regular web search as a placeholder
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
    
    // Open in current tab
    gBrowser.loadURI(Services.io.newURI(searchUrl), {
      triggeringPrincipal: Services.scriptSecurityManager.getSystemPrincipal(),
    });
    
    // Optionally close AI Mode after search
    // this.toggleAIMode();
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
    // Clean up event listeners and restore original state
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

// Export for use in other modules if needed
if (typeof module !== "undefined") {
  module.exports = AIMode;
}