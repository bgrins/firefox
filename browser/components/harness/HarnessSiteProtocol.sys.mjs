/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

const lazy = {};

ChromeUtils.defineLazyGetter(lazy, "logConsole", () =>
  console.createInstance({
    prefix: "HarnessSiteProtocol",
    maxLogLevelPref: "browser.harness.loglevel",
  })
);

/**
 * harness-site://<name>/<path> serves agent-published static sites from
 * the workspace's sites/<name>/ directory. Each site name is a distinct
 * host and thus a distinct content-principal origin, which gives sites
 * real isolated storage (IndexedDB; localStorage needs dom/clients work,
 * see docs/quick-artifacts-spike.md) — unlike the file: staging used for
 * one-shot widgets. HTML responses get a network-blocking CSP injected at serve
 * time (see actors/HarnessSiteParent.sys.mjs).
 *
 * Channels are created in the loading (content) process, which cannot read
 * the profile; bytes come from the HarnessSite actor pair, following the
 * moz-newtab-remote-renderer pattern.
 */
export class HarnessSiteProtocolHandler {
  QueryInterface = ChromeUtils.generateQI(["nsIProtocolHandler"]);

  scheme = "harness-site";

  allowPort() {
    return false;
  }

  newChannel(uri, loadInfo) {
    const channel = Cc["@mozilla.org/network/input-stream-channel;1"]
      .createInstance(Ci.nsIInputStreamChannel)
      .QueryInterface(Ci.nsIChannel);
    channel.setURI(uri);
    channel.loadInfo = loadInfo;

    const suspended = Services.io.newSuspendableChannelWrapper(channel);
    suspended.suspend();

    this.#fetch(uri, loadInfo)
      .then(({ buffer, contentType }) => {
        const stream = Cc[
          "@mozilla.org/io/arraybuffer-input-stream;1"
        ].createInstance(Ci.nsIArrayBufferInputStream);
        stream.setData(buffer, 0, buffer.byteLength);
        channel.contentStream = stream;
        channel.contentType = contentType;
        channel.contentCharset = "utf-8";
      })
      .catch(e => {
        lazy.logConsole.warn(`serve failed for ${uri.spec}: ${e.message}`);
        try {
          channel.cancel(Cr.NS_ERROR_FILE_NOT_FOUND);
        } catch (inner) {
          // channel already torn down
        }
      })
      .finally(() => suspended.resume());
    return suspended;
  }

  async #fetch(uri, loadInfo) {
    if (Services.appinfo.processType == Services.appinfo.PROCESS_TYPE_DEFAULT) {
      const { HarnessSiteParent } = ChromeUtils.importESModule(
        "moz-src:///browser/components/harness/actors/HarnessSiteParent.sys.mjs"
      );
      return HarnessSiteParent.fetchSite(uri.spec);
    }
    const windowGlobal = loadInfo.browsingContext?.window?.windowGlobalChild;
    const actor = windowGlobal?.getActor("HarnessSite");
    if (!actor) {
      throw new Error("no HarnessSite actor for load");
    }
    return actor.sendQuery("HarnessSite:Fetch", { spec: uri.spec });
  }
}
