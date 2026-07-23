/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * nsIAboutModule for about:harness, the micro-VM sandbox fiddle. Loads in the
 * parent process with the system principal so the page script can drive
 * HarnessVM directly.
 */
export class AboutHarness {
  QueryInterface = ChromeUtils.generateQI(["nsIAboutModule"]);

  getURIFlags() {
    return (
      Ci.nsIAboutModule.ALLOW_SCRIPT |
      Ci.nsIAboutModule.HIDE_FROM_ABOUTABOUT |
      Ci.nsIAboutModule.IS_SECURE_CHROME_UI
    );
  }

  newChannel(uri, loadInfo) {
    const chromeURI = Services.io.newURI(
      "chrome://browser/content/harness/aboutHarness.html"
    );
    const channel = Services.io.newChannelFromURIWithLoadInfo(
      chromeURI,
      loadInfo
    );
    channel.originalURI = uri;
    return channel;
  }
}
