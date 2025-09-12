/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

"use strict";

var SmartWindow = {
  _initialized: false,
  _smartWindowActive: false,
  SESSION_STORE_KEY: "smart-window-active",

  init() {
    if (this._initialized) {
      return;
    }

    this._initialized = true;

    if (!gSmartWindowEnabled) {
      console.log("[Smart Window] Feature disabled by pref");
      return;
    }

    this.initToggleButton();

    // Check if this window was opened with Smart Window active from parent window
    let shouldActivateSmartWindow = false;

    // Check window.arguments[1] for extraOptions property bag
    if (
      window.arguments &&
      window.arguments.length >= 2 &&
      window.arguments[1]
    ) {
      try {
        const extraOptions = window.arguments[1];
        // Check if it's a property bag with our Smart Window flag
        if (
          extraOptions instanceof Ci.nsIPropertyBag2 &&
          extraOptions.hasKey("smartWindowActive") &&
          extraOptions.getPropertyAsBool("smartWindowActive")
        ) {
          console.log(
            "[Smart Window] New window opened with Smart Window active from parent"
          );
          shouldActivateSmartWindow = true;
        }
      } catch (e) {
        console.log("[Smart Window] Error checking window arguments:", e);
      }
    }

    if (shouldActivateSmartWindow) {
      // Activate Smart Window immediately for proper state
      this._smartWindowActive = true;
      document.documentElement.setAttribute("smart-window", "true");

      // Update UI elements
      const toggleButton = document.getElementById("smart-window-toggle");
      toggleButton?.setAttribute("checked", "true");

      // Notify observers about Smart Window state
      Services.obs.notifyObservers(window, "smart-window-state-changed");

      console.log("[Smart Window] New window Smart Window activated");
    } else {
      // Otherwise restore Smart Window state from session storage
      this.restoreState();
    }

    console.log("Smart Window initialized");
  },

  saveState() {
    try {
      // Check if window is ready for SessionStore and not closing
      if (!window.__SSi || !SessionStore || window.closed) {
        console.log(
          "[Smart Window] Window not ready or closing, skipping save"
        );
        return;
      }

      // Additional check to ensure window is still in SessionStore's tracking
      try {
        // Try to get a value first to check if window is still valid
        SessionStore.getCustomWindowValue(window, this.SESSION_STORE_KEY);
      } catch (e) {
        console.log(
          "[Smart Window] Window no longer tracked by SessionStore, skipping save"
        );
        return;
      }

      console.log(`[Smart Window] Saving state: ${this._smartWindowActive}`);
      SessionStore.setCustomWindowValue(
        window,
        this.SESSION_STORE_KEY,
        String(this._smartWindowActive)
      );
    } catch (e) {
      console.error("[Smart Window] Failed to save state:", e);
    }
  },

  restoreState() {
    try {
      // Check if SessionStore is ready
      if (!window.__SSi || !SessionStore) {
        console.log("[Smart Window] SessionStore not ready for restore");
        return;
      }

      // Only restore state if the feature is enabled
      if (!gSmartWindowEnabled) {
        console.log(
          "[Smart Window] Feature disabled by pref, skipping restore"
        );
        return;
      }

      console.log("[Smart Window] Attempting to restore state...");

      const savedState = SessionStore.getCustomWindowValue(
        window,
        this.SESSION_STORE_KEY
      );
      console.log(`[Smart Window] Found saved state: "${savedState}"`);

      if (savedState === "true") {
        // Restore Smart Window if it was previously active
        console.log(
          "[Smart Window] Restoring Smart Window from session storage"
        );
        this.toggleSmartWindow(true); // Pass true to skip saving during restore
      } else {
        console.log("[Smart Window] No active state to restore");
      }
    } catch (e) {
      // It's normal for this to fail if there's no saved state
      console.log("[Smart Window] Error during restore:", e.message);
    }
  },

  initToggleButton() {
    const toggleButton = document.getElementById("smart-window-toggle");

    if (toggleButton) {
      // Show the button only if the feature is enabled
      if (gSmartWindowEnabled) {
        toggleButton.hidden = false;

        // Add click event listener to the toggle button
        toggleButton.addEventListener("command", () => {
          this.toggleSmartWindow();
        });
      }
    }
  },

  toggleSmartWindow(skipSave = false) {
    console.log(
      `[Smart Window] toggleSmartWindow called, current state: ${this._smartWindowActive}, skipSave: ${skipSave}`
    );

    const root = document.documentElement;
    const toggleButton = document.getElementById("smart-window-toggle");

    if (!this._smartWindowActive) {
      // Activate Smart Window
      this._smartWindowActive = true;
      root.setAttribute("smart-window", "true");
      toggleButton?.setAttribute("checked", "true");

      // Hide bookmarks toolbar immediately
      updateBookmarkToolbarVisibility();

      // Notify observers about Smart Window state change
      Services.obs.notifyObservers(window, "smart-window-state-changed");

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

      // Clean up any smart window sidebar state
      this.cleanupSmartWindowSidebar();

      // Restore bookmarks toolbar visibility based on user preference
      updateBookmarkToolbarVisibility();

      // Notify observers about Smart Window state change
      Services.obs.notifyObservers(window, "smart-window-state-changed");

      console.log("Smart Window deactivated");

      // Save the state unless we're restoring
      if (!skipSave) {
        this.saveState();
      }
    }
  },

  isSmartWindowActive() {
    return this._smartWindowActive;
  },

  handleNewTabNavigation(url, event, where, params, resultDetails, browser) {
    console.log("[Smart Window] Handling new tab navigation to:", url);
    console.log("[Smart Window] Current browser URI:", browser.currentURI?.spec);
    
    // Get the current tab (which has the new tab page)
    const currentTab = gBrowser.selectedTab;
    
    // Create a new tab with the URL
    const newTab = gBrowser.addTab(url, {
      triggeringPrincipal: params.triggeringPrincipal || 
        Services.scriptSecurityManager.getSystemPrincipal(),
      allowThirdPartyFixup: params.allowThirdPartyFixup,
      relatedToCurrent: false, // Not related to preserve clean history
      userContextId: params.userContextId,
      fromExternal: params.fromExternal,
      globalHistoryOptions: params.globalHistoryOptions,
      referrerInfo: params.referrerInfo,
      postData: params.postData,
      allowInheritPrincipal: params.allowInheritPrincipal,
    });
    
    // Switch to the new tab immediately
    gBrowser.selectedTab = newTab;
    
    // Remove the original new tab
    if (currentTab && !currentTab.closing && currentTab.parentNode) {
      gBrowser.removeTab(currentTab, { animate: false });
    }
    
    // Prepare sidebar arguments with the connected tab info
    const sidebarArgs = {
      smartWindowMode: true,
      connectedTab: newTab  // The tab that was navigated to
    };
    
    // Store the args and open sidebar
    SidebarController._smartWindowArgs = sidebarArgs;
    
    // Open the smart window sidebar panel
    SidebarController.show("viewSmartWindowSidebar").then(() => {
      console.log("[Smart Window] Smart window sidebar opened with connected tab:", newTab.label);
    });
  },

  exitSmartWindow() {
    if (this.isSmartWindowActive()) {
      // Clean up any smart window sidebar state
      this.cleanupSmartWindowSidebar();
      this.toggleSmartWindow();
    }
  },
  
  cleanupSmartWindowSidebar() {
    // Clear any pending smart window sidebar args
    if (SidebarController._smartWindowArgs) {
      delete SidebarController._smartWindowArgs;
    }
    
    // If smart window sidebar is open, close it
    if (
      SidebarController.isOpen && 
      SidebarController.currentID === "viewSmartWindowSidebar"
    ) {
      console.log("[Smart Window] Closing smart window sidebar");
      SidebarController.hide();
    }
  },

  shutdown() {
    // Don't save state during shutdown as SessionStore may not be available
    // State is already saved on each toggle

    // Clean up event listeners
    if (gBrowser) {
      const tabContainer = gBrowser.tabContainer;
      // Remove TabOpen listener
      const tabOpenListeners = tabContainer._getListeners?.("TabOpen") || [];
      tabOpenListeners.forEach(listener => {
        if (listener.toString().includes("SmartWindow")) {
          tabContainer.removeEventListener("TabOpen", listener);
        }
      });
    }

    console.log("Smart Window shutdown complete");
  },
};
