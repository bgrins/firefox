/* vim: set ts=2 sw=2 sts=2 et tw=80: */
/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import { XPCOMUtils } from "resource://gre/modules/XPCOMUtils.sys.mjs";
import { AppConstants } from "resource://gre/modules/AppConstants.sys.mjs";
import { PrivateBrowsingUtils } from "resource://gre/modules/PrivateBrowsingUtils.sys.mjs";
import { RemotePageChild } from "resource://gre/actors/RemotePageChild.sys.mjs";

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
  NimbusFeatures: "resource://nimbus/ExperimentAPI.sys.mjs",
});

XPCOMUtils.defineLazyPreferenceGetter(
  lazy,
  "ACTIVITY_STREAM_DEBUG",
  "browser.newtabpage.activity-stream.debug",
  false
);

let gNextPortID = 0;

export class AboutNewTabChild extends RemotePageChild {
  receiveMessage(message) {
    console.log(`[AboutNewTabChild] Received message: ${message.name}`, message.data);
    
    switch (message.name) {
      case "UpdateSmartWindowState":
        console.log("[AboutNewTabChild] Processing UpdateSmartWindowState:", message.data);
        // Notify the content window about Smart Window state change
        if (this.contentWindow) {
          console.log("[AboutNewTabChild] Dispatching smart-window-changed event to content window");
          this.contentWindow.dispatchEvent(
            new this.contentWindow.CustomEvent("smart-window-changed", {
              detail: { active: message.data.smartWindowActive },
            })
          );
        } else {
          console.log("[AboutNewTabChild] No content window available");
        }
        break;
      default:
        console.log(`[AboutNewTabChild] Unhandled message: ${message.name}`);
    }
  }

  handleEvent(event) {
    if (event.type == "DOMDocElementInserted") {
      let portID = Services.appinfo.processID + ":" + ++gNextPortID;

      this.sendAsyncMessage("Init", {
        portID,
        url: this.contentWindow.document.documentURI.replace(/[\#|\?].*$/, ""),
      });
      
      // Check if parent window has Smart Window active and notify content
      console.log("[AboutNewTabChild] Checking initial Smart Window state...");
      try {
        console.log("[AboutNewTabChild] contentWindow:", this.contentWindow);
        console.log("[AboutNewTabChild] windowRoot:", this.contentWindow.windowRoot);
        console.log("[AboutNewTabChild] ownerGlobal:", this.contentWindow.windowRoot?.ownerGlobal);
        
        const chromeWindow = this.contentWindow.windowRoot.ownerGlobal;
        if (chromeWindow) {
          console.log("[AboutNewTabChild] Got chrome window:", chromeWindow);
          console.log("[AboutNewTabChild] Chrome document:", chromeWindow.document);
          console.log("[AboutNewTabChild] Chrome documentElement:", chromeWindow.document?.documentElement);
          
          if (chromeWindow.document && chromeWindow.document.documentElement) {
            const hasSmartWindow = chromeWindow.document.documentElement.hasAttribute("smart-window");
            console.log("[AboutNewTabChild] Chrome window has smart-window attribute:", hasSmartWindow);
            
            if (hasSmartWindow) {
              console.log("[AboutNewTabChild] Parent has Smart Window active, dispatching event");
              this.contentWindow.dispatchEvent(
                new this.contentWindow.CustomEvent("smart-window-changed", {
                  detail: { active: true },
                })
              );
              console.log("[AboutNewTabChild] Event dispatched successfully");
            } else {
              console.log("[AboutNewTabChild] Parent does not have Smart Window active");
            }
          } else {
            console.log("[AboutNewTabChild] Chrome window document not accessible");
          }
        } else {
          console.log("[AboutNewTabChild] No chrome window found");
        }
      } catch (e) {
        console.log("[AboutNewTabChild] Error checking Smart Window state:", e.message, e.stack);
      }
    } else if (event.type == "load") {
      this.sendAsyncMessage("Load");
    } else if (event.type == "DOMContentLoaded") {
      if (!this.contentWindow.document.body.firstElementChild) {
        return; // about:newtab is a blank page
      }

      const debug = !AppConstants.RELEASE_OR_BETA && lazy.ACTIVITY_STREAM_DEBUG;
      const debugString = debug ? "-dev" : "";

      // This list must match any similar ones in render-activity-stream-html.js.
      const scripts = [
        "chrome://browser/content/contentSearchUI.js",
        "chrome://browser/content/contentSearchHandoffUI.js",
        "chrome://browser/content/contentTheme.js",
        `chrome://global/content/vendor/react${debugString}.js`,
        `chrome://global/content/vendor/react-dom${debugString}.js`,
        "chrome://global/content/vendor/prop-types.js",
        "chrome://global/content/vendor/react-transition-group.js",
        "chrome://global/content/vendor/redux.js",
        "chrome://global/content/vendor/react-redux.js",
        "resource://newtab/data/content/activity-stream.bundle.js",
        "resource://newtab/data/content/newtab-render.js",
      ];

      for (let script of scripts) {
        Services.scriptloader.loadSubScript(script, this.contentWindow);
      }
    } else if (event.type == "unload") {
      try {
        this.sendAsyncMessage("Unload");
      } catch (e) {
        // If the tab has been closed the frame message manager has already been
        // destroyed
      }
    } else if (event.type == "pageshow" || event.type == "visibilitychange") {
      // Don't show the notification in non-permanent private windows
      // since it is expected to have very little opt-in here.
      let contentWindowPrivate = PrivateBrowsingUtils.isContentWindowPrivate(
        this.contentWindow
      );
      if (
        this.document.visibilityState == "visible" &&
        (!contentWindowPrivate ||
          (contentWindowPrivate &&
            PrivateBrowsingUtils.permanentPrivateBrowsing))
      ) {
        this.sendAsyncMessage("AboutNewTabVisible");

        // Note: newtab feature info is currently being loaded in PrefsFeed.sys.mjs,
        // But we're recording exposure events here.
        lazy.NimbusFeatures.newtab.recordExposureEvent({ once: true });
      }
    }
  }
}
